"""
Ingests the DS-001 (institutional) and DS-002 (academic) datasets from
database/seed_data/ into the KnowledgeArticle and FAQ tables.

Idempotent: re-running skips articles/FAQs that already exist (matched by
title), so it's safe to run again after adding new dataset files.

Run with:
    python -m scripts.seed_knowledge_base
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.session import AsyncSessionLocal  # noqa: E402
from app.models.content import FAQ, KnowledgeArticle  # noqa: E402
from app.models.enums import ContentStatus  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_DATA_DIR = REPO_ROOT / "database" / "seed_data"

DS001_DIR = SEED_DATA_DIR / "ds001_institution"
DS002_DIR = SEED_DATA_DIR / "ds002_academic"

# DS-002 subject files ingested as knowledge articles (quiz_bank/flashcards/
# learning_paths are reference datasets, not individually ingested as articles).
DS002_SUBJECT_FILES = [
    "programming.json",
    "algorithms.json",
    "database.json",
    "networking.json",
    "operating_systems.json",
    "software_engineering.json",
    "artificial_intelligence.json",
    "cybersecurity.json",
    "mathematics.json",
]

DS001_ARTICLE_FILES = [
    "institution.json",
    "department.json",
    "academic_regulations.json",
    "student_services.json",
]


def _load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _format_academic_content(record: dict) -> str:
    """Combine a DS-002 record's explanation, example, and quiz into one article body."""
    parts = [record["content"]]
    if record.get("example"):
        parts.append(f"\n**Example:**\n{record['example']}")
    if record.get("quiz"):
        quiz_lines = ["\n**Practice Questions:**"]
        for q in record["quiz"]:
            quiz_lines.append(f"- {q['question']}")
        parts.append("\n".join(quiz_lines))
    return "\n".join(parts)


async def seed_knowledge_base() -> None:
    async with AsyncSessionLocal() as db:
        existing_titles = {
            row[0] for row in (await db.execute(select(KnowledgeArticle.title))).all()
        }
        existing_questions = {row[0] for row in (await db.execute(select(FAQ.question))).all()}

        created_articles = 0
        created_faqs = 0

        # --- DS-001 institutional articles ---
        for filename in DS001_ARTICLE_FILES:
            path = DS001_DIR / filename
            if not path.exists():
                continue
            for record in _load_json(path):
                if record["title"] in existing_titles:
                    continue
                db.add(
                    KnowledgeArticle(
                        title=record["title"],
                        category=record["category"],
                        content=record["content"],
                        keywords=record.get("keywords"),
                        related_topics=record.get("related_topics"),
                        source=record.get("source"),
                        status=ContentStatus.PUBLISHED,
                    )
                )
                existing_titles.add(record["title"])
                created_articles += 1

        # --- DS-001 FAQs ---
        faq_path = DS001_DIR / "faq.json"
        if faq_path.exists():
            for record in _load_json(faq_path):
                if record["question"] in existing_questions:
                    continue
                db.add(
                    FAQ(
                        category=record["category"],
                        question=record["question"],
                        answer=record["answer"],
                        is_pinned=record.get("is_pinned", False),
                        status=ContentStatus.PUBLISHED,
                    )
                )
                existing_questions.add(record["question"])
                created_faqs += 1

        # --- DS-002 academic articles ---
        for filename in DS002_SUBJECT_FILES:
            path = DS002_DIR / filename
            if not path.exists():
                continue
            for record in _load_json(path):
                title = record["topic"]
                if title in existing_titles:
                    continue
                db.add(
                    KnowledgeArticle(
                        title=title,
                        category=record["category"],
                        content=_format_academic_content(record),
                        keywords=record.get("keywords"),
                        related_topics=record.get("related_topics"),
                        source="; ".join(record.get("references", [])) or None,
                        status=ContentStatus.PUBLISHED,
                    )
                )
                existing_titles.add(title)
                created_articles += 1

        await db.commit()
        print(f"Knowledge base seed complete: {created_articles} article(s), {created_faqs} FAQ(s) created.")


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
