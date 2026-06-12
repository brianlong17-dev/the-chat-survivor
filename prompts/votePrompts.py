class VotePromptLibrary:
    immunity_all_players_reset = (
        "All players have immunity this round! This means... NO ONE HAS IMMUNITY. You are all again at risk of being voted out."
    )

    immunity_players_prefix = (
        "The following players have immunity, and cannot be voted for to leave in this round of voting:"
    )
    elimination_players_prefix = "The following players are up for elimination:"

    elimination_host_msg = (
        "A JOURNEY COMES TO AN END- THE RESULTS ARE FINAL. "
        "*{victim_name}* HAS BEEN EJECTED FROM THE CHAT. ☠ ☠ ☠  \n"
    )

    
    vote_one_player_turn_prompt = (
        "You must vote for one player you want to leave the competition. "
        "They player with the most votes will leave the game. "
        "Who do you vote to leave? Who do you eliminate from {eligible_player_names} and why?"
    )
    vote_one_player_name_field_prompt = "The exact name of the agent to you want to leave the competition.."

    collect_votes_invalid_skip_msg = "Invalid vote by {agent_name}: '{vote}'. Their vote is skipped."
    collect_votes_invalid_self_msg = (
        "Invalid vote by {agent_name} for '{vote}'. This vote will count as a vote against themselves."
    )

    voting_round_random_elimination_msg = (
        "⚡ The tribe is too stubborn. The Judge steps in and eliminates someone at random!"
    )
    voting_tally_msg = "🗳️ VOTING TALLY: {tally}"
    voting_round_tie_msg = (
        "⚖️ We have a tie between {players_with_most_votes}! "
        "We need to revote on these contestants..."
    )
    voting_round_complete_deadlock_msg = (
        "🌀 COMPLETE DEADLOCK. Everyone received {max_votes} vote(s)! You must REVOTE."
    )
    voting_round_no_valid_votes_msg = (
        "No valid votes were cast. The Judge will eliminate someone at random."
    )
