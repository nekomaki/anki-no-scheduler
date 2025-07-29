try:
    from ...fsrs.fsrs4 import FSRS4
except ImportError:
    from fsrs.fsrs4 import FSRS4

from .interfaces import KnowledgeDiscountedMixin


class FSRS4KnowledgeDiscounted(KnowledgeDiscountedMixin, FSRS4): ...
