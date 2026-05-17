from maze_generator.maze_gen import Maze
from render import DrawingMaze
import sys


def loop_hook(param):
    draw, rand, maze = param
    try:
        if maze.algo == "hunt_and_kill":
            if draw.maze.phase != "done":
                if not draw.maze.started:
                    draw.maze.current_x = rand.randint(0, draw.maze.width - 1)
                    draw.maze.current_y = rand.randint(0, draw.maze.height - 1)
                    draw.maze.visited[draw.maze.current_y][draw.maze.current_x] = True
                    draw.maze.started = True
                alive = draw.maze.step()
                if not alive:
                    draw.maze.save(draw.maze.hexa_maze())
        elif maze.algo == "prim":
            if draw.maze.phase != "done":
                if not draw.maze.started:
                    draw.maze.init_prim()
                    draw.maze.started = True
                alive = draw.maze.step_prim()
                if not alive:
                    draw.maze.save(draw.maze.hexa_maze())
        elif maze.algo == "backtracking" or maze.algo == "DFS":
            if draw.maze.phase != "done":
                if not draw.maze.started:
                    draw.maze.init_backtracking()
                    draw.maze.started = True
                alive = draw.maze.step_backtracking()
                if not alive:
                    draw.maze.save(draw.maze.hexa_maze())
        if draw.maze.phase == "done":
            if draw.maze.solve_phase == "idle":
                draw.maze.init_solve()
            if draw.maze.solve_phase not in ("idle", "done"):
                draw.maze.step_solve()
            if draw.maze.solve_phase == "done" and not draw.saved:
                draw.maze.solve()
                draw.maze.save(draw.maze.hexa_maze())
                draw.saved = True
        draw.draw_cell()
        return 0
    except Exception as e:
        print("Program interupted - ", e)
        sys.exit(0)


def print_menu(maze) -> None:
    w = 50
    border = "═" * (w - 2)

    def row(label: str, value: str) -> str:
        content = f"  {label:<18}{value}"
        return f"║ {content:<{w - 4}} ║"

    def section(title: str) -> str:
        return f"╠{'═' * (w - 2)}╣\n║ {title.center(w - 4)} ║"

    seed_str   = str(maze.seed) if maze.seed is not None else "random"
    entry_str  = f"({maze.entry[0]}, {maze.entry[1]})"
    exit_str   = f"({maze.exit[0]}, {maze.exit[1]})"
    perfect    = "yes" if maze.perfect else "no"
    pattern    = maze.pattern_ or "none"

    lines = [
        f"╔{border}╗",
        f"║{'A-MAZE-ING'.center(w - 2)}║",
        section("=== Maze configuration ==="),
        row("Algorithm :",   maze.algo),
        row("Size :",        f"{maze.width} x {maze.height}"),
        row("Entry :",       entry_str),
        row("Exit :",        exit_str),
        row("Perfect :",     perfect),
        row("Pattern :",     pattern),
        row("Seed :",        seed_str),
        row("Output file :", maze.output_file),
        section("=== Controls ==="),
        row("SPACE","→ change wall color"),
        row("ENTER","→ regenerate maze"),
        row("P",  "→ show/hide path"),
        row("ESC",  "→ quit"),
        f"╚{border}╝",
    ]

    print("\n".join(lines))

def main() -> None:
    try:
        maze = Maze()
        draw = DrawingMaze(maze, None, 0xFF000000)
        draw.saved = False
        draw.m.mlx_loop_hook(draw.mlx, loop_hook, [draw, maze.rand, maze])
        print_menu(maze)
        draw.m.mlx_loop(draw.mlx)
    except KeyboardInterrupt as e:
        print("Program interupted - ", e)
        sys.exit(0)
    except Exception as e:
        print("Program interupted - ", e)
        sys.exit(0)
    except EOFError as e:
        print("Program interupted - ", e)
        sys.exit(0)


if __name__ == "__main__":
    main()