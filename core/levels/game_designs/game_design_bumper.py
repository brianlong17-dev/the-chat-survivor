from core.levels.game_designs.game_design_beginner8 import *


class GameDesignBumper(GameDesignBeginner8):

    @classmethod
    def min_players(cls) -> int:
        return 6

    @classmethod
    def max_players(cls) -> int:
        return 11

    @classmethod
    def get_phase_description(cls, phase_number, agent_number, cfg: GameConfig):
        if agent_number == 11:
            rounds = [IntroRound, DiscussionRoundDirected, GameGuess, VoteElectLeader]
            cfg.set_directed_discussion_group_allowed(True)
            cfg.pd_get_reactions = False
            cfg.set_pd_pairing_random()
            cfg.allow_revote = False
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        directed_turn_prompt="You're meeting the other players for the first time! Direct messages can build early alliances. ",
                        directed_public_response_prompt="Be conversational, chatty and reactive. "
                    )]),
            )
            return PhaseDescription(rounds=rounds)

        if agent_number == 10:
            rounds = [DiscussionRoundDirectedShort, GameTargetedChoiceGiveOrTake, VoteElectLeader]
            cfg.set_directed_discussion_group_allowed(True)
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="How does everyone feel about the first phase? After the next game, players will elect a leader to eliminate another player. Only non-nominated players are in danger. ",
                        turn_prompt=("Bring up the last phase, or plan for the vote later?"),)])
            )
            return PhaseDescription(rounds=rounds)

        if agent_number == 9:
            rounds = [GameCircle, DiscussionRoundDirectedShort, VoteElectLeader]
            cfg.set_directed_discussion_group_allowed(True)
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="Same again- you'll elect a leader to send a player home. Nominated players are safe. ",
                        turn_prompt=("Bring up the last phase, or plan for the vote later?"),)])
            )
            return PhaseDescription(rounds=rounds)

        if agent_number == 8:
            rounds = [DiscussionRoundDirectedShort, GameGuess, VoteElectLeader]
            cfg.set_directed_discussion_group_allowed(True)
            cfg.pd_get_reactions = False
            cfg.set_pd_pairing_random()
            cfg.allow_revote = False
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="Same again- you'll elect a leader to send a player home. Nominated players are safe. ",
                        turn_prompt=("Bring up the last phase, or plan for the vote later?"),)])
            )
            return PhaseDescription(rounds=rounds)

        return super().get_phase_description(phase_number, agent_number, cfg)
