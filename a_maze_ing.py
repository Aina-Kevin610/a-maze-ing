from parsing import parse_config
from maze_gen import Maze


if __name__ == "__main__":
    maze = Maze()
    grid = maze.hunt_and_kill()
    # print(grid)
    maze.save(grid)