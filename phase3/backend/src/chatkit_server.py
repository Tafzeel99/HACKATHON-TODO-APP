"""ChatKit Server implementation for Phase 3 AI Chatbot.

This module integrates the ChatKit Python SDK with our existing
AgentService to provide a proper ChatKit-compatible backend.
"""

import logging
import uuid
from collections import defaultdict
from datetime import datetime
from typing import AsyncIterator

from chatkit.server import ChatKitServer
from chatkit.store import NotFoundError, Store
from chatkit.types import (
    Attachment,
    AssistantMessageContent,
    AssistantMessageItem,
    Page,
    ThreadItem,
    ThreadItemDoneEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)

from src.services.agent_service import get_agent_service
from src.db import async_session_maker

logger = logging.getLogger(__name__)


class TodoChatKitStore(Store[dict]):
    """In-memory store for ChatKit threads and items.

    This store maintains conversation state in memory for the ChatKit protocol.
    For production, this could be extended to persist to the database.
    """

    def __init__(self):
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, list[ThreadItem]] = defaultdict(list)
        self.attachments: dict[str, Attachment] = {}

    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        if thread_id not in self.threads:
            raise NotFoundError(f"Thread {thread_id} not found")
        return self.threads[thread_id]

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        self.threads[thread.id] = thread

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: dict
    ) -> Page[ThreadMetadata]:
        threads = list(self.threads.values())
        return self._paginate(
            threads,
            after,
            limit,
            order,
            sort_key=lambda t: t.created_at,
            cursor_key=lambda t: t.id,
        )

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: dict
    ) -> Page[ThreadItem]:
        items = self.items.get(thread_id, [])
        return self._paginate(
            items,
            after,
            limit,
            order,
            sort_key=lambda i: i.created_at,
            cursor_key=lambda i: i.id,
        )

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: dict
    ) -> None:
        self.items[thread_id].append(item)

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        items = self.items[thread_id]
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item
                return
        items.append(item)

    async def load_item(self, thread_id: str, item_id: str, context: dict) -> ThreadItem:
        for item in self.items.get(thread_id, []):
            if item.id == item_id:
                return item
        raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")

    async def delete_thread(self, thread_id: str, context: dict) -> None:
        self.threads.pop(thread_id, None)
        self.items.pop(thread_id, None)

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: dict
    ) -> None:
        self.items[thread_id] = [
            item for item in self.items.get(thread_id, []) if item.id != item_id
        ]

    async def save_attachment(self, attachment: Attachment, context: dict) -> None:
        self.attachments[attachment.id] = attachment

    async def load_attachment(self, attachment_id: str, context: dict) -> Attachment:
        if attachment_id not in self.attachments:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        return self.attachments[attachment_id]

    async def delete_attachment(self, attachment_id: str, context: dict) -> None:
        self.attachments.pop(attachment_id, None)

    def _paginate(
        self,
        rows: list,
        after: str | None,
        limit: int,
        order: str,
        sort_key,
        cursor_key,
    ) -> Page:
        sorted_rows = sorted(rows, key=sort_key, reverse=order == "desc")
        start = 0
        if after:
            for idx, row in enumerate(sorted_rows):
                if cursor_key(row) == after:
                    start = idx + 1
                    break
        data = sorted_rows[start : start + limit]
        has_more = start + limit < len(sorted_rows)
        next_after = cursor_key(data[-1]) if has_more and data else None
        return Page(data=data, has_more=has_more, after=next_after)


class TodoChatKitServer(ChatKitServer[dict]):
    """ChatKit server that uses our AgentService for AI responses.

    This integrates the OpenAI Agents SDK with the ChatKit protocol,
    allowing the ChatKit frontend to work with our custom backend.
    """

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Process user message and yield assistant response events.

        This method is called by ChatKit when a user sends a message.
        It uses our existing AgentService to process the message and
        yields ChatKit-compatible response events.
        """
        if input_user_message is None:
            return

        # Extract the user message text
        user_text = ""
        for content in input_user_message.content:
            if hasattr(content, "text"):
                user_text = content.text
                break

        if not user_text:
            return

        # Get user_id from context (set by the endpoint)
        user_id = context.get("user_id", str(uuid.uuid4()))

        # Build conversation history from thread items
        conversation_history: list[dict] = []
        thread_items = self.store.items.get(thread.id, [])
        for item in thread_items:
            if isinstance(item, UserMessageItem):
                for content in item.content:
                    if hasattr(content, "text"):
                        conversation_history.append({
                            "role": "user",
                            "content": content.text,
                        })
                        break
            elif isinstance(item, AssistantMessageItem):
                for content in item.content:
                    if hasattr(content, "text"):
                        conversation_history.append({
                            "role": "assistant",
                            "content": content.text,
                        })
                        break

        try:
            # Get agent service and process the message
            agent_service = get_agent_service()

            # Create a database session for tool operations
            async with async_session_maker() as session:
                result = await agent_service.process_message(
                    user_id=user_id,
                    message=user_text,
                    conversation_history=conversation_history,
                    session=session,
                )
                # Commit any changes made by tool operations (add, update, delete, complete)
                await session.commit()

            # Extract response text
            response_text = result.get("response", "I processed your request.")

            # Yield the assistant message event
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("message", thread, context),
                    created_at=datetime.now(),
                    content=[AssistantMessageContent(text=response_text)],
                ),
            )

        except Exception as e:
            logger.error(f"Error in ChatKit respond: {e}")
            # Yield an error response
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("message", thread, context),
                    created_at=datetime.now(),
                    content=[
                        AssistantMessageContent(
                            text="I'm sorry, I encountered an error processing your request. Please try again."
                        )
                    ],
                ),
            )


# Global ChatKit server instance
_chatkit_store: TodoChatKitStore | None = None
_chatkit_server: TodoChatKitServer | None = None


def get_chatkit_server() -> TodoChatKitServer:
    """Get or create the global ChatKit server instance."""
    global _chatkit_store, _chatkit_server
    if _chatkit_server is None:
        _chatkit_store = TodoChatKitStore()
        _chatkit_server = TodoChatKitServer(store=_chatkit_store)
    return _chatkit_server
