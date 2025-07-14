try:
    from ..fsrs_utils.fsrs4 import DECAY, fsrs_simulate
    from ..fsrs_utils.types import State
except ImportError:
    from fsrs_utils.fsrs4 import DECAY, fsrs_simulate
    from fsrs_utils.types import State

from .fsrs6 import calc_knowledge as calc_knowledge_v6


def calc_knowledge(state: State, elapsed_days: float) -> float:
    return calc_knowledge_v6(state, DECAY, elapsed_days)


def _calc_reviewed_knowledge(
    state: State, fsrs_params: tuple, elapsed_days: float
) -> float:
    next_states = fsrs_simulate(state, fsrs_params, elapsed_days)

    knowledge = sum(
        prob * calc_knowledge(new_state, elapsed_days=0)
        for prob, new_state, _ in next_states
    )

    return knowledge


def exp_knowledge_gain(state: State, fsrs_params: tuple, elapsed_days: float) -> float:
    current_knowledge = calc_knowledge(state, elapsed_days=elapsed_days)
    reviewed_knowledge = _calc_reviewed_knowledge(
        state, fsrs_params=fsrs_params, elapsed_days=elapsed_days
    )

    return reviewed_knowledge - current_knowledge


if __name__ == "__main__":
    state = State(1.0, 1.0)
    fsrs_params = (
        1.0191,
        8.2268,
        17.8704,
        100.0000,
        6.6634,
        0.7805,
        2.2023,
        0.0241,
        1.9304,
        0.0000,
        1.3965,
        1.7472,
        0.1247,
        0.1160,
        2.2431,
        0.4258,
        3.1303,
    )
    elapsed_days = 10

    knowledge_gain = exp_knowledge_gain(state, fsrs_params, elapsed_days)
    print(f"Expected knowledge gain: {knowledge_gain:.3f}")
