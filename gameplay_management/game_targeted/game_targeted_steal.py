from gameplay_management.games.game_mechanicsMixin import GameMechanicsMixin
from prompts.gamePrompts import GamePromptLibrary


class GameTargetedChoiceSteal(GameMechanicsMixin):

    @classmethod
    def display_name(cls, cfg):
        return "Stealer"

    @classmethod
    def rules_description(cls, cfg):
        return "Choose a player to steal points from!"

    def _game_intro(self, points_amount):
        return (
            f"Well, it's time to lay down your mark.. "
            f"In this round, you will get to *STEAL*. Whatever player you pick, you will receive {points_amount} points... and they will *LOSE* them! "
            f"If you choose a player with less than {points_amount} points, their points wont go below zero, and you won't receive the full {points_amount} points."
        )

    def _player_intro(self, player):
        return f"{player.name}! You're up- what player are you choosing to steal from, and why?"

    def run_game(self):
        points_amount = GamePromptLibrary.targeted_games_points
        game_instruction = (
            f"Choose one player to steal {points_amount} points from. "
            f"If you steal from a player with less than {points_amount}, you'll only get whatever points they have, maybe zero. "
            f"The name of the player whose points you are going to STEAL:"
        )
        thought_nudge = f"If you try to steal from someone with 0 points, you essentially pass."

        self.game_board.host_broadcast(self._game_intro(points_amount), animate_as_player=True)

        ordered_agents = self._shuffled_agents()
        while ordered_agents:
            player = ordered_agents.pop(0)
            self.game_board.host_broadcast(self._player_intro(player))

            other_names = self._names(self._other_agents(player))
            action_fields = self.turn_manager._choose_name_field(other_names, game_instruction)

            response = self.turn_manager.take_turn(
                player, game_instruction,
                model_name="StealPointsModel",
                action_fields=action_fields,
                additional_thought_nudge=thought_nudge,
                broadcast=True,
                is_reply=True,
            )

            target_name = self.turn_manager._get_target_name_from_response(response)
            target_agent = self._agent_by_name(target_name)

            if target_agent and target_agent in ordered_agents:
                ordered_agents.remove(target_agent)
                ordered_agents.append(target_agent)

            current_victim_points = self.game_board.get_agent_score(target_agent.name)
            actual_steal = min(points_amount, max(0, current_victim_points))

            ledger_message = None
            if actual_steal <= 0:
                result = (
                    f"Awkward... {player.name} tried to steal from {target_agent.name}, "
                    f"but they have empty pockets! No points changed hands."
                )
                reactor = player
            else:
                result = (
                    f"Oooooh! {player.name} steals from {target_agent.name}! "
                    f"{player.name} gains {actual_steal} points, and {target_agent.name} loses them!"
                    )
                ledger_message = f"{player.name} stole from {target_agent.name}."
                
                
                reactor = target_agent

            self.game_board.append_agent_points(player.name, actual_steal)
            self.game_board.append_agent_points(target_agent.name, -actual_steal)

            self.game_board.host_broadcast(result, is_reply=True)
            reaction = self.turn_manager.respond_to(reactor, result, is_reply=True)
            self.turn_manager._output_response(reactor, reaction, is_reply=True)
            self.game_board.system_broadcast(self.game_board.agent_scores, private=True)
            #needs to push after react, so they don't think it happened twice
            if ledger_message:
                self.game_log._push_to_game_ledger(ledger_message)
