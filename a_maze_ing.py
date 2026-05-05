import random
from maze_gen import Maze
from render import DrawingMaze
from render import Menu


def loop_hook(param):
    draw, rand = param
    if draw.maze.phase == "done":
        return 
    if not draw.maze.started:
        draw.maze.current_x = rand.randint(0, draw.maze.width - 1)
        draw.maze.current_y = rand.randint(0, draw.maze.height - 1)
        draw.maze.visited[draw.maze.current_y][draw.maze.current_x] = True
        draw.maze.started = True
    alive = draw.maze.step()
    if not alive:
        draw.maze.save(draw.maze.hexa_maze())
    draw.draw_cell()



def main() -> None:
    
    # menu = Menu()
    maze = Maze()
    draw = DrawingMaze(maze, None, 0xFF000000)
    draw.m.mlx_loop_hook(draw.mlx, loop_hook, [draw, maze.rand])
    draw.m.mlx_loop(draw.mlx)
    draw.maze.generate()
    


if __name__ == "__main__":
    main()