import math

from fsrs.fsrs4 import DECAY
from fsrs.types import State
from longterm_knowledge.discounted.fsrs4 import FSRS4KnowledgeDiscounted
from longterm_knowledge.discounted.fsrs5 import FSRS5KnowledgeDiscounted
from longterm_knowledge.discounted.fsrs6 import FSRS6KnowledgeDiscounted


def test_knowledge_discounted():
    fsrs4 = FSRS4KnowledgeDiscounted.from_list([0] * 17)
    fsrs5 = FSRS5KnowledgeDiscounted.from_list([0] * 19)
    fsrs6 = FSRS6KnowledgeDiscounted.from_list([0] * 19 + [0.0, -DECAY])

    for difficulty in [1.0, 5.0, 10.0]:
        for stability in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 36500.0]:
            for elapsed_days in [0.0, 1.0, 30.0, 365.0]:
                state = State(difficulty=difficulty, stability=stability)
                knowledge_fsrs4 = fsrs4.calc_knowledge(state, elapsed_days)
                knowledge_fsrs5 = fsrs5.calc_knowledge(state, elapsed_days)
                knowledge_fsrs6 = fsrs6.calc_knowledge(state, elapsed_days)

                assert math.isclose(
                    knowledge_fsrs6, knowledge_fsrs5, rel_tol=1e-9
                ), f"Knowledge FSRS6 vs FSRS5 mismatch for state {state}: {knowledge_fsrs6} != {knowledge_fsrs5}"

                assert math.isclose(
                    knowledge_fsrs6, knowledge_fsrs4, rel_tol=1e-9
                ), f"Knowledge FSRS6 vs FSRS4 mismatch for state {state}: {knowledge_fsrs6} != {knowledge_fsrs4}"
