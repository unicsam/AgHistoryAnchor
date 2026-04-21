import sys

# Windows UTF-8 Fix
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class UI:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    ORANGE = "\033[38;5;208m"
    RED = "\033[91m"
    BRED = "\033[91;1m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    @staticmethod
    def header(text):
        print(f"\n{UI.BOLD}{UI.BLUE}{'='*80}{UI.RESET}")
        print(f"{UI.BOLD}{UI.BLUE}  {text}{UI.RESET}")
        print(f"{UI.BOLD}{UI.BLUE}{'='*80}{UI.RESET}")

    @staticmethod
    def info(msg): print(f"{UI.BLUE}[i]{UI.RESET} {msg}")
    @staticmethod
    def success(msg): print(f"{UI.GREEN}[✓]{UI.RESET} {msg}")
    @staticmethod
    def warn(msg): print(f"{UI.YELLOW}[⚠]{UI.RESET} {msg}")
    @staticmethod
    def error(msg): print(f"{UI.RED}[✗]{UI.RESET} {msg}")
    @staticmethod
    def sim(msg): print(f"{UI.YELLOW}[SIMULATION]{UI.RESET} {msg}")
