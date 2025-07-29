try:
    from ...fsrs.fsrs6 import FSRS6
except ImportError:
    from fsrs.fsrs6 import FSRS6

from .interfaces import KnowledgeDiscountedMixin


class FSRS6KnowledgeDiscounted(KnowledgeDiscountedMixin, FSRS6): ...
