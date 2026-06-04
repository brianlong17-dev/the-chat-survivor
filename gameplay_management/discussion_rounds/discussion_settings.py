from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DiscussionLoop:
    turn_prompt: str = "Chat and strategise"
    host_message: Optional[str] = None
    additional_thought_prompt: Optional[str] = None
    directed_turn_prompt: str = ""
    directed_public_response_prompt: str = ""
    directed_additional_thought_prompt: str = ""


@dataclass
class DiscussionRoundSettings:
    loops: list[DiscussionLoop] = field(
        default_factory=lambda: [DiscussionLoop()]
    )

    @property
    def loop_count(self) -> int:
        return len(self.loops)


@dataclass
class PhaseDiscussionRoundSettings:
    settings: list[DiscussionRoundSettings] = field(
        default_factory=lambda: [DiscussionRoundSettings()]
    )
    
    def settings_for_index(self, i):
        if i > len(self.settings) - 1:
            print(f"Out of index discussion setting for {i}. " )
            return DiscussionRoundSettings()

        else:
            return self.settings[i]
