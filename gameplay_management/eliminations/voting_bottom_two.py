from collections import Counter
from typing import Optional, Sequence
from gameplay_management.eliminations.vote_mechanicsMixin import VoteMechanicsMixin
from prompts.gamePrompts import GamePromptLibrary

class VoteBottomTwo(VoteMechanicsMixin):

    @classmethod
    def display_name(cls, cfg):
        return "Bottom Two"

    @classmethod
    def rules_description(cls, cfg):
        return "The bottom two players will face the vote to be removed. "

    def rules_description_detailed(self):
        cfg = self.cfg
        rules_string = self.rules_description(cfg)
        if cfg.vote_dont_miss:
            rules_string += GamePromptLibrary.dont_miss_string.format(points=cfg.vote_missed_points)
            
        return rules_string
           
    def run_vote(self, immunity_players: Optional[Sequence[str]]):
        self.run_voting_bottom_players(immunity_players, expand_ties = self.cfg.vote_bottom_two_expand_ties,
                                       dont_miss = self.cfg.vote_dont_miss)

    
    def run_voting_bottom_players(self, immunity_players: Optional[Sequence[str]] = None, dont_miss: bool = True, expand_ties: bool = False):

        immunity_players = self._validate_immunity(immunity_players)
        players_up_for_elimination = self._players_up_for_elimination(immunity_players)
        players_up_for_elimination = self.get_bottom_players(players_up_for_elimination, min = 2, expand_ties=expand_ties)
        host_intro_msg = "Welcome to the elimination round. "
        host_intro_msg += (self.rules_description_detailed())
        host_intro_msg += self.immunity_string(immunity_players, 
                                               self._names(players_up_for_elimination))
        if len(players_up_for_elimination) > 2:
            host_intro_msg += "Since we have a tie at the bottom of scoreboard, additional players will face the vote. "
        host_intro_msg += self._facing_the_vote_string(self._names(players_up_for_elimination))
        self._host_broadcast(host_intro_msg)
        
        
        self._initialise_voting_widget(self._names(players_up_for_elimination), self._names(self.agents), theme="blood")
        victim_name, votes = self._run_vote_process(players_up_for_elimination)
        self._vote_widget_vote_finalised()
        if dont_miss:
            self._dispense_victim_points(victim_name, votes)
        self.eliminate_player_by_name(victim_name)
       
    def revote(self, candidates):
        votes = []
        self._initialise_voting_widget(self._names(candidates), self._names(self.agents), theme="blood")
        leader = self.get_strategic_players(self.agents, top_player = True, multiple = False)[0]
        self._host_broadcast(f"As we have a tie, we will now have a revote. If this vote ends in a tie, the leader of the game, {leader.name}, will decide who is going home. "
        "Once again, let's hear from the players facing the vote. ")
        
        for agent in candidates:
            response = self._collect_vote_from_candidate_revote(agent, candidates)
            self._handle_vote_response(votes, agent, response)
            
        self._host_broadcast("And now from the remaining voters. ")
        non_candidates = [agent for agent in self.agents if agent not in candidates]
        responses = self._run_tasks(
            [(agent, candidates, True) for agent in non_candidates],
            self._collect_vote_normal,
        )
        
        self._handle_voter_responses(votes, non_candidates, responses)
        players_with_top_votes = self._get_top_votes(votes)
        if len(players_with_top_votes) == 1:
            return players_with_top_votes[0], votes
        else:
            return self.leader_chooses(leader, candidates), votes
    
    def _handle_voter_responses(self, votes, voters, responses):
        for agent, response in zip(voters, responses):
            self._handle_vote_response(votes, agent, response)
                
    def _run_vote_process(self, candidates):
        votes = []
        
        everyone_up = len(self.agents) == len(candidates)
        if everyone_up:
            self._host_broadcast("Looks like everybody's up for elimination! ")
            responses = self._run_tasks(
                [(agent, candidates) for agent in candidates],
                self._collect_vote_normal,
            )
            self._handle_voter_responses(votes, candidates, responses)
        else:
            self._host_broadcast("Candidates — tell us who you are voting for, and make your case for why the others should keep you in the competition. ")
            for agent in candidates:
                response = self._collect_vote_from_candidate(agent, candidates)
                self._handle_vote_response(votes, agent, response)
            
            self._host_broadcast("Now to the other's vote. Reveal who you are voting to eliminate, and tell us why. ")
            non_candidates = [agent for agent in self.agents if agent not in candidates]
            responses = self._run_tasks(
                [(agent, candidates) for agent in non_candidates],
                self._collect_vote_normal,
            )
            self._handle_voter_responses(votes, non_candidates, responses)
                
        players_with_top_votes = self._get_top_votes(votes)
        if len(players_with_top_votes) == 1:
            return players_with_top_votes[0], votes
        else:
            tied_agents = [a for a in self.agents if a.name in players_with_top_votes]
            if self.cfg.allow_revote:
                return self.revote(tied_agents)
            else:
                leader = self.get_strategic_players(self.agents, top_player = True, multiple = False)[0]
                return self.leader_chooses(leader, tied_agents), votes
        
    def _dispense_victim_points(self, victim_name, votes):
        points_per_survived_vote = GamePromptLibrary.points_per_survived_vote
        vote_counts = Counter(name for name in votes if name and name != victim_name)
        survivors_rewarded = {name: count * points_per_survived_vote for name, count in vote_counts.items()}
        for name, pts in survivors_rewarded.items():
            self.game_board.append_agent_points(name, pts)

        if survivors_rewarded:
            reward_str = ", ".join([f"{name} (+{pts})" for name, pts in survivors_rewarded.items()])
            self._host_broadcast(
                f"🛡️ BULLET DODGER BONUS! The following players took heat but survived the vote. "
                f"They receive points for every vote they survived: {reward_str}"
            )

    def _get_top_votes(self, votes):
        vote_counts = Counter(votes)
        results_str = "The results of the vote are: "
        results_str += self.format_list([f"{name}: {count} votes" for name, count in vote_counts.items()])
        self._host_broadcast(results_str)
        max_votes = max(vote_counts.values())
        return [name for name, count in vote_counts.items() if count == max_votes]
        
    def get_bottom_players(self, players_up_for_elimination, min = 2, expand_ties = False):
        selected_players = []
        pool = list(players_up_for_elimination)
        while len(selected_players) < min and pool:
            batch = self.get_strategic_players(pool, top_player = False, multiple = expand_ties)
            if not batch:
                break
            selected_players.extend(batch)
            pool = [p for p in pool if p not in selected_players]
        return selected_players
    
    ##
    #--- Voting Calls ----
    ##
    
    
    def leader_chooses(self, leader, candidates):
        self._host_broadcast(f"{leader.name}, as the leader of the game, the decision falls to you. Who are you sending home? ")
        turn_prompt = ("The revote is tied and as the leader of the game, you have the deciding vote. "
        "You will choose which of the candidates is eliminated. ")
        public_response_prompt = ("After your choice is revealed — explain why you chose to ELIMINATE this person from the game. "
            "If you have already stated your reasons and your vote hasn't changed, be BRIEF, and just reaffirm that your vote hasn't changed. "
            "However, IF you are emotional, you can reflect upon the responsibility and pressure this choice puts on you- since you alone are directly responsible for sending someone home. ")
        additional_thought_nudge = ("Who do you want to send home? Will you change your vote or stick with it? ")
        response = self.turn_manager._targeted_turn(leader, self._names(candidates),
                                                   "Who do you choose to eliminate from the competition? ",
                                                   turn_prompt,
                                                   public_response_prompt, additional_thought_nudge)
        return self._handle_vote_response([], leader, response)
    
    def _reminder(self, candidates):
        #SCAF
        return f"REMINDER: You can only choose from the players up for elimination: {self.format_list(candidates)}"
    
    def _collect_vote_from_candidate_revote(self, agent, candidates):
        turn_prompt = ("You're up for elimination and it's a revote. You've already stated your case, "
        "and seen what the others have had to say. Don't repeat your case, but you can rebut what anyone had to say in the vote.\n"
        f"{self._reminder(candidates)}")
        public_response_prompt = ("After your vote is revealed — if you haven't changed your vote you don't need to say anything about it. "
        "Don't repeat your case, only speak directly to individual players if you want to clap back, or change their mind. Keep it snappy. ")
        additional_thought_nudge = ("Do you think you can change anyone's mind? ")
        return self.turn_manager._targeted_turn(agent, self._names(candidates), 
                                        "Who do you vote to eliminate from the competition? ",
                                        turn_prompt,
                               public_response_prompt, additional_thought_nudge)
    
    def _collect_vote_from_candidate(self, agent, candidates):
        
        turn_prompt = ("You are up for elimination. You and the other candidates vote first. "
        "Reveal who you are sending home, then explain your reasoning. You could make your case why you shouldn't be eliminated. \n"
        f"{self._reminder(candidates)}\n"
        )
        public_response_prompt = ("After your vote is revealed — explain WHY you chose to vote to ELIMINATE this person. This is also where "
        "you can state your case to the other voters- should they vote to ELIMINATE another player? ")
        additional_thought_nudge = ("Who do you want to send home and why? What can you say to get others to vote with you? ")
        return self.turn_manager._targeted_turn(agent, self._names(candidates), 
                                        "Who do you vote to eliminate from the competition? ",
                                        turn_prompt,
                               public_response_prompt, additional_thought_nudge)
        
    def _collect_vote_normal(self, agent, candidates, revote = False):
        if revote:
            turn_prompt = ("It's going to a revote. Will you change your vote? If you are changing your vote, explain why and what changed your mind.\n"
                           f"{self._reminder(candidates)}" )
            public_response_prompt = ("After your vote is revealed, give your reason. If your vote hasn't changed, just a one liner response please. ")
            additional_thought_nudge = ("After hearing from everyone, do you want to change your vote? ")
        else:
            turn_prompt = ("You are safe and not up for elimination. Reveal your vote to the group, "
                "then say who you are voting for and why. ")
            public_response_prompt = ("After your vote is revealed — explain why you chose to vote to ELIMINATE this person from the game. "
            "You can explain your choice, or choose not to. Or give a zippy one-liner. ")
            additional_thought_nudge = ("Who do you want to send home, and why is this the right move for your game? Will you explain yourself or just a give a quip? ")
        return self.turn_manager._targeted_turn(agent, self._names(candidates), 
                                        "Who do you vote to eliminate from the competition? ",
                                        turn_prompt,
                               public_response_prompt, additional_thought_nudge)
     