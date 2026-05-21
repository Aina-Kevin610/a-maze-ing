from maze_generator.maze_gen import Maze
from render import DrawingMaze
import sys
from render_terminal import print_menu


def loop_hook(param):
    draw, rand, maze = param
    try:
        frame = 1

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