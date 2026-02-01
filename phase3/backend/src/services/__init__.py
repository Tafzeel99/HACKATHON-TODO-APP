"""Phase 3 services."""

from src.services.agent_service import AgentService, get_agent_service
from src.services.chat_service import ChatService, get_chat_service
from src.services.context_manager import (
    ContextManager,
    ConversationContext,
    TaskReference,
    get_context_manager,
)
from src.services.suggestions import (
    SuggestionService,
    TaskSuggestion,
    TimeEstimate,
    WorkloadAnalysis,
    get_suggestion_service,
)
from src.services.auto_categorizer import (
    CategorizationResult,
    TagSuggestion,
    auto_categorize,
    categorize_with_llm,
    extract_keywords_tags,
    suggest_priority,
)

__all__ = [
    # Agent & Chat
    "AgentService",
    "ChatService",
    "get_agent_service",
    "get_chat_service",
    # Context
    "ContextManager",
    "ConversationContext",
    "TaskReference",
    "get_context_manager",
    # Suggestions
    "SuggestionService",
    "TaskSuggestion",
    "TimeEstimate",
    "WorkloadAnalysis",
    "get_suggestion_service",
    # Auto-categorization
    "CategorizationResult",
    "TagSuggestion",
    "auto_categorize",
    "categorize_with_llm",
    "extract_keywords_tags",
    "suggest_priority",
]
