from gameplay_management.games.game_mechanicsMixin import GameMechanicsMixin


class BaseTargetedGame(GameMechanicsMixin):

    def _init_queue(self, agents):
        self._agent_queue = list(agents)

    def _init_widget(self):
        self._widget_turns = [{"actor": a.name, "state": "waiting"} for a in self._agent_queue]
        self._emit_widget()

    def _widget_active_agent(self, agent):
        for turn in self._widget_turns:
            if turn["actor"] == agent.name:
                turn["state"] = "picked"
                self._emit_widget()
                return

    def _update_row(self, active_name, target_name, action, amount=None, actor_amount=None, target_amount=None):
        for turn in self._widget_turns:
            if turn["actor"] == active_name:
                turn["state"] = "revealed"
                turn["target"] = target_name
                turn["action"] = action
                if amount is not None:
                    turn["amount"] = amount
                if actor_amount is not None:
                    turn["actor_amount"] = actor_amount
                if target_amount is not None:
                    turn["target_amount"] = target_amount
                self._emit_widget()
                return

    def _pop_agent_from_queue(self):
        agent = self._agent_queue.pop(0)
        self._widget_active_agent(agent)
        return agent

    def _bump_to_back_of_queue(self, agent):
        if agent in self._agent_queue:
            self._agent_queue.remove(agent)
            self._agent_queue.append(agent)
            for turn in self._widget_turns:
                if turn["actor"] == agent.name:
                    self._widget_turns.remove(turn)
                    self._widget_turns.append(turn)
                    break
            self._emit_widget()
