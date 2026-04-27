from collections import defaultdict
from dataclasses import dataclass

from gameplay_management.game_cycle.game_cycle import CycleRound
from models.player_models import DynamicModelFactory


@dataclass
class _PlayerState:
    agent: object
    held: int = 1   # knives currently in hand
    stabs: int = 0  # knives received this round (resets each round)

    @property
    def name(self) -> str:
        return self.agent.name


class GameKnives2(CycleRound):

    PASS = "Pass"
    SOLE_SURVIVOR_BONUS = 5

    # Behaviour toggles — flip in cfg or subclass for variants.
    CHATTY_STABBING = False
    RUNNER_UP_POINTS = True

    @classmethod
    def display_name(cls, cfg):
        return "Knives"

    @classmethod
    def rules_description(cls, cfg):
        return (
            "Every player starts with a knife. The lights go off — each player secretly stabs someone or passes "
            "(keeping their knife for later). The lights come back on: the player with the most knives in their "
            "back dies. Ties mean all tied players die. Dead players' knives are randomly redistributed among "
            "survivors. Players who passed accumulate knives for future rounds. If every remaining player dies "
            "simultaneously, they all win and earn bonus points (1 point in round 1, 2 in round 2, etc.). "
            "Last 3 standing earn points."
        )

    @classmethod
    def is_game(cls):
        return True

    # ─────────────────────────── formatting helpers ───────────────────────────

    def _knife_string(self, count):
        return f"{count} {'knife' if count == 1 else 'knives'}"

    def _knives_count_string(self, players):
        grouped = defaultdict(list)
        for p in players:
            grouped[p.held].append(p.name)

        lines = ["Each of you holds —"]
        for count in sorted(grouped, reverse=True):
            lines.append(f"{'🗡' * count} - {self.format_list(grouped[count])}")
        return "\n".join(lines)

    # ─────────────────────────── per-player turn ───────────────────────────

    def _make_choice(self, state, players, chatty):
        circle_names = [p.name for p in players]
        allowed_choices = circle_names + [self.PASS]

        action_fields = {}
        for i in range(1, state.held + 1):
            action_fields |= self.create_choice_field(
                f"knife_{i}",
                allowed_choices,
                f"Knife {i}: name a target, or pass.",
            )

        public_response_prompt = (
            "Speak, or don't. The lights are out. No one sees what you do — only what you say."
            if chatty
            else "Optional. Not broadcast."
        )

        model = DynamicModelFactory.create_model_(
            state.agent,
            action_fields=action_fields,
            public_response_prompt=public_response_prompt,
            additional_thought_nudge=(
                "Who is the threat? Spread the knives, or focus them? "
                "Pass — and keep them for later?"
            ),
        )

        other_names = [n for n in circle_names if n != state.name]
        user_content = (
            f"The lights are out. You hold {self._knife_string(state.held)}. "
            f"For each — name a target, or pass and keep it. "
            f"You may stab the same player twice. You may stab yourself. "
            f"The circle: {self.format_list(other_names)}."
        )

        result = state.agent.take_turn_standard(user_content, self.gameBoard, model)
        if chatty:
            self.gameBoard.handle_public_private_output(state.agent, result)

        targets = []
        for i in range(1, state.held + 1):
            choice = getattr(result, f"knife_{i}").strip()
            # Treat unknown choices as Pass — Pydantic Literal should make this unreachable.
            if choice in circle_names:
                targets.append(choice)

        if targets:
            self.debug_print(
                f"{state.name} ({self._knife_string(state.held)}) stabs {self.format_list(targets)}"
            )
        else:
            self.debug_print(f"{state.name} ({self._knife_string(state.held)}) passes.")

        return state.name, targets

    # ─────────────────────────── announcements ───────────────────────────

    def _announce_stabbings(self, players_by_stabs_desc):
        lines = ["The lights return."]
        for p in players_by_stabs_desc:
            if p.stabs > 0:
                lines.append(f"{p.name} — {'🔪' * p.stabs}")
        self._host_broadcast("\n".join(lines), 1)

    def _announce_deaths(self, dead_names, count):
        self.gameBoard.host_broadcast(
            f"{self._knife_string(count)}. {self.format_list(dead_names)}. They fall."
        )
        for name in dead_names:
            self.private_system_message(
                self._agent_by_name(name),
                f"{name} — you fell in the dark. You did not fall from the game. Onwards.",
                silent=True,
            )

    # ─────────────────────────── post-round flourishes ───────────────────────────

    def _runner_up_bonus(self, players_by_stabs_desc):
        max_stabs = max(p.stabs for p in players_by_stabs_desc)
        survivors = [p for p in players_by_stabs_desc if p.stabs < max_stabs]
        if not survivors:
            return

        top = survivors[0].stabs  # already sorted descending
        if top == 0:
            return

        runners_up = [p for p in survivors if p.stabs == top]
        plural = "s" if top > 1 else ""
        self.gameBoard.host_broadcast(
            f"Most-wounded survivor — {self.format_list([p.name for p in runners_up])}. "
            f"{top} blade{plural}. {top} point{plural}.",
            delay=1,
        )
        for p in runners_up:
            self.gameBoard.append_agent_points(p.name, top)

        for p in runners_up:
            self._basic_turn(
                p.agent,
                f"{top} blade{plural} found you. You stand. "
                f"Speak — accuse, or hold your tongue.",
                "Address the circle, in your own voice.",
            )

    def _optional_pitch(self, players):
        for p in players:
            self._basic_turn(
                p.agent,
                "The lights still hold. Speak, before they die again.",
                "A few words to the circle, or silence. Either is allowed.",
                private_thoughts_prompt="Direct the group? Or draw attention to yourself?",
                optional=True,
            )

    # ─────────────────────────── round mechanics ───────────────────────────

    def _collect_stabs(self, players):
        """Run choices in parallel and mutate held/stabs on each PlayerState."""
        for p in players:
            p.stabs = 0

        tasks = [(p, players, self.CHATTY_STABBING) for p in players if p.held > 0]
        results = self._run_tasks(tasks, self._make_choice)

        by_name = {p.name: p for p in players}
        for player_name, targets in results:
            by_name[player_name].held -= len(targets)
            for target_name in targets:
                by_name[target_name].stabs += 1

    def _reveal_stabs_privately(self, players):
        for p in players:
            if p.stabs == 0:
                self.private_system_message(p.agent, "You feel for blades. None.", silent=True)
            else:
                plural = "s" if p.stabs > 1 else ""
                self.private_system_message(
                    p.agent, f"{p.stabs} blade{plural}. Still standing.", silent=True
                )

    def _award_round_points(self, players_by_stabs_desc, survivors):
        if self.RUNNER_UP_POINTS:
            self._runner_up_bonus(players_by_stabs_desc)
            return
        self.gameBoard.host_broadcast(
            f"{self.format_list([p.name for p in survivors])}. A point each, for standing."
        )
        for p in survivors:
            self.gameBoard.append_agent_points(p.name, 1)

    def _redistribute(self, pool_size, survivors):
        """Round-robin the dead's knives starting from the least-stabbed survivor."""
        if not pool_size or not survivors:
            return
        ordered = sorted(survivors, key=lambda p: p.stabs)
        for i in range(pool_size):
            ordered[i % len(ordered)].held += 1

    # ─────────────────────────── main loop ───────────────────────────

    def run_game(self):
        self._cycle_game_setup()
        self._debug = False

        players = [_PlayerState(agent=a) for a in self._shuffled_agents()]
        for p in players:
            self.private_system_message(
                p.agent,
                "A parlor game. The knives are theatre. The points are not. "
                "Neither is your place in this competition. Play it cold.",
            )
        self._broadcast_welcome()

        round_number = 0
        while len(players) > 1:
            self._compress_round()
            round_number += 1
            next_players = self._play_round(players, round_number)
            if next_players is None:
                break
            players = next_players

        self._cycle_game_teardown()

    def _broadcast_welcome(self):
        points_string = (
            "The most-wounded survivor takes a point for each blade."
            if self.RUNNER_UP_POINTS
            else "A point for every round you remain."
        )
        self.gameBoard.host_broadcast(
            "A circle. A knife each.\n"
            "The lights die. Choose, or pass.\n"
            "The lights return. The most-stabbed falls. Ties fall together.\n"
            "Survive a stabbing — the blades are yours next round.\n"
            "Fall together, win together.\n"
            f"{points_string}\n"
            "Lights out."
        )

    def _play_round(self, players, round_number):
        """Run one round. Returns the surviving players, or None if the game ends."""
        self.gameBoard.host_broadcast(self._knives_count_string(players), delay=1)
        if self.optional_responses_in_use:
            self._optional_pitch(players)
        self.gameBoard.host_broadcast(f"Round {round_number}. Lights out.", delay=1)

        self._collect_stabs(players)
        self._reveal_stabs_privately(players)

        max_stabs = max(p.stabs for p in players)
        dead = [p for p in players if p.stabs == max_stabs]
        survivors = [p for p in players if p.stabs < max_stabs]
        by_stabs_desc = sorted(players, key=lambda p: p.stabs, reverse=True)

        self._announce_stabbings(by_stabs_desc)

        # Everyone tied — either nobody got stabbed (continue) or the whole circle goes down.
        if not survivors:
            if max_stabs == 0:
                self.gameBoard.host_broadcast("The dark passed quietly. Again.")
                return players
            self.gameBoard.host_broadcast(
                f"{self.format_list([p.name for p in players])} — "
                f"{self._knife_string(max_stabs)} each. The circle falls together."
            )
            return None

        self._announce_deaths([p.name for p in dead], max_stabs)
        self._award_round_points(by_stabs_desc, survivors)

        # Pool the dead's knives (held + lodged-in-back) for redistribution to survivors.
        pool_size = sum(p.held + p.stabs for p in dead)

        if len(survivors) == 1:
            sole = survivors[0]
            self.gameBoard.host_broadcast(
                f"One stands. {sole.name}. {self.SOLE_SURVIVOR_BONUS} points to the last to stand."
            )
            self.gameBoard.append_agent_points(sole.name, self.SOLE_SURVIVOR_BONUS)
            return None

        self.gameBoard.host_broadcast(
            f"{self._knife_string(pool_size)}, taken from the fallen. Redivided.",
            delay=1,
        )
        # Survivors keep the knives in their backs as next-round ammunition.
        for p in survivors:
            p.held += p.stabs
        self._redistribute(pool_size, survivors)

        return survivors
