
from gameplay_management.base_manager import BaseRound
from models.player_models import DynamicModelFactory


class InterviewRound(BaseRound):
    #This is for dev testing

    @classmethod
    def display_name(cls, cfg):
        return "Interview Round"

    @classmethod
    def rules_description(cls, cfg):
        return "The host interviews each player one-on-one in a private conversation."

    @classmethod
    def is_discussion(cls):
        return False

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
                conversation_id = self.gameBoard.log_new_restricted_conversation(users, "Host", question)
            else:
                self.gameBoard.log_message_to_conversation(conversation_id, "Host", question)

            public_response_prompt = "This is your public response to the host. "
            user_content = "Continue the conversation. "
            basic_model = DynamicModelFactory.create_model_(player, "basic_turn", public_response_prompt=public_response_prompt)
            result = player.take_turn_standard(user_content, self.gameBoard, basic_model)
            self.gameBoard.log_message_to_conversation(conversation_id, player.name, result.public_response)
            print(f"{player.name}: {result.public_response} \n")

            action = self.gameBoard.game_sink.get_user_input_multiple_choice(
                "continue", "What would you like to do?", ["Continue conversation", "End conversation"]
            )
            should_continue = action == "Continue conversation"

        return conversation_id

    def run_game(self):
        for agent in self._shuffled_agents():
            conv_id = self._interview_player(agent)
            if conv_id:
                self.gameBoard.close_private_conversation(conv_id)
