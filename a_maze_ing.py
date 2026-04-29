from maze_gen import Maze
from render import DrawingMaze
import sys


def read_maze(filename: str = "maze.txt") -> str:
    try:
        with open(filename, "r") as f:
            return f.read()
    except FileNotFoundError:
        print("Error - OUTPUT_FILE not generated !")
        sys.exit(0)


def main() -> None:
    
    maze = Maze()
    grid = maze.generate()
    maze.save(grid)
    hexa_maze = read_maze()
    hexa_maze = hexa_maze.split("\n")
    draw = DrawingMaze(maze, hexa_maze, 0xffffffff)
    draw.draw_maze()
    draw.m.mlx_loop(draw.mlx)


if __name__ == "__main__":
    main()