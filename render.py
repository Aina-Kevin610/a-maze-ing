from mlx import Mlx
import sys

class Drawing:
    def __init__(self, maze, hexa_maze, color) -> None:
        h_win = 720
        w_win = 720
        self.m = Mlx()
        self.mlx = self.m.mlx_init()
        self.win =  self.m.mlx_new_window(self.mlx, w_win, h_win, "A-MAZE-ING !")
        if not self.win:
            sys.exit(0)
        self.cell_size_w = w_win // maze.width
        self.cell_size_h = h_win // maze.height
        self.color = color
        self.maze = maze
        self.hexa_maze = hexa_maze
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


    def north(self, x, y):
        self.draw_line_h(x, x + self.cell_size_w, y)
        
    def south(self, x, y):
        self.draw_line_h(x, x + self.cell_size_w, y + self.cell_size_h)

    def east(self, x, y):
        self.draw_line_v(x + self.cell_size_w, y, y + self.cell_size_h)

    def west(self, x, y):
        self.draw_line_v(x, y, y + self.cell_size_h)

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
    
    def draw_maze(self):
        x, y = 0, 0
        for i in range(0, self.maze.height):
            x = 0
            for j in range(0, self.maze.width):
                cell = int(self.hexa_maze[i][j], 16)
                if cell == 0b0001:
                    self.west(x, y)
                elif cell == 0b0010:
                    self.south(x, y)
                elif cell == 0b0011:
                    self.south(x, y)
                    self.west(x, y)
                elif cell == 0b0100:
                    self.east(x, y)
                elif cell == 0b0101:
                    self.east(x, y)
                    self.west(x, y)
                elif cell == 0b0110:
                    self.east(x, y)
                    self.south(x, y)
                elif cell == 0b0111:
                    self.east(x, y)
                    self.south(x, y)
                    self.west(x, y)
                elif cell == 0b1000:
                    self.north(x, y)
                elif cell == 0b1001:
                    self.north(x, y)
                    self.west(x, y)
                elif cell == 0b1010:
                    self.north(x, y)
                    self.south(x, y)
                elif cell == 0b1011:
                    self.north(x, y)
                    self.south(x, y)
                    self.west(x, y)
                elif cell == 0b1100:
                    self.north(x, y)
                    self.east(x, y)
                elif cell == 0b1101:
                    self.north(x, y)
                    self.east(x, y)
                    self.west(x, y)
                elif cell == 0b1110: 
                    self.north(x, y)
                    self.east(x, y)
                    self.south(x, y)
                elif cell == 0b1111: 
                    self.north(x, y)
                    self.east(x, y)
                    self.south(x, y)
                    self.west(x, y)
                x += self.cell_size_w
            y += self.cell_size_h
