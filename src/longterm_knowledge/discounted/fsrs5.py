from typing import TYPE_CHECKING

try:
    from ...fsrs.fsrs5 import DECAY, FSRS5
    from ...fsrs.types import State
    from ..knowledge import KnowledgeMixin
    from .fsrs6 import FSRS6Knowledge
except ImportError:
    from fsrs.fsrs5 import DECAY, FSRS5
    from fsrs.types import State
    from longterm_knowledge.discounted.fsrs6 import FSRS6Knowledge
    from longterm_knowledge.knowledge import KnowledgeMixin

if TYPE_CHECKING:

    class _FSRS5(FSRS5):
        pass

else:
    _FSRS5 = FSRS5


class FSRS5Knowledge(KnowledgeMixin, _FSRS5):
    _fsrs6: FSRS6Knowledge

    def __init__(self, params: tuple[float, ...]):
        fsrs6 = FSRS6Knowledge(params + (0.0, -DECAY))
        super().__init__(params=params, fsrs6=fsrs6)

    def calc_knowledge(self, state: State, elapsed_days: float) -> float:
        return self._fsrs6.calc_knowledge(state, elapsed_days)
