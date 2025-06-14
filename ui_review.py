from anki import hooks
from anki.template import TemplateRenderContext, TemplateRenderOutput
from aqt import mw

from .config import get_config
from .fsrs_knowledge_v5 import exp_knowledge_gain as exp_knowledge_gain_v5
from .fsrs_knowledge_v6 import exp_knowledge_gain as exp_knowledge_gain_v6
from .utils import get_last_review_date, get_new_rating_probs

config = get_config()


def _on_card_did_render(
    output: TemplateRenderOutput, context: TemplateRenderContext
) -> None:
    if not config.display:
        return

    card = context.card()
    deck_id = card.did

    state = (
        (float(card.memory_state.difficulty), float(card.memory_state.stability))
        if card.memory_state
        else (0.0, 0.0)
    )

    elapsed_days = mw.col.sched.today - get_last_review_date(card)

    deck_config = mw.col.decks.config_dict_for_deck_id(deck_id)
    fsrs_params_v6 = deck_config.get("fsrsParams6")
    fsrs_params_v5 = deck_config.get("fsrsWeights")

    new_card_probs = get_new_rating_probs(deck_id)

    ekg = None

    if isinstance(fsrs_params_v6, list) and len(fsrs_params_v6) == 21:
        ekg = exp_knowledge_gain_v6(state, fsrs_params_v6, elapsed_days, new_card_probs)
    elif isinstance(fsrs_params_v5, list) and len(fsrs_params_v5) == 19:
        ekg = exp_knowledge_gain_v5(state, fsrs_params_v5, elapsed_days, new_card_probs)

    if ekg is None:
        return

    msg = f"""<br><br>
    <div style="text-align: center;">
        <span id="ekg_status" style="font-size:12px;opacity:0.5;font-family:monospace;">
            Expected knowledge gain: {ekg:.3f}
        </span>
    </div>"""

    output.answer_text += msg


def init_ui_review_hook():
    hooks.card_did_render.append(_on_card_did_render)
