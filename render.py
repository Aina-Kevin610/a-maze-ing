from mlx import Mlx
import sys

class Drawing:
    def __init__(self, maze, color) -> None:
        h_win = 720
        w_win = 1080
        self.m = Mlx()
        self.mlx = self.m.mlx_init()
        self.win =  self.m.mlx_new_window(self.mlx, w_win, h_win, "A-MAZE-ING !")
        if not self.win:
            sys.exit(0)
        self.cell_size_w = w_win // maze.width
        self.cell_size_h = h_win // maze.height
        self.color = color
        self.maze = maze
        self.m.mlx_hook(self.win, 2, 1, self.exit_win, [self])


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


    def exit_win(self, keycode, params):
        if keycode == 65307:
            print("Exited with ESC ...")
            self.m.mlx_destroy_window(self.mlx, self.win)
            self.m.mlx_loop_exit(self.mlx)
        return 0
