# Research: Phase 3 - Todo AI Chatbot

**Date**: 2026-01-19
**Feature**: Phase 3 AI Chatbot
**Purpose**: Resolve technical decisions and document research findings

---

## 1. OpenAI Agents SDK Integration

### Decision
Use OpenAI Agents SDK with function calling for natural language task management.

### Rationale
- Official SDK with maintained support
- Built-in function calling for MCP tool integration
- Handles conversation context management
- Streaming support for real-time responses

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| LangChain | More complex, additional abstraction layer not needed |
| Direct OpenAI API | Lacks agent orchestration features |
| Anthropic Claude API | Constitution requires OpenAI Agents SDK for Phase 3 |

### Implementation Approach
```python
from openai_agents import Agent, Runner

agent = Agent(
    name="TodoAssistant",
    instructions="You help users manage their todo tasks...",
    tools=[add_task, list_tasks, complete_task, delete_task, update_task]
)

runner = Runner(agent=agent)
response = await runner.run(messages=conversation_history)
```

---

## 2. MCP Server Architecture

### Decision
Embed MCP server within FastAPI backend as a module (not separate service).

### Rationale
- Simpler deployment for Phase 3
- Direct database access without network overhead
- Easier debugging and testing
- Can be extracted to separate service in Phase 4/5 if needed

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Separate MCP service | Adds deployment complexity, overkill for Phase 3 |
| REST API wrapper | Loses MCP protocol benefits |
| gRPC service | Different protocol, not MCP compliant |

### MCP Tool Structure
```python
from mcp import Tool, ToolResult

@tool
def add_task(user_id: str, title: str, description: str = None) -> ToolResult:
    """Create a new task for the user."""
    # Database operation
    return ToolResult(task_id=task.id, status="created", title=task.title)
```

---

## 3. ChatKit UI Integration

### Decision
Use OpenAI ChatKit with custom backend endpoint integration.

### Rationale
- Official OpenAI UI component library
- Pre-built chat UI with streaming support
- Consistent with OpenAI design patterns
- Reduces frontend development effort

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Custom React chat UI | More development effort, no streaming built-in |
| Vercel AI SDK UI | Good option but ChatKit is constitution requirement |
| Third-party chat widgets | Less customizable, potential vendor lock-in |

### Configuration
```typescript
// ChatKit configuration
const chatConfig = {
  endpoint: '/api/{user_id}/chat',
  headers: {
    Authorization: `Bearer ${token}`
  }
};
```

---

## 4. Conversation State Management

### Decision
Store all conversation state in Neon PostgreSQL database.

### Rationale
- Stateless server architecture (Phase 3 requirement)
- Persistence across server restarts
- Enables horizontal scaling
- Audit trail for conversations

### Database Schema
- `conversations` table: user_id, id, created_at, updated_at
- `messages` table: id, conversation_id, role, content, created_at

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Redis for session state | Violates stateless requirement |
| In-memory cache | Lost on server restart |
| Client-side storage | Security concerns, limited capacity |

---

## 5. Authentication Integration

### Decision
Reuse Phase 2 Better Auth JWT tokens for chat endpoint authentication.

### Rationale
- Consistent authentication across phases
- No additional auth infrastructure needed
- Proven working from Phase 2
- User isolation via user_id in token

### Implementation
```python
@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(403, "Access denied")
    # Process chat...
```

---

## 6. Error Handling Strategy

### Decision
Graceful degradation with user-friendly error messages.

### Error Categories
| Category | Handling |
|----------|----------|
| AI Service Down | "I'm having trouble connecting. Please try again." |
| Task Not Found | "I couldn't find that task. Would you like to see your task list?" |
| Invalid Input | "I didn't understand that. Try saying 'add task [title]'" |
| Database Error | "Something went wrong. Please try again in a moment." |
| Rate Limited | "You're sending messages too quickly. Please slow down." |

### Implementation
```python
try:
    result = await agent.run(message)
except OpenAIError:
    return ChatResponse(response="I'm having trouble connecting. Please try again.")
except TaskNotFoundError:
    return ChatResponse(response="I couldn't find that task...")
```

---

## 7. Natural Language Patterns

### Decision
Define intent recognition patterns for the 5 core operations.

### Intent Mapping
| User Pattern | Detected Intent | MCP Tool |
|--------------|-----------------|----------|
| "add", "create", "remember", "need to" | CREATE | add_task |
| "show", "list", "what's", "see my" | LIST | list_tasks |
| "done", "complete", "finished", "mark" | COMPLETE | complete_task |
| "delete", "remove", "cancel" | DELETE | delete_task |
| "change", "update", "rename", "modify" | UPDATE | update_task |

### Agent Instructions
```
You are a helpful todo assistant. When users:
- Want to add tasks: Use add_task tool
- Want to see tasks: Use list_tasks tool
- Complete tasks: Use complete_task tool
- Remove tasks: Use delete_task tool
- Modify tasks: Use update_task tool

Always confirm actions with friendly responses.
```

---

## 8. Performance Considerations

### Decision
Target < 3 second response time for chat messages.

### Optimization Strategies
1. **Database**: Index on user_id for fast filtering
2. **Conversation Loading**: Limit to last 50 messages for context
3. **Streaming**: Use streaming responses for better perceived performance
4. **Connection Pooling**: Reuse database connections

### Benchmarks
| Operation | Target |
|-----------|--------|
| Database query | < 50ms |
| Agent processing | < 2500ms |
| Total response | < 3000ms |

---

## Summary

All technical decisions align with:
- ✅ Constitution requirements (Phase 3 technology stack)
- ✅ Stateless architecture principle
- ✅ Production quality standards
- ✅ Security best practices

Ready to proceed with data model and contract generation.
