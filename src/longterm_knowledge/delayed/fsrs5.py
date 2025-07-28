try:
    from ...fsrs.fsrs5 import FSRS5
except ImportError:
    from fsrs.fsrs5 import FSRS5

from .interfaces import KnowledgeDelayedMixin


class FSRS5KnowledgeDelayed(KnowledgeDelayedMixin, FSRS5): ...
