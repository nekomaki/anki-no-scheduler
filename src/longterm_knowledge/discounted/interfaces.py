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
    def _calc_knowledge_gain(self, state: State, elapsed_days: float) -> float: ...
    def _calc_knowledge_gain_future(
        self,
        state: State,
        elapsed_days: float,
    ) -> float: ...
    def exp_knowledge_gain(
        self,
        state: State,
        elapsed_days: float,
        future_estimator=False,
        require_non_increasing=False,
    ) -> float: ...


class KnowledgeDiscountedMixin:
    def calc_knowledge(
        self: KnowledgeDiscountedProtocol, state: State, elapsed_days: float
    ) -> float:
        return knowledge_discounted_integral(
            stability=state.stability,
            decay=self.decay,
            factor=self.factor,
            t_begin=elapsed_days,
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

    def _calc_knowledge_gain(
        self: KnowledgeDiscountedProtocol, state: State, elapsed_days: float
    ) -> float:
        current_knowledge = self.calc_knowledge(state, elapsed_days=elapsed_days)
        reviewed_knowledge = self._calc_reviewed_knowledge(state, elapsed_days=elapsed_days)
        knowledge_gain = reviewed_knowledge - current_knowledge

        return knowledge_gain

    def _calc_knowledge_gain_futurev1(
        self: KnowledgeDiscountedProtocol,
        state: State,
        elapsed_days: float,
    ) -> float:
        """
        Calculate the expected knowledge gain including a few future reviews with FSRS simulation.
        Arguments:
            state: Memory state of the card.
            elapsed_days: Elapsed days since the last review.
        Returns:
            Expected knowledge gain including future reviews.
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

    def _calc_knowledge_gain_future(
        self: KnowledgeDiscountedProtocol,
        state: State,
        elapsed_days: float,
    ) -> float:
        """
        Calculate the expected knowledge gain including a few future reviews with FSRS simulation.
        Arguments:
            state: Memory state of the card.
            elapsed_days: Elapsed days since the last review.
        Returns:
            Expected knowledge gain including future reviews.
        """
        if MAX_DEPTH == 0:
            return self.exp_knowledge_gain(state, elapsed_days=elapsed_days)

        initial_knowledge = self.calc_knowledge(state, elapsed_days=elapsed_days)

        def dfs(state: State, last_knowledge: float, depth: int) -> float:
            next_states = self.simulate(state, elapsed_days)
            next_knowledges = [
                self.calc_knowledge(next_state[1], elapsed_days=0) for next_state in next_states
            ]
            expected_knowledge = sum(
                prob * knowledge for (prob, _), knowledge in zip(next_states, next_knowledges)
            )

            if (
                depth == 0
                or (expected_knowledge - initial_knowledge) / (depth + 1)
                > (last_knowledge - initial_knowledge) / depth
            ):
                # Do review
                if depth < MAX_DEPTH:
                    # Do search
                    total = 0.0
                    for (next_prob, next_state), next_knowledge in zip(
                        next_states, next_knowledges
                    ):
                        total += next_prob * dfs(
                            next_state,
                            next_knowledge,
                            depth + 1,
                        )
                    return total
                else:
                    return (expected_knowledge - initial_knowledge) / (depth + 1)
            else:
                # No review
                return (last_knowledge - initial_knowledge) / depth

        return dfs(state, initial_knowledge, 0)

    # def _calc_knowledge_gain_future(
    #     self: KnowledgeDiscountedProtocol,
    #     state: State,
    #     elapsed_days: float,
    # ) -> float:
    #     """
    #     Calculate the expected knowledge gain including a few future reviews with FSRS simulation.
    #     Arguments:
    #         state: Memory state of the card.
    #         elapsed_days: Elapsed days since the last review.
    #     Returns:
    #         Expected knowledge gain including future reviews.
    #     """
    #     if MAX_DEPTH == 0:
    #         return self.exp_knowledge_gain(state, elapsed_days=elapsed_days)

    #     initial_knowledge = self.calc_knowledge(state, elapsed_days=elapsed_days)
    #     stk = [(state, 0, 0.0, 1.0)]

    #     result = 0.0
    #     prob_sum = 0.0

    #     while stk:
    #         state, length, prev_knowledge, prob = stk.pop()

    #         next_states = self.simulate(state, elapsed_days)
    #         next_knowledges = [
    #             self.calc_knowledge(next_state[1], elapsed_days=0) for next_state in next_states
    #         ]
    #         next_knowledges_cutoff = [
    #             next_knowledge
    #             - self.calc_knowledge(next_state[1], elapsed_days=elapsed_days)
    #             * GAMMA**elapsed_days
    #             for (next_state, next_knowledge) in zip(next_states, next_knowledges)
    #         ]

    #         expected_knowledge = sum(
    #             prob * knowledge for (prob, _), knowledge in zip(next_states, next_knowledges)
    #         )

    #         knowledge_if_not_review = prev_knowledge + self.calc_knowledge(
    #             state, elapsed_days=elapsed_days
    #         ) * GAMMA ** (length * elapsed_days)
    #         knowledge_if_review = prev_knowledge + expected_knowledge * GAMMA ** (
    #             length * elapsed_days
    #         )

    #         if (
    #             length == 0
    #             or (knowledge_if_review - initial_knowledge) / (length + 1)
    #             > (knowledge_if_not_review - initial_knowledge) / length
    #         ):
    #             if length < MAX_DEPTH:
    #                 for (next_prob, next_state), next_knowledge_cutoff in zip(
    #                     next_states, next_knowledges_cutoff
    #                 ):
    #                     stk.append(
    #                         (
    #                             next_state,
    #                             length + 1,
    #                             prev_knowledge
    #                             + next_knowledge_cutoff * GAMMA ** (length * elapsed_days),
    #                             prob * next_prob,
    #                         )
    #                     )
    #             else:
    #                 result += prob * (knowledge_if_review - initial_knowledge) / (length + 1)
    #         else:
    #             result += prob * (knowledge_if_not_review - initial_knowledge) / length
    #             prob_sum += prob

    #     return result

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

    def exp_knowledge_gain(
        self: KnowledgeDiscountedProtocol,
        state: State,
        elapsed_days: float,
        lookahead: int = 0,
    ) -> float:
        """
        Calculate the expected knowledge gain.
        Arguments:
            state: Memory state of the card.
            elapsed_days: Elapsed days since the last review.
            lookahead: Lookahead strategy for future reviews.
                0: No lookahead.
                1: Only next day's knowledge check.
                2: Future estimator.
        Returns:
            Expected knowledge gain.
        """
        if lookahead >= 1:
            reviewed_knowledge = self._calc_reviewed_knowledge(state, elapsed_days=elapsed_days)
            tomorrow_reviewed_knowledge = self._calc_reviewed_knowledge(
                state, elapsed_days=elapsed_days + 1
            )
            if reviewed_knowledge < tomorrow_reviewed_knowledge:
                return 0.0

        if lookahead >= 2:
            return self._calc_knowledge_gain_future(state, elapsed_days=elapsed_days)

        return self._calc_knowledge_gain(state, elapsed_days=elapsed_days)
