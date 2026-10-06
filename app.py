import streamlit as st

st.set_page_config(page_title="StudyMate", page_icon="📖", layout="wide")

from core.session_state import init_state  # noqa: E402
from features.chat import render_chat  # noqa: E402
from features.flashcards import render_flashcards  # noqa: E402
from features.progress import render_progress  # noqa: E402
from features.slides import render_slides  # noqa: E402
from features.quiz import render_quiz  # noqa: E402
from ui.dashboard import render_dashboard  # noqa: E402
from ui.materials import render_materials  # noqa: E402
from ui.settings import render_settings  # noqa: E402
from ui.sidebar import render_sidebar  # noqa: E402
from ui.styles import inject_css  # noqa: E402

ROUTES = {
    "Dashboard": render_dashboard,
    "AI Tutor": render_chat,
    "Study Materials": render_materials,
    "Quiz": render_quiz,
    "Flashcards": render_flashcards,
    "Slides": render_slides,
    "Progress": render_progress,
    "Settings": render_settings,
}


def main():
    init_state()
    inject_css()
    render_sidebar()
    page = st.session_state.page if st.session_state.page in ROUTES else "Dashboard"
    try:
        ROUTES[page]()
    except Exception as e:  # last-resort guard so students never see a traceback
        if type(e).__name__ in ("RerunException", "StopException"):
            raise
        st.error("Something unexpected happened. Please try again, or reset the session in Settings.")


main()
