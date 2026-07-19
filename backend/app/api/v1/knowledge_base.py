"""
Knowledge base routes.

Search is available to any authenticated user (it's what powers chat
retrieval and the in-app search bar). Create/update/delete are admin-only.
Full admin management UI arrives in ES-003; these are the API primitives.
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.content import FAQ, KnowledgeArticle
from app.models.enums import UserRole
from app.schemas.knowledge import (
    FAQCreate,
    FAQOut,
    KnowledgeArticleCreate,
    KnowledgeArticleOut,
    KnowledgeArticleUpdate,
    KnowledgeSearchResult,
)
from app.services.knowledge_service import search_knowledge

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])


@router.get("/search", response_model=KnowledgeSearchResult)
async def search(
    q: str = Query(min_length=2),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    context = await search_knowledge(db, q)
    return KnowledgeSearchResult(query=q, context_found=bool(context), results_preview=context[:1500])


@router.get("/articles", response_model=list[KnowledgeArticleOut])
async def list_articles(
    category: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    stmt = select(KnowledgeArticle)
    if category:
        stmt = stmt.where(KnowledgeArticle.category == category)
    result = await db.execute(stmt.order_by(KnowledgeArticle.created_at.desc()))
    articles = result.scalars().all()
    return [KnowledgeArticleOut.model_validate({**a.__dict__, "id": str(a.id)}) for a in articles]


@router.post("/articles", response_model=KnowledgeArticleOut, status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: KnowledgeArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    article = KnowledgeArticle(**payload.model_dump(), created_by=current_user.id)
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return KnowledgeArticleOut.model_validate({**article.__dict__, "id": str(article.id)})


@router.patch("/articles/{article_id}", response_model=KnowledgeArticleOut)
async def update_article(
    article_id: uuid.UUID,
    payload: KnowledgeArticleUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    article = await db.get(KnowledgeArticle, article_id)
    if not article:
        raise NotFoundError("Knowledge article not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(article, field, value)
    await db.commit()
    await db.refresh(article)
    return KnowledgeArticleOut.model_validate({**article.__dict__, "id": str(article.id)})


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    article = await db.get(KnowledgeArticle, article_id)
    if not article:
        raise NotFoundError("Knowledge article not found")
    await db.delete(article)
    await db.commit()


@router.get("/faqs", response_model=list[FAQOut])
async def list_faqs(
    category: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    stmt = select(FAQ)
    if category:
        stmt = stmt.where(FAQ.category == category)
    result = await db.execute(stmt.order_by(FAQ.is_pinned.desc(), FAQ.created_at.desc()))
    faqs = result.scalars().all()
    return [FAQOut.model_validate({**f.__dict__, "id": str(f.id)}) for f in faqs]


@router.post("/faqs", response_model=FAQOut, status_code=status.HTTP_201_CREATED)
async def create_faq(
    payload: FAQCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    faq = FAQ(**payload.model_dump())
    db.add(faq)
    await db.commit()
    await db.refresh(faq)
    return FAQOut.model_validate({**faq.__dict__, "id": str(faq.id)})


@router.delete("/faqs/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    faq = await db.get(FAQ, faq_id)
    if not faq:
        raise NotFoundError("FAQ not found")
    await db.delete(faq)
    await db.commit()
