from anki import hooks
from anki.template import TemplateRenderContext, TemplateRenderOutput
from aqt import mw

from .config_manager import get_config
from .fsrs.types import State
from .utils import get_knowledge_gain, get_last_review_date

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

    state = State(
        float(card.memory_state.difficulty), float(card.memory_state.stability)
    )

    elapsed_days = mw.col.sched.today - get_last_review_date(card)

    deck_config = mw.col.decks.config_dict_for_deck_id(deck_id)
    fsrs_params_v6 = deck_config.get("fsrsParams6")
    fsrs_params = deck_config.get("fsrsWeights")

    ekg = get_knowledge_gain(state, elapsed_days=elapsed_days, deck_config=deck_config)

    if ekg is not None:
        if ekg >= 0.1:
            indicator = "High"
        elif ekg >= 0.05:
            indicator = "Medium"
        else:
            indicator = "Low"
        ekg_message = f"Expected knowledge gain: {ekg:.3f} ({indicator})"
    elif fsrs_params is not None or fsrs_params_v6 is not None:
        ekg_message = "Expected knowledge gain is not supported for this FSRS version. Please delete and update your FSRS parameters."
    else:
        ekg_message = (
            "Expected knowledge gain unavailable. Please ensure FSRS is enabled."
        )

    msg = f"""<br><br>
    <div style="text-align: center;">
        <span id="ekg_status" style="font-size:12px;opacity:0.5;font-family:monospace;">
            {ekg_message}
        </span>
    </div>"""

    output.answer_text += msg


def init_ui_review_hook():
    hooks.card_did_render.append(_on_card_did_render)
