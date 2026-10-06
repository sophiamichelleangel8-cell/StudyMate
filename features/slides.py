import streamlit as st

from core.ai_client import ask_json
from core.prompts import slides_prompt
from core.session_state import go, log_activity
from rag.text_splitter import select_context
from ui.styles import empty_state, esc, html, page_header


def validate_slides(data):
    items = data.get("slides") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        title = str(it.get("title", "")).strip()
        bullets = it.get("bullets", it.get("points"))
        if not isinstance(bullets, list):
            continue
        bullets = [str(b).strip() for b in bullets if str(b).strip()]
        if title and len(bullets) >= 2:
            out.append({"title": title, "bullets": bullets[:5]})
    if len(out) < 4:
        raise ValueError
    return out[:8]


def create_slides_for(doc_id):
    ss = st.session_state
    doc = ss.docs.get(doc_id)
    if not doc:
        st.error("Please upload and process a PDF first.")
        return False
    with st.spinner("Building your slideshow…"):
        context = select_context(doc["chunks"], max_chars=9000)
        slides, err = ask_json(slides_prompt(context), validate_slides, temperature=0.4)
    if err:
        st.error(err)
        return False
    ss.slides = {"doc_id": doc_id, "doc_name": doc["name"], "slides": slides, "i": 0}
    log_activity(f"{doc['name']} slideshow", f"{len(slides)} slides generated")
    return True


def _move(delta):
    s = st.session_state.slides
    s["i"] = max(0, min(len(s["slides"]) - 1, s["i"] + delta))


def _jump(i):
    st.session_state.slides["i"] = i


def render_slides():
    page_header("Slides", "A slideshow of the key ideas in your study material, ready to present or revise from.")
    ss = st.session_state
    if not ss.docs:
        empty_state("No study material yet", "Upload and process a PDF first, then come back to build a slideshow.")
        st.button("Go to Study Materials", on_click=go, args=("Study Materials",))
        return

    docs = ss.docs
    ids = list(docs.keys())
    default = ids.index(ss.slides["doc_id"]) if ss.slides and ss.slides["doc_id"] in ids else 0
    c1, c2 = st.columns([3, 1])
    pick = c1.selectbox("Study material", ids, index=default, format_func=lambda i: docs[i]["name"], key="slides_doc_pick")
    c2.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
    if c2.button("Generate slideshow" if not ss.slides else "Regenerate", type="primary", use_container_width=True):
        if create_slides_for(pick):
            st.rerun()

    s = ss.slides
    if not s:
        empty_state("No slideshow yet", "Choose a document and generate your first slideshow.")
        return

    n, i = len(s["slides"]), s["i"]
    slide = s["slides"][i]
    bullets = "".join(f"<li>{esc(b)}</li>" for b in slide["bullets"])
    html(
        f'<div class="sm-slide"><div class="sm-slide-n">Slide {i + 1} of {n} · {esc(s["doc_name"])}</div>'
        f'<div class="sm-slide-t">{esc(slide["title"])}</div><ul>{bullets}</ul></div>'
    )
    dots = "".join(f'<span class="sm-dot{" on" if k == i else ""}"></span>' for k in range(n))
    html(f'<div class="sm-dots">{dots}</div>')
    b = st.columns([1, 1, 1])
    b[0].button("Previous", on_click=_move, args=(-1,), disabled=i == 0, use_container_width=True)
    b[1].button("Restart", on_click=_jump, args=(0,), disabled=i == 0, use_container_width=True)
    b[2].button("Next", on_click=_move, args=(1,), disabled=i == n - 1, type="primary", use_container_width=True)