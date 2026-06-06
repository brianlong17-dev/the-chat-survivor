from pydantic import Field

from gameplay_management.games.game_mechanicsMixin import GameMechanicsMixin


class GamePerformBase(GameMechanicsMixin):
    """Shared 'perform → peers score 1-10 → average becomes points' mechanic.

    Subclasses supply the prompt hooks below to choose register (sob story,
    comedy roast, etc.). The run loop, scoring math, and broadcasting are
    identical across variants.
    """

    # --- Class-level labels (override on subclass) ---
    _performance_model_name = "Performance"
    _judge_model_name = "PerformanceJudge"
    _results_header = "🎭 RESULTS"

    # ------------------------------------------------------------------
    # Prompt hooks — subclasses override these
    # ------------------------------------------------------------------

    def _host_intro_text(self):
        raise NotImplementedError

    def _performance_prompt(self):
        raise NotImplementedError

    def _performance_public_response_prompt(self):
        raise NotImplementedError

    def _performance_thought_nudge(self):
        raise NotImplementedError

    def _take_stage_text(self, performer):
        raise NotImplementedError

    def _judging_prompt(self, performer, story_text):
        raise NotImplementedError

    def _score_field_description(self, performer):
        raise NotImplementedError

    def _judging_criteria_description(self):
        raise NotImplementedError

    def _judge_public_response_prompt(self, performer):
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Core run loop and helpers
    # ------------------------------------------------------------------

    def _get_performance(self, player, turn_prompt, response_model):
        response = player.take_turn_standard(turn_prompt, self.game_board, response_model, use_higher_model=False)
        return player, response

    def _get_judgement(self, judge, turn_prompt, response_model, run_in_parallel):
        response = judge.take_turn_standard(turn_prompt, self.game_board, response_model)
        if not run_in_parallel:
            self.publicPrivateResponse(judge, response, delay=0)
        return judge, response

    def _build_score_summary(self, performer_name: str, scores: dict[str, int]) -> tuple[str, int]:
        individual = ",  ".join(f"{name}: {score}" for name, score in scores.items())
        average = round(sum(scores.values()) / len(scores)) if scores else 0
        summary = (
            f"🎭 Scores for {performer_name} — {individual}\n"
            f"⭐ Average: {average} points awarded!"
        )
        return summary, average

    def _get_performances(self, agents, run_in_parallel):
        performance_prompt = self._performance_prompt()
        tasks = []
        for player in agents:
            response_model = self.turn_manager._create_model(
                player,
                model_name=self._performance_model_name,
                public_response_prompt=self._performance_public_response_prompt(),
                additional_thought_nudge=self._performance_thought_nudge(),
            )
            tasks.append((player, performance_prompt, response_model))

        return self._run_tasks(tasks, self._get_performance, parallel=run_in_parallel)

    def _get_judgement_model(self, player_judging, performer):
        score_choices = [str(i) for i in range(1, 11)]

        action_fields = self.turn_manager.create_choice_field(
            "score",
            score_choices,
            self._score_field_description(performer),
        )

        game_logic_fields = {
            "judging_criteria": (
                str,
                Field(description=self._judging_criteria_description()),
            ),
        }
        return self.turn_manager._create_model(
            player_judging,
            model_name=self._judge_model_name,
            game_logic_fields=game_logic_fields,
            action_fields=action_fields,
            public_response_prompt=self._judge_public_response_prompt(performer),
            private_thoughts_prompt="What do you secretly think?",
        )

    def _get_judgements(self, performer, other_players, story_text, run_in_parallel):
        judge_tasks = []
        for judge in other_players:
            judging_prompt = self._judging_prompt(performer, story_text)
            response_model = self._get_judgement_model(judge, performer)
            judge_tasks.append((judge, judging_prompt, response_model, run_in_parallel))

        return self._run_tasks(judge_tasks, self._get_judgement, parallel=run_in_parallel)

    def _broadcast_performance(self, performer, performance_response, delay=1):
        self.game_board.host_broadcast(self._take_stage_text(performer))
        self.publicPrivateResponse(performer, performance_response, delay)

    def run_game(self):
        return self.run_game_perform()

    def run_game_perform(self):
        # --- Host intro -------------------------------------------------------
        self.game_board.host_broadcast(self._host_intro_text())
        agents = self._shuffled_agents()
        run_in_parallel = True

        # --- Phase 1: Generate all performances in parallel (higher model) ---
        performances = self._get_performances(agents, run_in_parallel)

        # --- Phase 2: Perform and judge one by one ---------------------------
        round_scores: dict[str, int] = {}

        for performer, performance_response in performances:
            self._broadcast_performance(performer, performance_response)

            other_players = [a for a in agents if a is not performer]
            story_text = performance_response.public_response
            judgements = self._get_judgements(performer, other_players, story_text, run_in_parallel)

            scores = {}
            for judge, judgement in judgements:
                raw_score = getattr(judgement, "score", None)
                if run_in_parallel:
                    self.game_board.handle_public_private_output(
                        judge, judgement, delay=1, is_reply=True, pre_string=f"*{raw_score}*"
                    )

                try:
                    scores[judge.name] = int(raw_score)
                except (TypeError, ValueError):
                    scores[judge.name] = 5  # fallback if model misbehaves

            summary, average = self._build_score_summary(performer.name, scores)
            self.game_board.host_broadcast(summary)
            self.game_board.append_agent_points(performer.name, average)
            round_scores[performer.name] = average
            
            if False: #score reaction
                performer_score_response = self.turn_manager.respond_to(performer, summary)
                self.publicPrivateResponse(performer, performer_score_response)

        # --- Final scoreboard -------------------------------------------------
        round_summary_str = ",  ".join(
            f"{name}: {score}" for name, score in round_scores.items()
        )
        overall_str = ",  ".join(
            f"{name}: {score}" for name, score in self.game_board.agent_scores.items()
        )
        self.game_board.host_broadcast(
            f"{self._results_header} — {round_summary_str}\n"
            f"🏆 Overall standings — {overall_str}\n"
        )
