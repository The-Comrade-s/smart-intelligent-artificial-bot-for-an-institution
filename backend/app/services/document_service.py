"""
Document processing: extracts text from uploaded PDF/DOCX/TXT files so it
can be summarized, quizzed on, or (in a future phase) chunked and indexed
for semantic search.
"""
import io

import docx
from pypdf import PdfReader

from app.core.exceptions import AppError


class UnsupportedFileTypeError(AppError):
    def __init__(self, extension: str):
        super().__init__(f"Unsupported file type: .{extension}", code="UNSUPPORTED_FILE_TYPE", status_code=415)


def extract_text(filename: str, file_bytes: bytes) -> str:
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension == "pdf":
        return _extract_pdf(file_bytes)
    if extension == "docx":
        return _extract_docx(file_bytes)
    if extension == "txt":
        return file_bytes.decode("utf-8", errors="ignore")

    raise UnsupportedFileTypeError(extension)


def _extract_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()


def _extract_docx(file_bytes: bytes) -> str:
    document = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def truncate_for_prompt(text: str, max_chars: int = 12000) -> str:
    """Keep uploaded-document context within a safe prompt budget."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[...document truncated...]"
