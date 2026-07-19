"""
Chat routes: send a message and get a complete response, or stream it
token-by-token via Server-Sent Events.
"""
import json
import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.limiter import limiter
from app.db.session import get_db
from app.models.enums import MessageRole
from app.models.user import User
from app.schemas.chat import ChatResponse, MessageOut, SendMessageRequest
from app.services import chat_service
from app.services.ai_providers.base import AIProviderError

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def send_message(
    request: Request,
    payload: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation_id = uuid.UUID(payload.conversation_id) if payload.conversation_id else None
    conversation = await chat_service.get_or_create_conversation(db, current_user.id, conversation_id, payload.message)

    history, mode, provider, config = await chat_service.prepare_ai_call(db, conversation, payload.message)

    with chat_service.Timer() as t:
        try:
            ai_response = await provider.generate(history, config)
        except AIProviderError:
            # Never hard-fail the chat — fall back to a graceful message.
            from app.services.ai_providers.mock_provider import MockProvider

            ai_response = await MockProvider().generate(history, config)

    assistant_msg = await chat_service.persist_assistant_message(
        db, conversation, ai_response.content, ai_response.provider or provider.name, ai_response.tokens_used, t.elapsed_ms
    )

    return ChatResponse(
        conversation_id=str(conversation.id),
        message=MessageOut.model_validate({**assistant_msg.__dict__, "id": str(assistant_msg.id)}),
        suggestions=chat_service.generate_suggestions(mode),
    )


@router.post("/stream")
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def stream_message(
    request: Request,
    payload: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation_id = uuid.UUID(payload.conversation_id) if payload.conversation_id else None
    conversation = await chat_service.get_or_create_conversation(db, current_user.id, conversation_id, payload.message)
    history, mode, provider, config = await chat_service.prepare_ai_call(db, conversation, payload.message)
    conversation_id_str = str(conversation.id)

    async def event_generator():
        full_text = []
        yield f"event: conversation\ndata: {json.dumps({'conversation_id': conversation_id_str})}\n\n"

        with chat_service.Timer() as t:
            try:
                async for chunk in provider.stream(history, config):
                    full_text.append(chunk)
                    yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"
            except AIProviderError:
                from app.services.ai_providers.mock_provider import MockProvider

                async for chunk in MockProvider().stream(history, config):
                    full_text.append(chunk)
                    yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"

        content = "".join(full_text)
        assistant_msg = await chat_service.persist_assistant_message(
            db, conversation, content, provider.name, None, t.elapsed_ms
        )
        suggestions = chat_service.generate_suggestions(mode)
        yield (
            "event: done\ndata: "
            + json.dumps(
                {
                    "message_id": str(assistant_msg.id),
                    "suggestions": suggestions,
                }
            )
            + "\n\n"
        )

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.patch("/messages/{message_id}/reaction", response_model=MessageOut)
async def react_to_message(
    message_id: uuid.UUID,
    liked: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.core.exceptions import ForbiddenError, NotFoundError
    from app.models.chat import Message

    message = await db.get(Message, message_id)
    if not message:
        raise NotFoundError("Message not found")
    conversation = await chat_service.get_conversation_or_404(db, message.conversation_id, current_user.id)
    if message.role != MessageRole.ASSISTANT:
        raise ForbiddenError("Only assistant messages can be reacted to")

    message.liked = liked
    await db.commit()
    await db.refresh(message)
    return MessageOut.model_validate({**message.__dict__, "id": str(message.id)})
