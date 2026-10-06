import uuid
from datetime import datetime, timedelta, timezone

import streamlit as st

IST = timezone(timedelta(hours=5, minutes=30))

PAGES = [
    "Dashboard",
    "AI Tutor",
    "Study Materials",
    "Quiz",
    "Flashcards",
    "Slides",
    "Progress",
    "Settings",
]


def init_state():
    defaults = {
        "sid": lambda: uuid.uuid4().hex[:12],
        "page": lambda: "Dashboard",
        "docs": dict,
        "chat": list,
        "chat_scope": lambda: "all",
        "questions_asked": lambda: 0,
        "quiz": lambda: None,
        "quiz_run": lambda: 0,
        "quiz_history": list,
        "flash": lambda: None,
        "slides": lambda: None,
        "flashcards_generated": lambda: 0,
        "activity": list,
        "uploader_key": lambda: 0,
        "notice": lambda: None,
        "open_summary": lambda: None,
    }
    for key, factory in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = factory()


def go(page):
    st.session_state.page = page


def log_activity(title, detail):
    st.session_state.activity.append(
        {"title": title, "detail": detail, "time": datetime.now(IST).strftime("%I:%M %p").lstrip("0")}
    )


def doc_name(doc_id):
    d = st.session_state.docs.get(doc_id)
    return d["name"] if d else "Document"


def reset_all():
    from rag import vector_store

    vector_store.reset()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
