from core.levels.game_designs.game_design import GameDesign

class ScriptedGameDesign(GameDesign):
    def __init__(self, phases):
        self.phases = phases
        self.phase_request = 0

    def get_phase_description(self, phase_number, agent_number, cfg, **kwargs):
        phase = self.phases[self.phase_request]
        self.phase_request += 1
        return phase
