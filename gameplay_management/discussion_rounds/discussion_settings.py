from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DiscussionLoop:
    topic: str
    host_message: Optional[str] = None
    additional_thought_prompt: Optional[str] = None


@dataclass
class DiscussionRoundSettings:
    loops: list[DiscussionLoop] = field(
        default_factory=lambda: [DiscussionLoop(topic="Chat and strategise")]
    )

    @property
    def loop_count(self) -> int:
        return len(self.loops)

    @property
    def opening_topic(self) -> str:
        return self.loops[0].topic
