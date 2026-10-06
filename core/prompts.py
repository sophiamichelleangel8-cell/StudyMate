TUTOR_SYSTEM = (
    "You are StudyMate, a warm, clear and accurate AI tutor for college students. "
    "Explain concepts step by step, simplify difficult ideas, and give short concrete examples. "
    "Use short paragraphs and bullet points where they help. Never invent facts; "
    "if you are unsure, say so."
)


def tutor_prompt(question, passages):
    if not passages:
        return question
    ctx = "\n\n".join(
        f"[Passage {i}] (from {p['doc_name']})\n{p['text']}" for i, p in enumerate(passages, 1)
    )
    return (
        "Use the study-material passages below to answer the student's question. "
        "Prioritise the passages. If they do not cover the question, say so briefly "
        "and then answer from general knowledge.\n\n"
        f"Study material:\n{ctx}\n\nStudent question: {question}"
    )


def summary_prompt(context):
    return f"""Read the study material below and produce a revision summary for a student.

Return ONLY a JSON object with exactly these keys:
{{
  "main_topics": ["short topic", "..."],
  "important_concepts": [{{"name": "concept", "explanation": "1-2 sentence explanation"}}],
  "key_definitions": [{{"term": "term", "definition": "clear definition"}}],
  "important_points": ["key point", "..."],
  "revision_points": ["exam-focused point to memorise", "..."]
}}

Give 3-6 items per list. Use only information from the material.

STUDY MATERIAL:
{context}"""


def quiz_prompt(context):
    return f"""Create exactly 5 multiple-choice questions from the study material below.

Rules:
- Test understanding of the material; questions must be clear and unambiguous.
- Each question has exactly 4 distinct options and exactly one correct option.
- Do not prefix options with letters or numbers.
- "answer" must be the exact text of the correct option.
- "explanation" is one short sentence.

Return ONLY a JSON object in this shape:
{{"questions": [{{"question": "...", "options": ["...", "...", "...", "..."], "answer": "...", "explanation": "..."}}]}}

STUDY MATERIAL:
{context}"""


def flashcard_prompt(context, avoid=None):
    extra = ""
    if avoid:
        extra = "\nDo not repeat these earlier questions:\n- " + "\n- ".join(avoid) + "\n"
    return f"""Create exactly 5 flashcards from the study material below.
Each flashcard has a short question and a concise answer (1-3 sentences).
{extra}
Return ONLY a JSON object in this shape:
{{"flashcards": [{{"question": "...", "answer": "..."}}]}}

STUDY MATERIAL:
{context}"""

def slides_prompt(context):
    return f"""Turn the study material below into a 6-slide study slideshow.

Slide 1 is an overview of the topic. The remaining slides each cover one key idea in order.
Each slide has a short title and 3 or 4 concise bullet points (under 18 words each).
Use only information from the material.

Return ONLY a JSON object in this shape:
{{"slides": [{{"title": "...", "bullets": ["...", "...", "..."]}}]}}

STUDY MATERIAL:
{context}"""