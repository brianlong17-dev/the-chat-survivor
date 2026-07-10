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
            cfg.set_directed_discussion_group_allowed(True)
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="How does everyone feel about the game so far? After the next game, players will elect a leader to eliminate another player. Only non-nominated players are in danger. ",
                        turn_prompt=("Bring up the last phase, or plan for the vote later?"),)])
            )
            return PhaseDescription(rounds=rounds)

        if agent_number == 6: #IntroRound, DiscussionRoundDirectedPreVote
            rounds = [GamePrisonersDilemma, DiscussionRoundDirectedShort , VoteElectLeader]
            cfg.set_directed_discussion_group_allowed(False)
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="Discuss the previous game, but soon you'll elect a leader to send a player home- any nominated players will be safe. ",
                        additional_thought_prompt="Do you need to react to what happened in prisoner's dilemma?",
                        turn_prompt=("Be confrontational and reactive if needed."),)])
            )
            return PhaseDescription(rounds=rounds)
        
        if agent_number == 5:
            rounds = [GameTargetedChoiceGive, DiscussionRoundDirectedShort, VoteBottomTwo]
            cfg.set_directed_discussion_group_allowed(True)
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="There is time now to discuss the state of the game, but first an announcement: No more electing executioners. From here on, everyone will vote directly who to eliminate from the bottom two.",
                        additional_thought_prompt="The rules have changed- every player's vote is equal and only the bottom two are in danger. Does that change your strategy? ",
                        turn_prompt=("Speak about previous events or discuss the upcoming elimination."),)])
            )
            return PhaseDescription(rounds=rounds)

        return super().get_phase_description(phase_number, agent_number, cfg)
