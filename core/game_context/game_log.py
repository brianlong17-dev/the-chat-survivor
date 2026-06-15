from collections import deque
from core.game_context.models import MessageEntry, MessageBlock, RoundBlock


SYS_ADMIN = "SYS_ADMIN"


class GameLog:
    def __init__(self):
        self.message_id = 0
        self.current_round: RoundBlock = None
        self.completed_round_entries: list[RoundBlock] = []
        self._current_round_summarisation: str = ""
        self._current_round_summarisation_until: int = None

    def all_round_entries(self):
        if self.current_round:
            return self.completed_round_entries + [self.current_round]
        return self.completed_round_entries
        
    def _push_to_game_ledger(self, log):
        self.current_round.game_ledger += f" - {log}\n"
        
    def most_recent_message_id(self) -> int:
        return self.message_id

    def push_current_round_summarisation(self, summary: str, last_message_id: int):
        self._current_round_summarisation = summary
        self._current_round_summarisation_until = last_message_id

    def _is_sys_admin_message(self, message: MessageBlock) -> bool:
        return bool(message.visibility_restriction and SYS_ADMIN in message.visibility_restriction)

    def messages_since(self, message_id: int) -> list[MessageBlock]:
        return [m for m in self.current_round.conversation_entries if m.id > message_id and not self._is_sys_admin_message(m)]

    def _current_round_messages_up_to(self, message_id: int) -> list[MessageBlock]:
                return [m for m in self.current_round.conversation_entries if m.id <= message_id and not self._is_sys_admin_message(m)]

    def _current_round_most_recent_player_entry(self, reserved_names):
        for message_block in reversed(self.current_round.conversation_entries):
            if len(message_block.message_entries) == 1 and message_block.message_entries[0].speaker not in reserved_names:
                return message_block
        return None


    def _current_round_most_recent_conversation_entry(self):
        message_blocks = [
            message_block for message_block in self.current_round.conversation_entries
            if message_block.visibility_restriction is None
        ]
        return message_blocks[-1] if message_blocks else None

    def _is_host_message(self, message_block, host_name: str) -> bool:
        if not message_block.message_entries or len(message_block.message_entries) != 1:
            return False
        return message_block.message_entries[0].speaker == host_name

    def _get_conversation_entry(self, conversation_id) -> MessageBlock | None:
        return next((mb for mb in self.current_round.conversation_entries if mb.id == conversation_id), None)

    def _update_history(self, player_name: str, message: str, private_thought_brief=None, visibility_restriction=None) -> int:
        self.message_id += 1
        message_block = MessageBlock(
            message_entries=[MessageEntry(speaker=player_name, public_output=message, private_thought_brief=private_thought_brief)],
            id=self.message_id,
            visibility_restriction=visibility_restriction
        )
        self.current_round.conversation_entries.append(message_block)
        return self.message_id

    def completed_phase_rounds(self, phase_number: int) -> list[RoundBlock]:
        return [r for r in self.completed_round_entries if r.phase_number == phase_number]

    def start_round(self, phase_number: int, round_number: int):
        self._current_round_summarisation = ""
        self._current_round_summarisation_until = None
        self.current_round = RoundBlock(phase_number=phase_number, round_number=round_number, conversation_entries=[])

    def close_round(self):
        self.completed_round_entries.append(self.current_round)
