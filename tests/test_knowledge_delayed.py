import math

from fsrs.fsrs4 import DECAY
from fsrs.types import State
from longterm_knowledge.delayed.fsrs4 import FSRS4KnowledgeDelayed
from longterm_knowledge.delayed.fsrs5 import FSRS5KnowledgeDelayed
from longterm_knowledge.delayed.fsrs6 import FSRS6KnowledgeDelayed


def test_knowledge_delayed():
    fsrs4 = FSRS4KnowledgeDelayed.from_list_with_due([0] * 17, due=1000.0)
    fsrs5 = FSRS5KnowledgeDelayed.from_list_with_due([0] * 19, due=1000.0)
    fsrs6 = FSRS6KnowledgeDelayed.from_list_with_due(
        [0] * 19 + [0.0, -DECAY], due=1000.0
    )

    for difficulty in [1.0, 5.0, 10.0]:
        for stability in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 36500.0]:
            for elapsed_days in [0.0, 1.0, 30.0, 365.0]:
                state = State(difficulty=difficulty, stability=stability)
                today = max(0.0, elapsed_days - 1)
                knowledge_fsrs4 = fsrs4.calc_knowledge(state, elapsed_days, today)
                knowledge_fsrs5 = fsrs5.calc_knowledge(state, elapsed_days, today)
                knowledge_fsrs6 = fsrs6.calc_knowledge(state, elapsed_days, today)

                assert math.isclose(
                    knowledge_fsrs6, knowledge_fsrs5, rel_tol=1e-9
                ), f"Knowledge FSRS6 vs FSRS5 mismatch for state {state}: {knowledge_fsrs6} != {knowledge_fsrs5}"

                assert math.isclose(
                    knowledge_fsrs6, knowledge_fsrs4, rel_tol=1e-9
                ), f"Knowledge FSRS6 vs FSRS4 mismatch for state {state}: {knowledge_fsrs6} != {knowledge_fsrs4}"
