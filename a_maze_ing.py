from maze_gen import Maze
from mlx import Mlx
import sys
from render import Drawing

def main() -> None:
    maze = Maze()
    grid = maze.generate()
    maze.save(grid)

    draw = Drawing(maze, 0xffffffff)
    draw.draw_grid()
    draw.m.mlx_loop(draw.mlx)


if __name__ == "__main__":
    main()
