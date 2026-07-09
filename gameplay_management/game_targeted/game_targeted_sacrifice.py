from gameplay_management.game_targeted.base_targeted import BaseTargetedGame
from pydantic import Field


class GameTargetedChoiceSacrifice(BaseTargetedGame):

    @classmethod
    def display_name(cls, cfg):
        return "Sacrificer"

    @classmethod
    def rules_description(cls, cfg):
        return "Use your own points to hurt another player"

    def _game_intro(self):
        return (
            f"This is a game of self-sacrifice, of sabotage... "
            f"In this round, you can SPEND your own points to damage another player. "
            f"For every 1 point you spend, your target also loses a point! "
            f"The minimum points a player can have is zero- don't spend points trying to get them to negative points. "
            f"You can choose to pass if you want to save your strength."
        )

    def _player_intro(self, player):
        return f"{player.name}! You have the floor. Will you sabotage someone, or stay safe?"

    def _emit_widget(self):
        self.game_board.game_sink.on_widget_update({"kind": "give_take", "turns": self._widget_turns})

    def run_game(self):
        self._init_queue(self._shuffled_agents())
        self._init_widget()
        game_instruction = (
            "Decide if you want to attack. If yes, choose a target and an amount to spend. "
            "If no, choose 'Pass' as the target."
        )
        self.game_board.host_broadcast(self._game_intro())
        while self._agent_queue:
            player = self._pop_agent_from_queue()
            self.game_board.host_broadcast(self._player_intro(player))
            my_score =  self._agent_score(player.name)

            if my_score <= 0:
                result = f"{player.name} has no points, so has no choice but to sit this one out."
                self.game_board.host_broadcast(result, is_reply=True)
                self._update_row(player.name, None, "pass", actor_amount=0, target_amount=0)
                continue

            targets = self._names(self._other_agents(player)) + ["Pass"]
            action_fields = self.turn_manager._choose_name_field(targets, "Choose a player to attack, or 'Pass'.")
            action_fields["points_to_spend"] = (
                int,
                Field(description=(
                    f"How many of your own points will you spend? You have {my_score} points. "
                    f"Your target player can't go into negative points, so don't waste points. "
                    f"Enter 0 if passing."
                ))
            )
            scores_str = ", ".join([f"{k}: {v}" for k, v in self.game_board.agent_scores.items()])
            thought_nudge = f"Reminder- attacking a player with no points has no effect. Current scores: {scores_str}."

            response = self.turn_manager.take_turn(
                player, game_instruction,
                model_name="SabotageModel",
                action_fields=action_fields,
                additional_thought_nudge=thought_nudge,
                broadcast=True,
                is_reply=True,
            )

            target_name = self.turn_manager._get_target_name_from_response(response)
            spent = response.points_to_spend

            ledger_message = None
            if str(target_name).strip().lower() == "pass" or spent <= 0:
                result = f"{player.name} chooses mercy (or cowardice?) and passes. No blood is shed."
                reactor = player
                self._update_row(player.name, None, "pass", actor_amount=0, target_amount=0)
            else:
                target_agent = self._agent_by_name(target_name)
                if target_agent:
                    self._bump_to_back_of_queue(target_agent)
                victim_score = self.game_board.get_agent_score(target_agent.name)
                actual_spend = max(0, min(spent, my_score))
                damage = min(victim_score, actual_spend)

                if victim_score == 0:
                    result = f"{target_agent.name} has no points, so the attack does nothing. Perhaps just to make a point?"
                    reactor = player
                    self._update_row(player.name, target_agent.name, "take", actor_amount=0, target_amount=0)
                else:
                    self.game_board.append_agent_points(player.name, -actual_spend)
                    self.game_board.append_agent_points(target_agent.name, -damage)
                    result = (
                        f"BRUTAL! {player.name} sacrifices {actual_spend} of their own points... "
                        f"to crush {target_agent.name} for {damage} damage! "
                        f"{target_agent.name}, wow... this must sting!"
                    )
                    reactor = target_agent
                    ledger_message = f"{player.name} sacrificed points to attack {target_agent.name}."
                    self._update_row(player.name, target_agent.name, "take", actor_amount=-actual_spend, target_amount=-damage)

            self.game_board.host_broadcast(result, is_reply=True)
            reaction = self.turn_manager.respond_to(reactor, result, is_reply=True)
            self.turn_manager._output_response(reactor, reaction, is_reply=True)
            self.game_board.system_broadcast(self.game_board.agent_scores, private=True)
            #needs to push after react, so they don't think it happened twice
            if ledger_message:
                self.game_log._push_to_game_ledger(ledger_message)
