from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class State:
    difficulty: float
    stability: float
