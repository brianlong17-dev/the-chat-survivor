
from gameplay_management.base_manager import BaseRound


class InterviewRound(BaseRound):
    #This is for dev testing

    @classmethod
    def display_name(cls, cfg):
        return "Interview Round"

    @classmethod
    def rules_description(cls, cfg):
        return "The host interviews each player one-on-one in a private conversation."

    @classmethod
    def is_private_round(cls):
        return True

    def _interview_player(self, player):
        should_continue = True
        users = ["Host", player.name]
        conversation_id = None

        while should_continue:
            print(f"Now speaking to {player.name} \n")
            question = input("Host: ").strip()
            if not conversation_id:
                conversation_id = self.game_board.log_new_restricted_conversation(users, "Host", question)
            else:
                self.game_board.log_message_to_conversation(conversation_id, "Host", question)

            result = self.turn_manager.take_turn(player, "Continue the conversation. ",
                model_name="basic_turn",
                public_response_prompt="This is your public response to the host. ")
            self.game_board.log_message_to_conversation(conversation_id, player.name, result.public_response)
            print(f"{player.name}: {result.public_response} \n")

            action = self.game_board.game_sink.get_user_input_multiple_choice(
                "continue", "What would you like to do?", ["Continue conversation", "End conversation"]
            )
            should_continue = action == "Continue conversation"

        return conversation_id

    def run_game(self):
        for agent in self._shuffled_agents():
            conv_id = self._interview_player(agent)
            if conv_id:
                self.game_board.close_private_conversation(conv_id)
