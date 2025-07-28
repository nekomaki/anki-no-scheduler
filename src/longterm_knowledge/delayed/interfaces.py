from functools import cache
from typing import Protocol, Type, TypeVar

try:
    from ...fsrs.interfaces import FSRSProtocol
    from ...fsrs.types import State
except ImportError:
    from fsrs.interfaces import FSRSProtocol
    from fsrs.types import State

from . import MAX_DEPTH

T = TypeVar("T", bound="KnowledgeDelayedProtocol")


class KnowledgeDelayedProtocol(FSRSProtocol, Protocol):
    due: float

    @classmethod
    def from_tuple_with_due(
        cls: Type[T], params: tuple[float, ...], due: float
    ) -> T: ...
    @classmethod
    def from_list_with_due(cls: Type[T], params: list[float], due: float) -> T: ...
    def calc_knowledge(
        self,
        state: State,
        elapsed_days: float,
        today: float,
    ) -> float: ...
    def _calc_reviewed_knowledge(
        self, state: State, elapsed_days: float, today: float
    ) -> float: ...
    def exp_knowledge_gain(
        self, state: State, elapsed_days: float, today: float
    ) -> float: ...
    def exp_knowledge_gain_future(
        self,
        state: State,
        elapsed_days: float,
        today: float,
    ) -> float: ...


class KnowledgeDelayedMixin:
    @classmethod
    @cache
    def from_tuple_with_due(cls: Type[T], params: tuple[float, ...], due: float) -> T:
        inst = cls.from_tuple(params)
        inst.due = due
        return inst

    @classmethod
    def from_list_with_due(cls: Type[T], params: list[float], due: float) -> T:
        return cls.from_tuple_with_due(tuple(params), due)

    def calc_knowledge(
        self: KnowledgeDelayedProtocol,
        state: State,
        elapsed_days: float,
        today: float,
    ) -> float:
        assert self.due - today >= 0, "Due date must be in the future"
        return self.power_forgetting_curve(
            elapsed_days + self.due - today + 1, state.stability
        )

    def _calc_reviewed_knowledge(
        self: KnowledgeDelayedProtocol, state: State, elapsed_days: float, today: float
    ) -> float:
        next_states = self.simulate(state, elapsed_days)

        knowledge = sum(
            prob * self.calc_knowledge(next_state, elapsed_days=0, today=today)
            for prob, next_state in next_states
        )

        return knowledge

    @cache
    def exp_knowledge_gain(
        self: KnowledgeDelayedProtocol, state: State, elapsed_days: float, today: float
    ) -> float:
        current_knowledge = self.calc_knowledge(
            state, elapsed_days=elapsed_days, today=today
        )
        reviewed_knowledge = self._calc_reviewed_knowledge(
            state, elapsed_days=elapsed_days, today=today
        )

        return reviewed_knowledge - current_knowledge

    @cache
    def exp_knowledge_gain_future(
        self: KnowledgeDelayedProtocol, state: State, elapsed_days: float, today: float
    ) -> float:
        """
        Calculate the expected knowledge gain including a few future reviews with FSRS simulation.
        """
        stk = [(state, self.exp_knowledge_gain(state, elapsed_days, today), 1, 1.0)]

        if MAX_DEPTH == 0:
            return stk[0][1]

        result = 0.0

        while stk:
            state, knowledge_gain_avg, workload, prob = stk.pop()

            next_states = self.simulate(state, elapsed_days)

            for next_prob, next_state in next_states:
                next_knowledge_gain = self.exp_knowledge_gain(
                    next_state, elapsed_days=elapsed_days, today=today
                )
                if next_knowledge_gain > knowledge_gain_avg:
                    next_knowledge_gain_avg = (
                        knowledge_gain_avg * workload + next_knowledge_gain
                    ) / (workload + 1)
                    if workload + 1 < MAX_DEPTH and today + workload <= self.due:
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
