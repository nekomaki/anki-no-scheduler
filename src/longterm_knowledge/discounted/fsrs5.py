try:
    from ...fsrs.fsrs5 import FSRS5
except ImportError:
    from fsrs.fsrs5 import FSRS5

from .interfaces import KnowledgeDiscountedMixin


class FSRS5KnowledgeDiscounted(KnowledgeDiscountedMixin, FSRS5): ...
