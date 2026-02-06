"""Smart task suggestions service.

Provides intelligent task suggestions based on user's task history and patterns.
Enhanced with time estimation, conflict detection, workload balancing, and habit tracking.
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from collections import Counter, defaultdict
import re


@dataclass
class TaskSuggestion:
    """A smart task suggestion."""

    suggestion_type: str  # "priority", "due_date", "tag", "similar", "focus", "time_estimate", "conflict", "workload", "habit"
    message: str
    confidence: float  # 0.0 to 1.0
    data: Optional[Dict[str, Any]] = None


@dataclass
class TimeEstimate:
    """Time estimation for a task based on historical data."""

    estimated_hours: float
    confidence: float
    based_on_count: int  # Number of similar tasks used for estimation
    category: str  # Category of similar tasks


@dataclass
class WorkloadAnalysis:
    """Workload analysis for a date or period."""

    date: datetime
    task_count: int
    high_priority_count: int
    estimated_hours: float
    is_overloaded: bool
    recommendation: str


class SuggestionService:
    """Service for generating smart task suggestions."""

    # Urgency keywords that suggest high priority
    HIGH_PRIORITY_KEYWORDS = {
        # English
        "urgent", "asap", "emergency", "critical", "important",
        "deadline", "due soon", "overdue", "immediately",
        "must", "need to", "have to", "crucial", "vital",
        "priority", "high priority",
        # Roman Urdu
        "zaroori", "zaruri", "fori", "jaldi", "abhi",
        "lazmi", "ahem", "zaroor",
        # Urdu script
        "ضروری", "فوری", "جلدی", "ابھی",
    }

    # Keywords suggesting low priority
    LOW_PRIORITY_KEYWORDS = {
        # English
        "whenever", "someday", "eventually", "if possible",
        "when free", "no rush", "later", "maybe",
        "optional", "nice to have",
        # Roman Urdu
        "jab bhi", "kabi bhi", "baad mein", "phir kabhi",
        # Urdu script
        "جب بھی", "بعد میں",
    }

    # Time-related keywords
    TIME_SENSITIVE_KEYWORDS = {
        "today", "tonight", "this morning", "this afternoon",
        "tomorrow", "next week", "by monday", "by friday",
        "end of day", "eod", "end of week", "eow",
        "aaj", "kal", "آج", "کل",
    }

    def suggest_priority(self, task_title: str, task_description: Optional[str] = None) -> TaskSuggestion:
        """Suggest a priority level based on task content."""
        text = f"{task_title} {task_description or ''}".lower()

        # Check for high priority indicators
        for keyword in self.HIGH_PRIORITY_KEYWORDS:
            if keyword in text:
                return TaskSuggestion(
                    suggestion_type="priority",
                    message=f"This task seems urgent based on '{keyword}'. Suggesting high priority.",
                    confidence=0.85,
                    data={"suggested_priority": "high", "trigger": keyword},
                )

        # Check for low priority indicators
        for keyword in self.LOW_PRIORITY_KEYWORDS:
            if keyword in text:
                return TaskSuggestion(
                    suggestion_type="priority",
                    message=f"This task seems flexible based on '{keyword}'. Suggesting low priority.",
                    confidence=0.75,
                    data={"suggested_priority": "low", "trigger": keyword},
                )

        # Check for time-sensitive keywords (medium-high priority)
        for keyword in self.TIME_SENSITIVE_KEYWORDS:
            if keyword in text:
                return TaskSuggestion(
                    suggestion_type="priority",
                    message=f"This task has a time element. Suggesting medium to high priority.",
                    confidence=0.7,
                    data={"suggested_priority": "medium", "trigger": keyword},
                )

        # Default: medium priority
        return TaskSuggestion(
            suggestion_type="priority",
            message="No specific urgency indicators found. Defaulting to medium priority.",
            confidence=0.5,
            data={"suggested_priority": "medium", "trigger": None},
        )

    def suggest_tags_from_history(
        self,
        task_title: str,
        user_tags_history: List[str],
    ) -> TaskSuggestion:
        """Suggest tags based on user's tag history and task content."""
        if not user_tags_history:
            return TaskSuggestion(
                suggestion_type="tag",
                message="No tag history available for suggestions.",
                confidence=0.0,
                data={"suggested_tags": []},
            )

        # Count tag frequency
        tag_counts = Counter(user_tags_history)
        most_common = tag_counts.most_common(5)

        title_lower = task_title.lower()
        suggested_tags = []

        # Check if any common tags appear in the title
        for tag, count in most_common:
            if tag.lower() in title_lower or any(word in tag.lower() for word in title_lower.split()):
                suggested_tags.append(tag)

        if suggested_tags:
            return TaskSuggestion(
                suggestion_type="tag",
                message=f"Based on your history and task content, consider these tags: {', '.join(suggested_tags)}",
                confidence=0.7,
                data={"suggested_tags": suggested_tags},
            )

        # Fall back to most common tags
        top_tags = [tag for tag, _ in most_common[:3]]
        return TaskSuggestion(
            suggestion_type="tag",
            message=f"Your most used tags are: {', '.join(top_tags)}",
            confidence=0.5,
            data={"suggested_tags": top_tags, "is_fallback": True},
        )

    def suggest_focus_tasks(
        self,
        tasks: List[Dict[str, Any]],
    ) -> TaskSuggestion:
        """Suggest which tasks to focus on today."""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        focus_tasks = []
        overdue_tasks = []
        due_today = []
        high_priority = []

        for task in tasks:
            if task.get("completed"):
                continue

            due_date_str = task.get("due_date")
            priority = task.get("priority", "medium")

            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                    if due_date < today:
                        overdue_tasks.append(task)
                    elif due_date < tomorrow:
                        due_today.append(task)
                except (ValueError, AttributeError):
                    pass

            if priority == "high":
                high_priority.append(task)

        # Build focus list
        # 1. Overdue tasks first
        focus_tasks.extend(overdue_tasks[:2])
        # 2. Due today
        focus_tasks.extend([t for t in due_today if t not in focus_tasks][:2])
        # 3. High priority
        focus_tasks.extend([t for t in high_priority if t not in focus_tasks][:2])

        if not focus_tasks:
            return TaskSuggestion(
                suggestion_type="focus",
                message="No urgent tasks! You're all caught up. Consider working on any pending tasks.",
                confidence=0.5,
                data={"focus_tasks": [], "summary": "all_clear"},
            )

        # Build message
        messages = []
        if overdue_tasks:
            messages.append(f"{len(overdue_tasks)} overdue task(s)")
        if due_today:
            messages.append(f"{len(due_today)} due today")
        if high_priority:
            messages.append(f"{len(high_priority)} high priority")

        focus_titles = [t.get("title", "Unknown") for t in focus_tasks[:3]]

        return TaskSuggestion(
            suggestion_type="focus",
            message=f"Focus on: {', '.join(messages)}. Top tasks: {', '.join(focus_titles)}",
            confidence=0.85,
            data={
                "focus_tasks": focus_tasks[:5],
                "overdue_count": len(overdue_tasks),
                "due_today_count": len(due_today),
                "high_priority_count": len(high_priority),
            },
        )

    def suggest_similar_tasks(
        self,
        new_task_title: str,
        existing_tasks: List[Dict[str, Any]],
        max_suggestions: int = 3,
    ) -> TaskSuggestion:
        """Find similar existing tasks to avoid duplicates."""
        new_words = set(new_task_title.lower().split())

        similar = []
        for task in existing_tasks:
            if task.get("completed"):
                continue

            task_title = task.get("title", "")
            task_words = set(task_title.lower().split())

            # Calculate Jaccard similarity
            intersection = len(new_words & task_words)
            union = len(new_words | task_words)
            if union > 0:
                similarity = intersection / union
                if similarity >= 0.3:  # 30% word overlap threshold
                    similar.append((task, similarity))

        # Sort by similarity
        similar.sort(key=lambda x: x[1], reverse=True)
        top_similar = [t for t, _ in similar[:max_suggestions]]

        if not top_similar:
            return TaskSuggestion(
                suggestion_type="similar",
                message="No similar tasks found. This appears to be a new task.",
                confidence=0.5,
                data={"similar_tasks": []},
            )

        titles = [t.get("title", "Unknown") for t in top_similar]
        return TaskSuggestion(
            suggestion_type="similar",
            message=f"Found similar existing tasks: {', '.join(titles)}. Consider if this is a duplicate.",
            confidence=0.75,
            data={"similar_tasks": top_similar},
        )

    def estimate_time(
        self,
        task_title: str,
        completed_tasks: List[Dict[str, Any]],
    ) -> TaskSuggestion:
        """Estimate time for a task based on similar completed tasks.

        Analyzes completed tasks with similar keywords to provide time estimates.
        Example: "Tasks like this take ~2 hours"
        """
        # Task categories and their typical time ranges (hours)
        TASK_CATEGORIES = {
            "meeting": {"keywords": ["meeting", "call", "sync", "standup"], "avg_hours": 1.0},
            "coding": {"keywords": ["implement", "code", "develop", "fix bug", "build"], "avg_hours": 3.0},
            "review": {"keywords": ["review", "check", "approve", "feedback"], "avg_hours": 0.5},
            "writing": {"keywords": ["write", "document", "draft", "report"], "avg_hours": 2.0},
            "research": {"keywords": ["research", "explore", "investigate", "analyze"], "avg_hours": 2.5},
            "admin": {"keywords": ["email", "invoice", "paperwork", "update"], "avg_hours": 0.5},
            "errands": {"keywords": ["buy", "pick up", "grocery", "shopping"], "avg_hours": 1.0},
            "exercise": {"keywords": ["gym", "workout", "run", "exercise", "yoga"], "avg_hours": 1.0},
            "learning": {"keywords": ["study", "course", "learn", "read", "tutorial"], "avg_hours": 1.5},
        }

        title_lower = task_title.lower()

        # Find matching category
        matched_category = None
        for category, info in TASK_CATEGORIES.items():
            for keyword in info["keywords"]:
                if keyword in title_lower:
                    matched_category = (category, info)
                    break
            if matched_category:
                break

        # Look for similar completed tasks with actual duration data
        similar_durations = []
        new_words = set(title_lower.split())

        for task in completed_tasks:
            if not task.get("completed"):
                continue

            task_title_comp = task.get("title", "").lower()
            task_words = set(task_title_comp.split())

            # Calculate similarity
            intersection = len(new_words & task_words)
            union = len(new_words | task_words)
            similarity = intersection / union if union > 0 else 0

            if similarity >= 0.25:  # 25% word overlap
                # Check if we have duration data
                created = task.get("created_at")
                completed_at = task.get("completed_at") or task.get("updated_at")

                if created and completed_at:
                    try:
                        if isinstance(created, str):
                            created = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        if isinstance(completed_at, str):
                            completed_at = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))

                        duration_hours = (completed_at - created).total_seconds() / 3600
                        # Filter out unrealistic durations (< 5 min or > 24 hours for a single task)
                        if 0.08 <= duration_hours <= 24:
                            similar_durations.append((duration_hours, similarity))
                    except (ValueError, TypeError):
                        pass

        # Calculate weighted average if we have duration data
        if similar_durations:
            total_weight = sum(sim for _, sim in similar_durations)
            weighted_avg = sum(dur * sim for dur, sim in similar_durations) / total_weight
            count = len(similar_durations)

            return TaskSuggestion(
                suggestion_type="time_estimate",
                message=f"Tasks like this take ~{weighted_avg:.1f} hours based on {count} similar completed tasks.",
                confidence=min(0.9, 0.5 + count * 0.1),
                data={
                    "estimated_hours": round(weighted_avg, 1),
                    "based_on_count": count,
                    "category": matched_category[0] if matched_category else "general",
                },
            )

        # Fall back to category-based estimate
        if matched_category:
            category, info = matched_category
            return TaskSuggestion(
                suggestion_type="time_estimate",
                message=f"Based on similar {category} tasks, this might take ~{info['avg_hours']} hours.",
                confidence=0.6,
                data={
                    "estimated_hours": info["avg_hours"],
                    "based_on_count": 0,
                    "category": category,
                },
            )

        # No estimate available
        return TaskSuggestion(
            suggestion_type="time_estimate",
            message="Not enough data to estimate time for this task.",
            confidence=0.0,
            data={"estimated_hours": None, "based_on_count": 0, "category": "unknown"},
        )

    def detect_scheduling_conflicts(
        self,
        new_task_due_date: datetime,
        existing_tasks: List[Dict[str, Any]],
        max_daily_hours: float = 8.0,
    ) -> TaskSuggestion:
        """Detect if adding a task creates scheduling conflicts.

        Checks for:
        - Too many tasks on the same day
        - Overloaded time slots
        - Conflicts with existing high-priority tasks
        """
        # Get all tasks on the same day
        target_date = new_task_due_date.replace(hour=0, minute=0, second=0, microsecond=0)
        next_day = target_date + timedelta(days=1)

        same_day_tasks = []
        for task in existing_tasks:
            if task.get("completed"):
                continue

            due_date_str = task.get("due_date")
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                    due_date = due_date.replace(tzinfo=None)  # Remove tz for comparison
                    if target_date <= due_date < next_day:
                        same_day_tasks.append(task)
                except (ValueError, TypeError):
                    pass

        # Count high priority tasks
        high_priority_count = sum(1 for t in same_day_tasks if t.get("priority") == "high")
        task_count = len(same_day_tasks)

        # Estimate total hours for that day
        estimated_hours = task_count * 1.5  # Default 1.5 hours per task

        # Check for conflicts
        conflicts = []

        if task_count >= 6:
            conflicts.append(f"{task_count} tasks already scheduled")

        if high_priority_count >= 3:
            conflicts.append(f"{high_priority_count} high-priority tasks")

        if estimated_hours > max_daily_hours:
            conflicts.append(f"~{estimated_hours:.0f}h of work (exceeds {max_daily_hours:.0f}h)")

        if conflicts:
            conflict_str = ", ".join(conflicts)
            return TaskSuggestion(
                suggestion_type="conflict",
                message=f"⚠️ Scheduling conflict on {target_date.strftime('%B %d')}: {conflict_str}. Consider a different date.",
                confidence=0.85,
                data={
                    "conflict_date": target_date.isoformat(),
                    "existing_task_count": task_count,
                    "high_priority_count": high_priority_count,
                    "estimated_hours": estimated_hours,
                    "conflicts": conflicts,
                    "alternative_dates": self._suggest_alternative_dates(target_date, existing_tasks),
                },
            )

        return TaskSuggestion(
            suggestion_type="conflict",
            message=f"No scheduling conflicts detected for {target_date.strftime('%B %d')}.",
            confidence=0.9,
            data={
                "conflict_date": None,
                "existing_task_count": task_count,
                "estimated_hours": estimated_hours,
            },
        )

    def _suggest_alternative_dates(
        self,
        target_date: datetime,
        existing_tasks: List[Dict[str, Any]],
        days_to_check: int = 7,
    ) -> List[str]:
        """Find less busy alternative dates."""
        alternatives = []

        for i in range(1, days_to_check + 1):
            check_date = target_date + timedelta(days=i)
            next_day = check_date + timedelta(days=1)

            task_count = 0
            for task in existing_tasks:
                if task.get("completed"):
                    continue
                due_date_str = task.get("due_date")
                if due_date_str:
                    try:
                        due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                        due_date = due_date.replace(tzinfo=None)
                        if check_date <= due_date < next_day:
                            task_count += 1
                    except (ValueError, TypeError):
                        pass

            if task_count < 4:  # Less busy day
                alternatives.append(check_date.strftime("%B %d (%A)"))

            if len(alternatives) >= 3:
                break

        return alternatives

    def analyze_workload(
        self,
        tasks: List[Dict[str, Any]],
        days_ahead: int = 7,
    ) -> TaskSuggestion:
        """Analyze workload distribution over the coming days.

        Example: "You have 8 tasks due Friday - consider spreading them out."
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Group tasks by due date
        tasks_by_date: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for task in tasks:
            if task.get("completed"):
                continue

            due_date_str = task.get("due_date")
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                    due_date = due_date.replace(tzinfo=None)

                    # Only count upcoming days
                    if today <= due_date <= today + timedelta(days=days_ahead):
                        date_key = due_date.strftime("%Y-%m-%d")
                        tasks_by_date[date_key].append(task)
                except (ValueError, TypeError):
                    pass

        # Find overloaded days (more than 5 tasks)
        overloaded_days = []
        total_upcoming = 0

        for date_str, date_tasks in tasks_by_date.items():
            task_count = len(date_tasks)
            total_upcoming += task_count
            high_priority = sum(1 for t in date_tasks if t.get("priority") == "high")

            if task_count >= 5 or high_priority >= 3:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                overloaded_days.append({
                    "date": date_obj,
                    "date_str": date_obj.strftime("%A, %B %d"),
                    "task_count": task_count,
                    "high_priority_count": high_priority,
                })

        if overloaded_days:
            # Sort by task count
            overloaded_days.sort(key=lambda x: x["task_count"], reverse=True)
            busiest = overloaded_days[0]

            return TaskSuggestion(
                suggestion_type="workload",
                message=f"📊 Heavy workload: {busiest['task_count']} tasks due {busiest['date_str']}. Consider spreading tasks across days.",
                confidence=0.85,
                data={
                    "overloaded_days": overloaded_days,
                    "total_upcoming": total_upcoming,
                    "busiest_day": busiest,
                    "avg_per_day": round(total_upcoming / days_ahead, 1) if days_ahead > 0 else 0,
                },
            )

        # Balanced workload
        avg_per_day = round(total_upcoming / days_ahead, 1) if days_ahead > 0 else 0
        return TaskSuggestion(
            suggestion_type="workload",
            message=f"✅ Workload balanced: {total_upcoming} tasks over {days_ahead} days (~{avg_per_day}/day).",
            confidence=0.8,
            data={
                "overloaded_days": [],
                "total_upcoming": total_upcoming,
                "avg_per_day": avg_per_day,
            },
        )

    def track_habits(
        self,
        completed_tasks: List[Dict[str, Any]],
    ) -> TaskSuggestion:
        """Track completion habits and patterns.

        Example: "You complete gym tasks 80% of mornings"
        """
        # Group completions by category and time of day
        category_patterns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        category_totals: Dict[str, int] = defaultdict(int)

        # Category keywords
        CATEGORIES = {
            "gym": ["gym", "workout", "exercise", "fitness", "run", "yoga"],
            "work": ["meeting", "call", "email", "report", "project", "review"],
            "personal": ["shopping", "grocery", "clean", "laundry", "cook"],
            "learning": ["study", "read", "course", "learn", "practice"],
            "health": ["doctor", "dentist", "medicine", "health"],
        }

        for task in completed_tasks:
            if not task.get("completed"):
                continue

            title_lower = task.get("title", "").lower()
            completed_at = task.get("completed_at") or task.get("updated_at")

            if not completed_at:
                continue

            try:
                if isinstance(completed_at, str):
                    completed_at = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))

                # Determine time of day
                hour = completed_at.hour
                if 5 <= hour < 12:
                    time_of_day = "morning"
                elif 12 <= hour < 17:
                    time_of_day = "afternoon"
                elif 17 <= hour < 21:
                    time_of_day = "evening"
                else:
                    time_of_day = "night"

                # Find category
                for category, keywords in CATEGORIES.items():
                    if any(kw in title_lower for kw in keywords):
                        category_patterns[category][time_of_day] += 1
                        category_totals[category] += 1
                        break

            except (ValueError, TypeError):
                pass

        # Find notable patterns (>60% at specific time)
        habits = []
        for category, times in category_patterns.items():
            total = category_totals[category]
            if total < 3:  # Need at least 3 instances
                continue

            for time_of_day, count in times.items():
                percentage = (count / total) * 100
                if percentage >= 60:
                    habits.append({
                        "category": category,
                        "time_of_day": time_of_day,
                        "percentage": round(percentage),
                        "count": count,
                        "total": total,
                    })

        if habits:
            # Sort by percentage
            habits.sort(key=lambda x: x["percentage"], reverse=True)
            top_habit = habits[0]

            messages = [
                f"You complete {h['category']} tasks {h['percentage']}% in the {h['time_of_day']}"
                for h in habits[:3]
            ]

            return TaskSuggestion(
                suggestion_type="habit",
                message="🎯 Habit patterns detected: " + ". ".join(messages) + ".",
                confidence=0.75,
                data={
                    "habits": habits,
                    "strongest_habit": top_habit,
                    "total_analyzed": len(completed_tasks),
                },
            )

        return TaskSuggestion(
            suggestion_type="habit",
            message="📊 Building your habit profile... Complete more tasks to see patterns.",
            confidence=0.3,
            data={
                "habits": [],
                "total_analyzed": len(completed_tasks),
            },
        )

    def get_all_suggestions(
        self,
        task_title: str,
        task_description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        existing_tasks: Optional[List[Dict[str, Any]]] = None,
        completed_tasks: Optional[List[Dict[str, Any]]] = None,
        user_tags_history: Optional[List[str]] = None,
    ) -> List[TaskSuggestion]:
        """Get all relevant suggestions for a task.

        Returns a list of suggestions sorted by confidence.
        """
        suggestions = []
        existing_tasks = existing_tasks or []
        completed_tasks = completed_tasks or []

        # Priority suggestion
        suggestions.append(self.suggest_priority(task_title, task_description))

        # Tag suggestions
        if user_tags_history:
            suggestions.append(self.suggest_tags_from_history(task_title, user_tags_history))

        # Similar task check
        if existing_tasks:
            suggestions.append(self.suggest_similar_tasks(task_title, existing_tasks))

        # Time estimation
        if completed_tasks:
            suggestions.append(self.estimate_time(task_title, completed_tasks))

        # Scheduling conflict detection
        if due_date and existing_tasks:
            suggestions.append(self.detect_scheduling_conflicts(due_date, existing_tasks))

        # Workload analysis
        if existing_tasks:
            suggestions.append(self.analyze_workload(existing_tasks))

        # Habit tracking
        if completed_tasks:
            suggestions.append(self.track_habits(completed_tasks))

        # Sort by confidence (highest first)
        suggestions.sort(key=lambda s: s.confidence, reverse=True)

        return suggestions


# Global service instance
_suggestion_service: Optional[SuggestionService] = None


def get_suggestion_service() -> SuggestionService:
    """Get the global suggestion service instance."""
    global _suggestion_service
    if _suggestion_service is None:
        _suggestion_service = SuggestionService()
    return _suggestion_service
