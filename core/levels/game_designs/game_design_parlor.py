from core.levels.game_designs.game_design import GameDesign


class GameDesignParlor(GameDesign):

    @classmethod
    def min_players(cls) -> int:
        return 8

    @classmethod
    def max_players(cls) -> int:
        return 12

    @classmethod
    def get_phase_description(cls, phase_number, agent_number, cfg, **kwargs):
        raise NotImplementedError("GameDesignParlor phases not yet implemented")
