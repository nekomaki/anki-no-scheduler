from aqt import mw
from aqt.qt import QAction
from aqt.reviewer import Reviewer

from .config import get_config
from .ranker import get_next_v3_card_custom
from .ui_review import init_ui_review_hook

_get_next_v3_card_original = Reviewer._get_next_v3_card

config = get_config()

def update_ranker():
    if config.sort_cards:
        Reviewer._get_next_v3_card = get_next_v3_card_custom
    else:
        Reviewer._get_next_v3_card = _get_next_v3_card_original

def toggle_sort_cards():
    config.sort_cards = not config.sort_cards
    action_sort_cards.setChecked(config.sort_cards)
    update_ranker()


def toggle_display_knowledge_gain():
    config.display = not config.display
    action_display_knowledge_gain.setChecked(config.display)


menu = mw.form.menuTools.addMenu("Review order by knowledge gain")

action_sort_cards = QAction("Order cards by knowledge gain", mw, checkable=True)
action_sort_cards.triggered.connect(toggle_sort_cards)
action_sort_cards.setChecked(config.sort_cards)

action_display_knowledge_gain = QAction("Display knowledge gain", mw, checkable=True)
action_display_knowledge_gain.triggered.connect(toggle_display_knowledge_gain)
action_display_knowledge_gain.setChecked(config.display)

menu.addAction(action_sort_cards)
menu.addSeparator()
menu.addAction(action_display_knowledge_gain)

update_ranker()
init_ui_review_hook()
