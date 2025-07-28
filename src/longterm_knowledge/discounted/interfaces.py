from functools import cache
from typing import Optional, Protocol

try:
    from ...fsrs.interfaces import FSRSProtocol
    from ...fsrs.types import State
except ImportError:
    from fsrs.interfaces import FSRSProtocol
    from fsrs.types import State

from . import MAX_DEPTH


class KnowledgeDiscountedProtocol(FSRSProtocol, Protocol):
    def calc_knowledge(self, state: State, elapsed_days: float) -> float: ...
    def _calc_reviewed_knowledge(self, state: State, elapsed_days: float) -> float: ...
    def exp_knowledge_gain(self, state: State, elapsed_days: float) -> float: ...
    def exp_knowledge_gain_future(
        self,
        state: State,
        elapsed_days: float,
    ) -> float: ...


class KnowledgeDiscountedMixin:
    def calc_knowledge(
        self: KnowledgeDiscountedProtocol,
        state: State,
        elapsed_days: float,
    ) -> float:
        raise NotImplementedError

    def _calc_reviewed_knowledge(
        self: KnowledgeDiscountedProtocol, state: State, elapsed_days: float
    ) -> float:
        next_states = self.simulate(state, elapsed_days)

        knowledge = sum(
            prob * self.calc_knowledge(next_state, elapsed_days=0)
            for prob, next_state in next_states
        )

        return knowledge

    @cache
    def exp_knowledge_gain(
        self: KnowledgeDiscountedProtocol, state: State, elapsed_days: float
    ) -> float:
        current_knowledge = self.calc_knowledge(state, elapsed_days=elapsed_days)
        reviewed_knowledge = self._calc_reviewed_knowledge(
            state, elapsed_days=elapsed_days
        )

        return reviewed_knowledge - current_knowledge

    @cache
    def exp_knowledge_gain_future(
        self: KnowledgeDiscountedProtocol,
        state: State,
        elapsed_days: float,
    ) -> float:
        """
        Calculate the expected knowledge gain including a few future reviews with FSRS simulation.
        """
        stk = [(state, self.exp_knowledge_gain(state, elapsed_days), 1, 1.0)]

        if MAX_DEPTH == 0:
            return stk[0][1]

        result = 0.0

        while stk:
            state, knowledge_gain_avg, workload, prob = stk.pop()

            next_states = self.simulate(state, elapsed_days)

            for next_prob, next_state in next_states:
                next_knowledge_gain = self.exp_knowledge_gain(
                    next_state, elapsed_days=elapsed_days
                )
                if next_knowledge_gain > knowledge_gain_avg:
                    next_knowledge_gain_avg = (
                        knowledge_gain_avg * workload + next_knowledge_gain
                    ) / (workload + 1)
                    if workload + 1 < MAX_DEPTH:
                        stk.append(
                            (
                                next_state,
                                next_knowledge_gain_avg,
                                workload + 1,
                                prob * next_prob,
                            )
                        )
                    else:
                        result += prob * next_prob * next_knowledge_gain_avg
                else:
                    result += prob * next_prob * knowledge_gain_avg

        return result
