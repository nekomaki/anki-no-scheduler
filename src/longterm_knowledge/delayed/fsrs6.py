try:
    from ...fsrs.fsrs6 import FSRS6
    from ...fsrs.types import State
except ImportError:
    from fsrs.fsrs6 import FSRS6
    from fsrs.types import State

from .interfaces import KnowledgeDelayedMixin


class FSRS6KnowledgeDelayed(KnowledgeDelayedMixin, FSRS6): ...


if __name__ == "__main__":
    state = State(difficulty=10.0, stability=0.01)
    elapsed_days = 30

    import time

    tic = time.time()

    today = time.time() // 86400
    due = 30

    # for i in range(10000):
    fsrs = FSRS6KnowledgeDelayed.from_list_with_due(
        due=due,
        params=[
            0.8457,
            8.1627,
            17.1531,
            100.0000,
            6.2004,
            0.8907,
            3.0530,
            0.0282,
            2.3039,
            0.0302,
            1.2036,
            1.3832,
            0.0883,
            0.1358,
            1.5999,
            0.5648,
            2.2040,
            0.7055,
            0.1141,
            0.0916,
            0.1000,
        ],
    )
    # retrivibility = fsrs.power_forgetting_curve(elapsed_days, state.stability)
    day = 30
    knowledge_gain = fsrs.exp_knowledge_gain_future(state, elapsed_days=day, today=day)

    print(f"Expected knowledge gain: {knowledge_gain}")
    # print(f"Retrievability: {retrivibility}")

    toc = time.time()
    print(f"Time taken: {toc - tic:.4f} seconds")
