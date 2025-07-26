from typing import Optional

from . import FSRS
from .fsrs6 import FSRS6
from .types import State

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

DECAY = -0.5
FACTOR = 0.9 ** (1 / DECAY) - 1


class FSRS5(FSRS):
    EXPECTED_LENGTH = 19
    VERSION = 5

    def __init__(self, params: tuple[float, ...], fsrs6: Optional[FSRS6] = None):
        super().__init__(params=params)
        self._fsrs6 = fsrs6 or FSRS6(params + (0.0, -DECAY))

    @classmethod
    def power_forgetting_curve(cls, t: float, s: float) -> float:
        return (1 + FACTOR * t / s) ** DECAY

    @classmethod
    def interval_from_retention(cls, state: State, retention: float) -> float:
        alpha = (retention ** (1 / DECAY) - 1) / FACTOR
        interval = state.stability * alpha
        return interval

    def simulate(
        self,
        state: State,
        t_review: float,
        retention: Optional[float] = None,
    ) -> list[tuple[float, State]]:
        return self._fsrs6.simulate(state, t_review, retention)
