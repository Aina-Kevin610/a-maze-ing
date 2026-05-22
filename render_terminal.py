import time
import sys


RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
RESET   = "\033[0m"


def loading():
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + 2
    while time.time() < end:
        for f in frames:
            sys.stdout.write(f"\r{CYAN}{f}{RESET} Generating maze...")
            sys.stdout.flush()
            time.sleep(0.08)
    sys.stdout.write(f"\r{CYAN}✓{RESET} Done!              \n")


def box(msg: str | list[str], label: str, color: str) -> None:
    w = 50
    prefix = "┏━━━━━━━━━━>>>"
    suffix = "<<<"
    dashes = "━" * (w - len(prefix) - len(label) - len(suffix) - 1)
    header = f"{prefix}{label}{suffix}{dashes}┓"

    if isinstance(msg, str):
        msgs = [msg]
    else:
        msgs = msg

    lines = [f"{color}{header}{RESET}"]
    for m in msgs:
        lines.append(f"{color}┃{RESET}  {m:<{w - 6}}  {color}┃{RESET}")
    lines.append(f"{color}┗{'━' * (w - 2)}┛{RESET}")

    print("\n".join(lines))

def print_box(maze, param) -> None:
    mess, label, color = param
    loading()
    box(mess, label, color)