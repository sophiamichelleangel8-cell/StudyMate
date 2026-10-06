import streamlit as st

from core.ai_client import provider_label
from core.session_state import PAGES, go
from ui.styles import html


def render_sidebar():
    with st.sidebar:
        html(
            '<div class="sm-brand">StudyMate</div>'
            '<div class="sm-tag">AI-powered personal study assistant</div>'
        )
        for p in PAGES[:-1]:
            st.button(
                p,
                key=f"nav_{p}",
                use_container_width=True,
                type="primary" if st.session_state.page == p else "secondary",
                on_click=go,
                args=(p,),
            )
        st.markdown("---")
        st.button(
            "Settings",
            key="nav_Settings",
            use_container_width=True,
            type="primary" if st.session_state.page == "Settings" else "secondary",
            on_click=go,
            args=("Settings",),
        )
        st.caption(f"AI engine: {provider_label()}")
        st.caption(f"Documents loaded: {len(st.session_state.docs)}")
