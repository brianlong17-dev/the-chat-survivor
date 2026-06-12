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

    def _get_performance(self, player, turn_prompt):
        response = self.turn_manager.take_turn(player, turn_prompt, 
                public_response_prompt=self._performance_public_response_prompt(),
                additional_thought_nudge=self._performance_thought_nudge(), use_higher_model = True)
        
        return player, response

    def _get_judgement(self, judge, performer, turn_prompt, run_in_parallel):
        score_choices = [str(i) for i in range(1, 11)]
        response = self.turn_manager.take_turn(
            judge, turn_prompt,
            model_name=self._judge_model_name,
            game_logic_fields={"judging_criteria": (str, Field(description=self._judging_criteria_description()))},
            action_fields=self.turn_manager.create_choice_field("score", score_choices, self._score_field_description(performer)),
            public_response_prompt=self._judge_public_response_prompt(performer),
            private_thoughts_prompt="What do you secretly think?",
        )
        if not run_in_parallel:
            self.turn_manager._output_response(judge, response, pre_message_choice_reveal="score", delay=0, is_reply=True)
        return judge, response

    def _build_score_summary(self, performer_name: str, scores: dict[str, int]) -> tuple[str, int]:
        individual = ",  ".join(f"{name}: {score}" for name, score in scores.items())
        average = round(sum(scores.values()) / len(scores)) if scores else 0
        summary = (
            f"*Scores for {performer_name}* — {individual}\n"
            f"*Average score*: {average}\n"
        )
        return summary, average

    def _get_performances(self, agents, run_in_parallel):
        performance_prompt = self._performance_prompt()
        tasks = []
        for player in agents:
            
            tasks.append((player, performance_prompt))

        return self._run_tasks(tasks, self._get_performance, parallel=run_in_parallel)

    def _get_judgements(self, performer, other_players, story_text, run_in_parallel):
        judge_tasks = [
            (judge, performer, self._judging_prompt(performer, story_text), run_in_parallel)
            for judge in other_players
        ]
        return self._run_tasks(judge_tasks, self._get_judgement, parallel=run_in_parallel)

    def _broadcast_performance(self, performer, performance_response, delay=1):
        self.game_board.host_broadcast(self._take_stage_text(performer))
        self.turn_manager._output_response(performer, performance_response, delay=delay)

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
                    self.turn_manager._output_response(judge, judgement, pre_message_choice_reveal="score", delay=1, is_reply=True)
                scores[judge.name] = int(raw_score)

            summary, average = self._build_score_summary(performer.name, scores)
            self.game_board.host_broadcast(summary)
            self.game_board.append_agent_points(performer.name, average)
            round_scores[performer.name] = average

        # --- Final scoreboard -------------------------------------------------
        round_summary_str = ",  ".join(
            f"{name}: {score}" for name, score in round_scores.items()
        )
        overall_str = ",  ".join(
            f"{name}: {score}" for name, score in self.game_board.agent_scores.items()
        )
        self.game_board.host_broadcast(
            f"{self._results_header} — {round_summary_str}\n"
            f"Final standings after the round: {overall_str}\n"
        )
