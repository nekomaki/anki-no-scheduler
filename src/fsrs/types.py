from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class State:
    difficulty: float
    stability: float


class FSRSProtocol(Protocol):
    def simulate(
        self,
        state: State,
        t_review: float,
        retention: Optional[float] = None,
    ) -> list[tuple[float, State]]: ...
