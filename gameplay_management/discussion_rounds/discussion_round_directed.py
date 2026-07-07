from gameplay_management.base_manager import BaseRound


class DiscussionRoundDirected(BaseRound):

    @classmethod
    def display_name(cls, cfg):
        return "Discussion Round"

    @classmethod
    def rules_description(cls, cfg):
        return "Discussion round with directed messages"

    def run_game(self):
        return self.run_round(short=False)

    def run_round(self, short=False):
        settings = self.cfg.get_discussion_settings()
        group_allowed = self.cfg.directed_discussion_group_allowed
       
        for loop in settings.loops:
            ordered_agents = self._shuffled_agents()
            if loop.host_message:
                self._host_broadcast(loop.host_message)
                
            while ordered_agents:
                player = ordered_agents.pop(0)

                names = [agent.name for agent in self.agents if agent != player]

                turn_prompt = "You can directly address another player and get a response. Be direct and specific, not performative. "
                if group_allowed:
                    names.append("Group")
                    turn_prompt += "Choose Group if you want to address the group. Directing questions is often key to building alliances and building strategy."
                
                    
                public_response_prompt = "Your statement to the group or person. Can be a one liner. Doesn't need to be a question. "
                additional_thought_nudge = "Have you already spoken in this round? What new can you say? You only want to speak if it avoids repetition. "
                public_response_prompt += loop.directed_public_response_prompt
                additional_thought_nudge += loop.directed_additional_thought_prompt
                turn_prompt += loop.directed_turn_prompt
                
                
                response = self.turn_manager._ask_directed_question(player, names, turn_prompt, public_response_prompt, additional_thought_nudge)

                chosen_name = self.turn_manager._get_target_name_from_response(response)
                chosen_agent = self._agent_by_name(chosen_name.strip())

                appendage = ""
                if chosen_agent:
                    if chosen_agent in ordered_agents:
                        ordered_agents.remove(chosen_agent)
                        if ordered_agents and not short:
                            ordered_agents.append(chosen_agent)
                        else:
                            appendage = "This is your last turn in the discussion round. Say anything else you want to say. "
                            #in this case they should also get the thought prompt etc

                    user_prompt = f"Respond directly to {player.name}'s last message to you. Don't ask a question in response. {appendage}"
                    self.turn_manager.respond_to(chosen_agent, user_prompt, public_response_prompt="Your public response. ",
                                                broadcast=True, is_reply=True, prefix_respond_to=False)
        self.cfg.discussion_index += 1
