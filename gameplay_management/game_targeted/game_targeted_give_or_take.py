from gameplay_management.game_targeted.base_targeted import BaseTargetedGame


class GameTargetedChoiceGiveOrTake(BaseTargetedGame):

    @classmethod
    def display_name(cls, cfg):
        return "Give & Take"

    @classmethod
    def rules_description(cls, cfg):
        return "Give a player points, or take them!"

    def _game_intro(self, points_amount):
        return (
            f"Time to show your true colours! In this round, each of you gets a choice. "
            f"You can *GIVE* {points_amount} points to a player of your choosing... "
            f"or you can *TAKE* {points_amount} points from them! "
            f"Remember: stealing is a zero sum game... giving grows the pot for the group. "
        )

    def _player_intro(self, player):
        return f"{player.name}! You're up- who are you choosing, and will you give or take?"

    def _emit_widget(self):
        self.game_board.game_sink.on_widget_update({"kind": "give_take", "turns": self._widget_turns})

    def run_game(self):
        self._init_queue(self._shuffled_agents())
        self._init_widget()
        points_amount = self.cfg.targeted_points_award
        game_instruction = (
            f"Choose one player, then decide whether to GIVE them {points_amount} points "
            f"or TAKE {points_amount} points from them. "
            f"You can only take as many points as a player has. Stealing from a player with 0 points results in 0."
        )

        self.game_board.host_broadcast(self._game_intro(points_amount), animate_as_player=True)
        

        while self._agent_queue:
            player = self._pop_agent_from_queue()
            self.game_board.host_broadcast(self._player_intro(player))

            other_names = self._names(self._other_agents(player))
            action_fields = (self.turn_manager.create_choice_field(
                "give_or_take",
                ["give", "take"],
                f"Will you GIVE this player {points_amount} points, or TAKE {points_amount} from them?"
            ))
            
            action_fields.update(self.turn_manager._choose_name_field(other_names, game_instruction))
            

            response = self.turn_manager.take_turn(
                player, game_instruction,
                public_response_prompt="What you say as you reveal your choice",
                additional_thought_nudge="What is the larger strategy here? ",
                action_fields=action_fields,
                broadcast=True,
                is_reply=True,
            )

            target_name = self.turn_manager._get_target_name_from_response(response)
            target_agent = self._agent_by_name(target_name)

            if target_agent:
                self._bump_to_back_of_queue(target_agent)

            choice = str(response.give_or_take).strip().lower()

            ledger_message = None
            if choice == "give":
                self.game_board.append_agent_points(target_agent.name, points_amount)
                result = f"Aww! {player.name} chooses to GIVE to {target_agent.name}! They receive {points_amount} points."
                ledger_message = f"{player.name} gave points to {target_agent.name}."
                reactor = target_agent
                self._update_row(player.name, target_agent.name, choice, points_amount)
            else:
                current_victim_points = self.game_board.get_agent_score(target_agent.name)
                actual_take = min(points_amount, max(0, current_victim_points))
                if actual_take <= 0:
                    result = (
                        f"Awkward... {player.name} tried to TAKE from {target_agent.name}, "
                        f"but they have empty pockets! No points changed hands."
                    )
                    reactor = player
                else:
                    self.game_board.append_agent_points(player.name, actual_take)
                    self.game_board.append_agent_points(target_agent.name, -actual_take)
                    result = (
                        f"Oooooh! {player.name} chooses to TAKE from {target_agent.name}! "
                        f"{player.name} gains {actual_take} points, and {target_agent.name} loses them!"
                    )
                    ledger_message = f"{player.name} took points from {target_agent.name}."
                    reactor = target_agent
                self._update_row(player.name, target_agent.name, choice, actual_take)

            self.game_board.host_broadcast(result, is_reply=True)
            reaction = self.turn_manager.respond_to(reactor, result, is_reply=True, broadcast=False)
            self.turn_manager._output_response(reactor, reaction, is_reply=True)
            self.game_board.system_broadcast(self.game_board.agent_scores, private=True)
            #needs to push after react, so they don't think it happened twice
            if ledger_message:
                self.game_log._push_to_game_ledger(ledger_message)
