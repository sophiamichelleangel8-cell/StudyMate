import random
import re


def split_text(pages, chunk_size=900, overlap=150):
    """Sentence-aware chunking with a small overlap between chunks."""
    text = "\n\n".join(pages)
    sentences = re.split(r"(?<=[.!?])\s+|\n\n", text)
    chunks, cur = [], ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        while len(s) > chunk_size:  # very long unbroken text
            if cur:
                chunks.append(cur)
                cur = ""
            chunks.append(s[:chunk_size])
            s = s[chunk_size - overlap:]
        if len(cur) + len(s) + 1 <= chunk_size:
            cur = f"{cur} {s}".strip()
        else:
            if cur:
                chunks.append(cur)
            tail = cur[-overlap:] if cur else ""
            tail = tail[tail.find(" ") + 1:] if " " in tail else ""
            cur = f"{tail} {s}".strip()
    if cur:
        chunks.append(cur)
    return [c for c in chunks if len(c) >= 20]


def select_context(chunks, max_chars=9000, randomize=False):
    """Pick chunks spread across the document so the prompt stays small."""
    if not chunks:
        return ""
    total = sum(len(c) + 2 for c in chunks)
    if total <= max_chars:
        return "\n\n".join(chunks)
    avg = total / len(chunks)
    n = max(1, min(len(chunks), int(max_chars / avg)))
    if randomize:
        idxs = sorted(random.sample(range(len(chunks)), n))
    else:
        idxs = sorted({int(i * len(chunks) / n) for i in range(n)})
    return "\n\n".join(chunks[i] for i in idxs)
