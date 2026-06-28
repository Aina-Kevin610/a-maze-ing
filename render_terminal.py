from typing import Any

from utils import (  # noqa: F401
    red,
    green,
    yellow,
    bleu,
    magenta,
    cyan,
    reset,
)


def box(msg: str | list[str], label: str, color: str) -> None:
    """
    Print a decorated terminal box around a message.

    Args:
        msg: Message string or list of strings to display.
        label: Label shown in the box header.
        color: ANSI color code applied to the box borders.
    """
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


def print_box(param: Any) -> None:
    """
    Unpack a parameter tuple and call box().

    Args:
        param: A tuple of (message, label, color).
    """
    mess, label, color = param
    box(mess, label, color)
