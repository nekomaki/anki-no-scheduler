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
