try:
    from ...fsrs.fsrs5 import DECAY, FSRS5
    from ...fsrs.types import State
    from .fsrs6 import FSRS6KnowledgeDiscounted
except ImportError:
    from fsrs.fsrs5 import DECAY, FSRS5
    from fsrs.types import State
    from longterm_knowledge.discounted.fsrs6 import FSRS6KnowledgeDiscounted

from .interfaces import KnowledgeDiscountedMixin


class FSRS5KnowledgeDiscounted(KnowledgeDiscountedMixin, FSRS5):
    _fsrs6: FSRS6KnowledgeDiscounted

    def __init__(self, params: tuple[float, ...]):
        fsrs6 = FSRS6KnowledgeDiscounted(params + (0.0, -DECAY))
        super().__init__(params=params, fsrs6=fsrs6)

    def calc_knowledge(self, state: State, elapsed_days: float) -> float:
        return self._fsrs6.calc_knowledge(state, elapsed_days)


if __name__ == "__main__":
    state = State(difficulty=10.0, stability=0.01)
    elapsed_days = 30

    import time

    tic = time.time()

    for i in range(1000):
        fsrs = FSRS5KnowledgeDiscounted.from_list(
            [
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
                0.1141
            ]
        )
        retrivibility = fsrs.power_forgetting_curve(elapsed_days, state.stability)
        knowledge_gain = fsrs.exp_knowledge_gain_future(state, i)
    print(f"Expected knowledge gain: {knowledge_gain}")
    print(f"Retrievability: {retrivibility}")

    toc = time.time()
    print(f"Time taken: {toc - tic:.4f} seconds")
