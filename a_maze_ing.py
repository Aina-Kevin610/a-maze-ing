from maze_generator.maze_gen import Maze
from render import DrawingMaze
import sys
from render_terminal import print_box
from utils import *


def main() -> None:
    try:
        maze = Maze()
        mess_menu = [
            "P          show/hide path",
            "Enter      regenerate",
            "Space      change wall color",
            "ESC        quit",
        ]

        mess_info = [
            f"Algorithm  {maze.algo}",
            f"Size       {maze.width} x {maze.height}",
            f"Entry      {maze.entry[0]}, {maze.entry[1]}",
            f"Exit       {maze.exit[0]}, {maze.exit[1]}",
            f"Speed      {maze.speed}",
            f"Seed       {maze.seed}",
            f"Perfect    {maze.perfect}",
            f"Output     {maze.output_file}",
        ]
        draw = DrawingMaze(maze, None, 0xFF000000)
        loading("Generating maze", 0.08)
        draw.saved = False
        draw.m.mlx_loop_hook(draw.mlx, loop_hook, [draw, maze.rand, maze])
        print_box([mess_menu, "menu", green])
        print_box([mess_info, "info", cyan])
        draw.m.mlx_loop(draw.mlx)
    except KeyboardInterrupt as e:
        print_box(["Program interupted - " + e, "faillure", yellow])
        sys.exit(0)
    except Exception as e:
        print_box([f"Program interupted - {e}" , "faillure", yellow])
        sys.exit(0)
    except EOFError as e:
        print_box(["Program interupted - " + e, "faillure", yellow])
        sys.exit(0)


if __name__ == "__main__":
    main()