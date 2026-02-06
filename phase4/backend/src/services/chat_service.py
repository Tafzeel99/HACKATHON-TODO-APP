"""Chat service for handling conversation logic."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Conversation, Message, MessageRole
from src.services.agent_service import get_agent_service


class ChatService:
    """Service for managing chat conversations and messages."""

    def __init__(self) -> None:
        self.agent_service = get_agent_service()

    async def process_chat(
        self,
        user_id: uuid.UUID,
        message: str,
        session: AsyncSession,
        conversation_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        """Process a chat message and return AI response.

        Args:
            user_id: The authenticated user's ID
            message: The user's message
            session: Database session
            conversation_id: Optional existing conversation ID

        Returns:
            Dict with conversation_id, response, and tool_calls
        """
        user_id_str = str(user_id)

        # Get or create conversation
        if conversation_id:
            conversation = await self._get_conversation(session, conversation_id, user_id_str)
            if not conversation:
                # Create new conversation if not found
                conversation = await self._create_conversation(session, user_id_str)
        else:
            conversation = await self._create_conversation(session, user_id_str)

        # Load conversation history
        history = await self._get_conversation_history(session, conversation.id, limit=50)

        # Store user message
        user_message = Message(
            conversation_id=conversation.id,
            user_id=user_id_str,
            role=MessageRole.USER.value,
            content=message,
        )
        session.add(user_message)

        # Process with AI agent
        result = await self.agent_service.process_message(
            user_id=user_id_str,
            message=message,
            conversation_history=history,
            session=session,
        )

        # Store assistant response
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=user_id_str,
            role=MessageRole.ASSISTANT.value,
            content=result["response"],
            tool_calls=result["tool_calls"] if result["tool_calls"] else None,
        )
        session.add(assistant_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()

        await session.commit()

        return {
            "conversation_id": str(conversation.id),
            "response": result["response"],
            "tool_calls": result["tool_calls"],
        }

    async def _get_conversation(
        self,
        session: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: str,
    ) -> Conversation | None:
        """Get a conversation by ID and verify ownership."""
        result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def _create_conversation(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.flush()  # Get the ID
        return conversation

    async def _get_conversation_history(
        self,
        session: AsyncSession,
        conversation_id: uuid.UUID,
        limit: int = 50,
    ) -> list[dict[str, str]]:
        """Get conversation history formatted for OpenAI API."""
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        messages = result.scalars().all()

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def get_conversations(
        self,
        user_id: uuid.UUID,
        session: AsyncSession,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get user's conversations ordered by most recent."""
        user_id_str = str(user_id)
        result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id_str)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        conversations = result.scalars().all()

        return [
            {
                "id": str(conv.id),
                "user_id": conv.user_id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            }
            for conv in conversations
        ]

    async def get_conversation_with_messages(
        self,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        session: AsyncSession,
        message_limit: int = 50,
    ) -> dict[str, Any] | None:
        """Get a conversation with its messages."""
        user_id_str = str(user_id)

        # Get conversation
        conversation = await self._get_conversation(session, conversation_id, user_id_str)
        if not conversation:
            return None

        # Get messages
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(message_limit)
        )
        messages = result.scalars().all()

        return {
            "id": str(conversation.id),
            "user_id": conversation.user_id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {
                    "id": str(msg.id),
                    "conversation_id": str(msg.conversation_id),
                    "role": msg.role,
                    "content": msg.content,
                    "tool_calls": msg.tool_calls,
                    "created_at": msg.created_at.isoformat(),
                }
                for msg in messages
            ],
        }

    async def delete_conversation(
        self,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        session: AsyncSession,
    ) -> bool:
        """Delete a conversation and all its messages."""
        user_id_str = str(user_id)

        conversation = await self._get_conversation(session, conversation_id, user_id_str)
        if not conversation:
            return False

        await session.delete(conversation)
        await session.commit()
        return True


# Global chat service instance
_chat_service: ChatService | None = None


def get_chat_service() -> ChatService:
    """Get or create the global chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
