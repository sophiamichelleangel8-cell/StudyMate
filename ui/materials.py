import hashlib
import uuid

import streamlit as st

from core.ai_client import AIError
from core.session_state import go, log_activity
from features.flashcards import create_flashcards_for
from features.slides import create_slides_for
from features.quiz import create_quiz_for
from features.summary import generate_summary, render_summary
from rag import vector_store
from rag.pdf_loader import PDFError, extract_pages
from rag.text_splitter import split_text
from ui.styles import empty_state, esc, html, page_header


def _process(upload):
    ss = st.session_state
    data = upload.getvalue()
    digest = hashlib.sha1(data).hexdigest()
    if any(d["hash"] == digest for d in ss.docs.values()):
        st.info("This file has already been processed.")
        return
    with st.status("Processing PDF…", expanded=True) as status:
        try:
            st.write("Extracting text…")
            pages, total_pages = extract_pages(data)
            st.write("Cleaning and splitting into sections…")
            chunks = split_text(pages)
            if not chunks:
                raise PDFError("There was not enough text in this PDF to study from.")
            st.write(f"Building the search index for {len(chunks)} sections (the first run downloads a small model)…")
            doc_id = uuid.uuid4().hex[:8]
            vector_store.add_document(doc_id, upload.name, chunks)
        except PDFError as e:
            status.update(label="Could not process this PDF", state="error")
            st.error(str(e))
            return
        except Exception:
            status.update(label="Could not process this PDF", state="error")
            st.error(
                "StudyMate could not build the search index. Check your internet connection "
                "(needed once to download the embedding model) and try again."
            )
            return
        status.update(label="PDF processed", state="complete")
    ss.docs[doc_id] = {
        "id": doc_id,
        "name": upload.name,
        "hash": digest,
        "pages": total_pages,
        "chunks": chunks,
        "summary": None,
    }
    log_activity(upload.name, f"Processed · {len(chunks)} sections")
    ss.notice = ("success", f"{upload.name} is ready. {len(chunks)} sections indexed.")
    ss.uploader_key += 1
    st.rerun()


def _ask(doc_id):
    st.session_state.chat_scope = doc_id
    go("AI Tutor")


def _remove(doc_id):
    vector_store.delete_document(doc_id)
    ss = st.session_state
    ss.docs.pop(doc_id, None)
    if ss.quiz and ss.quiz["doc_id"] == doc_id:
        ss.quiz = None
    if ss.flash and ss.flash["doc_id"] == doc_id:
        ss.flash = None
    if ss.slides and ss.slides["doc_id"] == doc_id:
        ss.slides = None
    if ss.chat_scope == doc_id:
        ss.chat_scope = "all"


def render_materials():
    page_header(
        "Study Materials",
        "Upload a PDF, process it, then ask questions, summarize it, or turn it into a quiz and flashcards.",
    )
    ss = st.session_state
    if ss.notice:
        kind, msg = ss.notice
        getattr(st, kind)(msg)
        ss.notice = None

    with st.container(border=True):
        st.markdown("#### Upload a PDF")
        upload = st.file_uploader("PDF file", type=["pdf"], key=f"up_{ss.uploader_key}", label_visibility="collapsed")
        if upload is not None:
            st.caption(f"{upload.name} · {upload.size / 1024:.0f} KB")
            if st.button("Process PDF", type="primary"):
                _process(upload)

    st.markdown("### Your documents")
    if not ss.docs:
        empty_state("No documents yet", "Upload a PDF above and press Process PDF.")
        return

    for doc_id, d in list(ss.docs.items()):
        with st.container(border=True):
            html(
                f'<div class="sm-doc-title">{esc(d["name"])}</div>'
                f'<div class="sm-doc-meta"><span class="sm-ok">✓ Processed</span>{len(d["chunks"])} sections · {d["pages"]} pages</div>'
            )
            c = st.columns(6)
            c[0].button("Ask Questions", key=f"ask_{doc_id}", on_click=_ask, args=(doc_id,), use_container_width=True)
            if c[1].button("Summarize", key=f"sum_{doc_id}", use_container_width=True):
                if d["summary"] is None:
                    with st.spinner("Summarizing your material…"):
                        result, err = generate_summary(d)
                    if err:
                        st.error(err)
                    else:
                        d["summary"] = result
                        log_activity(d["name"], "Summary generated")
                if d["summary"]:
                    ss.open_summary = doc_id
                    st.rerun()
            if c[2].button("Quiz", key=f"quiz_{doc_id}", use_container_width=True):
                if create_quiz_for(doc_id):
                    go("Quiz")
                    st.rerun()
            if c[3].button("Flashcards", key=f"fc_{doc_id}", use_container_width=True):
                if create_flashcards_for(doc_id):
                    go("Flashcards")
                    st.rerun()
            if c[4].button("Slides", key=f"sl_{doc_id}", use_container_width=True):
                if create_slides_for(doc_id):
                      go("Slides")
                      st.rerun()
            c[5].button("Remove", key=f"rm_{doc_id}", on_click=_remove, args=(doc_id,), use_container_width=True)
            if d["summary"]:
                with st.expander(f"Summary of {d['name']}", expanded=ss.open_summary == doc_id):
                    render_summary(d["summary"])
