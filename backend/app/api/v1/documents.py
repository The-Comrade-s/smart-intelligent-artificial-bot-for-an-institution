"""
Document routes: upload lecture notes (PDF/DOCX/TXT) for text extraction,
then run AI analysis (summarize, explain, quiz, flashcards, or Q&A) over
the extracted text.

Persistent document storage/indexing (browsable library, RAG chunking) is
a natural ES-003/ES-005 extension; this phase covers extraction + analysis.
"""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.exceptions import AppError
from app.db.session import get_db
from app.models.user import User
from app.schemas.documents import DocumentAnalyzeRequest, DocumentAnalyzeResponse, DocumentExtractResponse
from app.services.ai_providers.base import AIProviderError, AIRequestConfig, ChatMessage
from app.services.ai_providers.manager import AIManager
from app.services.document_service import extract_text, truncate_for_prompt

router = APIRouter(prefix="/documents", tags=["Documents"])

_ALLOWED_EXTENSIONS = {e.strip().lower() for e in settings.ALLOWED_UPLOAD_EXTENSIONS.split(",")}

_ACTION_INSTRUCTIONS = {
    "summarize": "Summarize the following document in clear, student-friendly bullet points.",
    "explain": "Explain the key concepts in the following document as if teaching a Computer Science student.",
    "quiz": "Generate a 5-question quiz (mix of multiple choice and short answer, with an answer key) based on the following document.",
    "flashcards": "Generate 8 flashcards (Q: / A: format) covering the most important points in the following document.",
    "question": "Answer the student's question using only the following document as context. If the document doesn't contain the answer, say so clearly.",
}


@router.post("/extract", response_model=DocumentExtractResponse)
async def upload_and_extract(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
):
    extension = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    if extension not in _ALLOWED_EXTENSIONS:
        raise AppError(
            f"File type .{extension} is not supported. Allowed types: {', '.join(sorted(_ALLOWED_EXTENSIONS))}",
            code="UNSUPPORTED_FILE_TYPE",
            status_code=415,
        )

    file_bytes = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise AppError(f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit", code="FILE_TOO_LARGE", status_code=413)

    text = extract_text(file.filename, file_bytes)
    return DocumentExtractResponse(filename=file.filename, character_count=len(text), extracted_text=text)


@router.post("/analyze", response_model=DocumentAnalyzeResponse)
async def analyze_document(
    payload: DocumentAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    instruction = _ACTION_INSTRUCTIONS.get(payload.action)
    if not instruction:
        raise AppError(
            f"Unknown action '{payload.action}'. Valid actions: {', '.join(_ACTION_INSTRUCTIONS)}",
            code="INVALID_ACTION",
            status_code=400,
        )
    if payload.action == "question" and not payload.question:
        raise AppError("'question' is required when action is 'question'", code="MISSING_QUESTION", status_code=400)

    document_text = truncate_for_prompt(payload.text)
    user_prompt = instruction + "\n\n---\n" + document_text
    if payload.action == "question":
        user_prompt += f"\n---\n\nStudent's question: {payload.question}"

    manager = AIManager(db)
    provider, config = await manager.resolve_provider()
    config = AIRequestConfig(
        temperature=config.temperature,
        max_tokens=max(config.max_tokens, 1024),
        system_prompt="You are COSIB AI, helping a student study from their own uploaded material. Be accurate and only use the provided document content.",
    )

    try:
        response = await provider.generate([ChatMessage(role="user", content=user_prompt)], config)
    except AIProviderError:
        from app.services.ai_providers.mock_provider import MockProvider

        response = await MockProvider().generate([ChatMessage(role="user", content=user_prompt)], config)

    return DocumentAnalyzeResponse(action=payload.action, result=response.content)
