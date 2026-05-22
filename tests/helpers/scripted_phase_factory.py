from core.levels.phase_recipe_factory import PhaseRecipeFactory

class ScriptedPhaseFactory(PhaseRecipeFactory):
    def __init__(self, phases):
        self.phases = phases
        self.phase_request = 0

    def get_phase_recipe(self, phase_number, agent_number, cfg, **kwargs):
        phase = self.phases[self.phase_request]
        self.phase_request += 1
        return phase
