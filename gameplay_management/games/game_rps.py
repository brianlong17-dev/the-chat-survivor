from concurrent.futures import ThreadPoolExecutor
from gameplay_management.games.game_mechanicsMixin import GameMechanicsMixin


class GameRockPaperScissors(GameMechanicsMixin):

    BEATS = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock",
    }

    @classmethod
    def display_name(cls, cfg):
        return "Rock Paper Scissors"

    @classmethod
    def rules_description(cls, cfg):
        cfg_ = cfg
        return (
            f"Win: {cfg_.rps_points_win} pts | Tie: {cfg_.rps_points_tie} pts each | Lose: 0 pts."
        )

    def _points_string(self):
        cfg = self.cfg
        return (
            f"- WIN  → {cfg.rps_points_win} points\n"
            f"- TIE  → {cfg.rps_points_tie} points each\n"
            f"- LOSE → 0 points\n"
        )

    def _get_rps_choice(self, player, opponent):
        turn_prompt = (
            "ROCK PAPER SCISSORS!\n"
            f"You are facing {opponent.name}.\n"
            "Points on the line:\n"
            f"{self._points_string()}"
            "Choose your move — what will it be?"
        )
        choices = ["rock", "paper", "scissors"]
        action_fields = self.turn_manager.create_choice_field("action", choices)
        additional_thought_nudge = (
            "Think carefully — what would your opponent choose? "
            "Is there a psychological edge you can exploit?"
        )
        return self.turn_manager.take_turn(player, turn_prompt,
            model_name="rps_choice",
            additional_thought_nudge=additional_thought_nudge,
            action_fields=action_fields,
        )

    def _calculate_outcome(self, choice0, choice1, name0, name1):
        cfg = self.cfg
        c0 = choice0.strip().lower().replace(".", "")
        c1 = choice1.strip().lower().replace(".", "")

        if c0 not in self.BEATS or c1 not in self.BEATS:
            return 0, 0, f"Someone made an invalid move! No points awarded."

        if c0 == c1:
            pts = cfg.rps_points_tie
            msg = f"It's a TIE! Both {name0} and {name1} chose *{c0}*. Each gets {pts} points."
            return pts, pts, msg

        if self.BEATS[c0] == c1:
            pts = cfg.rps_points_win
            msg = f"*{c0.upper()}* beats {c1}! {name0} WINS and earns {pts} points!"
            return pts, 0, msg

        pts = cfg.rps_points_win
        msg = f"*{c1.upper()}* beats {c0}! {name1} WINS and earns {pts} points!"
        return 0, pts, msg

    def _widget_update_entry(self, name, state=None, choice=None, result=None, points=None):
        for pair in self._widget_pairs:
            for entry in pair:
                if entry["name"] == name:
                    if state:
                        entry["state"] = state
                    if choice:
                        entry["choice"] = choice
                    if result:
                        entry["result"] = result
                    if points is not None:
                        entry["points"] = points
                    self._emit_widget()
                    return

    def _widget_pair_entry_initial(self, pair):
        couple = []
        for agent in pair:
            entry = {"name": agent.name, "state": "waiting"}
            entry["choice"] = None
            entry["result"] = None
            entry["points"] = None
            couple.append(entry)
        return couple

    def _emit_widget(self):
        self.game_board.game_sink.on_widget_update({"kind": "rps", "pairs": self._widget_pairs})

    def _initialise_widget(self, pairs):
        self._widget_pairs = [self._widget_pair_entry_initial(pair) for pair in pairs]
        self._emit_widget()

    def _execute_pairs(self, pairs):
        for agent0, agent1 in pairs:
            self.game_board.host_broadcast(f"{agent0.name} vs {agent1.name} — Rock, Paper, or Scissors?\n")

            with ThreadPoolExecutor() as executor:
                future0 = executor.submit(self._get_rps_choice, agent0, agent1)
                future1 = executor.submit(self._get_rps_choice, agent1, agent0)
                results = [future0.result(), future1.result()]

            for agent in (agent0, agent1):
                self._widget_update_entry(agent.name, state="picked")

            choices = []
            for agent, res in zip((agent0, agent1), results):
                self.turn_manager._output_response(agent, res, post_message_choice_reveal="action", is_reply=True)
                choice = res.action.strip().lower()
                self._widget_update_entry(agent.name, state="revealed", choice=choice)
                choices.append(choice)

            p0_gain, p1_gain, msg = self._calculate_outcome(choices[0], choices[1], agent0.name, agent1.name)

            if p0_gain > p1_gain:
                winner, loser = agent0.name, agent1.name
            elif p1_gain > p0_gain:
                winner, loser = agent1.name, agent0.name
            else:
                winner, loser = "draw", "draw"

            for agent, gain in zip((agent0, agent1), (p0_gain, p1_gain)):
                result = "draw" if winner == "draw" else ("winner" if winner == agent.name else "loser")
                self._widget_update_entry(agent.name, result=result, points=gain)
                self.game_board.append_agent_points(agent.name, gain)

            self.game_board.host_broadcast(f"{msg}\n")

            for agent in (agent0, agent1):
                self.turn_manager.respond_to(agent, msg, broadcast=True, is_reply=True)

    def run_game(self):
        rps_game_intro = (
        "*ROCK PAPER SCISSORS!*\n"
        "It's the oldest game in the book — pure instinct, pure psychology.\n"
        "You'll be paired up and make your move simultaneously. "
        "Read your opponent, trust your gut, and may the best hand win!"
    )
        self.game_board.host_broadcast(rps_game_intro)

        agents = list(self.simulationEngine.agents)
        pairs, leftover = self._generate_random_pairings(agents)

        if leftover:
            auto_pts = self.cfg.rps_odd_player_auto_points
            self.game_board.host_broadcast(
                f"{leftover.name} has no opponent this round — they automatically receive {auto_pts} points.\n\n"
            )
            self.game_board.append_agent_points(leftover.name, auto_pts)
            
        
        self._initialise_widget(pairs)
        self._execute_pairs(pairs)
