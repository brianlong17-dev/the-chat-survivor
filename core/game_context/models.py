from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MessageEntry:
    speaker: str
    public_output: str
    private_thought_brief: Optional[str] = None


@dataclass
class MessageBlock:
    #Typically just one message, but can be a private conversation
    message_entries: list[MessageEntry] 
    id: int
    visibility_restriction: set[str] | None = None
    closed: bool = False

@dataclass
class RoundBlock:
    phase_number: int
    round_number: int
    conversation_entries: list[MessageBlock]
    game_ledger: str = ""
