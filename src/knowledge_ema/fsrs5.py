from .fsrs6 import calc_knowledge as calc_knowledge_v6
from .fsrs6 import exp_knowledge_gain as exp_knowledge_gain_v6
from .fsrs6 import power_forgetting_curve as power_forgetting_curve_v6
from .types import State

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

NEW_WORKLOAD = 1
FORGET_WORKLOAD = 1

DECAY = -0.5
FACTOR = 0.9 ** (1 / DECAY) - 1


def power_forgetting_curve(t: float, s: float) -> float:
    return power_forgetting_curve_v6(t, s, DECAY)


def calc_knowledge(state: State, elapsed_days: float) -> float:
    return calc_knowledge_v6(state, decay=DECAY, elapsed_days=elapsed_days)


def exp_knowledge_gain(state: State, fsrs_params: tuple, elapsed_days: float) -> float:
    fsrs_params = tuple(fsrs_params) + (0.0, -DECAY)

    return exp_knowledge_gain_v6(
        state,
        fsrs_params=fsrs_params,
        elapsed_days=elapsed_days,
    )
