try:
    from ...fsrs.fsrs4 import FSRS4
except ImportError:
    from fsrs.fsrs4 import FSRS4

from .interfaces import KnowledgeDelayedMixin


class FSRS4KnowledgeDelayed(KnowledgeDelayedMixin, FSRS4): ...
