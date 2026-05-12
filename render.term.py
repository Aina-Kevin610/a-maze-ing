from maze_generator.maze_gen import Maze

class TerminalRender:

    def __init__(self, maze: Maze):
        self.maze = maze

    def draw_cell(self):
        print("--")
        print("|")
