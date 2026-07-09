from gameplay_management.game_targeted.base_targeted import BaseTargetedGame
from prompts.gamePrompts import GamePromptLibrary


class GameTargetedChoiceGive(BaseTargetedGame):

    @classmethod
    def display_name(cls, cfg):
        return "Giver"

    @classmethod
    def rules_description(cls, cfg):
        return "Choose a player to receive points!"
    
    def _give_game_intro(self, targeted_games_points):
        return (f"Well, enough of the scheming, lying, conning... whatever happened to *giving*!? "
        f"In this round, you will get to *pick a pal*. The player you pick will receive *{targeted_games_points} points!* "
        f"Everyone is happy! Well... except any player with no friends! hehe")
    
    def _player_intro(self, player):
        return (f"{player.name}! You're up- what player are you choosing, and why?")

    def _emit_widget(self):
        self.game_board.game_sink.on_widget_update({"kind": "give_take", "turns": self._widget_turns})

    def run_game(self):
        self._init_queue(self._shuffled_agents())
        self._init_widget()
        points_amount = GamePromptLibrary.targeted_games_points
        game_instruction = f"Choose one player to receive {points_amount} points. Explain why."

        self.game_board.host_broadcast(self._give_game_intro(points_amount),  animate_as_player=True)

        while self._agent_queue:
            player = self._pop_agent_from_queue()
            self.game_board.host_broadcast(self._player_intro(player))

            other_names = self._names(self._other_agents(player))
            action_fields = self.turn_manager._choose_name_field(other_names, game_instruction)

            response = self.turn_manager.take_turn(player, game_instruction,
                model_name="GivePointsModel", action_fields=action_fields,
                broadcast=True,
                is_reply=True)

            target_name = self.turn_manager._get_target_name_from_response(response)
            target_agent = self._agent_by_name(target_name)

            if target_agent:
                self._bump_to_back_of_queue(target_agent)

            self.game_board.append_agent_points(target_name, points_amount)
            result = f"Yay! {player.name} chooses {target_name}! They receive {points_amount} points."
            self._update_row(player.name, target_name, "give", points_amount)

            self.game_board.host_broadcast(result, is_reply=True)
            reaction = self.turn_manager.respond_to(target_agent, result, is_reply=True)
            self.turn_manager._output_response(target_agent, reaction, is_reply=True)
            self.game_board.system_broadcast(self.game_board.agent_scores, private=True)
            #needs to push after react, so they don't think it happened twice
            self.game_log._push_to_game_ledger(f"{player.name} gave points to {target_name}.")
