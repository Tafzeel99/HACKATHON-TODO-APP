"""Natural language date parsing utility.

Supports English, Roman Urdu, and Urdu date expressions.
"""

import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional


@dataclass
class DateParseResult:
    """Result of date parsing."""

    date: Optional[datetime]
    original_text: str
    confidence: float  # 0.0 to 1.0


# Day name mappings
DAY_NAMES = {
    # English
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
    # Roman Urdu
    "peer": 0, "pir": 0, "somwar": 0,
    "mangal": 1,
    "budh": 2,
    "jumerat": 3, "jumeraat": 3,
    "juma": 4, "jumma": 4,
    "hafta": 5, "saneechar": 5, "sanichar": 5,
    "itwar": 6, "itwaar": 6,
}

# Relative date expressions
RELATIVE_DATES = {
    # English
    "today": 0, "tod": 0,
    "tomorrow": 1, "tmrw": 1, "tmr": 1, "tom": 1,
    "day after tomorrow": 2,
    "yesterday": -1,
    # Roman Urdu
    "aaj": 0, "aj": 0,
    "kal": 1,  # Note: "kal" means both tomorrow and yesterday in context
    "parson": 2, "parso": 2,
    "agla din": 1,
    # Urdu script
    "آج": 0,
    "کل": 1,
    "پرسوں": 2,
}

# Week expressions
WEEK_EXPRESSIONS = {
    # English
    "next week": 7,
    "this week": 0,
    "in a week": 7,
    "in 2 weeks": 14,
    "in two weeks": 14,
    "end of week": None,  # Special handling
    "end of month": None,  # Special handling
    "next quarter": None,  # Special handling
    # Roman Urdu
    "aglay hafta": 7, "aglay hafte": 7, "agli week": 7,
    "is hafta": 0, "is hafte": 0,
    # Urdu script
    "اگلے ہفتے": 7,
    "اس ہفتے": 0,
}

# Time of day expressions
TIME_OF_DAY = {
    "morning": (9, 0),
    "afternoon": (14, 0),
    "evening": (18, 0),
    "night": (21, 0),
    "noon": (12, 0),
    "midnight": (0, 0),
    # Roman Urdu
    "subah": (9, 0),
    "dopehar": (14, 0),
    "shaam": (18, 0),
    "raat": (21, 0),
}


def _get_next_weekday(target_weekday: int, from_date: Optional[datetime] = None) -> datetime:
    """Get the next occurrence of a weekday."""
    if from_date is None:
        from_date = datetime.now()

    days_ahead = target_weekday - from_date.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7

    return from_date + timedelta(days=days_ahead)


def parse_natural_date(text: str, reference_date: Optional[datetime] = None) -> DateParseResult:
    """Parse natural language date expressions.

    Args:
        text: The text containing a date expression
        reference_date: The reference date for relative expressions (defaults to now)

    Returns:
        DateParseResult with the parsed date or None if no date found

    Examples:
        - "tomorrow" -> next day
        - "kal" -> next day (Roman Urdu)
        - "next Monday" -> upcoming Monday
        - "aglay hafta" -> next week (Roman Urdu)
        - "in 3 days" -> 3 days from now
    """
    if reference_date is None:
        reference_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    text_lower = text.lower().strip()
    original_text = text

    # Check for end of week/month/quarter
    if "end of week" in text_lower:
        # End of week = Sunday
        days_until_sunday = 6 - reference_date.weekday()
        if days_until_sunday < 0:
            days_until_sunday = 0
        result_date = reference_date + timedelta(days=days_until_sunday)
        return DateParseResult(date=result_date.replace(hour=23, minute=59), original_text=original_text, confidence=0.9)

    if "end of month" in text_lower:
        # Last day of current month
        import calendar
        last_day = calendar.monthrange(reference_date.year, reference_date.month)[1]
        result_date = reference_date.replace(day=last_day, hour=23, minute=59)
        return DateParseResult(date=result_date, original_text=original_text, confidence=0.9)

    if "next quarter" in text_lower:
        # First day of next quarter
        current_quarter = (reference_date.month - 1) // 3
        next_quarter_month = ((current_quarter + 1) % 4) * 3 + 1
        next_quarter_year = reference_date.year if next_quarter_month > reference_date.month else reference_date.year + 1
        result_date = datetime(next_quarter_year, next_quarter_month, 1)
        return DateParseResult(date=result_date, original_text=original_text, confidence=0.85)

    # Check for relative dates
    for pattern, days in RELATIVE_DATES.items():
        if pattern in text_lower:
            result_date = reference_date + timedelta(days=days)
            return DateParseResult(date=result_date, original_text=original_text, confidence=0.95)

    # Check for week expressions
    for pattern, days in WEEK_EXPRESSIONS.items():
        if pattern in text_lower:
            result_date = reference_date + timedelta(days=days)
            return DateParseResult(date=result_date, original_text=original_text, confidence=0.9)

    # Check for "next <day>" pattern
    next_patterns = [
        r"next\s+(\w+)",
        r"agla\s+(\w+)",
        r"agli\s+(\w+)",
        r"agle\s+(\w+)",
    ]

    for pattern in next_patterns:
        match = re.search(pattern, text_lower)
        if match:
            day_name = match.group(1)
            if day_name in DAY_NAMES:
                target_weekday = DAY_NAMES[day_name]
                result_date = _get_next_weekday(target_weekday, reference_date)
                return DateParseResult(date=result_date, original_text=original_text, confidence=0.9)

    # Check for "this <day>" pattern
    this_patterns = [
        r"this\s+(\w+)",
        r"is\s+(\w+)",
        r"ye\s+(\w+)",
    ]

    for pattern in this_patterns:
        match = re.search(pattern, text_lower)
        if match:
            day_name = match.group(1)
            if day_name in DAY_NAMES:
                target_weekday = DAY_NAMES[day_name]
                days_diff = target_weekday - reference_date.weekday()
                if days_diff < 0:
                    days_diff = 0  # If the day has passed, use today
                result_date = reference_date + timedelta(days=days_diff)
                return DateParseResult(date=result_date, original_text=original_text, confidence=0.85)

    # Check for "in X days" pattern
    in_days_patterns = [
        r"in\s+(\d+)\s*days?",
        r"(\d+)\s*days?\s+(?:from now|later)",
        r"(\d+)\s*din\s*(?:baad|mein)?",
        r"(\d+)\s*دن",
    ]

    for pattern in in_days_patterns:
        match = re.search(pattern, text_lower)
        if match:
            days = int(match.group(1))
            result_date = reference_date + timedelta(days=days)
            return DateParseResult(date=result_date, original_text=original_text, confidence=0.9)

    # Check for standalone day names
    for day_name, weekday in DAY_NAMES.items():
        if re.search(rf"\b{re.escape(day_name)}\b", text_lower):
            result_date = _get_next_weekday(weekday, reference_date)
            return DateParseResult(date=result_date, original_text=original_text, confidence=0.7)

    # Check for ISO date format
    iso_pattern = r"(\d{4})-(\d{1,2})-(\d{1,2})"
    match = re.search(iso_pattern, text)
    if match:
        try:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            result_date = datetime(year, month, day)
            return DateParseResult(date=result_date, original_text=original_text, confidence=1.0)
        except ValueError:
            pass

    # Check for common date format (MM/DD or DD/MM)
    date_pattern = r"(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?"
    match = re.search(date_pattern, text)
    if match:
        try:
            num1, num2 = int(match.group(1)), int(match.group(2))
            year = int(match.group(3)) if match.group(3) else reference_date.year
            if year < 100:
                year += 2000
            # Assume MM/DD format for US, but be flexible
            if num1 <= 12:
                result_date = datetime(year, num1, num2)
            else:
                result_date = datetime(year, num2, num1)  # DD/MM
            return DateParseResult(date=result_date, original_text=original_text, confidence=0.8)
        except ValueError:
            pass

    # No date found
    return DateParseResult(date=None, original_text=original_text, confidence=0.0)


def format_date_for_display(date: datetime) -> str:
    """Format a date for display."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    diff = (date.replace(hour=0, minute=0, second=0, microsecond=0) - today).days

    if diff == 0:
        return "today"
    elif diff == 1:
        return "tomorrow"
    elif diff == -1:
        return "yesterday"
    elif 0 < diff <= 7:
        return date.strftime("%A")  # Day name
    else:
        return date.strftime("%B %d, %Y")


def parse_time_from_text(text: str) -> tuple[int, int] | None:
    """Parse time from natural language text.

    Returns:
        Tuple of (hour, minute) or None if no time found

    Examples:
        - "3pm" -> (15, 0)
        - "3:30 pm" -> (15, 30)
        - "morning" -> (9, 0)
        - "at 14:00" -> (14, 0)
    """
    text_lower = text.lower().strip()

    # Check for time of day expressions
    for expr, (hour, minute) in TIME_OF_DAY.items():
        if expr in text_lower:
            return (hour, minute)

    # Check for explicit time patterns
    time_patterns = [
        # 12-hour format with am/pm
        r"(\d{1,2}):?(\d{2})?\s*(am|pm|a\.m\.|p\.m\.)",
        # 24-hour format
        r"(\d{1,2}):(\d{2})",
        # Just hour with am/pm
        r"(\d{1,2})\s*(am|pm|a\.m\.|p\.m\.)",
    ]

    for pattern in time_patterns:
        match = re.search(pattern, text_lower)
        if match:
            groups = match.groups()

            if len(groups) == 3:  # 12-hour format with minutes
                hour = int(groups[0])
                minute = int(groups[1]) if groups[1] else 0
                is_pm = 'p' in groups[2].lower()

                if is_pm and hour != 12:
                    hour += 12
                elif not is_pm and hour == 12:
                    hour = 0

                return (hour, minute)

            elif len(groups) == 2:
                if groups[1] and groups[1].isdigit():
                    # 24-hour format
                    return (int(groups[0]), int(groups[1]))
                else:
                    # Hour with am/pm
                    hour = int(groups[0])
                    is_pm = 'p' in groups[1].lower() if groups[1] else False

                    if is_pm and hour != 12:
                        hour += 12
                    elif not is_pm and hour == 12:
                        hour = 0

                    return (hour, 0)

    return None


def parse_date_and_time(text: str, reference_date: Optional[datetime] = None) -> DateParseResult:
    """Parse both date and time from natural language text.

    Args:
        text: The text containing date and/or time expression
        reference_date: The reference date for relative expressions

    Returns:
        DateParseResult with combined date and time
    """
    if reference_date is None:
        reference_date = datetime.now().replace(second=0, microsecond=0)

    # First, parse the date
    date_result = parse_natural_date(text, reference_date.replace(hour=0, minute=0))

    if date_result.date is None:
        return date_result

    # Then, try to parse time
    time_result = parse_time_from_text(text)

    if time_result:
        hour, minute = time_result
        result_date = date_result.date.replace(hour=hour, minute=minute)
        # Slightly increase confidence if we found both date and time
        confidence = min(date_result.confidence + 0.05, 1.0)
        return DateParseResult(date=result_date, original_text=date_result.original_text, confidence=confidence)

    return date_result
