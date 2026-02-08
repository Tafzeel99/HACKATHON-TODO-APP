"""Auto-categorization service using LLM for intelligent tag suggestions.

This service analyzes task content and suggests relevant tags
using keyword extraction and LLM-based categorization.
"""

import os
import re
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class TagSuggestion:
    """A suggested tag with confidence score."""

    tag: str
    confidence: float  # 0.0 to 1.0


@dataclass
class CategorizationResult:
    """Result of auto-categorization."""

    suggested_tags: list[TagSuggestion]
    suggested_priority: Optional[str]  # low, medium, high
    reason: str


# Common tags for keyword matching
KEYWORD_TAGS = {
    # Work-related
    "meeting": ["work", "meeting"],
    "call": ["work", "call"],
    "email": ["work", "email"],
    "report": ["work", "report"],
    "deadline": ["work", "urgent"],
    "presentation": ["work", "presentation"],
    "review": ["work", "review"],
    "project": ["work", "project"],

    # Personal
    "gym": ["health", "fitness"],
    "workout": ["health", "fitness"],
    "exercise": ["health", "fitness"],
    "doctor": ["health", "appointment"],
    "dentist": ["health", "appointment"],
    "grocery": ["shopping", "errands"],
    "shopping": ["shopping"],
    "buy": ["shopping"],
    "pick up": ["errands"],
    "pay": ["finance", "bills"],
    "bill": ["finance", "bills"],
    "bank": ["finance"],

    # Home
    "clean": ["home", "chores"],
    "laundry": ["home", "chores"],
    "cook": ["home", "food"],
    "repair": ["home", "maintenance"],
    "fix": ["home", "maintenance"],

    # Learning
    "study": ["learning", "education"],
    "read": ["learning", "reading"],
    "course": ["learning", "education"],
    "learn": ["learning"],
    "practice": ["learning"],

    # Social
    "birthday": ["social", "celebration"],
    "party": ["social"],
    "dinner": ["social", "food"],
    "lunch": ["social", "food"],
    "friend": ["social"],
    "family": ["family"],

    # Urgency indicators
    "urgent": ["urgent"],
    "asap": ["urgent"],
    "important": ["important"],
    "critical": ["urgent", "important"],
}

# Priority keywords
PRIORITY_KEYWORDS = {
    "high": ["urgent", "asap", "critical", "immediately", "today", "deadline", "important", "must", "essential"],
    "low": ["sometime", "eventually", "maybe", "consider", "think about", "when possible", "optional"],
}


def extract_keywords_tags(title: str, description: str | None = None) -> list[TagSuggestion]:
    """Extract tags based on keyword matching.

    Args:
        title: Task title
        description: Optional task description

    Returns:
        List of suggested tags with confidence scores
    """
    text = f"{title} {description or ''}".lower()
    found_tags: dict[str, float] = {}

    for keyword, tags in KEYWORD_TAGS.items():
        if keyword in text:
            for tag in tags:
                # Higher confidence for title matches
                confidence = 0.8 if keyword in title.lower() else 0.6
                if tag in found_tags:
                    found_tags[tag] = max(found_tags[tag], confidence)
                else:
                    found_tags[tag] = confidence

    # Sort by confidence and return top tags
    suggestions = [
        TagSuggestion(tag=tag, confidence=conf)
        for tag, conf in sorted(found_tags.items(), key=lambda x: -x[1])
    ]

    return suggestions[:5]  # Return top 5


def suggest_priority(title: str, description: str | None = None) -> tuple[str | None, float]:
    """Suggest a priority based on keywords.

    Returns:
        Tuple of (priority, confidence) or (None, 0.0) if no suggestion
    """
    text = f"{title} {description or ''}".lower()

    for priority, keywords in PRIORITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                confidence = 0.7 if keyword in title.lower() else 0.5
                return (priority, confidence)

    return (None, 0.0)


async def categorize_with_llm(
    title: str,
    description: str | None = None,
    existing_tags: list[str] | None = None,
) -> CategorizationResult | None:
    """Use LLM to suggest tags for a task.

    Args:
        title: Task title
        description: Optional task description
        existing_tags: List of user's existing tags for consistency

    Returns:
        CategorizationResult or None if LLM call fails
    """
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    common_tags = ", ".join(existing_tags[:20]) if existing_tags else "work, personal, health, finance, shopping, meeting, urgent"

    prompt = f"""Analyze this task and suggest 1-3 relevant tags.
Task: "{title}"
Description: "{description or 'None'}"

Common tags in this system: {common_tags}

Respond with JSON only:
{{"tags": ["tag1", "tag2"], "priority": "medium", "reason": "Brief explanation"}}

Priority should be: low, medium, or high
Prefer existing common tags when appropriate.
"""

    try:
        base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": os.environ.get("CATEGORIZATION_MODEL", "gpt-3.5-turbo"),
                    "messages": [
                        {"role": "system", "content": "You are a task categorization assistant. Respond only with valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 150,
                },
                timeout=10.0,
            )

            if response.status_code != 200:
                return None

            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Parse JSON response
            import json
            # Extract JSON from response (might have markdown code blocks)
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                tags = result.get("tags", [])
                priority = result.get("priority")
                reason = result.get("reason", "")

                suggestions = [
                    TagSuggestion(tag=tag.lower().strip(), confidence=0.85)
                    for tag in tags[:3]
                ]

                return CategorizationResult(
                    suggested_tags=suggestions,
                    suggested_priority=priority if priority in ("low", "medium", "high") else None,
                    reason=reason,
                )

    except Exception as e:
        print(f"LLM categorization failed: {e}")

    return None


async def auto_categorize(
    title: str,
    description: str | None = None,
    existing_tags: list[str] | None = None,
    use_llm: bool = True,
) -> CategorizationResult:
    """Auto-categorize a task using keyword matching and optionally LLM.

    Args:
        title: Task title
        description: Optional task description
        existing_tags: User's existing tags for consistency
        use_llm: Whether to use LLM for categorization

    Returns:
        CategorizationResult with suggested tags and priority
    """
    # Start with keyword-based extraction
    keyword_tags = extract_keywords_tags(title, description)
    suggested_priority, priority_confidence = suggest_priority(title, description)

    # Try LLM categorization if enabled
    if use_llm:
        llm_result = await categorize_with_llm(title, description, existing_tags)

        if llm_result:
            # Merge keyword and LLM suggestions
            all_tags: dict[str, float] = {}

            for tag_sugg in keyword_tags:
                all_tags[tag_sugg.tag] = tag_sugg.confidence

            for tag_sugg in llm_result.suggested_tags:
                if tag_sugg.tag in all_tags:
                    # Boost confidence if both methods agree
                    all_tags[tag_sugg.tag] = min(all_tags[tag_sugg.tag] + 0.15, 1.0)
                else:
                    all_tags[tag_sugg.tag] = tag_sugg.confidence

            merged_suggestions = [
                TagSuggestion(tag=tag, confidence=conf)
                for tag, conf in sorted(all_tags.items(), key=lambda x: -x[1])
            ][:5]

            # Prefer LLM priority if it has one
            final_priority = llm_result.suggested_priority or suggested_priority

            return CategorizationResult(
                suggested_tags=merged_suggestions,
                suggested_priority=final_priority,
                reason=llm_result.reason or "Based on task content analysis",
            )

    # Return keyword-only results
    return CategorizationResult(
        suggested_tags=keyword_tags,
        suggested_priority=suggested_priority,
        reason="Based on keyword matching",
    )
