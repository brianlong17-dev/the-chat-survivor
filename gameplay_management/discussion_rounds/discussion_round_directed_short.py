from gameplay_management.discussion_rounds.discussion_round_directed import DiscussionRoundDirected


class DiscussionRoundDirectedShort(DiscussionRoundDirected):

    @classmethod
    def display_name(cls, cfg):
        return "Quick Discussion Round"

    def run_game(self, host_intro=None):
        return self.run_round(short=True, host_intro=host_intro)