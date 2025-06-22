from anki.cards import Card
from anki.scheduler.v3 import QueuedCards
from anki.scheduler.v3 import Scheduler as V3Scheduler
from aqt import gui_hooks, mw
from aqt.reviewer import Reviewer, V3CardInfo

from .config import get_config
from .knowledge_ema.fsrs_v5 import exp_knowledge_gain as exp_knowledge_gain_v5
from .knowledge_ema.fsrs_v6 import exp_knowledge_gain as exp_knowledge_gain_v6
from .utils import (
    get_last_review_date,
    is_valid_fsrs5_params,
    is_valid_fsrs6_params,
)

config = get_config()

_get_next_v3_card_original = Reviewer._get_next_v3_card

cache = {}


def _key_exp_knowledge_gain(x):
    card = x.card
    deck_id = card.original_deck_id or card.deck_id

    state = (
        (float(card.memory_state.difficulty), float(card.memory_state.stability))
        if card.memory_state
        else (1.0, 0.0)
    )

    elapsed_days = cache["today"] - get_last_review_date(card)

    deck_config = mw.col.decks.config_dict_for_deck_id(deck_id)
    fsrs_params_v6 = deck_config.get("fsrsParams6")
    fsrs_params_v5 = deck_config.get("fsrsWeights")

    if is_valid_fsrs6_params(fsrs_params_v6):
        return -exp_knowledge_gain_v6(state, fsrs_params_v6, elapsed_days)
    elif is_valid_fsrs5_params(fsrs_params_v5):
        return -exp_knowledge_gain_v5(state, fsrs_params_v5, elapsed_days)
    else:
        return 0


def _get_next_v3_card_patched(self) -> None:
    assert isinstance(self.mw.col.sched, V3Scheduler)
    output = self.mw.col.sched.get_queued_cards()
    if not output.cards:
        return
    self._v3 = V3CardInfo.from_queue(output)

    idx, counts = self._v3.counts()
    queue_to_index = {
        QueuedCards.NEW: 0,
        QueuedCards.LEARNING: 1,
        QueuedCards.REVIEW: 2,
    }

    # TODO: Relearning cards will refresh the cache
    # TODO: Avoid reviewing cards too soon
    # Skip new cards
    if idx != 0:
        deck_id = self.mw.col.decks.current()['id']

        if (
            not hasattr(self, "_cards_cached")
            or self._cards_cached is None
            or getattr(self, "_deck_id_cached", None) != deck_id
            or sum(counts[1:]) != len(self._cards_cached)
            or counts[queue_to_index[self._cards_cached[-1].queue]] <= 0
            or mw.col.sched.today != cache.get("today", None)
        ):
            # Refresh the cache
            self._deck_id_cached = deck_id

            # Fetch all cards
            extend_limits = self.mw.col.card_count()

            self.mw.col.sched.extend_limits(0, extend_limits)
            output_all = self.mw.col.sched.get_queued_cards(fetch_limit=extend_limits)
            self.mw.col.sched.extend_limits(0, -extend_limits)

            # Filter out new cards
            cards = [card for card in output_all.cards if card.queue != QueuedCards.NEW]

            # Sort the cards by expected knowledge gain
            cache["today"] = mw.col.sched.today
            sorted_cards = sorted(cards, key=_key_exp_knowledge_gain)

            # Filter cards based on the counts
            filtered_counts = [0, 0, 0]
            filtered_cards = []
            for card in sorted_cards:
                index = queue_to_index[card.queue]
                if filtered_counts[index] < counts[index]:
                    filtered_cards.append(card)
                    filtered_counts[index] += 1

            # Make a stack of the filtered cards
            self._cards_cached = list(reversed(filtered_cards))
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
        Reviewer._get_next_v3_card = _get_next_v3_card_patched
    else:
        Reviewer._get_next_v3_card = _get_next_v3_card_original


def init_ranker():
    update_ranker()
    gui_hooks.reviewer_did_answer_card.append(_on_card_answered)
