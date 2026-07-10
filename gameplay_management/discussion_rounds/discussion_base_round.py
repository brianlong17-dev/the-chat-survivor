from gameplay_management.base_manager import BaseRound


class DiscussionBaseRound(BaseRound):

    @classmethod
    def is_discussion(cls):
        return True

    def run_game(self):
        self.game_board.log_boundary("\n\n[DISCUSSION ROUND START — no actions here, just speaking —]\n\n")
        self.run_round()
        self.game_board.log_boundary("\n\n[DISCUSSION ROUND END]\n\n")

    def run_round(self):
        raise NotImplementedError
