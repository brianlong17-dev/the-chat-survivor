from dataclasses import dataclass


@dataclass
class MessageEntry:
    messages: list[dict]  # [{"speaker": name, "message": text}] #TODO should also be dataclass since now it has ptb
    id: int #sequential number, allow you to append / access specific convos
    visibility_restriction: set[str] | None = None  # None = public
    closed: bool = False

@dataclass
class RoundEntry:
    phase_number: int
    round_number: int
    messageEntries: list[MessageEntry]
    game_ledger: str = ""
