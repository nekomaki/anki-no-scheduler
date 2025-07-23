try:
    from ..fsrs_utils.types import State
except ImportError:
    from fsrs_utils.types import State

MAX_DEPTH = 10


def exp_knowledge_gain_future_greedy(
    state: State,
    fsrs_params: tuple,
    elapsed_days: float,
    fsrs_simulate_func: callable,
    exp_knowledge_gain_func: callable,
) -> float:
    """
    Calculate the expected knowledge gain including a few future reviews with FSRS simulation.
    """
    stk = [(state, exp_knowledge_gain_func(state, fsrs_params, elapsed_days), 1, 1.0)]

    result = 0.0

    while stk:
        state, knowledge_gain_avg, workload, prob = stk.pop()

        next_states = fsrs_simulate_func(state, fsrs_params, elapsed_days)
        for next_prob, next_state, _ in next_states:
            next_knowledge_gain = exp_knowledge_gain_func(
                next_state, fsrs_params=fsrs_params, elapsed_days=elapsed_days
            )
            if workload < MAX_DEPTH and next_knowledge_gain > knowledge_gain_avg:
                next_knowledge_gain_avg = (
                    knowledge_gain_avg * workload + next_knowledge_gain
                ) / (workload + 1)
                stk.append(
                    (
                        next_state,
                        next_knowledge_gain_avg,
                        workload + 1,
                        prob * next_prob,
                    )
                )
            else:
                result += prob * next_prob * knowledge_gain_avg

    return result
