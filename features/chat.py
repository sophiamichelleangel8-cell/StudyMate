import streamlit as st

from core.ai_client import AIError, ask_ai
from core.prompts import TUTOR_SYSTEM, tutor_prompt
from core.session_state import go, log_activity
from rag import vector_store
from ui.styles import empty_state, page_header

SUGGESTIONS = "Try: “Explain this topic simply”, “Give me an example”, or “What are the key points of chapter 1?”"


def _clear():
    st.session_state.chat = []


def answer_question(question, scope):
    docs = st.session_state.docs
    passages = []
    if docs and scope != "none":
        target = None if scope == "all" or scope not in docs else scope
        passages = vector_store.query(question, k=4, doc_id=target)
    history = st.session_state.chat[-6:]
    reply = ask_ai(tutor_prompt(question, passages), system=TUTOR_SYSTEM, history=history)
    sources = sorted({p["doc_name"] for p in passages})
    return reply, sources, passages


def render_chat():
    page_header("AI Tutor", "Ask for explanations, examples, or help with your uploaded material.")
    ss = st.session_state
    docs = ss.docs

    top = st.columns([3, 1])
    scope = "none"
    if docs:
        opts = [("all", "All study materials")] + [(i, d["name"]) for i, d in docs.items()] + [
            ("none", "General knowledge only")
        ]
        ids = [o[0] for o in opts]
        labels = dict(opts)
        idx = ids.index(ss.chat_scope) if ss.chat_scope in ids else 0
        scope = top[0].selectbox("Answer from", ids, index=idx, format_func=labels.get)
        ss.chat_scope = scope
    else:
        top[0].info("No document uploaded yet. I can still answer general study questions.")
    top[1].markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
    top[1].button("Clear conversation", on_click=_clear, use_container_width=True, disabled=not ss.chat)

    if not ss.chat:
        empty_state("Start a conversation", SUGGESTIONS)

    for m in ss.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("sources"):
                with st.expander("Passages used"):
                    st.caption("From: " + ", ".join(m["sources"]))
                    for p in m.get("passages", []):
                        st.write(p[:400] + ("…" if len(p) > 400 else ""))

    prompt = st.chat_input("Ask a study question…")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking…"):
                    reply, sources, passages = answer_question(prompt, scope)
            except AIError as e:
                st.error(str(e))
                return
            except Exception:
                st.error("Something went wrong while answering. Please try again.")
                return
            st.markdown(reply)
        ss.chat.append({"role": "user", "content": prompt})
        ss.chat.append(
            {"role": "assistant", "content": reply, "sources": sources, "passages": [p["text"] for p in passages]}
        )
        ss.questions_asked += 1
        log_activity("AI Tutor", f"Asked: {prompt[:60]}")
        st.rerun()
