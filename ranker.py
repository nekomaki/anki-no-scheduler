from anki.cards import Card
from anki.scheduler.v3 import QueuedCards
from anki.scheduler.v3 import Scheduler as V3Scheduler
from aqt import mw
from aqt.reviewer import V3CardInfo

from .fsrs_knowledge_v5 import exp_knowledge_gain as exp_knowledge_gain_v5
from .fsrs_knowledge_v6 import exp_knowledge_gain as exp_knowledge_gain_v6
from .utils import get_last_review_date, get_new_rating_probs


def _key_difficulty(x):
    """
    Sorting key function for a backend card, based on custom difficulty field.
    """
    difficulty = float(x.card.memory_state.difficulty)
    return difficulty


def _key_exp_knowledge_gain(x):
    card = x.card
    deck_id = card.deck_id

    state = (
        (float(card.memory_state.difficulty), float(card.memory_state.stability))
        if card.memory_state
        else (0.0, 0.0)
    )

    elapsed_days = mw.col.sched.today - get_last_review_date(card)

    deck_config = mw.col.decks.config_dict_for_deck_id(deck_id)
    fsrs_params_v6 = deck_config.get("fsrsParams6")
    fsrs_params_v5 = deck_config.get("fsrsWeights")

    new_rating_probs = get_new_rating_probs(deck_id)

    if isinstance(fsrs_params_v6, list) and len(fsrs_params_v6) == 21:
        return -exp_knowledge_gain_v6(
            state, fsrs_params_v6, elapsed_days, new_rating_probs
        )
    elif isinstance(fsrs_params_v5, list) and len(fsrs_params_v5) == 19:
        return -exp_knowledge_gain_v5(
            state, fsrs_params_v5, elapsed_days, new_rating_probs
        )
    else:
        return -_key_difficulty(x)


def get_next_v3_card_custom(self) -> None:
    assert isinstance(self.mw.col.sched, V3Scheduler)
    output = self.mw.col.sched.get_queued_cards(fetch_limit=3000)
    if not output.cards:
        return

    self._v3 = V3CardInfo.from_queue(output)

    idx, counts = self._v3.counts()

    extend_limts = self.mw.col.card_count()
    # temporay extend the limts try get all the queued cards and sort these
    self.mw.col.sched.extend_limits(0, extend_limts)
    output_all = self.mw.col.sched.get_queued_cards(fetch_limit=extend_limts)
    # restore to configed limists
    self.mw.col.sched.extend_limits(0, -extend_limts)

    cards = output_all.cards

    # Sort the cards by expected knowledge gain
    sorted_cards = sorted(
        cards,
        key=_key_exp_knowledge_gain,
    )

    new_counts = [0, 0, 0]
    new_cards = []
    for card in sorted_cards:
        if card.queue == QueuedCards.NEW and new_counts[0] < counts[0]:
            new_cards.append(card)
            new_counts[0] += 1
        elif card.queue == QueuedCards.LEARNING and new_counts[1] < counts[1]:
            new_cards.append(card)
            new_counts[1] += 1
        elif card.queue == QueuedCards.REVIEW and new_counts[2] < counts[2]:
            new_cards.append(card)
            new_counts[2] += 1

    # make a new V3CardInfo use new top_card just like V3CardInfo.from_queue
    top_card = new_cards[0]

    del self._v3.queued_cards.cards[:]
    self._v3.queued_cards.cards.extend(new_cards)

    self._v3.states = top_card.states
    self._v3.states.current.custom_data = top_card.card.custom_data
    self._v3.context = top_card.context

    self.card = Card(self.mw.col, backend_card=self._v3.top_card().card)
    self.card.start_timer()
