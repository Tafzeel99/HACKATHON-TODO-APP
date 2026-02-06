"""Context manager for tracking task references in conversations.

Tracks recently mentioned tasks and resolves pronouns like "it", "that", "the one I mentioned".
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from collections import OrderedDict


@dataclass
class TaskReference:
    """A reference to a task in the conversation."""

    task_id: str
    task_title: str
    mentioned_at: datetime
    mention_type: str  # "created", "listed", "updated", "completed", "deleted"


@dataclass
class ConversationContext:
    """Context for a user's conversation."""

    user_id: str
    task_references: List[TaskReference] = field(default_factory=list)
    last_action: Optional[str] = None
    last_task_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_task_reference(self, task_id: str, task_title: str, mention_type: str) -> None:
        """Add a task reference to the context."""
        ref = TaskReference(
            task_id=task_id,
            task_title=task_title,
            mentioned_at=datetime.now(),
            mention_type=mention_type,
        )
        self.task_references.append(ref)
        self.last_task_id = task_id
        self.last_action = mention_type
        self.updated_at = datetime.now()

        # Keep only the last 10 references
        if len(self.task_references) > 10:
            self.task_references = self.task_references[-10:]

    def get_most_recent_task(self) -> Optional[TaskReference]:
        """Get the most recently mentioned task."""
        if self.task_references:
            return self.task_references[-1]
        return None

    def get_task_by_partial_title(self, partial_title: str) -> Optional[TaskReference]:
        """Find a task reference by partial title match."""
        partial_lower = partial_title.lower()
        for ref in reversed(self.task_references):
            if partial_lower in ref.task_title.lower():
                return ref
        return None

    def clear(self) -> None:
        """Clear the context."""
        self.task_references = []
        self.last_action = None
        self.last_task_id = None


class ContextManager:
    """Manages conversation context for multiple users."""

    # Pronouns and references that indicate the most recent task
    RECENT_TASK_INDICATORS = {
        # English
        "it", "that", "this", "the task", "that task", "this task",
        "the one", "that one", "this one",
        "the one i mentioned", "that one i mentioned",
        "my last task", "the last task", "the last one",
        "the previous task", "the previous one",
        # Roman Urdu
        "wo", "woh", "ye", "yeh",
        "wo task", "ye task",
        "wala", "wali",
        "pichla", "pichla task",
        # Urdu script
        "وہ", "یہ",
    }

    def __init__(self, max_contexts: int = 1000, context_ttl_hours: int = 24):
        """Initialize the context manager.

        Args:
            max_contexts: Maximum number of user contexts to keep in memory
            context_ttl_hours: Hours before a context expires
        """
        self._contexts: OrderedDict[str, ConversationContext] = OrderedDict()
        self._max_contexts = max_contexts
        self._context_ttl = timedelta(hours=context_ttl_hours)

    def get_context(self, user_id: str) -> ConversationContext:
        """Get or create a context for a user."""
        self._cleanup_expired()

        if user_id in self._contexts:
            # Move to end (most recently used)
            self._contexts.move_to_end(user_id)
            return self._contexts[user_id]

        # Create new context
        context = ConversationContext(user_id=user_id)
        self._contexts[user_id] = context

        # Evict oldest if at capacity
        while len(self._contexts) > self._max_contexts:
            self._contexts.popitem(last=False)

        return context

    def record_task_mention(
        self,
        user_id: str,
        task_id: str,
        task_title: str,
        mention_type: str,
    ) -> None:
        """Record that a task was mentioned in the conversation."""
        context = self.get_context(user_id)
        context.add_task_reference(task_id, task_title, mention_type)

    def resolve_task_reference(
        self,
        user_id: str,
        text: str,
    ) -> Optional[TaskReference]:
        """Resolve a task reference from text.

        Args:
            user_id: The user's ID
            text: The text that may contain a task reference

        Returns:
            TaskReference if resolved, None otherwise
        """
        context = self.get_context(user_id)
        text_lower = text.lower()

        # Check for pronouns/indicators that refer to the most recent task
        for indicator in self.RECENT_TASK_INDICATORS:
            if indicator in text_lower:
                return context.get_most_recent_task()

        # Check for partial title match
        # Extract quoted text as potential title
        import re

        quoted_matches = re.findall(r'"([^"]+)"', text)
        for quoted in quoted_matches:
            ref = context.get_task_by_partial_title(quoted)
            if ref:
                return ref

        # Check for task ID mentioned explicitly
        task_id_match = re.search(r"task\s*#?\s*([a-zA-Z0-9-]+)", text_lower)
        if task_id_match:
            task_id = task_id_match.group(1)
            for ref in context.task_references:
                if task_id in ref.task_id.lower():
                    return ref

        return None

    def clear_context(self, user_id: str) -> None:
        """Clear a user's context."""
        if user_id in self._contexts:
            self._contexts[user_id].clear()

    def _cleanup_expired(self) -> None:
        """Remove expired contexts."""
        now = datetime.now()
        expired_keys = [
            key for key, ctx in self._contexts.items()
            if now - ctx.updated_at > self._context_ttl
        ]
        for key in expired_keys:
            del self._contexts[key]


# Global context manager instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get the global context manager instance."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
