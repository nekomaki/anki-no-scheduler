from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    difficulty: float
    stability: float
