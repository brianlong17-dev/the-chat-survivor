from typing import TYPE_CHECKING
from core.game_context.dashboard import Dashboard
from core.game_context.models import RoundBlock, MessageBlock

if TYPE_CHECKING:
    from core.gameboard import GameBoard
    from core.game_context.game_log import GameLog
    from agents.base_agent import BaseAgent



class ContextBuilder:

    def __init__(self, game_board: 'GameBoard', game_log: 'GameLog'):
        self.game_board = game_board
        self.game_log = game_log
        self.min_rounds_for_context = 0 #for 2.5, they can't handle the excessive context.
        self._recent_rounds_in_full = 1
        #some settings can probably move here

    def current_round_formatted(self, agent: 'BaseAgent', incl_scores=False):
        current_round = self.game_log.current_round
        score_footer = None

        score_header = f"{self._round_header(current_round)}\n\n"
        if incl_scores:
            if self.game_board.score_changed_in_round:
                score_header += f"{self._round_score_topper_modified()}\n"
                score_footer = f"\n{self._round_score_updated(agent)}\n"
            else:
                score_header +=  f"{self._round_score_topper_unchanged(agent)}\n"
            
        if self.game_log._current_round_summarisation:
            round_to_format = self._round_after_id(current_round,
                            self.game_log._current_round_summarisation_until)
            round_text = self.game_log._current_round_summarisation + self._formatted_round(round_to_format, agent, incl_header=False)
        else:
            round_text = self._formatted_round(self.game_log.current_round, agent, incl_header=False)
        
        parts = [p for p in [score_header, round_text, score_footer] if p]
        return "".join(parts)
        
    def _round_score_topper_unchanged(self, agent):
        scores = dict(self.game_board.agent_scores)
        header = self._scores_inline(scores, "SCORES (CURRENT)")
        return f"{header}\n{self._score_status_string(agent, scores)}"

    def _round_score_topper_modified(self):
        scores = self.game_board.scores_at_round_start
        return self._scores_inline(scores, "SCORES (START OF ROUND)")

    def _round_score_updated(self, agent):
        scores = dict(self.game_board.agent_scores)
        header = self._scores_inline(scores, "SCORES (UPDATED)")
        return f"{header}\n{self._score_status_string(agent, scores)}"

    def _score_status_string(self, agent, scores=None):
        if scores is None:
            scores = dict(self.game_board.agent_scores)
        if not scores:
            return ""
        max_score = max(scores.values())
        leaders = [name for name, score in scores.items() if score == max_score]
        my_score = scores.get(agent.name, 0)
        status = ""
        if agent.name in leaders:
            if my_score == 0:
                return ""
            if len(leaders) > 1:
                return "STATUS: Tied for 1st."
            return "STATUS: You are winning."
        return f"STATUS: You are {max_score - my_score} points behind the leader."

    def _scores_inline(self, scores: dict, label: str) -> str:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        inner = " | ".join(f"{name}: {score}" for name, score in sorted_scores)
        return Dashboard.header(f"{label}: {inner}")

    def _round_after_id(self, round_block, message_id):
        round_messages = []
        for message_block in round_block.conversation_entries:
            if message_block.id > message_id:
                round_messages.append(message_block)
        return RoundBlock(phase_number=round_block.phase_number, round_number=round_block.round_number, conversation_entries=round_messages)

    def _previous_round_entries_for_context(self):
        rounds = self.game_log.completed_phase_rounds(self.game_board.phase_number)
        if len(rounds) < self.min_rounds_for_context:
            #will never reach here if 0
            rounds = self.game_log.completed_round_entries[-self.min_rounds_for_context:]
        return rounds
        
    def previous_rounds_formatted(self, agent: 'BaseAgent',  use_game_ledger=False):
        rounds = self._previous_round_entries_for_context()
        if len(rounds) == 0:
            return ""
        formatted = []
        for i, r in enumerate(rounds):
            is_recent = i == len(rounds) - self._recent_rounds_in_full
            if not is_recent and r.game_ledger and use_game_ledger:
                formatted.append(f"\n{self._round_header(r)}\n===ROUND SUMMARY LEDGER===\n{r.game_ledger}")
            else:
                formatted.append(self._formatted_round(r, agent))
        rounds_string = f"=== PAST {len(rounds)} ROUNDS  ===\n"
        rounds_string += "\n\n".join(formatted)
        return rounds_string
    
    def phase_rounds_string(self, agent: 'BaseAgent'):  # Used to make a phase to summarise
        return self._formatted_phase(self.game_board.phase_number, agent)

    def _formatted_phase(self, phase_number, agent):
        rounds = self.game_log.completed_phase_rounds(phase_number)
        if len(rounds) == 0:
            return "This is the first round. There is no prior history."

        history_blocks = []
        for i, round_block in enumerate(rounds):
            history_blocks.append(self._formatted_round(round_block, agent))
        return "\n\n".join(history_blocks)

    def _round_header(self, round_block):
        return f"--- Phase: {round_block.phase_number}, Round: {round_block.round_number} ---"

    
    def _formatted_round(self, round_block: 'RoundBlock', agent: 'BaseAgent', incl_header=True):

        output = f"\n{self._round_header(round_block)}\n" if incl_header else ""

        if len(round_block.conversation_entries) == 0:
            return output + "No messages yet for round."

        for message_block in round_block.conversation_entries:
            if message_block.visibility_restriction is None:
                output += self._formatted_public_block(round_block, message_block, agent)
            elif agent.name in message_block.visibility_restriction:
                output += self._formatted_restricted_block(message_block)
        if round_block.game_ledger:
            output += "\n\n===ROUND SUMMARY LEDGER===\n"
            output += round_block.game_ledger
        return output

    def _formatted_public_block(self, round_block: 'RoundBlock', message_block: 'MessageBlock', agent: 'BaseAgent') -> str:
        anchor_message_normal = "\n===[ ^^^ This was your last message — react to what's happened since. Don't repeat above message. ]===\n"
        anchor_message_successive_turn = "\n===[ ^^^ This was your last message — it's already been said. Your turn now is a fresh action, not a reaction. Don't repeat or recap the above; respond only to what the host says below. ]===\n"

        output = ""
        for i, message_entry in enumerate(message_block.message_entries):
            output += f"\n{message_entry.speaker}: {message_entry.public_output}"
            if message_entry.speaker == agent.name and message_entry.private_thought_brief:
                output += f"\n[YOUR INTERNAL PRIVATE THOUGHT]: {message_entry.private_thought_brief} [/END THOUGHT] \n"

            if agent.last_message_id and message_block.id == agent.last_message_id[0] and i == agent.last_message_id[1]:
                if self._player_message_block_after(round_block, message_block, i):
                    output += anchor_message_normal
                else:
                    output += anchor_message_successive_turn
        return output

    def _formatted_restricted_block(self, message_block: 'MessageBlock') -> str:
        if self.game_board.SYS_ADMIN in message_block.visibility_restriction:
            #We dont need the tags for a sys_admin message
            output = ""
            for message_entry in message_block.message_entries:
                output += f"\n [Private System Message] {message_entry.public_output} [End Private Message]"
            return output

        names = ", ".join(message_block.visibility_restriction)
        output = f"\n=== Private Conversation between {names} ===\n"
        for message_entry in message_block.message_entries:
            output += f"\n{message_entry.speaker}: {message_entry.public_output}"
        if message_block.closed:
            output += f"\n=== END OF Private Conversation between {names} ===\n"
        return output

    def _next_round_block(self, round_block):
        rounds = self.game_log.completed_round_entries
        for i, a_round_block in enumerate(rounds):
            if a_round_block is round_block:
                if i + 1 < len(rounds):
                    return rounds[i + 1]
                return self.game_log.current_round #if round_block is in completed rounds it never gets here - returns None
            
        return None
                
    def _player_message_in_message_block_after(self, message_block: 'MessageBlock', index):
        for i, message_entry in enumerate(message_block.message_entries):
            if i > index and message_entry.speaker not in self.game_board.RESERVED_NAMES:
                return True
        return False
        
    def _player_message_block_after(self, round_block: 'RoundBlock', anchor_message_block: 'MessageBlock', index) -> bool:
        if self._player_message_in_message_block_after(anchor_message_block, index):
            return True
        else:
            while round_block:
                for message_block in round_block.conversation_entries:
                    if message_block.id > anchor_message_block.id:
                        for message_entry in message_block.message_entries:
                            if message_entry.speaker not in self.game_board.RESERVED_NAMES:
                                return True
                round_block = self._next_round_block(round_block)
            return False

    def get_dashboard_string(self, agent: 'BaseAgent') -> str:
        return Dashboard.render(agent, self.game_board)
       