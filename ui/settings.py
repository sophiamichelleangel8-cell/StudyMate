import streamlit as st

from core.ai_client import AIError, GROQ_MODEL, OLLAMA_MODEL, OLLAMA_URL, ask_ai, provider
from core.session_state import reset_all
from rag.vector_store import EMBED_MODEL
from ui.styles import page_header


def render_settings():
    page_header("Settings", "See which AI engine StudyMate is using and manage your session.")
    if provider() == "groq":
        st.success(f"Using Groq with model {GROQ_MODEL}. The API key is read from your secrets and is never shown.")
    else:
        st.info(f"Using local Ollama ({OLLAMA_MODEL}) at {OLLAMA_URL}. Add GROQ_API_KEY to switch to Groq.")
    st.caption(f"Embedding model: {EMBED_MODEL} · Vector store: ChromaDB (in-memory)")

    st.markdown("### Test the AI connection")
    if st.button("Run test"):
        try:
            with st.spinner("Contacting the AI…"):
                ask_ai("Reply with the single word: ready", max_tokens=200)
            st.success("The AI responded successfully.")
        except AIError as e:
            st.error(str(e))

    st.markdown("### Reset")
    st.caption("Clears uploaded documents, chat, quizzes, flashcards and progress for this session.")
    if st.button("Reset session"):
        reset_all()
        st.rerun()
