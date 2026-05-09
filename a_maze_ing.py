from maze_generator.maze_gen import Maze
from render import DrawingMaze
from maze_generator.pattern import Pattern


def loop_hook(param):
    draw, rand, maze = param

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


def main() -> None:
    maze = Maze()
    draw = DrawingMaze(maze, None, 0xFF000000)
    draw.saved = False
    draw.m.mlx_loop_hook(draw.mlx, loop_hook, [draw, maze.rand, maze])
    draw.m.mlx_loop(draw.mlx)


if __name__ == "__main__":
    main()