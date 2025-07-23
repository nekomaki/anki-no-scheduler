from aqt import mw
from aqt.qt import QAction

from .config_manager import get_config
from .reordering import init_reordering, update_reordering
from .ui_review import init_ui_review_hook

config = get_config()


def toggle_reorder_cards():
    config.reorder_cards = not config.reorder_cards
    action_reorder_cards.setChecked(config.reorder_cards)
    update_reordering()


menu = mw.form.menuTools.addMenu("Review Order by Knowledge Gain")

action_reorder_cards = QAction("Order cards by knowledge gain", mw, checkable=True)
action_reorder_cards.setChecked(config.reorder_cards)
action_reorder_cards.triggered.connect(toggle_reorder_cards)

action_future_estimator = QAction("Use future estimator", mw, checkable=True)
action_future_estimator.setChecked(config.future_estimator)
action_future_estimator.triggered.connect(
    lambda: setattr(config, "future_estimator", action_future_estimator.isChecked())
)

action_display_status = QAction("Display knowledge gain", mw, checkable=True)
action_display_status.setChecked(config.display_status)
action_display_status.triggered.connect(
    lambda: setattr(config, "display_status", action_display_status.isChecked())
)


menu.addAction(action_reorder_cards)
menu.addAction(action_future_estimator)
menu.addAction(action_display_status)

init_reordering()
init_ui_review_hook()
