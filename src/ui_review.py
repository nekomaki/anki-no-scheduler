from anki import hooks
from anki.template import TemplateRenderContext, TemplateRenderOutput
from aqt import mw

from .config import get_config
from .knowledge_ema.fsrs_v5 import exp_knowledge_gain as exp_knowledge_gain_v5
from .knowledge_ema.fsrs_v6 import exp_knowledge_gain as exp_knowledge_gain_v6
from .utils import (
    get_last_review_date,
    is_valid_fsrs5_params,
    is_valid_fsrs6_params,
)

config = get_config()


def _on_card_did_render(
    output: TemplateRenderOutput, context: TemplateRenderContext
) -> None:
    if not config.display_status:
        return

    card = context.card()
    deck_id = card.odid or card.did

    # Skip new cards
    if not card.memory_state:
        return

    state = (
        (float(card.memory_state.difficulty), float(card.memory_state.stability))
    )

    elapsed_days = mw.col.sched.today - get_last_review_date(card)

    deck_config = mw.col.decks.config_dict_for_deck_id(deck_id)
    fsrs_params_v6 = deck_config.get("fsrsParams6")
    fsrs_params_v5 = deck_config.get("fsrsWeights")

    ekg = None

    if is_valid_fsrs6_params(fsrs_params_v6):
        ekg = exp_knowledge_gain_v6(state, fsrs_params_v6, elapsed_days)
    elif is_valid_fsrs5_params(fsrs_params_v5):
        ekg = exp_knowledge_gain_v5(state, fsrs_params_v5, elapsed_days)

    if ekg is not None:
        ekg_message = f"Expected knowledge gain: {ekg:.3f}"
    elif fsrs_params_v5 is not None or fsrs_params_v6 is not None:
        ekg_message = "Expected knowledge gain is not supported for this FSRS version. Please delete your current FSRS parameters and recompute them to make sure FSRS 5 or 6 is used."
    else:
        ekg_message = "Expected knowledge gain unavailable. Please ensure FSRS is enabled."

    msg = f"""<br><br>
    <div style="text-align: center;">
        <span id="ekg_status" style="font-size:12px;opacity:0.5;font-family:monospace;">
            {ekg_message}
        </span>
    </div>"""

    output.answer_text += msg


def init_ui_review_hook():
    hooks.card_did_render.append(_on_card_did_render)
