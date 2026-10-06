import streamlit as st

from core.ai_client import ask_json
from core.prompts import flashcard_prompt
from core.session_state import go, log_activity
from rag.text_splitter import select_context
from ui.styles import empty_state, esc, html, page_header


def validate_cards(data):
    items = data.get("flashcards") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        q = str(it.get("question", it.get("front", ""))).strip()
        a = str(it.get("answer", it.get("back", ""))).strip()
        if q and a:
            out.append({"question": q, "answer": a})
    if len(out) < 5:
        raise ValueError
    return out[:5]


def create_flashcards_for(doc_id):
    """Generate flashcards and store them in session state. Returns True on success."""
    ss = st.session_state
    doc = ss.docs.get(doc_id)
    if not doc:
        st.error("Please upload and process a PDF first.")
        return False
    avoid = []
    if ss.flash and ss.flash["doc_id"] == doc_id:
        avoid = [c["question"] for c in ss.flash["cards"]]
    with st.spinner("Creating flashcards…"):
        context = select_context(doc["chunks"], max_chars=8000, randomize=True)
        cards, err = ask_json(flashcard_prompt(context, avoid), validate_cards)
    if err:
        st.error(err)
        return False
    ss.flash = {"doc_id": doc_id, "doc_name": doc["name"], "cards": cards, "i": 0, "show": False}
    ss.flashcards_generated += len(cards)
    log_activity(f"{doc['name']} flashcards", f"{len(cards)} cards generated")
    return True


def _move(delta):
    f = st.session_state.flash
    f["i"] = max(0, min(len(f["cards"]) - 1, f["i"] + delta))
    f["show"] = False


def _toggle():
    f = st.session_state.flash
    f["show"] = not f["show"]


def render_flashcards():
    page_header("Flashcards", "Flip through five cards made from your study material.")
    ss = st.session_state
    if not ss.docs:
        empty_state("No study material yet", "Upload and process a PDF first, then come back to create flashcards.")
        st.button("Go to Study Materials", on_click=go, args=("Study Materials",))
        return

    docs = ss.docs
    ids = list(docs.keys())
    default = ids.index(ss.flash["doc_id"]) if ss.flash and ss.flash["doc_id"] in ids else 0
    c1, c2 = st.columns([3, 1])
    pick = c1.selectbox("Study material", ids, index=default, format_func=lambda i: docs[i]["name"], key="flash_doc_pick")
    c2.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
    label = "Generate new flashcards" if ss.flash else "Generate flashcards"
    if c2.button(label, type="primary", use_container_width=True):
        if create_flashcards_for(pick):
            st.rerun()

    f = ss.flash
    if not f:
        empty_state("No flashcards yet", "Choose a document and generate your first set.")
        return

    n, i = len(f["cards"]), f["i"]
    card = f["cards"][i]
    answer = (
        f'<div class="sm-ans"><div class="sm-qn">Answer</div>{esc(card["answer"])}</div>' if f["show"] else ""
    )
    html(
        f'<div class="sm-card" style="padding:2rem 2rem 1.6rem"><div class="sm-qn">Card {i + 1} of {n} · {esc(f["doc_name"])}</div>'
        f'<div class="sm-q" style="font-size:1.6rem">{esc(card["question"])}</div>{answer}</div>'
    )
    b = st.columns(3)
    b[0].button("Previous", on_click=_move, args=(-1,), disabled=i == 0, use_container_width=True)
    b[1].button("Hide Answer" if f["show"] else "Show Answer", on_click=_toggle, type="primary", use_container_width=True)
    b[2].button("Next", on_click=_move, args=(1,), disabled=i == n - 1, use_container_width=True)
