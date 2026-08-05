from dataclasses import dataclass


@dataclass
class ModelOption:
    id: str
    name: str
    default: bool = False
