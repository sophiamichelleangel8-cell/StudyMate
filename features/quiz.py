import random
import re

import streamlit as st

from core.ai_client import ask_json
from core.prompts import quiz_prompt
from core.session_state import go, log_activity
from rag.text_splitter import select_context
from ui.styles import empty_state, esc, html, page_header

LETTERS = "ABCD"


def _norm_option(o):
    return re.sub(r"^\(?[A-Da-d][\).:]\s+", "", str(o).strip()).strip()


def _answer_index(item, opts):
    ans = item.get("answer", item.get("correct_answer", item.get("correct")))
    if isinstance(ans, int) and 0 <= ans < 4:
        return ans
    if isinstance(ans, str):
        a = ans.strip()
        if len(a) == 1 and a.upper() in LETTERS:
            return LETTERS.index(a.upper())
        low = [o.lower() for o in opts]
        for cand in (a.lower(), _norm_option(a).lower()):
            if cand in low:
                return low.index(cand)
    return None


def validate_quiz(data):
    items = data.get("questions") if isinstance(data, dict) else data
    if not isinstance(items, list):
        raise ValueError
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        q = str(it.get("question", "")).strip()
        opts = it.get("options")
        if isinstance(opts, dict):
            opts = list(opts.values())
        if not q or not isinstance(opts, list) or len(opts) != 4:
            continue
        opts = [_norm_option(o) for o in opts]
        if any(not o for o in opts) or len({o.lower() for o in opts}) != 4:
            continue
        idx = _answer_index(it, opts)
        if idx is None:
            continue
        correct = opts[idx]
        random.shuffle(opts)
        out.append(
            {"question": q, "options": opts, "answer": correct, "explanation": str(it.get("explanation", "")).strip()}
        )
    if len(out) < 5:
        raise ValueError
    return out[:5]


def create_quiz_for(doc_id):
    """Generate a quiz and store it in session state. Returns True on success."""
    ss = st.session_state
    doc = ss.docs.get(doc_id)
    if not doc:
        st.error("Please upload and process a PDF first.")
        return False
    with st.spinner("Writing your quiz…"):
        context = select_context(doc["chunks"], max_chars=8000, randomize=True)
        questions, err = ask_json(quiz_prompt(context), validate_quiz)
    if err:
        st.error(err)
        return False
    ss.quiz_run += 1
    ss.quiz = {
        "doc_id": doc_id,
        "doc_name": doc["name"],
        "questions": questions,
        "run": ss.quiz_run,
        "submitted": False,
        "choices": [],
        "score": 0,
        "review": False,
    }
    log_activity(f"{doc['name']} quiz", "Quiz generated")
    return True


def _try_again():
    ss = st.session_state
    ss.quiz_run += 1
    ss.quiz.update(run=ss.quiz_run, submitted=False, choices=[], score=0, review=False)


def _new_quiz():
    st.session_state.quiz = None


def _toggle_review():
    st.session_state.quiz["review"] = not st.session_state.quiz["review"]


def _generator():
    docs = st.session_state.docs
    ids = list(docs.keys())
    st.markdown("### Generate a quiz")
    pick = st.selectbox("Study material", ids, format_func=lambda i: docs[i]["name"], key="quiz_doc_pick")
    if st.button("Generate quiz", type="primary"):
        if create_quiz_for(pick):
            st.rerun()


def render_quiz():
    page_header("Quiz", "Five multiple-choice questions written from your own study material.")
    ss = st.session_state
    if not ss.docs:
        empty_state("No study material yet", "Upload and process a PDF first, then come back to generate a quiz.")
        st.button("Go to Study Materials", on_click=go, args=("Study Materials",))
        return
    quiz = ss.quiz
    if quiz is None:
        _generator()
        return

    qs = quiz["questions"]
    if not quiz["submitted"]:
        st.caption(f"From: {quiz['doc_name']}")
        picks = []
        for i, q in enumerate(qs):
            html(f'<div class="sm-qn">Question {i + 1} of {len(qs)}</div><div class="sm-q">{esc(q["question"])}</div>')
            picks.append(
                st.radio(
                    f"Question {i + 1}",
                    q["options"],
                    index=None,
                    key=f"q_{quiz['run']}_{i}",
                    label_visibility="collapsed",
                )
            )
            st.write("")
        missing = sum(1 for p in picks if p is None)
        if missing:
            st.caption(f"Select an answer for every question to submit ({missing} left).")
        if st.button("Submit quiz", type="primary", disabled=bool(missing)):
            score = sum(1 for p, q in zip(picks, qs) if p == q["answer"])
            quiz.update(submitted=True, choices=picks, score=score, review=False)
            pct = round(score / len(qs) * 100)
            ss.quiz_history.append(
                {"doc_name": quiz["doc_name"], "score": score, "total": len(qs), "pct": pct}
            )
            log_activity(f"{quiz['doc_name']} quiz", f"Score: {score}/{len(qs)}")
            st.rerun()
        with st.expander("Generate a different quiz"):
            if st.button("Start over with new questions"):
                _new_quiz()
                st.rerun()
        return

    score, total = quiz["score"], len(qs)
    pct = round(score / total * 100)
    msg = "Great job!" if pct >= 80 else "Good effort. A little more revision will help." if pct >= 60 else "Keep going. Review the answers and try again."
    html(
        f'<div class="sm-card"><div class="sm-qn">Quiz complete</div><div class="sm-big">{score} / {total}</div>'
        f'<div class="sm-q" style="margin-top:.5rem">{pct}% · {msg}</div></div>'
    )
    c1, c2 = st.columns(2)
    c1.markdown(stat_html(score, "Correct answers"), unsafe_allow_html=True)
    c2.markdown(stat_html(total - score, "Incorrect answers"), unsafe_allow_html=True)

    b = st.columns(3)
    b[0].button("Hide review" if quiz["review"] else "Review Answers", on_click=_toggle_review, use_container_width=True)
    b[1].button("Try Again", on_click=_try_again, use_container_width=True)
    b[2].button("New quiz", on_click=_new_quiz, use_container_width=True)

    if quiz["review"]:
        st.markdown("### Review")
        for i, (q, pick) in enumerate(zip(qs, quiz["choices"])):
            ok = pick == q["answer"]
            cls = "sm-good" if ok else "sm-bad"
            expl = f'<div class="sm-act-d" style="margin-top:.4rem">{esc(q["explanation"])}</div>' if q["explanation"] else ""
            html(
                f'<div class="sm-card"><div class="sm-qn">Question {i + 1}</div><div class="sm-q">{esc(q["question"])}</div>'
                f'<div style="margin-top:.6rem">Your answer: <span class="{cls}">{esc(pick)}</span></div>'
                f'<div>Correct answer: <span class="sm-good">{esc(q["answer"])}</span></div>{expl}</div>'
            )


def stat_html(v, label):
    return f'<div class="sm-card"><div class="sm-stat-n">{v}</div><div class="sm-stat-l">{esc(label)}</div></div>'
