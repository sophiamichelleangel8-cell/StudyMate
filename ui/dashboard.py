from datetime import datetime

import streamlit as st

from core.session_state import IST, go
from features.progress import compute_stats, pct_text
from ui.styles import empty_state, esc, html, page_header, stat_card


def _greeting():
    h = datetime.now(IST).hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


def render_dashboard():
    page_header(
        f"{_greeting()}, ready to learn?",
        "Upload your study material, ask questions, and turn your notes into an interactive learning experience.",
        script="Study smarter. Understand better. Learn with StudyMate.",
    )
    s = compute_stats()
    cols = st.columns(4)
    for col, (v, l) in zip(
        cols,
        [
            (s["documents"], "Documents"),
            (s["quizzes"], "Quizzes Completed"),
            (pct_text(s["avg"]), "Average Score"),
            (s["questions"], "Questions Asked"),
        ],
    ):
        col.markdown(stat_card(v, l), unsafe_allow_html=True)

    st.markdown("### Quick actions")
    actions = [
        ("Upload Material", "Study Materials"),
        ("Ask AI Tutor", "AI Tutor"),
        ("Generate Quiz", "Quiz"),
        ("Create Flashcards", "Flashcards"),
    ]
    cols = st.columns(4)
    for col, (label, page) in zip(cols, actions):
        col.button(label, key=f"qa_{page}", use_container_width=True, on_click=go, args=(page,))

    st.markdown("### Recent activity")
    acts = st.session_state.activity
    if not acts:
        empty_state("Nothing yet", "Upload a PDF in Study Materials to get started.")
        return
    for a in reversed(acts[-6:]):
        html(
            f'<div class="sm-card"><div class="sm-act-t">{esc(a["title"])}</div>'
            f'<div class="sm-act-d">{esc(a["detail"])} · {esc(a["time"])}</div></div>'
        )
