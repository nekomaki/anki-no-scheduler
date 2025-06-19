from aqt import mw
from aqt.qt import QAction

from .config import get_config
from .ranker import init_ranker, update_ranker
from .ui_review import init_ui_review_hook

config = get_config()


def toggle_sort_cards():
    config.sort_cards = not config.sort_cards
    action_sort_cards.setChecked(config.sort_cards)
    update_ranker()


menu = mw.form.menuTools.addMenu("Review Order by Knowledge Gain")

action_sort_cards = QAction("Order cards by knowledge gain", mw, checkable=True)
action_sort_cards.setChecked(config.sort_cards)
action_sort_cards.triggered.connect(toggle_sort_cards)

action_display_status = QAction("Display knowledge gain", mw, checkable=True)
action_display_status.setChecked(config.display_status)
action_display_status.triggered.connect(
    lambda: setattr(config, "display_status", action_display_status.isChecked())
)

menu.addAction(action_sort_cards)
menu.addSeparator()
menu.addAction(action_display_status)

init_ranker()
init_ui_review_hook()
