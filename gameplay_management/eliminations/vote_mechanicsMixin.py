from collections import Counter
from typing import List, Optional, Sequence
from gameplay_management.base_manager import *
from prompts.gamePrompts import GamePromptLibrary
from prompts.prompts import PromptLibrary
from prompts.votePrompts import VotePromptLibrary
    
   
class VoteMechanicsMixin(BaseRound):
    def __init__(self, game_board, simulationEngine):
        super().__init__(game_board, simulationEngine) 
    
    ###############
    #   Helper    #
    ###############
    
    @classmethod
    def is_vote(cls):
        return True
    
    
    def _validate_immunity(self, immunity_players: Optional[Sequence[str]]) -> list[str]:
        #Tosses out immunity if all players are immune? 
        if immunity_players is None:
            return []
        immunity_players = list(dict.fromkeys(immunity_players))
        if len(self.simulationEngine.agents) == len(immunity_players):
            host_message = VotePromptLibrary.immunity_all_players_reset
            self.game_board.host_broadcast(host_message)
            immunity_players = []
        return immunity_players
       
    def _facing_the_vote_string(self, players_up_for_elimination: Sequence[str]):
        players_up_for_elimination_string = (
            f"\nThe following players are up for elimination:\n *{self.format_list(players_up_for_elimination)}*"
        )
        return players_up_for_elimination_string
    
    def immunity_string(self, immunity_players: Sequence[str], players_up_for_elimination: Sequence[str]) -> str:
        immunity_string = ""
        if immunity_players:
            immunity_string = (
                f"{VotePromptLibrary.immunity_players_prefix}\n"
                f" {', '.join(immunity_players)}.\n"
            )
        
        return f"{immunity_string}\n"
            

    def _players_up_for_elimination(self, immunity_players: Optional[Sequence[str]]) -> List['Debater']:
        immunity_players = immunity_players or []
        return  [a for a in self.simulationEngine.agents if a.name not in immunity_players]
        
    ###############
    #   Logic     #
    ###############
    def vote_one_player_off(self, player, eligible_players_names):
        #If you are up for elimination - this has to double as the plea ? 
        names_str = self.format_list(eligible_players_names)
        turn_prompt = VotePromptLibrary.vote_one_player_turn_prompt.format(
            eligible_player_names=names_str
        )
        name_field_prompt = VotePromptLibrary.vote_one_player_name_field_prompt
        #----------------
        action_fields = self.turn_manager._choose_name_field(eligible_players_names, name_field_prompt)
        return self.turn_manager.take_turn(player, turn_prompt, model_name="vote_out_player", action_fields=action_fields, action_post_response=True)
    
    def _handle_vote_response(self, votes, agent, vote_response):
        actual_vote = self.turn_manager._get_target_name_from_response(vote_response)
        votes.append(actual_vote)
        self.turn_manager._output_response(agent, vote_response, is_reply=True, delay=2, pre_message_choice_reveal=self.TARGET_NAME_FIELD)
        self._update_voting_widget(agent.name, actual_vote or "—")
        return actual_vote #used in leader_chooses
        
    def _collect_votes(self, players_up_for_elimination: Sequence[str], pass_allowed: bool = False):
        votes = []
        voting_results = []
        voting_futures = []

        voter_names = [a.name for a in self.simulationEngine.agents]
        self._initialise_voting_widget(players_up_for_elimination, voter_names, theme="blood")
        voting_results = self._run_tasks([(agent, players_up_for_elimination) for agent in self.agents], 
                                            self.vote_one_player_off)

        for agent, vote_response in zip(self.simulationEngine.agents, voting_results):
            self._handle_vote_response(votes, agent, vote_response)
            
        return votes, voting_results
   
    def process_vote_rounds(self, players_up_for_elimination: Sequence[str], revote_count: int = 0, initial_votes = None):
        
        if revote_count > 3: #this should be done manually?
            self.game_board.host_broadcast(VotePromptLibrary.voting_round_random_elimination_msg)
            self._vote_widget_vote_finalised()
            return random.choice(players_up_for_elimination), initial_votes
            #easy to replace this later, with better choice...
        
        
        votes, voting_results = self._collect_votes(players_up_for_elimination)
        voting_results = initial_votes if initial_votes is not None else voting_results
        vote_counts = Counter(votes)
        tally_str = ", ".join([f"{name}: {count} votes" for name, count in vote_counts.items()])
        host_message = VotePromptLibrary.voting_tally_msg.format(tally=tally_str)
        self.game_board.host_broadcast(host_message)

        if not vote_counts:
            self.game_board.host_broadcast(VotePromptLibrary.voting_round_no_valid_votes_msg)
            self._vote_widget_vote_finalised()
            return random.choice(players_up_for_elimination), voting_results
        
        # Process results
        max_votes = max(vote_counts.values())
        players_with_most_votes = [name for name, count in vote_counts.items() if count == max_votes]
        
        if len(players_with_most_votes) > 1:
            deadlock_string = VotePromptLibrary.voting_round_tie_msg.format(
                players_with_most_votes=self.format_list(players_with_most_votes)
            )
            if len(players_with_most_votes) == len(self.simulationEngine.agents):
                deadlock_string = VotePromptLibrary.voting_round_complete_deadlock_msg.format(
                    max_votes=max_votes
                )
            self.game_board.host_broadcast(deadlock_string)
            return self.process_vote_rounds(players_with_most_votes, (revote_count + 1), voting_results)
        else:
            self._vote_widget_vote_finalised()
            return players_with_most_votes[0], voting_results
     
       
    def _dispense_victim_points(self, victim_name, voting_results, points_per_survived_vote=None):
        if not points_per_survived_vote:
            points_per_survived_vote = GamePromptLibrary.points_per_survived_vote
        survivors_rewarded = {}
        for vote_obj in voting_results:
            targeted_player = self.turn_manager._get_target_name_from_response(vote_obj)
            targeted_player = targeted_player.strip() if targeted_player else ""
            if targeted_player and targeted_player != victim_name:
                self.game_board.append_agent_points(targeted_player, points_per_survived_vote)
                survivors_rewarded[targeted_player] = survivors_rewarded.get(targeted_player, 0) + points_per_survived_vote

        if survivors_rewarded:
            reward_str = ", ".join([f"{name} (+{pts})" for name, pts in survivors_rewarded.items()])

            self.game_board.host_broadcast(
                f"🛡️ BULLET DODGER BONUS! The following players took heat but survived the vote. "
                f"They receive points for every vote they survived: {reward_str}"
            )
   
    ###############
    #   Running   #
    ###############        
    
    