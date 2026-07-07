import random
from collections import Counter
from gameplay_management.games.game_mechanicsMixin import GameMechanicsMixin


class GameWisdom(GameMechanicsMixin):

    WINNER_POINTS = 3
    CROWD_POINTS = 1

    @classmethod
    def display_name(cls, cfg):
        return "Wisdom of the crowd"

    @classmethod
    def rules_description(cls, cfg):
        return (f"Are you a leader? Or a follower? In this game it's good to be both! "
               "This is a game of superlatives! We will vote who we think is the most... cute, rude, funny whatever. "
               f"If you vote *with* the crowd, you get {cls.CROWD_POINTS} point! If you win the vote, you get {cls.WINNER_POINTS} points! "
        )

    def _questions(self):
        q1 = "Who do you think is the most vengeful player if you cross them? "
        q2 = "Which player do you think is the most unique voice in the competition? "
        q3 = "Who do you think is the biggest outsider? "
        q4 = "Who here has the warmest heart? "
        q5 = "Which player would you least like to meet in a dark alley? "
        return [q1, q2, q3, q4, q5]

    def _choice_field_name(self, i):
        return f"choice_{i}"

    def _statement_field_name(self, i):
        return f"statement_{i}"

    def _collect_votes(self, agent):
        names = self._names(self.agents)
        questions = self._questions()

        action_fields = {}
        for i, question in enumerate(questions):
            choice_field = self.turn_manager._choose_name_field(
                names, f"Who do you vote for: '{question}'", field_name=self._choice_field_name(i))
            statement_field = self.turn_manager.create_basic_field(
                self._statement_field_name(i), f"For '{question}' — what do you say as your vote is revealed? Keep it brief. ")
            action_fields.update(choice_field)
            action_fields.update(statement_field)

        response = self.turn_manager.take_turn(
            agent,
            turn_prompt=("This is your time to fill out your votes. It is done in secret and in unison before any votes are revealed. "
                         "For each question, choose a player and a one-liner for when your vote is revealed. "
                         "Voting with the majority earns you a point. "),
            private_thoughts_prompt="Will you try to anticipate the vote of the crowd, or stick to your gut? ",
            action_fields=action_fields,
            broadcast=False,
            multi_answer_model=True)
        return agent, response

    def _process_results(self, vote_counter, voters_by_choice):
        if not vote_counter:
            return

        top_count = max(vote_counter.values())
        winners = [name for name, count in vote_counter.items() if count == top_count]
        winner_string = "winner" if len(winners)==1 else "winners"

        self._host_broadcast(f"The crowd has spoken! {self.points_string(self.WINNER_POINTS)} to our {winner_string}: *{self.format_list(winners)}!* ")
        for winner in winners:
            self.game_board.append_agent_points(winner, self.WINNER_POINTS)

        crowd = []
        for winner in winners:
            for voter in voters_by_choice.get(winner, []):
                if voter not in crowd:
                    crowd.append(voter)

        if crowd:
            self._host_broadcast(f"Voting with the crowd, {self.points_string(self.CROWD_POINTS)} each to: {self.format_list(crowd)}. ")
            for voter in crowd:
                self.game_board.append_agent_points(voter, self.CROWD_POINTS)
                
        for winner in winners:
            host_question = self._get_host_question(winner, tie=len(winners) > 1)
            self._host_broadcast(host_question)
            self.turn_manager.respond_to(self._agent_by_name(winner), f"Respond to the host's question and result of the vote: {host_question}", public_response_prompt= "Be reactive and honest rather than performative", broadcast=True, is_reply=True)

    def _get_host_question(self, winner, tie=False):
        if tie:
            variations = [
                f"*{winner}*, you're sharing the top spot this round — does splitting the crowd feel like a win or a snub? ",
                f"A tie at the top, and *{winner}*, you're in it. What does it say that the room couldn't just pick you? ",
                f"*{winner}*, you tied for the lead this vote. How do you feel about company at the summit? ",
            ]
        else:
            variations = [
                f"*{winner}*, how does it feel to come out on top of this vote? ",
                f"*{winner}*, the room picked you this round. What's going through your head? ",
                f"*{winner}*, you're at the top this vote — is this where you expected to be? ",
            ]
        return random.choice(variations)

    def run_game(self):
        self._host_broadcast("We have a game where, turn by turn, we vote on which player best suits a category. If you vote with the majority, you win a point! ")

        questions = self._questions()
        results = self._run_tasks([(agent,) for agent in self.agents], self._collect_votes)

        for i, question in enumerate(questions):
            self._host_broadcast(f"Ok, question {i + 1}. {question}", delay=1)

            vote_counter = Counter()
            voters_by_choice = {}
            for agent, response in results:
                choice = getattr(response, self._choice_field_name(i))
                vote_counter[choice] += 1
                voters_by_choice.setdefault(choice, []).append(agent.name)
                statement=getattr(response, self._statement_field_name(i))
                output = f"*{choice}*\n{statement}"

                self.turn_manager._output_response(agent, response, single_message_overwrite=output, is_reply=True, delay = 1)

            self._process_results(vote_counter, voters_by_choice)
