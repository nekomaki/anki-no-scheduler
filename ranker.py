from anki.cards import Card
from anki.scheduler.v3 import QueuedCards
from anki.scheduler.v3 import Scheduler as V3Scheduler
from aqt import gui_hooks, mw
from aqt.reviewer import Reviewer, V3CardInfo

from .config import get_config
from .fsrs_knowledge_v5 import exp_knowledge_gain as exp_knowledge_gain_v5
from .fsrs_knowledge_v6 import exp_knowledge_gain as exp_knowledge_gain_v6
from .utils import get_last_review_date, get_new_rating_probs

config = get_config()

_get_next_v3_card_original = Reviewer._get_next_v3_card


cache = {}


def _key_exp_knowledge_gain(x):
    card = x.card

    deck_id = card.deck_id

    state = (
        (float(card.memory_state.difficulty), float(card.memory_state.stability))
        if card.memory_state
        else (0.0, 0.0)
    )

    elapsed_days = cache["today"] - get_last_review_date(card)

    deck_config = mw.col.decks.config_dict_for_deck_id(deck_id)
    fsrs_params_v6 = deck_config.get("fsrsParams6")
    fsrs_params_v5 = deck_config.get("fsrsWeights")

    if cache.get("new_rating_probs", {}).get(deck_id) is None:
        cache["new_rating_probs"][deck_id] = get_new_rating_probs(deck_id)
    new_rating_probs = cache["new_rating_probs"].get(deck_id)

    if isinstance(fsrs_params_v6, list) and len(fsrs_params_v6) == 21:
        return -exp_knowledge_gain_v6(
            state, fsrs_params_v6, elapsed_days, new_rating_probs
        )
    elif isinstance(fsrs_params_v5, list) and len(fsrs_params_v5) == 19:
        return -exp_knowledge_gain_v5(
            state, fsrs_params_v5, elapsed_days, new_rating_probs
        )
    else:
        return 0


def get_next_v3_card_patched(self) -> None:
    assert isinstance(self.mw.col.sched, V3Scheduler)
    output = self.mw.col.sched.get_queued_cards()
    if not output.cards:
        return
    self._v3 = V3CardInfo.from_queue(output)

    deck_id = self.mw.col.decks.current()['id']
    if (
        not hasattr(self, "_cards_cached")
        or getattr(self, "_deck_id_cached", None) != deck_id
        or mw.col.sched.today != cache.get("today", None)
    ):
        self._cards_cached = []
        self._deck_id_cached = deck_id

        # Fetch all cards
        extend_limits = self.mw.col.card_count()
        self.mw.col.sched.extend_limits(0, extend_limits)
        output_all = self.mw.col.sched.get_queued_cards(fetch_limit=extend_limits)
        self.mw.col.sched.extend_limits(0, -extend_limits)

        # Get the top card based on expected knowledge gain
        counts = self._v3.counts()[1]
        type_limits = {
            QueuedCards.NEW: counts[0],
            QueuedCards.LEARNING: counts[1],
            QueuedCards.REVIEW: counts[2],
        }
        filtered_cards = [
            card for card in output_all.cards if type_limits[card.queue] > 0
        ]

        cache["today"] = mw.col.sched.today
        cache["new_rating_probs"] = {}
        sorted_cards = sorted(filtered_cards, key=_key_exp_knowledge_gain, reverse=True)

        self._cards_cached = sorted_cards
    else:
        # Disable undo
        self.mw.col.sched.extend_limits(0, 0)

    top_card = self._cards_cached[-1]

    # Update the V3CardInfo with the top card
    del self._v3.queued_cards.cards[:]
    self._v3.queued_cards.cards.extend([top_card])
    self._v3.states = top_card.states
    self._v3.states.current.custom_data = top_card.card.custom_data
    self._v3.context = top_card.context

    self.card = Card(self.mw.col, backend_card=self._v3.top_card().card)
    self.card.start_timer()


def _on_card_answered(reviewer, card, ease):
    if (
        getattr(reviewer, "_cards_cached", None)
        and reviewer._cards_cached[-1].card.id == card.id
    ):
        reviewer._cards_cached.pop()
    else:
        reviewer._cards_cached = None


def update_ranker():
    if config.sort_cards:
        Reviewer._get_next_v3_card = get_next_v3_card_patched
    else:
        Reviewer._get_next_v3_card = _get_next_v3_card_original


def init_ranker():
    update_ranker()
    gui_hooks.reviewer_did_answer_card.append(_on_card_answered)
