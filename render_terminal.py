import time
import sys


RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
RESET   = "\033[0m"


def loading(mess: str, sec: float):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + 2
    while time.time() < end:
        for f in frames:
            sys.stdout.write(f"\r{CYAN}{f}{RESET} {mess}...")
            sys.stdout.flush()
            time.sleep(sec)
    sys.stdout.write(f"\r{CYAN}✓{RESET} Done!              \n")


def box(msg: str | list[str], label: str, color: str) -> None:
    prefix = "┏━━━━━━━━━━>>>"
    suffix = "<<<"

    if isinstance(msg, str):
        msgs = [msg]
    else:
        msgs = [str(m) for m in msg]

    min_w_header = len(prefix) + len(label) + len(suffix) + 1

    min_w_msg = max((len(m) + 6 for m in msgs), default=0)

    w = max(min_w_header, min_w_msg)

    dashes = "━" * (w - len(prefix) - len(label) - len(suffix) - 1)
    header = f"{prefix}{label}{suffix}{dashes}┓"

    lines = [f"{color}{header}{RESET}"]
    for m in msgs:
        lines.append(f"{color}┃{RESET}  {m:<{w - 6}}  {color}┃{RESET}")
    lines.append(f"{color}┗{'━' * (w - 2)}┛{RESET}")

    print("\n".join(lines))

def print_box(param) -> None:
    maze, mess, label, color = param
    loading("Generating maze", 0.08)
    box(mess, label, color)