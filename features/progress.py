import streamlit as st

from ui.styles import empty_state, esc, html, page_header, stat_card


def compute_stats():
    ss = st.session_state
    hist = ss.quiz_history
    avg = round(sum(h["pct"] for h in hist) / len(hist)) if hist else None
    return {
        "documents": len(ss.docs),
        "quizzes": len(hist),
        "avg": avg,
        "latest": hist[-1]["pct"] if hist else None,
        "questions": ss.questions_asked,
        "flashcards": ss.flashcards_generated,
    }


def pct_text(v):
    return "—" if v is None else f"{v}%"


def render_progress():
    page_header("Progress", "A simple view of how your studying is going in this session.")
    s = compute_stats()
    items = [
        (s["documents"], "Documents processed"),
        (s["quizzes"], "Quizzes completed"),
        (pct_text(s["latest"]), "Latest quiz score"),
        (pct_text(s["avg"]), "Average quiz score"),
        (s["questions"], "Questions asked"),
        (s["flashcards"], "Flashcards generated"),
    ]
    for row in (items[:3], items[3:]):
        cols = st.columns(3)
        for col, (v, l) in zip(cols, row):
            col.markdown(stat_card(v, l), unsafe_allow_html=True)

    st.markdown("### Recent quiz performance")
    hist = st.session_state.quiz_history
    if not hist:
        empty_state("No quizzes yet", "Take a quiz from the Quiz page and your scores will appear here.")
        return
    for h in reversed(hist[-8:]):
        html(
            f'<div class="sm-row"><span>{esc(h["doc_name"])}</span><span>{h["score"]}/{h["total"]} · {h["pct"]}%</span></div>'
            f'<div class="sm-bar"><div style="width:{h["pct"]}%"></div></div>'
        )
