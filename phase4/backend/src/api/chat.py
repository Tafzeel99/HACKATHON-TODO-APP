"""Chat API endpoints for Phase 3."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header, Path, Query, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import VerifiedUser, verify_user_access
from src.database import get_session
from src.errors import ChatError, EmptyMessageError, chat_error_to_http_exception
from src.services.chat_service import get_chat_service

router = APIRouter()


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = Field(default=None)


class ToolCallResponse(BaseModel):
    """Tool call result in response."""

    tool: str
    result: dict | None = None
    error: str | None = None


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""

    conversation_id: str
    response: str
    tool_calls: list[ToolCallResponse] = []


class ConversationResponse(BaseModel):
    """Conversation summary response."""

    id: str
    user_id: str
    title: str | None
    created_at: str
    updated_at: str


class ConversationsListResponse(BaseModel):
    """List of conversations response."""

    conversations: list[ConversationResponse]


class MessageResponse(BaseModel):
    """Message in conversation response."""

    id: str
    conversation_id: str
    role: str
    content: str
    tool_calls: list[ToolCallResponse] | None
    created_at: str


class ConversationWithMessagesResponse(ConversationResponse):
    """Conversation with messages response."""

    messages: list[MessageResponse]


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def send_chat_message(
    user_id: Annotated[str, Path(description="User ID")],
    request: ChatRequest,
    current_user: VerifiedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ChatResponse:
    """Send a chat message and get AI response.

    The AI assistant will understand the user's intent and execute
    appropriate MCP tools (add_task, list_tasks, complete_task, etc.).
    """
    # Validate message is not empty
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "empty_message", "message": "Message cannot be empty"},
        )

    try:
        chat_service = get_chat_service()

        # Parse conversation_id if provided
        conversation_id: uuid.UUID | None = None
        if request.conversation_id:
            try:
                conversation_id = uuid.UUID(request.conversation_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": "invalid_id", "message": "Invalid conversation ID format"},
                )

        result = await chat_service.process_chat(
            user_id=current_user,
            message=request.message,
            session=session,
            conversation_id=conversation_id,
        )

        return ChatResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            tool_calls=[
                ToolCallResponse(
                    tool=tc["tool"],
                    result=tc.get("result"),
                    error=tc.get("error"),
                )
                for tc in result.get("tool_calls", [])
            ],
        )

    except ChatError as e:
        raise chat_error_to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "message": "Something went wrong. Please try again."},
        ) from e


@router.get("/{user_id}/conversations", response_model=ConversationsListResponse)
async def get_conversations(
    user_id: Annotated[str, Path(description="User ID")],
    current_user: VerifiedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> ConversationsListResponse:
    """Get user's conversations ordered by most recent."""
    chat_service = get_chat_service()
    conversations = await chat_service.get_conversations(
        user_id=current_user,
        session=session,
        limit=limit,
    )

    return ConversationsListResponse(
        conversations=[
            ConversationResponse(
                id=conv["id"],
                user_id=conv["user_id"],
                title=conv["title"],
                created_at=conv["created_at"],
                updated_at=conv["updated_at"],
            )
            for conv in conversations
        ]
    )


@router.get(
    "/{user_id}/conversations/{conversation_id}",
    response_model=ConversationWithMessagesResponse,
)
async def get_conversation(
    user_id: Annotated[str, Path(description="User ID")],
    conversation_id: Annotated[str, Path(description="Conversation ID")],
    current_user: VerifiedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ConversationWithMessagesResponse:
    """Get a specific conversation with its messages."""
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_id", "message": "Invalid conversation ID format"},
        )

    chat_service = get_chat_service()
    result = await chat_service.get_conversation_with_messages(
        user_id=current_user,
        conversation_id=conv_uuid,
        session=session,
        message_limit=limit,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Conversation not found"},
        )

    return ConversationWithMessagesResponse(
        id=result["id"],
        user_id=result["user_id"],
        title=result["title"],
        created_at=result["created_at"],
        updated_at=result["updated_at"],
        messages=[
            MessageResponse(
                id=msg["id"],
                conversation_id=msg["conversation_id"],
                role=msg["role"],
                content=msg["content"],
                tool_calls=[
                    ToolCallResponse(tool=tc["tool"], result=tc.get("result"), error=tc.get("error"))
                    for tc in (msg["tool_calls"] or [])
                ]
                if msg["tool_calls"]
                else None,
                created_at=msg["created_at"],
            )
            for msg in result["messages"]
        ],
    )


@router.delete("/{user_id}/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    user_id: Annotated[str, Path(description="User ID")],
    conversation_id: Annotated[str, Path(description="Conversation ID")],
    current_user: VerifiedUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete a conversation and all its messages."""
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_id", "message": "Invalid conversation ID format"},
        )

    chat_service = get_chat_service()
    deleted = await chat_service.delete_conversation(
        user_id=current_user,
        conversation_id=conv_uuid,
        session=session,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Conversation not found"},
        )


