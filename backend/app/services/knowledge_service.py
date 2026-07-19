"""
Knowledge retrieval layer.

Architecture note: this performs keyword/ILIKE search today. It is
structured so that swapping in embedding-based semantic search later
(pgvector, or an external vector store) only requires changing
`_search_knowledge_articles` — callers and the context-formatting
contract stay the same. That's what "RAG-ready" means here.
"""
import re

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academics import Course, Lecturer
from app.models.content import FAQ, KnowledgeArticle
from app.models.enums import ContentStatus

_STOPWORDS = {
    "the", "is", "are", "a", "an", "of", "to", "for", "in", "on", "and", "or",
    "what", "who", "how", "when", "where", "does", "do", "i", "my", "me", "can",
    "please", "tell", "about", "explain",
}


def _extract_terms(text: str, limit: int = 6) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9]{3,}", text.lower())
    terms = [w for w in words if w not in _STOPWORDS]
    # de-duplicate while preserving order
    seen = set()
    unique = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique[:limit]


async def search_knowledge(db: AsyncSession, query: str, max_results: int = 4) -> str:
    """
    Search knowledge articles, FAQs, courses, and lecturers for terms in the
    query. Returns a formatted context block ready for prompt injection, or
    an empty string if nothing relevant was found.
    """
    terms = _extract_terms(query)
    if not terms:
        return ""

    context_blocks: list[str] = []

    # --- Knowledge articles ---
    like_clauses = [KnowledgeArticle.content.ilike(f"%{t}%") for t in terms] + [
        KnowledgeArticle.title.ilike(f"%{t}%") for t in terms
    ]
    result = await db.execute(
        select(KnowledgeArticle)
        .where(KnowledgeArticle.status == ContentStatus.PUBLISHED)
        .where(or_(*like_clauses))
        .limit(max_results)
    )
    for article in result.scalars().all():
        context_blocks.append(f"[Knowledge Article] {article.title}\n{article.content}")

    # --- FAQs ---
    faq_clauses = [FAQ.question.ilike(f"%{t}%") for t in terms] + [FAQ.answer.ilike(f"%{t}%") for t in terms]
    result = await db.execute(
        select(FAQ).where(FAQ.status == ContentStatus.PUBLISHED).where(or_(*faq_clauses)).limit(max_results)
    )
    for faq in result.scalars().all():
        context_blocks.append(f"[FAQ] Q: {faq.question}\nA: {faq.answer}")

    # --- Courses ---
    course_clauses = [Course.title.ilike(f"%{t}%") for t in terms] + [Course.code.ilike(f"%{t}%") for t in terms]
    result = await db.execute(select(Course).where(or_(*course_clauses)).limit(max_results))
    for course in result.scalars().all():
        context_blocks.append(
            f"[Course] {course.code} — {course.title} ({course.level}, {course.semester} semester, "
            f"{course.units} units)\n{course.description or ''}"
        )

    # --- Lecturers ---
    lecturer_clauses = [Lecturer.full_name.ilike(f"%{t}%") for t in terms]
    result = await db.execute(select(Lecturer).where(or_(*lecturer_clauses)).limit(max_results))
    for lecturer in result.scalars().all():
        context_blocks.append(
            f"[Lecturer] {lecturer.title or ''} {lecturer.full_name} — Office: {lecturer.office or 'N/A'}, "
            f"Office hours: {lecturer.office_hours or 'N/A'}"
        )

    if not context_blocks:
        return ""

    return "\n\n".join(context_blocks[: max_results * 2])
