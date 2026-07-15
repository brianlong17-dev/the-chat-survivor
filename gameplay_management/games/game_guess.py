from concurrent.futures import ThreadPoolExecutor
import random
from gameplay_management.games.game_mechanicsMixin import GameMechanicsMixin



class GameGuess(GameMechanicsMixin):
    @classmethod
    def display_name(cls, cfg):
        return "Guess"

    @classmethod
    def rules_description(cls, cfg):
        return f"Guess the correct number (1-{cfg.guess_number_range}) to win!"

    # ------------------------------------------------------------------
    # Guess the Number - this was an initial test for parallel turns
    # ------------------------------------------------------------------

    def _get_number_guess(self, player, turn_prompt, action_fields):
        response = self.turn_manager.take_turn(player, turn_prompt, action_fields = action_fields)
        return player, response

    def _widget_update_entry(self, name, state=None, guess=None, correct=None, points=None):
        for entry in self._widget_rows:
            if entry["name"] == name:
                if state:
                    entry["state"] = state
                if guess is not None:
                    entry["guess"] = guess
                if correct is not None:
                    entry["correct"] = correct
                if points is not None:
                    entry["points"] = points
                self._emit_widget()
                return

    def _emit_widget(self):
        self.game_board.game_sink.on_widget_update({
            "kind": "guess",
            "range": self._widget_range,
            "rows": self._widget_rows,
        })

    def _initialise_widget(self, agents, number_range):
        self._widget_range = {"min": 1, "max": number_range}
        self._widget_rows = [
            {"name": agent.name, "state": "waiting", "guess": None, "correct": None, "points": None}
            for agent in agents
        ]
        self._emit_widget()

    def _build_guess_the_number_result_string(self, correct, incorrect, number_range):
        parts = []

        if correct:
            names = self.format_list([p.name for p in correct])
            parts.append(f"CORRECT! {names} each earn *{number_range} points*!\n\n")

        if incorrect:
            names = self.format_list([p.name for p in incorrect])
            parts.append(f"FLOP! {names} missed the mark.\n\n")

        return "  ".join(parts) if parts else "No valid guesses this round."

    def run_game(self):
        self.run_game_guess_the_number()
        
    def run_game_guess_the_number(self): #just none while i set up

        # --- Config -----------------------------------------------------------
        
        number_range = self.cfg.guess_number_range 
        winning_number = random.randint(1, number_range)
        points_for_correct = number_range

        # --- Host intro -------------------------------------------------------
        host_intro = (
            f"GUESS THE NUMBER!\n"
            f"I'm thinking of a number between 1 and {number_range}.\n"
            f"Guess correctly and you'll win {points_for_correct} points!"
        )
        self.game_board.host_broadcast(host_intro)

        # --- Build the response model (same for everyone) ---------------------
        valid_choices = list(range(1, number_range + 1))
        action_fields = self.turn_manager.create_choice_field(
            "choice",
            [str(i) for i in valid_choices],
            f"Which number do you guess? Choose between 1 and {number_range}.",
        )
        player_prompt = (
            f"Guess a number between 1 and {number_range}. "
            f"A correct guess wins you {points_for_correct} points. "
            f"What number feels right?"
        )

        
        # --- Collect guesses in parallel (mirrors PD / vote patterns) ---------
        self._initialise_widget(self.simulationEngine.agents, number_range)

        futures = []
        with ThreadPoolExecutor() as executor:
            for agent in self.simulationEngine.agents:
                future = executor.submit(
                    self._get_number_guess, agent, player_prompt, action_fields
                )
                futures.append(future)

        for agent in self.simulationEngine.agents:
            self._widget_update_entry(agent.name, state="picked")

        results = [f.result() for f in futures]

        # --- Publish each player's public words & guess -----------------------
        correct = []
        incorrect = []

        for player, response in results:
            raw_choice = getattr(response, "choice", None)
            guess = int(raw_choice)
            self._widget_update_entry(player.name, state="revealed", guess=guess)
            self.turn_manager._output_response(player, response, pre_message_choice_reveal="choice", delay=1, is_reply=True)

            

            is_correct = guess == winning_number
            

            if is_correct:
                correct.append(player)
            else:
                incorrect.append(player)

        # --- Reveal and award points ------------------------------------------
        self.game_board.host_broadcast(
            f"The correct number was... **{winning_number}**!"
        )

        result_string = self._build_guess_the_number_result_string(
            correct, incorrect, points_for_correct
        )
        self.game_board.host_broadcast(result_string)

        for player in correct:
            self.game_board.append_agent_points(player.name, points_for_correct)
            self._widget_update_entry(player.name, correct=True, points=points_for_correct)
        for player in incorrect:
            self._widget_update_entry(player.name, correct=False)

        #DELAY
        # --- Reactions (optional but consistent with PD pattern) --------------
        
        reaction_futures = []
        agents_for_response = []
        if len(correct) == 1:
            agents_for_response.append(correct[0])
        if len(incorrect) == 1:
            agents_for_response.append(incorrect[0])
        if agents_for_response:
            with ThreadPoolExecutor() as executor:
                for player in agents_for_response:
                    future = executor.submit(self.turn_manager.respond_to, player, result_string, broadcast=False)
                    reaction_futures.append((player, future))

            
            for player, future in reaction_futures:
                reaction = future.result()
                self.turn_manager._output_response(player, reaction, delay=1, is_reply=True)
