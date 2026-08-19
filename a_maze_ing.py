"""Entry point for the a-maze-ing CLI application.

Parses the configuration file given on the command line, generates
and solves a maze, saves the result, then renders it either in ASCII
mode or in an interactive MLX window depending on the configuration.
"""

import sys
from render.ascii import ascii_render
from render.window_render import window_render
from mazegen import Maze
from render.tui_utils import loading

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)
    maze = Maze(sys.argv[1])
    loading("Generating maze")
    maze.generate()
    loading("Solving maze")
    maze.solve()
    loading("Saving maze")
    maze.save(maze.grid)
    win = False if maze.render == "ASCII" else True
    if win:
        window_render(
            maze.output_file,
            maze.protected,
            bold=maze.bold,
            animation=maze.animation,
            speed=maze.speed,
            config_filename=sys.argv[1],
        )
    else:
        ascii_render(maze.output_file, protected=maze.protected)
