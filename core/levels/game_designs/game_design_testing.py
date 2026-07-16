from core.levels.game_designs.game_design import GameDesign

class TestingGameDesign(GameDesign):
    #this is just for testing. it lets you put phases into and index
    #why? it lets you run a full game rather than a phase- you get The End
    
    def __init__(self, phases=None):
        self.phases = phases or []
        self.phase_request = 0

    @classmethod
    def min_players(cls) -> int:
        return 2

    @classmethod
    def max_players(cls) -> int:
        return 12

    def get_phase_description(self, phase_number, agent_number, cfg, **kwargs):
        phase = self.phases[self.phase_request]
        self.phase_request += 1
        return phase
