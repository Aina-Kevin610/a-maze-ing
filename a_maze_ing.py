from maze_gen import Maze
from mlx import Mlx
import sys


class Drawing:
    def __init__(self, maze, m, mlx, win, cell_size_w, cell_size_h, color) -> None:
        self.m = m
        self.mlx = mlx
        self.win = win
        self.cell_size_w = cell_size_w
        self.cell_size_h = cell_size_h
        self.color = color
        self.maze = maze


    def draw_line_h(self, x0, x1, y) -> None:
        for x in range(x0, x1):
            self.m.mlx_pixel_put(self.mlx, self.win, x, y, self.color)


    def draw_line_v(self, x, y0, y1) -> None:
        for y in range(y0, y1):
            self.m.mlx_pixel_put(self.mlx, self.win, x, y, self.color)

    
    def draw_cell(self, x, y) -> None:
        self.draw_line_h(x, x + self.cell_size_w, y)
        self.draw_line_h(x, x + self.cell_size_w, y + self.cell_size_h)
        self.draw_line_v(x, y, y + self.cell_size_h)
        self.draw_line_v(x + self.cell_size_w, y, y + self.cell_size_h)
        

    def draw_grid(self) -> None:
        i = 0
        x, y = 0, 0
        while i < self.maze.height:
            j = 0
            x = 0
            while j < self.maze.width:
                self.draw_cell(x, y)
                j += 1
                x += self.cell_size_w
            y += self.cell_size_h
            i += 1


def exit_win(keycode, params):
    m, mlx, win = params
    if keycode == 65307:
        print("Exited with ESC ...")
        m.mlx_destroy_window(mlx, win)
        m.mlx_loop_exit(mlx)
    return 0

        
def main() -> None:
    maze = Maze()
    grid = maze.generate()
    maze.save(grid)
    h_win = 720
    w_win = 720
    cell_size_w = w_win // maze.width
    cell_size_h= h_win // maze.height
    m = Mlx()
    mlx = m.mlx_init()
    if not mlx:
        sys.exit(0)
    win = m.mlx_new_window(mlx, w_win, h_win, "A-MAZE-ING !")
    if not win:
        sys.exit(0)
    draw = Drawing(maze, m, mlx, win, cell_size_w, cell_size_h, 0xffffffff)
    draw.draw_grid()

    m.mlx_hook(win, 2, 1, exit_win, [m, mlx, win])
    m.mlx_loop(mlx)


if __name__ == "__main__":
    main()
