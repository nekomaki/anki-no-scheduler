from .fsrs_v6 import compute_current_knowledge as compute_current_knowledge_v6
from .fsrs_v6 import exp_knowledge_gain as exp_knowledge_gain_v6
from .fsrs_v6 import knowledge_ema as knowledge_ema_v6
from .fsrs_v6 import power_forgetting_curve as power_forgetting_curve_v6

GAMMA = 0.99

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

NEW_WORKLOAD = 1
FORGET_WORKLOAD = 1

DECAY = -0.5
FACTOR = 0.9 ** (1 / DECAY) - 1


def power_forgetting_curve(t, s):
    return power_forgetting_curve_v6(t, s, DECAY)


def knowledge_ema(stability, t_begin=None, t_end=None, gamma=GAMMA):
    return knowledge_ema_v6(
        stability,
        factor=FACTOR,
        decay=DECAY,
        t_begin=t_begin,
        t_end=t_end,
        gamma=gamma,
    )


def compute_current_knowledge(state, elapsed_days):
    return compute_current_knowledge_v6(state, DECAY, elapsed_days)


def exp_knowledge_gain(state, fsrs_params, elapsed_days, new_rating_probs):
    fsrs_params = tuple(fsrs_params) + (0.0, -DECAY)

    return exp_knowledge_gain_v6(
        state,
        fsrs_params=fsrs_params,
        elapsed_days=elapsed_days,
        new_rating_probs=new_rating_probs,
    )
