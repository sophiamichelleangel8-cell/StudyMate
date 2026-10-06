import io
import re

from pypdf import PdfReader


class PDFError(Exception):
    """Raised with a message that is safe to show to the student."""


def clean_text(text):
    text = text.replace("\x00", " ")
    text = re.sub(r"-\n(?=[a-z])", "", text)      # re-join hyphenated line breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)   # single newlines inside paragraphs
    return text.strip()


def extract_pages(data):
    """Return (list_of_page_texts_with_text, total_page_count)."""
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception:
        raise PDFError("This file could not be opened as a PDF. Try exporting it again.")

    if reader.is_encrypted:
        try:
            ok = reader.decrypt("")
        except Exception:
            ok = 0
        if not ok:
            raise PDFError("This PDF is password-protected. Remove the password and upload it again.")

    pages = []
    total = len(reader.pages)
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        text = clean_text(text)
        if text:
            pages.append(text)

    if not pages:
        raise PDFError(
            "No readable text was found in this PDF. It may be a scanned document made of images. "
            "Try a PDF with selectable text."
        )
    return pages, total
