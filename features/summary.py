import streamlit as st

from core.ai_client import ask_json
from core.prompts import summary_prompt
from rag.text_splitter import select_context
from ui.styles import esc, html


def _items(v):
    return [x for x in v if x] if isinstance(v, list) else []


def validate_summary(data):
    if not isinstance(data, dict):
        raise ValueError
    out = {
        "main_topics": [str(x).strip() for x in _items(data.get("main_topics")) if str(x).strip()],
        "important_concepts": [],
        "key_definitions": [],
        "important_points": [str(x).strip() for x in _items(data.get("important_points")) if str(x).strip()],
        "revision_points": [str(x).strip() for x in _items(data.get("revision_points")) if str(x).strip()],
    }
    for x in _items(data.get("important_concepts")):
        if isinstance(x, dict):
            n, e = str(x.get("name", "")).strip(), str(x.get("explanation", "")).strip()
        else:
            n, e = str(x).strip(), ""
        if n:
            out["important_concepts"].append({"name": n, "explanation": e})
    for x in _items(data.get("key_definitions")):
        if isinstance(x, dict):
            t, d = str(x.get("term", "")).strip(), str(x.get("definition", "")).strip()
            if t and d:
                out["key_definitions"].append({"term": t, "definition": d})
    if sum(1 for v in out.values() if v) < 3:
        raise ValueError
    return out


def generate_summary(doc):
    context = select_context(doc["chunks"], max_chars=10000)
    return ask_json(summary_prompt(context), validate_summary, temperature=0.3)


def render_summary(s):
    if s["main_topics"]:
        st.markdown("#### Main topics")
        html("".join(f'<span class="sm-chip">{esc(t)}</span>' for t in s["main_topics"]))
    if s["important_concepts"]:
        st.markdown("#### Important concepts")
        cols = st.columns(2)
        for i, c in enumerate(s["important_concepts"]):
            cols[i % 2].markdown(
                f'<div class="sm-card"><div class="sm-act-t">{esc(c["name"])}</div>'
                f'<div class="sm-act-d">{esc(c["explanation"])}</div></div>',
                unsafe_allow_html=True,
            )
    if s["key_definitions"]:
        st.markdown("#### Key definitions")
        for d in s["key_definitions"]:
            st.markdown(
                f'<div class="sm-card"><b>{esc(d["term"])}</b><br>{esc(d["definition"])}</div>',
                unsafe_allow_html=True,
            )
    if s["important_points"]:
        st.markdown("#### Important points")
        st.markdown("\n".join(f"- {p}" for p in s["important_points"]))
    if s["revision_points"]:
        st.markdown("#### Exam-focused revision points")
        items = "".join(f"<li>{esc(p)}</li>" for p in s["revision_points"])
        st.markdown(f'<div class="sm-card sm-card-y"><ul style="margin:0">{items}</ul></div>', unsafe_allow_html=True)
