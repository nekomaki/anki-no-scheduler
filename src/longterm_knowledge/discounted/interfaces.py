from functools import cache
from typing import Protocol

try:
    from ...fsrs.interfaces import FSRSProtocol
    from ...fsrs.types import State
except ImportError:
    from fsrs.interfaces import FSRSProtocol
    from fsrs.types import State

from . import GAMMA, MAX_DEPTH, TOL
from .utils import knowledge_discounted_integral


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
    @cache
    def calc_knowledge(
        self: KnowledgeDiscountedProtocol, state: State, elapsed_days: float
    ) -> float:
        return knowledge_discounted_integral(
            stability=state.stability,
            decay=self.decay,
            factor=self.factor,
            t_begin=elapsed_days,
            gamma=GAMMA,
            tol=TOL,
        )

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
        reviewed_knowledge = self._calc_reviewed_knowledge(state, elapsed_days=elapsed_days)

        return reviewed_knowledge - current_knowledge

    @cache
    def exp_knowledge_gain_futurev1(
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
            state, kg_avg, length, prob = stk.pop()

            next_states = self.simulate(state, elapsed_days)

            for next_prob, next_state in next_states:
                next_kg = self.exp_knowledge_gain(next_state, elapsed_days=elapsed_days)
                if next_kg > kg_avg:
                    next_kg_avg = (kg_avg * length + next_kg) / (length + 1)
                    if length < MAX_DEPTH:
                        stk.append(
                            (
                                next_state,
                                next_kg_avg,
                                length + 1,
                                prob * next_prob,
                            )
                        )
                    else:
                        result += prob * next_prob * next_kg_avg
                else:
                    result += prob * next_prob * kg_avg

        return result

    @cache
    def exp_knowledge_gain_future(
        self: KnowledgeDiscountedProtocol,
        state: State,
        elapsed_days: float,
    ) -> float:
        """
        Calculate the expected knowledge gain including a few future reviews with FSRS simulation.
        """
        if MAX_DEPTH == 0:
            return self.exp_knowledge_gain(state, elapsed_days=elapsed_days)

        initial_knowledge = self.calc_knowledge(state, elapsed_days=elapsed_days)
        stk = [(state, initial_knowledge, 0, 1.0)]

        result = 0.0

        while stk:
            state, last_knowledge, length, prob = stk.pop()

            next_states = self.simulate(state, elapsed_days)
            next_knowledges = [
                self.calc_knowledge(next_state[1], elapsed_days=0) for next_state in next_states
            ]
            expected_knowledge = sum(
                prob * knowledge for (prob, _), knowledge in zip(next_states, next_knowledges)
            )

            if (
                length == 0
                or (expected_knowledge - initial_knowledge) / (length + 1)
                > (last_knowledge - initial_knowledge) / length
            ):
                for (next_prob, next_state), next_knowledge in zip(next_states, next_knowledges):
                    if length < MAX_DEPTH:
                        stk.append(
                            (
                                next_state,
                                next_knowledge,
                                length + 1,
                                prob * next_prob,
                            )
                        )
                    else:
                        result += (
                            prob * next_prob * (next_knowledge - initial_knowledge) / (length + 1)
                        )
            else:
                result += prob * (last_knowledge - initial_knowledge) / length

        return result

    # @cache
    # def exp_knowledge_gain_future(
    #     self: KnowledgeDiscountedProtocol,
    #     state: State,
    #     elapsed_days: float,
    # ) -> float:
    #     """
    #     Calculate the expected knowledge gain including a few future reviews with FSRS simulation.
    #     """
    #     if MAX_DEPTH == 0:
    #         return self.exp_knowledge_gain(state, elapsed_days)

    #     next_states = self.simulate(state, elapsed_days)
    #     current_knowledge = self.calc_knowledge(state, elapsed_days=elapsed_days)
    #     next_kgs = [
    #         self.calc_knowledge(next_state[1], elapsed_days=0) - current_knowledge
    #         for next_state in next_states
    #     ]
    #     stk = [
    #         (next_state, next_kg, 1, next_prob)
    #         for (next_prob, next_state), next_kg in zip(next_states, next_kgs)
    #     ]

    #     result = 0.0

    #     while stk:
    #         state, last_kg, length, prob = stk.pop()

    #         next_states = self.simulate(state, elapsed_days)
    #         current_knowledge = self.calc_knowledge(state, elapsed_days=elapsed_days)
    #         next_kgs = [
    #             self.calc_knowledge(next_state[1], elapsed_days=0) - current_knowledge
    #             for next_state in next_states
    #         ]

    #         for (next_prob, next_state), next_kg in zip(next_states, next_kgs):
    #             if next_kg > last_kg:
    #                 if length == MAX_DEPTH:
    #                     result += prob * next_prob * next_kg
    #                 else:
    #                     stk.append(
    #                         (
    #                             next_state,
    #                             next_kg,
    #                             length + 1,
    #                             prob * next_prob,
    #                         )
    #                     )
    #             else:
    #                 result += next_prob * prob * last_kg

    #     return result

    # @cache
    # def exp_knowledge_gain_future(
    #     self: KnowledgeDiscountedProtocol,
    #     state: State,
    #     elapsed_days: float,
    # ) -> float:
    #     """
    #     A simplified future estimator.
    #     """
    #     initial_knowledge = self.calc_knowledge(state, elapsed_days=elapsed_days)
    #     prob_current = 1.0
    #     result = 0.0

    #     for i in range(MAX_DEPTH + 1):
    #         next_states = self.simulate(state, elapsed_days)
    #         result += (
    #             prob_current
    #             * next_states[1][0]
    #             * (self.calc_knowledge(next_states[1][1], elapsed_days=0) - initial_knowledge)
    #             / (i + 1)
    #         )

    #         prob, state = next_states[0]
    #         prob_current *= prob

    #     result += (
    #         prob_current
    #         * (self.calc_knowledge(next_states[0][1], elapsed_days=0) - initial_knowledge)
    #         / (MAX_DEPTH + 1)
    #     )

    #     return result
