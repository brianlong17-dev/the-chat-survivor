from core.levels.game_designs.game_design_beginner import *
from gameplay_management.games.game_wisdom import GameWisdom
from gameplay_management.eliminations.voting_elect_leader import VoteElectLeader
from gameplay_management.game_targeted.game_targeted_give_or_take import GameTargetedChoiceGiveOrTake


class GameDesignBeginner8(GameDesignBeginner):

    @classmethod
    def min_players(cls) -> int:
        return 6

    @classmethod
    def max_players(cls) -> int:
        return 8

    @classmethod
    def get_phase_description(cls, phase_number, agent_number, cfg: GameConfig):
        if agent_number == 8:
            rounds = [IntroRound, DiscussionRoundDirectedShort, GameGuess, VoteElectLeader]
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

        if agent_number == 7:
            rounds = [DiscussionRoundDirectedShort, GameTargetedChoiceGiveOrTake, VoteElectLeader]
            cfg.set_directed_discussion_group_allowed(False)
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="How does everyone feel about the game so far? After the next game, players will elect a leader to eliminate another player. Only non-nominated players are in danger. ",
                        turn_prompt=("Bring up the last phase, or plan for the vote later?"),)])
            )
            return PhaseDescription(rounds=rounds)

        if agent_number == 6: #IntroRound, DiscussionRoundDirectedPreVote
            rounds = [GamePrisonersDilemma, DiscussionRoundDirectedShort , VoteElectLeader]
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="One more time, you'll elect a leader to send a player home- nominated players are safe. ",
                        additional_thought_prompt="Soon the group will vote to elimate a player from the bottom two. Does that shift who you need on your side?",
                        turn_prompt=("Speak about what happened in the last phase, discuss the upcoming elimination?"),)])
            )
            return PhaseDescription(rounds=rounds)

        if agent_number == 5:
            rounds = [GameTargetedChoiceGive, DiscussionRoundDirectedShort, VoteBottomTwo]
            cfg.set_directed_discussion_group_allowed(True)
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="No more electing a leader- from here on, you vote directly who to send home from the bottom two players.",
                        additional_thought_prompt="The rules have changed- your vote now sends someone toward the exit directly. Who do you trust, and who can't you afford to have voting against you?",
                        turn_prompt=("Speak about what happened in the last phase, discuss the upcoming elimination?"),)])
            )
            return PhaseDescription(rounds=rounds)

        return super().get_phase_description(phase_number, agent_number, cfg)
