from .fsrs6 import GAMMA
from .fsrs6 import calc_current_knowledge as compute_current_knowledge_v6
from .fsrs6 import exp_knowledge_gain as exp_knowledge_gain_v6
from .fsrs6 import knowledge_ema as knowledge_ema_v6
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


def knowledge_ema(
    stability: float,
    t_begin: float | None = None,
    t_end: float | None = None,
    gamma: float = GAMMA,
) -> float:
    return knowledge_ema_v6(
        stability,
        decay=DECAY,
        factor=FACTOR,
        t_begin=t_begin,
        t_end=t_end,
        gamma=gamma,
    )


def calc_current_knowledge(state: State, elapsed_days: float) -> float:
    return compute_current_knowledge_v6(state, DECAY, elapsed_days)


def exp_knowledge_gain(state: State, fsrs_params: tuple, elapsed_days: float) -> float:
    fsrs_params = tuple(fsrs_params) + (0.0, -DECAY)

    return exp_knowledge_gain_v6(
        state,
        fsrs_params=fsrs_params,
        elapsed_days=elapsed_days,
    )
