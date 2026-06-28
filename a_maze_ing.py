import sys
from utils import *
from render import DrawingMaze
from maze_generator.maze_gen import Maze
from render_terminal import print_box


def main() -> None:
    """
        Initialize and run the maze generator application.
        This function:
            - Creates a maze instance.
            - Displays configuration information.
            - Creates the graphical renderer.
            - Starts maze generation.
            - Registers MLX event hooks.
            - Launches the graphical event loop.
        Raises:
            KeyboardInterrupt: If the program is interrupted by the user.
            EOFError: If an unexpected end-of-file condition occurs.
            Exception: For any other unexpected runtime error.
    """
    try:
        maze = Maze(filename=sys.argv[1])
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
        print_box(["Program interupted - ", e, "faillure", yellow])
        sys.exit(0)
    except Exception as e:
        print_box([f"Program interupted - {e}" , "faillure", yellow])
        sys.exit(0)
    except BaseException as e:
        print_box(["Program interupted - ", e, "faillure", yellow])
        sys.exit(0)


if __name__ == "__main__":
    main()
