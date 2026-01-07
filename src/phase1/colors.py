"""
Color and formatting utilities for the Todo Console Application
"""
import sys

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

# Style shortcuts
class Styles:
    HEADER = Colors.BOLD + Colors.BRIGHT_MAGENTA
    SUBHEADER = Colors.BOLD + Colors.BRIGHT_WHITE
    SUCCESS = Colors.BOLD + Colors.GREEN
    ERROR = Colors.BOLD + Colors.RED
    WARNING = Colors.BOLD + Colors.YELLOW
    INFO = Colors.BLUE
    MENU = Colors.BRIGHT_WHITE
    RESET_ALL = Colors.RESET

def supports_color():
    """Check if the terminal supports color output"""
    return sys.stdout.isatty()

def supports_unicode():
    """Check if the terminal supports unicode characters"""
    try:
        # Try to encode some unicode characters
        test_str = "🎉❓✅➕📋✏️🗑️✅⏳📭📊⚠️↩️👋🌟✨📝"
        test_str.encode(sys.stdout.encoding or 'utf-8')
        return True
    except (UnicodeEncodeError, AttributeError):
        return False

def colored(text, color):
    """Apply color to text if terminal supports it"""
    if supports_color():
        # Replace Unicode emojis with ASCII alternatives on systems that don't support them
        if not supports_unicode():
            # Replace common emojis with ASCII equivalents
            replacements = {
                "🎉": "[WELCOME]",
                "❓": "[HELP]",
                "✅": "[DONE]",
                "➕": "[ADD]",
                "📋": "[VIEW]",
                "✏️": "[EDIT]",
                "🗑️": "[DEL]",
                "⏳": "[TODO]",
                "📭": "[EMPTY]",
                "📊": "[COUNT]",
                "⚠️": "[WARN]",
                "↩️": "[CANCEL]",
                "👋": "[BYE]",
                "🌟": "[STAR]",
                "✨": "[SHINE]",
                "📝": "[TASK]",
                "ℹ️": "[INFO]",
                "💡": "[TIP]"
            }
            for emoji, replacement in replacements.items():
                text = text.replace(emoji, replacement)

        return f"{color}{text}{Colors.RESET}"
    return text

def bold(text):
    """Make text bold if terminal supports it"""
    if supports_color():
        return f"{Colors.BOLD}{text}{Colors.RESET}"
    return text

def clear_screen():
    """Clear the terminal screen"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')