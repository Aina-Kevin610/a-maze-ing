import random

from maze_gen import Maze
# from render import Menu

from render import DrawingMaze
import sys


def read_maze(filename: str = "maze.txt") -> str:
    try:
        with open(filename, "r") as f:
            return f.read()
    except FileNotFoundError:
        print("Error - OUTPUT_FILE not generated !")
        sys.exit(0)


def loop_hook(param):
    draw = param
    if draw.maze.phase == "done":
        return 
    if not draw.maze.started:
        draw.maze.current_x = random.randint(0, draw.maze.width - 1)
        draw.maze.current_y = random.randint(0, draw.maze.height - 1)
        draw.maze.visited[draw.maze.current_y][draw.maze.current_x] = True
        draw.maze.started = True
    if draw.maze.phase == "kill":
        again = draw.maze.kill()
        if not again:
            draw.maze.phase = "hunt"
    elif draw.maze.phase == "hunt":
        result = draw.maze.hunt()
        if result is None:
            draw.maze.phase = "done"
        else:
            draw.maze.current_x, draw.maze.current_y = result
            draw.maze.phase = "kill"
    draw.draw_maze() 



def main() -> None:
    
    maze = Maze()
    # maze.generate()  # Remove this to allow step-by-step animation
    # hexa_maze = read_maze()  # Not needed for animation
    # hexa_maze = hexa_maze.split("\n")
    draw = DrawingMaze(maze, None, 0xFFFFFFFF)
    draw.draw_maze()
    draw.m.mlx_loop_hook(draw.mlx, loop_hook, draw)
    draw.m.mlx_loop(draw.mlx)
    # menu = Menu()


if __name__ == "__main__":
    main()