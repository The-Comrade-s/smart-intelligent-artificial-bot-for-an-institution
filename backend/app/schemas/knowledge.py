"""
Pydantic schemas for KnowledgeArticle and FAQ.
"""
from datetime import datetime

from pydantic import BaseModel


class KnowledgeArticleCreate(BaseModel):
    title: str
    category: str
    content: str
    keywords: list[str] | None = None
    related_topics: list[str] | None = None
    source: str | None = None
    status: str = "draft"


class KnowledgeArticleUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    content: str | None = None
    keywords: list[str] | None = None
    related_topics: list[str] | None = None
    source: str | None = None
    status: str | None = None


class KnowledgeArticleOut(BaseModel):
    id: str
    title: str
    category: str
    content: str
    keywords: list[str] | None = None
    related_topics: list[str] | None = None
    source: str | None = None
    status: str
    view_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FAQCreate(BaseModel):
    category: str
    question: str
    answer: str
    is_pinned: bool = False
    status: str = "published"


class FAQOut(BaseModel):
    id: str
    category: str
    question: str
    answer: str
    is_pinned: bool
    view_count: int
    helpful_count: int
    not_helpful_count: int
    status: str

    model_config = {"from_attributes": True}


class KnowledgeSearchResult(BaseModel):
    query: str
    context_found: bool
    results_preview: str
