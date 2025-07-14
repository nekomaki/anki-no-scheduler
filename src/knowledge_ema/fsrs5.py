try:
    from ..fsrs_utils.fsrs5 import DECAY
    from ..fsrs_utils.types import State
except ImportError:
    from fsrs_utils.fsrs5 import DECAY
    from fsrs_utils.types import State

from .fsrs6 import calc_knowledge as calc_knowledge_v6
from .fsrs6 import exp_knowledge_gain as exp_knowledge_gain_v6


def calc_knowledge(state: State, elapsed_days: float) -> float:
    return calc_knowledge_v6(state, decay=DECAY, elapsed_days=elapsed_days)


def exp_knowledge_gain(state: State, fsrs_params: tuple, elapsed_days: float) -> float:
    fsrs_params = tuple(fsrs_params) + (0.0, -DECAY)

    return exp_knowledge_gain_v6(
        state,
        fsrs_params=fsrs_params,
        elapsed_days=elapsed_days,
    )
