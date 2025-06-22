import math
from typing import List

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
from aqt import mw

BackendCard = cards_pb2.Card


def get_revlogs(cid: int):
    return mw.col.get_review_logs(cid)


def filter_revlogs(
    revlogs: List[CardStatsResponse.StatsRevlogEntry],
) -> List[CardStatsResponse.StatsRevlogEntry]:
    return list(
        filter(
            lambda x: x.button_chosen >= 1
            and (x.review_kind != REVLOG_CRAM or x.ease != 0),
            revlogs,
        )
    )


def get_last_review_date(card: Card):
    revlogs = get_revlogs(card.id)
    try:
        last_revlog = filter_revlogs(revlogs)[0]
        last_review_date = (
            math.ceil((last_revlog.time - mw.col.sched.day_cutoff) / 86400)
            + mw.col.sched.today
        )
    except IndexError:
        if isinstance(card, BackendCard):
            due = card.original_due if card.deck_id else card.due
            last_review_date = due - card.interval
        else:
            due = card.odue if card.odid else card.due
            last_review_date = due - card.ivl
    return last_review_date


def get_decay(card: Card):
    return getattr(card, "decay", 0.5) or 0.5


def is_valid_fsrs6_params(fsrs_params):
    return isinstance(fsrs_params, (list, tuple)) and len(fsrs_params) == 21


def is_valid_fsrs5_params(fsrs_params):
    return isinstance(fsrs_params, (list, tuple)) and len(fsrs_params) == 19


def is_valid_fsrs4_params(fsrs_params):
    return isinstance(fsrs_params, (list, tuple)) and len(fsrs_params) == 17


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
