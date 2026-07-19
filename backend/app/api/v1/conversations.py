"""
Conversation history routes: list, view, rename, pin, archive, delete, search.
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.chat import Conversation, Message
from app.models.user import User
from app.schemas.chat import ConversationDetailOut, ConversationOut, ConversationRenameRequest, MessageOut
from app.services.chat_service import get_conversation_or_404

router = APIRouter(prefix="/conversations", tags=["Conversation History"])


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    search: str | None = Query(default=None),
    include_archived: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Conversation).where(Conversation.user_id == current_user.id)
    if not include_archived:
        stmt = stmt.where(Conversation.is_archived.is_(False))
    if search:
        stmt = stmt.where(Conversation.title.ilike(f"%{search}%"))
    stmt = stmt.order_by(Conversation.is_pinned.desc(), Conversation.updated_at.desc())

    result = await db.execute(stmt)
    conversations = result.scalars().all()
    return [ConversationOut.model_validate({**c.__dict__, "id": str(c.id)}) for c in conversations]


@router.get("/{conversation_id}", response_model=ConversationDetailOut)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = await get_conversation_or_404(db, conversation_id, current_user.id)
    result = await db.execute(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at))
    messages = result.scalars().all()
    return ConversationDetailOut.model_validate(
        {
            **conversation.__dict__,
            "id": str(conversation.id),
            "messages": [MessageOut.model_validate({**m.__dict__, "id": str(m.id)}) for m in messages],
        }
    )


@router.patch("/{conversation_id}/rename", response_model=ConversationOut)
async def rename_conversation(
    conversation_id: uuid.UUID,
    payload: ConversationRenameRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = await get_conversation_or_404(db, conversation_id, current_user.id)
    conversation.title = payload.title
    await db.commit()
    await db.refresh(conversation)
    return ConversationOut.model_validate({**conversation.__dict__, "id": str(conversation.id)})


@router.patch("/{conversation_id}/pin", response_model=ConversationOut)
async def toggle_pin(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = await get_conversation_or_404(db, conversation_id, current_user.id)
    conversation.is_pinned = not conversation.is_pinned
    await db.commit()
    await db.refresh(conversation)
    return ConversationOut.model_validate({**conversation.__dict__, "id": str(conversation.id)})


@router.patch("/{conversation_id}/archive", response_model=ConversationOut)
async def toggle_archive(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = await get_conversation_or_404(db, conversation_id, current_user.id)
    conversation.is_archived = not conversation.is_archived
    await db.commit()
    await db.refresh(conversation)
    return ConversationOut.model_validate({**conversation.__dict__, "id": str(conversation.id)})


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = await get_conversation_or_404(db, conversation_id, current_user.id)
    await db.delete(conversation)
    await db.commit()
