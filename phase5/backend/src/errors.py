"""Error handling utilities for Phase 3."""

from fastapi import HTTPException, status


class ChatError(Exception):
    """Base exception for chat-related errors."""

    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class AIServiceUnavailableError(ChatError):
    """Raised when OpenAI API is unavailable."""

    def __init__(self, message: str = "AI service is temporarily unavailable. Please try again later."):
        super().__init__(message, "service_unavailable")


class TaskNotFoundError(ChatError):
    """Raised when a task is not found."""

    def __init__(self, task_id: str):
        super().__init__(
            f"I couldn't find task {task_id}. Would you like to see your task list?",
            "task_not_found",
        )


class ConversationNotFoundError(ChatError):
    """Raised when a conversation is not found."""

    def __init__(self, conversation_id: str):
        super().__init__(
            f"Conversation {conversation_id} not found.",
            "conversation_not_found",
        )


class EmptyMessageError(ChatError):
    """Raised when message is empty or whitespace only."""

    def __init__(self):
        super().__init__(
            "I didn't receive a message. Please try again.",
            "empty_message",
        )


class RateLimitError(ChatError):
    """Raised when rate limit is exceeded."""

    def __init__(self):
        super().__init__(
            "You're sending messages too quickly. Please slow down.",
            "rate_limited",
        )


class UnclearMessageError(ChatError):
    """Raised when message intent is unclear."""

    def __init__(self):
        super().__init__(
            "I didn't understand that. Try saying 'add task [title]', 'show my tasks', or 'complete task [number]'.",
            "unclear_message",
        )


def chat_error_to_http_exception(error: ChatError) -> HTTPException:
    """Convert a ChatError to an appropriate HTTPException."""
    status_map = {
        "service_unavailable": status.HTTP_503_SERVICE_UNAVAILABLE,
        "task_not_found": status.HTTP_404_NOT_FOUND,
        "conversation_not_found": status.HTTP_404_NOT_FOUND,
        "empty_message": status.HTTP_400_BAD_REQUEST,
        "rate_limited": status.HTTP_429_TOO_MANY_REQUESTS,
        "unclear_message": status.HTTP_400_BAD_REQUEST,
    }

    return HTTPException(
        status_code=status_map.get(error.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR),
        detail={"error": error.error_code, "message": error.message},
    )


# Friendly error messages for various scenarios
FRIENDLY_ERRORS = {
    "ai_unavailable": "I'm having trouble connecting. Please try again.",
    "task_not_found": "I couldn't find that task. Would you like to see your task list?",
    "invalid_input": "I didn't understand that. Try saying 'add task [title]'.",
    "database_error": "Something went wrong. Please try again in a moment.",
    "rate_limited": "You're sending messages too quickly. Please slow down.",
}
