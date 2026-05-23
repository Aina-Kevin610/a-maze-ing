from utils import *


def box(msg: str | list[str], label: str, color: str) -> None:
    prefix = "┏━━━━━━━━━━>>>"
    suffix = "<<<━━━━━━━━━━"

    if isinstance(msg, str):
        msgs = [msg]
    else:
        msgs = [str(m) for m in msg]

    min_w_header = len(prefix) + len(label) + len(suffix) + 1

    min_w_msg = max((len(m) + 6 for m in msgs), default=0)

    w = max(min_w_header, min_w_msg)

    dashes = "━" * (w - len(prefix) - len(label) - len(suffix) - 1)
    header = f"{prefix}{label}{suffix}{dashes}┓"

    lines = [f"{color}{header}{reset}"]
    for m in msgs:
        lines.append(f"{color}┃{reset}  {m:<{w - 6}}  {color}┃{reset}")
    lines.append(f"{color}┗{'━' * (w - 2)}┛{reset}")

    print("\n".join(lines))

def print_box(param) -> None:
    mess, label, color = param
    box(mess, label, color)