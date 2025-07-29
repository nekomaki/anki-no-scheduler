try:
    from ...fsrs.fsrs6 import FSRS6
except ImportError:
    from fsrs.fsrs6 import FSRS6

from .interfaces import KnowledgeDelayedMixin


class FSRS6KnowledgeDelayed(KnowledgeDelayedMixin, FSRS6): ...
