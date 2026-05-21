
# def print_menu(maze) -> None:
#     w = 50
#     border = "═" * (w - 2)

#     def row(label: str, value: str) -> str:
#         content = f"  {label:<18}{value}"
#         return f"║ {content:<{w - 4}} ║"

#     def section(title: str) -> str:
#         return f"╠{'═' * (w - 2)}╣\n║ {title.center(w - 4)} ║"

#     seed_str   = str(maze.seed) if maze.seed is not None else "random"
#     entry_str  = f"({maze.entry[0]}, {maze.entry[1]})"
#     exit_str   = f"({maze.exit[0]}, {maze.exit[1]})"
#     perfect    = "yes" if maze.perfect else "no"
#     pattern    = maze.pattern_ or "none"

#     lines = [
#         f"╔{border}╗",
#         f"║{'A-MAZE-ING'.center(w - 2)}║",
#         section("=== Maze configuration ==="),
#         row("Algorithm :",   maze.algo),
#         row("Size :",        f"{maze.width} x {maze.height}"),
#         row("Entry :",       entry_str),
#         row("Exit :",        exit_str),
#         row("Perfect :",     perfect),
#         row("Pattern :",     pattern),
#         row("Seed :",        seed_str),
#         row("Output file :", maze.output_file),
#         section("=== Controls ==="),
#         row("SPACE","→ change wall color"),
#         row("ENTER","→ regenerate maze"),
#         row("P",  "→ show/hide path"),
#         row("ESC",  "→ quit"),
#         f"╚{border}╝",
#     ]

#     print("\n".join(lines))



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



def print_menu(error: str) -> None:
    loading()
    print("Menu here")