from typing import Optional

from anki import cards_pb2
from anki.cards import Card
from anki.stats import (
    CARD_TYPE_REV,
    QUEUE_TYPE_DAY_LEARN_RELEARN,
    QUEUE_TYPE_LRN,
    QUEUE_TYPE_NEW,
    QUEUE_TYPE_PREVIEW,
    QUEUE_TYPE_REV,
    QUEUE_TYPE_SUSPENDED,
    REVLOG_CRAM,
    REVLOG_LRN,
    REVLOG_RELRN,
    REVLOG_RESCHED,
    REVLOG_REV,
)
from anki.stats_pb2 import CardStatsResponse
from anki.utils import int_time
from aqt import mw

from .config_manager import get_config
from .fsrs.types import State
from .longterm_knowledge.discounted.fsrs4 import FSRS4KnowledgeDiscounted
from .longterm_knowledge.discounted.fsrs5 import FSRS5KnowledgeDiscounted
from .longterm_knowledge.discounted.fsrs6 import FSRS6KnowledgeDiscounted
from .longterm_knowledge.discounted.interfaces import KnowledgeDiscountedProtocol

BackendCard = cards_pb2.Card

config = get_config()


def get_revlogs(cid: int):
    return mw.col.get_review_logs(cid)


def filter_revlogs(
    revlogs: list[CardStatsResponse.StatsRevlogEntry],
) -> list[CardStatsResponse.StatsRevlogEntry]:
    return list(
        filter(
            lambda x: x.button_chosen >= 1 and (x.review_kind != REVLOG_CRAM or x.ease != 0),
            revlogs,
        )
    )


def get_last_review_timestamp(card: Card) -> float:
    """Return last review time as Unix timestamp in seconds."""
    revlogs = get_revlogs(card.id)
    try:
        last_revlog = filter_revlogs(revlogs)[0]
        # last_revlog.time is in seconds since epoch (backend API), or ms in SQL
        return last_revlog.time
    except IndexError:
        # No revlog — estimate based on due and interval
        if isinstance(card, BackendCard):
            due = card.original_due if card.deck_id else card.due
            days_ago = card.interval
        else:
            due = card.odue if card.odid else card.due
            days_ago = card.ivl
        # Approximate: deck due date (sched.day_cutoff is today's start time)
        due_date_timestamp = mw.col.sched.day_cutoff + (due - mw.col.sched.today) * 86400
        return due_date_timestamp - days_ago * 86400


def get_elapsed_days(card: Card) -> float:
    """Return elapsed days since last review, as a float."""
    last_review_ts = get_last_review_timestamp(card)
    now_ts = int_time()
    return (now_ts - last_review_ts) / 86400.0


def get_decay(card: Card):
    return getattr(card, "decay", 0.5) or 0.5


def get_valid_fsrs6(fsrs_params):
    if isinstance(fsrs_params, list) and len(fsrs_params) == 21:
        return FSRS6KnowledgeDiscounted.from_list(fsrs_params)
    return None


def get_valid_fsrs5(fsrs_params):
    if isinstance(fsrs_params, list) and len(fsrs_params) == 19:
        return FSRS5KnowledgeDiscounted.from_list(fsrs_params)
    return None


def get_valid_fsrs4(fsrs_params):
    if isinstance(fsrs_params, list) and len(fsrs_params) == 17:
        return FSRS4KnowledgeDiscounted.from_list(fsrs_params)
    return None

def get_fsrs(deck_config: dict[str, list[float]]) -> Optional[KnowledgeDiscountedProtocol]:
    fsrs_params_v6 = deck_config.get("fsrsParams6")
    fsrs_params_v5_or_lower = deck_config.get("fsrsWeights")

    fsrs: Optional[KnowledgeDiscountedProtocol] = (
        get_valid_fsrs6(fsrs_params_v6)
        or get_valid_fsrs5(fsrs_params_v5_or_lower)
        or get_valid_fsrs4(fsrs_params_v5_or_lower)
    )

    return fsrs


def get_knowledge_gain(
    state: State, elapsed_days: float, deck_config: dict[str, list[float]]
) -> Optional[float]:
    fsrs = get_fsrs(deck_config)

    if fsrs is None:
        return None

    return fsrs.exp_knowledge_gain(state, elapsed_days, lookahead=2)


# def get_new_rating_probs(deck_id):
#     rows = mw.col.db.all(
#         f"""
#     SELECT r2.ease, COUNT(*) FROM (
#     SELECT r.cid, MIN(r.id) AS first_revlog_id
#     FROM revlog r
#     JOIN cards c ON r.cid = c.id
#     WHERE r.type = 0 AND c.did = {deck_id}
#     GROUP BY r.cid
#     ) AS first_rev
#     JOIN revlog r2 ON r2.id = first_rev.first_revlog_id
#     GROUP BY r2.ease
#     """
#     )

#     total = sum(count for _, count in rows)
#     new_card_probs = [(count + 1) / (total + 4) for _ease, count in rows]
#     return new_card_probs
