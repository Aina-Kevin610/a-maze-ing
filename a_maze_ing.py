import random
from maze_gen import Maze
from render import DrawingMaze


def loop_hook(param):
    draw = param
    if draw.maze.phase == "done":
        return 
    if not draw.maze.started:
        draw.maze.current_x = random.randint(0, draw.maze.width - 1)
        draw.maze.current_y = random.randint(0, draw.maze.height - 1)
        draw.maze.visited[draw.maze.current_y][draw.maze.current_x] = True
        draw.maze.started = True
    alive = draw.maze.step()
    if not alive:
        draw.maze.save(draw.maze.hexa_maze())
    draw.draw_cell()



def main() -> None:
    
    maze = Maze()
    draw = DrawingMaze(maze, None, 0xFF000000)
    draw.m.mlx_loop_hook(draw.mlx, loop_hook, draw)
    draw.m.mlx_loop(draw.mlx)
    # menu = Menu()


if __name__ == "__main__":
    main()