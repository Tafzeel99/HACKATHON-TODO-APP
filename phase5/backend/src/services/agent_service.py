"""OpenRouter Agent service for AI-powered chat.

Uses OpenRouter API which is OpenAI-compatible, allowing use of various LLM models.
"""

import json
import logging
import re
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.errors import AIServiceUnavailableError
from src.mcp.server import get_tool_registry

settings = get_settings()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Agent system instructions - SIMPLIFIED for better model compliance
AGENT_INSTRUCTIONS = """You are a friendly task assistant. Help users manage their todo list.

## YOUR TOOLS
You have these tools - USE THEM:
- add_task: Create a new task
- list_tasks: See all tasks
- update_task: Change a task
- complete_task: Mark task done
- delete_task: Remove a task
- get_analytics: See stats

## CRITICAL RULES

### 1. USE THE RIGHT TOOL
- "Add/create/remind me" → add_task
- "Show/list/what tasks" → list_tasks
- "Done/complete/finished" → complete_task
- "Delete/remove/cancel" → delete_task
- "Change/update/edit" → update_task

### 2. RESPOND NATURALLY
After tools run, respond in plain friendly language like:
- "Done! I've added 'Buy groceries' to your list."
- "You have 3 pending tasks."
- "Task completed!"

### 3. RECURRING TASKS
"Every Monday/week/day" means set recurrence_pattern:
- "every day" → recurrence_pattern="daily"
- "every week" or "every Monday" → recurrence_pattern="weekly"
- "every month" → recurrence_pattern="monthly"

### 4. DELETING TASKS
To delete by title: first call list_tasks to find the task ID, then delete_task.

## EXAMPLES

User: "Add a task to buy groceries"
→ Call add_task(title="Buy groceries")
→ Say: "Added 'Buy groceries' to your list!"

User: "Every Monday I have a meeting with staff"
→ Call add_task(title="Meeting with staff", recurrence_pattern="weekly")
→ Say: "Created recurring task 'Meeting with staff' for every week!"

User: "Show my tasks"
→ Call list_tasks()
→ Say: "You have X tasks: [list them naturally]"

User: "Delete the groceries task"
→ Call list_tasks() to find ID
→ Call delete_task(task_id="...")
→ Say: "Deleted 'Buy groceries' from your list."

User: "Mark task 1 as done"
→ Call complete_task(task_id="...")
→ Say: "Marked as complete!"

## LANGUAGE SUPPORT
Respond in the same language the user uses (English, Roman Urdu, or Urdu script).

Roman Urdu examples:
- "Task add karo" → add_task
- "Mere tasks dikhao" → list_tasks
- "Task complete karo" → complete_task
"""


class AgentService:
    """Service for interacting with LLMs via OpenRouter (OpenAI-compatible API)."""

    def __init__(self) -> None:
        logger.info("Initializing AgentService with OpenRouter...")

        if not settings.open_router_key:
            raise ValueError("OPEN_ROUTER_KEY environment variable is required")

        # Use OpenRouter's OpenAI-compatible API
        self.client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.open_router_key,
        )
        self.model = settings.llm_model
        self.tool_registry = get_tool_registry()

        logger.info(f"AgentService initialized with model: {self.model}")

    def _sanitize_response(self, content: str) -> str:
        """Remove ALL XML/tool call syntax from response content.

        This ensures the user NEVER sees raw tool call syntax.
        """
        if not content:
            return ""

        # Remove <tool_call>...</tool_call> blocks
        content = re.sub(r'<tool_call>.*?</tool_call>', '', content, flags=re.DOTALL)

        # Remove <function=...>...</function> blocks
        content = re.sub(r'<function=\w+>.*?</function>', '', content, flags=re.DOTALL)

        # Remove any remaining <parameter=...>...</parameter> tags
        content = re.sub(r'<parameter=\w+>.*?</parameter>', '', content, flags=re.DOTALL)

        # Remove any stray XML-like tags that might be tool-related
        content = re.sub(r'</?tool_call>', '', content)
        content = re.sub(r'</?function[^>]*>', '', content)
        content = re.sub(r'</?parameter[^>]*>', '', content)

        # Clean up excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()

        return content

    def _detect_intent(self, message: str) -> tuple[str | None, dict[str, Any]]:
        """Detect user intent from message and extract parameters.

        This is a code-level fallback that works with any LLM, even weak ones.
        Returns (tool_name, parameters) or (None, {}) if no clear intent.
        """
        msg = message.lower().strip()

        # Patterns for ADD task
        add_patterns = [
            r"^add\s+(?:a\s+)?(?:task\s+)?(?:to\s+)?(.+)",
            r"^create\s+(?:a\s+)?(?:task\s+)?(?:to\s+)?(.+)",
            r"^remind\s+me\s+(?:to\s+)?(.+)",
            r"^i\s+(?:need|have|want)\s+to\s+(.+)",
            r"^(?:gotta|got\s+to)\s+(.+)",
            r"^don'?t\s+forget\s+(?:to\s+)?(.+)",
            r"^task\s*:?\s*(.+)",
            # Roman Urdu
            r"^task\s+add\s+kar[o]?\s*:?\s*(.+)",
            r"^(.+)\s+add\s+kar[o]?",
            r"^ek\s+(?:naya\s+)?task\s+(?:banana?\s+hai\s+)?(.+)",
        ]

        for pattern in add_patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up the title
                title = re.sub(r'\s+to\s+my\s+list\.?$', '', title, flags=re.IGNORECASE)
                title = title.strip('.,!?')

                params = {"title": title.title() if len(title) < 50 else title}

                # Detect recurrence
                if re.search(r'every\s+(day|daily)', msg, re.IGNORECASE) or 'har roz' in msg:
                    params["recurrence_pattern"] = "daily"
                elif re.search(r'every\s+(week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)', msg, re.IGNORECASE) or 'har hafta' in msg:
                    params["recurrence_pattern"] = "weekly"
                elif re.search(r'every\s+month', msg, re.IGNORECASE) or 'har mahina' in msg:
                    params["recurrence_pattern"] = "monthly"

                # Detect priority
                if re.search(r'urgent|asap|critical|important|zaroori|zaruri', msg, re.IGNORECASE):
                    params["priority"] = "high"
                elif re.search(r'low\s+priority|whenever|no\s+rush', msg, re.IGNORECASE):
                    params["priority"] = "low"

                return ("add_task", params)

        # Patterns for LIST tasks
        list_patterns = [
            r"^show\s+(?:me\s+)?(?:my\s+)?(?:all\s+)?tasks?",
            r"^list\s+(?:my\s+)?(?:all\s+)?tasks?",
            r"^what\s+(?:are\s+)?(?:my\s+)?tasks?",
            r"^(?:my\s+)?tasks?\s*\??$",
            r"^what\s+do\s+i\s+have",
            r"^what'?s\s+pending",
            r"^pending\s+tasks?",
            # Roman Urdu
            r"^(?:mere\s+)?tasks?\s+dikha[o]?",
            r"^kya\s+pending\s+hai",
        ]

        for pattern in list_patterns:
            if re.search(pattern, msg, re.IGNORECASE):
                params = {}
                if "pending" in msg or "incomplete" in msg:
                    params["status"] = "pending"
                elif "completed" in msg or "done" in msg or "finished" in msg:
                    params["status"] = "completed"
                return ("list_tasks", params)

        # Patterns for COMPLETE task
        complete_patterns = [
            r"^(?:mark\s+)?(?:task\s+)?(.+?)\s+(?:as\s+)?(?:done|complete[d]?|finished)",
            r"^complete\s+(?:task\s+)?(.+)",
            r"^(?:i\s+)?(?:did|finished|done\s+with)\s+(.+)",
            r"^task\s+(.+?)\s+ho\s+gaya",
            r"^(.+?)\s+complete\s+kar[o]?",
        ]

        for pattern in complete_patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                task_ref = match.group(1).strip()
                return ("complete_task", {"task_ref": task_ref})

        # Patterns for DELETE task
        delete_patterns = [
            r"^delete\s+(?:the\s+)?(?:task\s+)?(.+)",
            r"^remove\s+(?:the\s+)?(?:task\s+)?(.+)",
            r"^cancel\s+(?:the\s+)?(?:task\s+)?(.+)",
            r"^(?:get\s+rid\s+of|scratch)\s+(.+)",
            r"^task\s+(.+?)\s+(?:delete|hata)\s*(?:kar[o]?|do)?",
            r"^(.+?)\s+(?:delete|hata)\s+kar[o]?",
        ]

        for pattern in delete_patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                task_ref = match.group(1).strip()
                # Check for "all tasks"
                if re.search(r'^all\s+(?:my\s+)?tasks?$', task_ref, re.IGNORECASE):
                    return ("delete_all", {})
                return ("delete_task", {"task_ref": task_ref})

        # Patterns for ANALYTICS
        analytics_patterns = [
            r"^(?:show\s+)?(?:my\s+)?(?:stats|statistics|analytics|progress)",
            r"^how\s+am\s+i\s+doing",
            r"^(?:kitne|how\s+many)\s+tasks?\s+(?:pending|done|completed)",
            r"^mera\s+progress",
        ]

        for pattern in analytics_patterns:
            if re.search(pattern, msg, re.IGNORECASE):
                return ("get_analytics", {})

        # No clear intent detected
        return (None, {})

    def _generate_natural_response(self, tool_calls_results: list[dict[str, Any]]) -> str:
        """Generate a natural language response from tool call results.

        This is more reliable than asking the LLM to generate a response.
        """
        responses = []

        for tc in tool_calls_results:
            tool = tc.get("tool", "")
            result = tc.get("result", {})
            error = tc.get("error")

            if error:
                responses.append(f"Sorry, there was an error: {error}")
                continue

            if tool == "add_task":
                title = result.get("title", "your task")
                task_id = result.get("task_id", "")[:8] if result.get("task_id") else ""
                recurrence = result.get("recurrence_pattern", "none")
                if recurrence and recurrence != "none":
                    responses.append(f"Done! I've added '{title}' as a {recurrence} recurring task.")
                else:
                    responses.append(f"Done! I've added '{title}' to your list.")

            elif tool == "list_tasks":
                tasks = result.get("tasks", [])
                count = result.get("count", len(tasks))
                if count == 0:
                    responses.append("You don't have any tasks right now.")
                else:
                    task_list = []
                    for i, task in enumerate(tasks[:10], 1):  # Limit to 10 tasks
                        status = "completed" if task.get("completed") else "pending"
                        title = task.get("title", "Untitled")
                        priority = task.get("priority", "medium")
                        task_list.append(f"{i}. {title} ({priority}, {status})")
                    tasks_str = "\n".join(task_list)
                    responses.append(f"You have {count} task(s):\n{tasks_str}")

            elif tool == "complete_task":
                title = result.get("title", "task")
                responses.append(f"Marked '{title}' as complete!")
                if result.get("next_task"):
                    next_title = result["next_task"].get("title", "")
                    responses.append(f"Created next recurring task: '{next_title}'")

            elif tool == "delete_task":
                title = result.get("title", "task")
                if result.get("error"):
                    responses.append(f"Couldn't delete: {result.get('message', 'Task not found')}")
                else:
                    responses.append(f"Deleted '{title}' from your list.")

            elif tool == "update_task":
                title = result.get("title", "task")
                responses.append(f"Updated '{title}'.")

            elif tool == "get_analytics":
                summary = result.get("summary", {})
                total = summary.get("total_tasks", 0)
                completed = summary.get("completed_count", 0)
                pending = summary.get("pending_count", 0)
                rate = summary.get("completion_rate", 0)
                responses.append(
                    f"You have {total} total tasks: {completed} completed, {pending} pending. "
                    f"Completion rate: {rate:.0f}%"
                )

        return " ".join(responses) if responses else "Done!"

    def _parse_text_tool_calls(self, content: str) -> list[dict[str, Any]] | None:
        """Parse tool calls from text if model outputs them as text instead of function calls.

        This handles cases where the model outputs <tool_call> XML instead of proper function calls.
        """
        if not content:
            return None
        if "<tool_call>" not in content and "<function=" not in content:
            return None

        tool_calls = []

        # Pattern to match <function=name>...<parameter=key>value</parameter>...</function>
        function_pattern = r'<function=(\w+)>(.*?)</function>'
        param_pattern = r'<parameter=(\w+)>([^<]*)</parameter>'

        for match in re.finditer(function_pattern, content, re.DOTALL):
            func_name = match.group(1)
            func_body = match.group(2)

            params = {}
            for param_match in re.finditer(param_pattern, func_body):
                key = param_match.group(1)
                value = param_match.group(2).strip()
                # Try to parse JSON arrays/objects
                if value.startswith('[') or value.startswith('{'):
                    try:
                        params[key] = json.loads(value)
                    except json.JSONDecodeError:
                        params[key] = value
                else:
                    params[key] = value

            if func_name:
                tool_calls.append({
                    "name": func_name,
                    "arguments": params,  # Can be empty dict
                })
                logger.info(f"Parsed tool call: {func_name} with args: {params}")

        return tool_calls if tool_calls else None

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_history: list[dict[str, str]],
        session: AsyncSession,
    ) -> dict[str, Any]:
        """Process a user message and return AI response with tool calls.

        Args:
            user_id: The user's ID for tool operations
            message: The user's message
            conversation_history: Previous messages in the conversation
            session: Database session for tool operations

        Returns:
            Dict with 'response' (str) and 'tool_calls' (list)
        """
        try:
            # Build messages array
            messages = [
                {"role": "system", "content": AGENT_INSTRUCTIONS},
                *conversation_history,
                {"role": "user", "content": message},
            ]

            # Get available tools
            tools = self.tool_registry.get_tool_schemas()

            logger.info(f"Processing message: {message[:100]}...")
            logger.info(f"Available tools: {[t['function']['name'] for t in tools] if tools else 'None'}")

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                max_tokens=settings.agent_max_tokens,
            )

            assistant_message = response.choices[0].message
            tool_calls_results: list[dict[str, Any]] = []

            logger.info(f"Response has tool_calls: {bool(assistant_message.tool_calls)}")
            logger.info(f"Response content preview: {(assistant_message.content or '')[:200]}")

            # Check if model used proper function calling
            has_proper_tool_calls = bool(assistant_message.tool_calls)

            # Check if model output tool calls as text (fallback)
            text_tool_calls = None
            if not has_proper_tool_calls and assistant_message.content:
                logger.info(f"No proper tool calls, checking for text-based tool calls...")
                logger.info(f"Content contains <tool_call>: {'<tool_call>' in assistant_message.content}")
                logger.info(f"Content contains <function=: {'<function=' in assistant_message.content}")
                text_tool_calls = self._parse_text_tool_calls(assistant_message.content)
                logger.info(f"Parsed text tool calls: {text_tool_calls}")
                if text_tool_calls:
                    logger.warning(f"Model output text-based tool calls, will execute: {text_tool_calls}")

            # Process proper tool calls if any
            if has_proper_tool_calls:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Add user_id and session to tool arguments
                    tool_args["user_id"] = user_id
                    tool_args["session"] = session

                    try:
                        result = await self.tool_registry.execute_tool(tool_name, **tool_args)
                        tool_calls_results.append({
                            "tool": tool_name,
                            "result": result,
                        })
                    except Exception as e:
                        logger.error(f"Tool execution error: {tool_name} - {e}")
                        tool_calls_results.append({
                            "tool": tool_name,
                            "error": str(e),
                        })

                # If tools were called, get final response
                if tool_calls_results:
                    # Add tool results to conversation
                    tool_messages = [
                        {"role": "assistant", "content": None, "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in assistant_message.tool_calls
                        ]},
                    ]

                    for i, tool_call in enumerate(assistant_message.tool_calls):
                        tool_result = tool_calls_results[i]
                        tool_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result.get("result", tool_result.get("error"))),
                        })

                    # Get final response after tool execution
                    final_response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=messages + tool_messages,
                        max_tokens=settings.agent_max_tokens,
                    )
                    final_content = final_response.choices[0].message.content or ""
                else:
                    final_content = assistant_message.content or ""

            # Handle text-based tool calls (fallback for models that don't use function calling)
            elif text_tool_calls:
                logger.info(f"Executing {len(text_tool_calls)} text-based tool calls")

                for tc in text_tool_calls:
                    tool_name = tc["name"]
                    tool_args = tc["arguments"]
                    tool_args["user_id"] = user_id
                    tool_args["session"] = session

                    try:
                        result = await self.tool_registry.execute_tool(tool_name, **tool_args)
                        tool_calls_results.append({
                            "tool": tool_name,
                            "result": result,
                        })
                        logger.info(f"Text tool call {tool_name} succeeded: {result}")
                    except Exception as e:
                        logger.error(f"Text tool call error: {tool_name} - {e}")
                        tool_calls_results.append({
                            "tool": tool_name,
                            "error": str(e),
                        })

                # Generate a natural response based on tool results
                if tool_calls_results:
                    # Generate response programmatically for reliability
                    final_content = self._generate_natural_response(tool_calls_results)
                else:
                    final_content = assistant_message.content or ""
                    if not final_content:
                        final_content = "I tried to process your request but encountered an issue. Please try again."

            else:
                # Model didn't call any tools - use intent detection as fallback
                logger.info("No tool calls detected, trying intent detection...")
                detected_tool, detected_params = self._detect_intent(message)

                if detected_tool:
                    logger.info(f"Intent detected: {detected_tool} with params: {detected_params}")

                    # Handle special cases
                    if detected_tool == "delete_all":
                        # First list all tasks, then delete each
                        list_result = await self.tool_registry.execute_tool(
                            "list_tasks", user_id=user_id, session=session
                        )
                        tasks = list_result.get("tasks", [])
                        deleted_count = 0
                        for task in tasks:
                            try:
                                await self.tool_registry.execute_tool(
                                    "delete_task",
                                    user_id=user_id,
                                    session=session,
                                    task_id=task["id"]
                                )
                                deleted_count += 1
                            except Exception:
                                pass
                        tool_calls_results.append({
                            "tool": "delete_all",
                            "result": {"deleted_count": deleted_count}
                        })
                        final_content = f"Deleted {deleted_count} task(s) from your list."

                    elif detected_tool in ("complete_task", "delete_task") and "task_ref" in detected_params:
                        # Need to resolve task reference to ID
                        task_ref = detected_params["task_ref"]
                        list_result = await self.tool_registry.execute_tool(
                            "list_tasks", user_id=user_id, session=session
                        )
                        tasks = list_result.get("tasks", [])

                        # Find matching task
                        matched_task = None
                        for task in tasks:
                            if task_ref.lower() in task["title"].lower():
                                matched_task = task
                                break

                        if matched_task:
                            try:
                                result = await self.tool_registry.execute_tool(
                                    detected_tool,
                                    user_id=user_id,
                                    session=session,
                                    task_id=matched_task["id"]
                                )
                                tool_calls_results.append({
                                    "tool": detected_tool,
                                    "result": {**result, "title": matched_task["title"]}
                                })
                                final_content = self._generate_natural_response(tool_calls_results)
                            except Exception as e:
                                final_content = f"Sorry, couldn't {detected_tool.replace('_', ' ')}: {e}"
                        else:
                            final_content = f"I couldn't find a task matching '{task_ref}'. Try 'show my tasks' to see your list."

                    else:
                        # Standard tool execution
                        try:
                            detected_params["user_id"] = user_id
                            detected_params["session"] = session
                            result = await self.tool_registry.execute_tool(detected_tool, **detected_params)
                            tool_calls_results.append({
                                "tool": detected_tool,
                                "result": result,
                            })
                            final_content = self._generate_natural_response(tool_calls_results)
                        except Exception as e:
                            logger.error(f"Intent-based tool error: {detected_tool} - {e}")
                            final_content = f"Sorry, something went wrong: {e}"
                else:
                    # No intent detected, use model's response or greeting
                    final_content = assistant_message.content or ""
                    if not final_content or "<" in final_content:
                        # Provide helpful greeting if model output is empty or contains XML
                        final_content = (
                            "Hi! I'm your task assistant. I can help you:\n"
                            "- Add tasks: 'Add a task to buy groceries'\n"
                            "- View tasks: 'Show my tasks'\n"
                            "- Complete tasks: 'Mark buy groceries as done'\n"
                            "- Delete tasks: 'Delete the groceries task'\n\n"
                            "What would you like to do?"
                        )

            # CRITICAL: Always sanitize the final response to remove any XML/tool syntax
            final_content = self._sanitize_response(final_content)

            # If sanitization removed everything, provide a fallback
            if not final_content:
                final_content = "I've processed your request. How can I help you further?"

            return {
                "response": final_content,
                "tool_calls": tool_calls_results,
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Agent service error: {e}")
            logger.error(f"Full traceback:\n{error_details}")

            # Check for specific error types
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                return {
                    "response": "I'm being rate limited. Please wait a moment and try again.",
                    "tool_calls": [],
                }
            elif "invalid api key" in error_str or "401" in error_str:
                return {
                    "response": "There's an issue with the AI configuration. Please contact support.",
                    "tool_calls": [],
                }
            elif "model" in error_str and ("not found" in error_str or "unsupported" in error_str):
                return {
                    "response": "The AI model is unavailable. Please try again later.",
                    "tool_calls": [],
                }

            raise AIServiceUnavailableError() from e


# Global agent service instance
_agent_service: AgentService | None = None


def get_agent_service() -> AgentService:
    """Get or create the global agent service instance."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
