from core.levels.game_designs.game_design_beginner8 import *


class GameDesignBumper(GameDesignBeginner8):

    @classmethod
    def min_players(cls) -> int:
        return 6

    @classmethod
    def max_players(cls) -> int:
        return 11

    @classmethod
    def get_phase_description(cls, phase_number, agent_number, cfg: GameConfig, voting=None, incl_games=True, speed=1):
        if agent_number == 11:
            rounds = [IntroRound, DiscussionRoundDirected, GameGuess, VoteElectLeader2]
            cfg.set_directed_discussion_group_allowed(False)
            cfg.pd_get_reactions = False
            cfg.set_pd_pairing_random()
            cfg.allow_revote = False
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        turn_prompt=("You are now entering the game and meeting the other players for the first time. "
                        "Everyone has a chance to speak so you can get to know other players. "
                        "You can either address the group or directly to one specific player, which they will be able to respond to- but everything in this round is public. "),)])
            )
            return PhaseDescription(rounds=rounds)

        if agent_number == 10:
            rounds = [DiscussionRoundDirectedShort, GameTargetedChoiceGiveOrTake, VoteElectLeader2]
            cfg.set_directed_discussion_group_allowed(False)
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="How does everyone feel about the first phase? Well in this phase, players will vote to elect a leader, and that leader will choose the next player to go home. Every player who receives a nomination will be safe. Discuss!",
                        turn_prompt=("Make discussion with the other players- speak about what happened in the last phase, but keep a mind on the upcoming elimination. Can you secure a nom for safety?"),)])
            )
            return PhaseDescription(rounds=rounds)

        if agent_number == 9:
            rounds = [GameCircle, DiscussionRoundDirectedShort, VoteElectLeader2]
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="The same rules will apply for the next elimination, players will elect a leader to send someone home. Each nominated player will be safe. ",
                        turn_prompt=("Make discussion with the other players- speak about what happened in the last phase, but keep a mind on the upcoming elimination. Can you secure a nom for safety?"),)])
            )
            return PhaseDescription(rounds=rounds)

        if agent_number == 8:
            rounds = [DiscussionRoundDirectedShort, GameGuess, VoteElectLeader2]
            cfg.set_directed_discussion_group_allowed(False)
            cfg.pd_get_reactions = False
            cfg.set_pd_pairing_random()
            cfg.allow_revote = False
            cfg.set_discussion_settings(
                DiscussionRoundSettings(loops=[
                    DiscussionLoop(
                        host_message="The vote will be the same again- elect a leader, and they will send a player home. Nominated players are safe. ",
                        turn_prompt=("Make discussion with the other players- speak about what happened in the last phase, but keep a mind on the upcoming elimination. Can you secure a nom for safety?"),)])
            )
            return PhaseDescription(rounds=rounds)

        return super().get_phase_description(phase_number, agent_number, cfg, voting, incl_games, speed)
