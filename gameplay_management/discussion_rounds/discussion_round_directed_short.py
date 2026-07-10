from gameplay_management.discussion_rounds.discussion_round_directed import DiscussionRoundDirected


class DiscussionRoundDirectedShort(DiscussionRoundDirected):

    short = True

    @classmethod
    def display_name(cls, cfg):
        return "Quick Discussion Round"
