from core.levels.game_designs.game_design import GameDesign


class GameDesignParlor(GameDesign):

    @classmethod
    def min_players(cls) -> int:
        return 8

    @classmethod
    def max_players(cls) -> int:
        return 12
    
    @classmethod
    def should_dead_players_summarise(cls) -> bool:
        return True #for reunion
    
    @classmethod
    def get_phase_description(cls, phase_number, agent_number, cfg):
        raise NotImplementedError("GameDesignParlor phases not yet implemented")
    
    
