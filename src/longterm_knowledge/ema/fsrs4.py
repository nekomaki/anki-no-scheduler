from typing import TYPE_CHECKING

try:
    from ...fsrs.fsrs4 import DECAY, FSRS4
    from ...fsrs.types import State
    from ..knowledge import KnowledgeMixin
except ImportError:
    from fsrs.fsrs4 import DECAY, FSRS4
    from fsrs.types import State
    from longterm_knowledge.knowledge import KnowledgeMixin

if TYPE_CHECKING:

    class _FSRS4(FSRS4):
        pass

else:
    _FSRS4 = FSRS4

from .fsrs6 import _calc_knowledge_cached as _calc_knowledge_cached_v6


class FSRS4Knowledge(KnowledgeMixin, _FSRS4):
    def calc_knowledge(self, state: State, elapsed_days: float) -> float:
        return _calc_knowledge_cached_v6(
            state.stability, decay=DECAY, elapsed_days=elapsed_days
        )


if __name__ == "__main__":
    state = State(1.0, 1.0)
    fsrs = FSRS4Knowledge.from_tuple(
        (
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
    )
    elapsed_days = 10

    knowledge_gain = fsrs.exp_knowledge_gain(state, elapsed_days)
    print(f"Expected knowledge gain: {knowledge_gain:.3f}")
