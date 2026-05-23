import sys
import time


RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
RESET   = "\033[0m"

def loop_hook(param):
    draw, rand, maze = param
    try:
        frame = maze.speed
        for _ in range(frame):
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
                break

        if draw.maze.phase == "done":
            if draw.maze.solve_phase == "idle":
                draw.maze.init_solve()
            if draw.maze.solve_phase not in ("idle", "done"):
                for _ in range(maze.speed - 2):
                    draw.maze.step_solve()
                    if draw.maze.solve_phase == "done":
                        break
            if draw.maze.solve_phase == "done" and not draw.saved:
                draw.maze.solve()
                draw.maze.save(draw.maze.hexa_maze())
                draw.saved = True

        draw.draw_cell()
        return 0
    except Exception as e:
        print("Program interupted - ", e)
        sys.exit(0)


def loading(mess: str, sec: float):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + 2
    while time.time() < end:
        for f in frames:
            sys.stdout.write(f"\r{CYAN}{f}{RESET} {mess}...")
            sys.stdout.flush()
            time.sleep(sec)
    sys.stdout.write(f"\r{CYAN}✓{RESET} Done!              \n")
