from .fsrs6 import fsrs_simulate as fsrs_simulate_v6
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


def fsrs_simulate(
    state: State, fsrs_params: tuple, t_review: float, retention: float | None = None
):
    fsrs_params = tuple(fsrs_params) + (0, -DECAY)
    return fsrs_simulate_v6(state, fsrs_params, t_review, retention)
