from mlx import Mlx
import random
import sys


class DrawingMaze:
    def __init__(self, maze, hexa_maze, wall_color = 0x00FF00FF, bg_color = 0x000000FF) -> None:
        self.h_win = 720
        self.w_win = 1080
        self.m = Mlx()
        self.mlx = self.m.mlx_init()
        if not self.mlx:
            sys.exit(0)
        self.win =  self.m.mlx_new_window(self.mlx, self.w_win, self.h_win, "A-MAZE-ING !")
        if not self.win:
            sys.exit(0)
        self.img = self.m.mlx_new_image(self.mlx, self.w_win, self.h_win)
        if not self.img:
            sys.exit(0)
        self.cell_size_w = self.w_win // maze.width
        self.cell_size_h = self.h_win // maze.height
        self.wall_color = wall_color
        self.bg_color = bg_color
        self.data, self.bpp, self.size_line , _ = self.m.mlx_get_data_addr(self.img)
        self.maze = maze
        self.hexa_maze = hexa_maze
        self.m.mlx_hook(self.win, 2, 1, self.handle_keys, [self])
        self.exit_color = 0xFFFF00FF
        self.entry_color = 0xFFFFFFFF
        self.fill_cell(int(self.maze.entry[0]), int(self.maze.entry[1]), self.entry_color)
        self.fill_cell(int(self.maze.exit[0]), int(self.maze.exit[1]), self.exit_color)



    def my_put_pixel(self, x, y, color):
        if x < 0 or y < 0 or x >= self.w_win or y >= self.h_win:
            return
        offset = (y * self.size_line) + (x * (self.bpp // 8))
        b = (color >> 24) & 0xFF
        g = (color >> 16) & 0xFF
        r = (color >> 8)  & 0xFF
        self.data[offset] = b
        self.data[offset + 1] = g
        self.data[offset + 2] = r
        self.data[offset + 3] = 0xFF


    def handle_keys(self, keycode, params):
        colors = [

        ]
        if keycode == 32:
            colors = [
                0xFFFFFFFF,
                0xFF0000FF,
                0x00FF00FF,
                0x0000FFFF,
                0xFFFF00FF,
                0x00FFFFFF,
                0xFF00FFFF,
                0x8B0000FF,
                0xDC143CFF,
                0xB22222FF
            ]
            print("Changing wall color...")
            self.wall_color = random.choice(colors)
            self.draw_cell()
        if keycode == 65307:
            print("Exited with ESC ...")
            self.m.mlx_destroy_window(self.mlx, self.win)
            self.m.mlx_loop_exit(self.mlx)
        if keycode == 65293:
            print("Restarting...")
            self.maze.generate()
            self.draw_cell()
        return 0


    def draw_line_h(self, x0, x1, y, color) -> None:
        for x in range(x0, x1):
            self.my_put_pixel(x, y, color)

    def draw_line_v(self, x, y0, y1, color) -> None:
        for y in range(y0, y1):
            self.my_put_pixel(x, y, color)

    
    # def draw_cell(self, x, y) -> None:
    #     self.draw_line_h(x, x + self.cell_size_w, y)
    #     self.draw_line_h(x, x + self.cell_size_w, y + self.cell_size_h)
    #     self.draw_line_v(x, y, y + self.cell_size_h)
    #     self.draw_line_v(x + self.cell_size_w, y, y + self.cell_size_h)

    def north(self, x, y):
        self.draw_line_h(x, x + self.cell_size_w, y, self.wall_color)
        
    def south(self, x, y):
        self.draw_line_h(x, x + self.cell_size_w, y + self.cell_size_h, self.wall_color)

    def east(self, x, y):
        self.draw_line_v(x + self.cell_size_w, y, y + self.cell_size_h, self.wall_color)

    def west(self, x, y):
        self.draw_line_v(x, y, y + self.cell_size_h, self.wall_color)

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
    

    def fill_cell(self, x, y, color):
        for i in range(y, y + self.cell_size_h):
            self.draw_line_h(x, x + self.cell_size_w, i, color)

    def draw_cell(self):
        self.clear_image()
        self.fill_cell(int(self.maze.entry[0]) * self.cell_size_w,
                       int(self.maze.entry[1]) * self.cell_size_h, self.entry_color)
        self.fill_cell(int(self.maze.exit[0]) * self.cell_size_w, 
                       int(self.maze.exit[1]) * self.cell_size_h, self.exit_color)
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.grid[y][x]
                px = x * self.cell_size_w
                py = y * self.cell_size_h
                if cell & 1:
                    self.west(px, py)
                if (cell >> 1) & 1:
                    self.south(px, py)
                if (cell >> 2) & 1:
                    self.east(px, py)
                if (cell >> 3) & 1:
                    self.north(px, py)
        self.m.mlx_put_image_to_window(self.mlx, self.win, self.img, 0, 0)

    def clear_image(self):
        for y in range(self.h_win):
            for x in range(self.w_win):
                offset = (y * self.size_line) + (x * (self.bpp // 8))
                self.data[offset]     = (self.bg_color >> 8)  & 0xFF
                self.data[offset + 1] = (self.bg_color >> 16) & 0xFF
                self.data[offset + 2] = (self.bg_color >> 24) & 0xFF
                self.data[offset + 3] = self.bg_color & 0xFF 

    def exit_win(self):
        print("Exited with ESC ...")
        self.m.mlx_destroy_window(self.mlx, self.win)
        self.m.mlx_loop_exit(self.mlx)


# class Menu:
#     def __init__(self, draw):
#         self.draw = draw
#         self.m = Mlx()
#         self.mlx = self.m.mlx_init()
#         self.win = self.m.mlx_new_window(self.mlx, 320, 320, "MENU !")
#         self.m.mlx_string_put(self.mlx, self.win, 320 // 2 + 50, 75, 0xffffffff, "OPTIONS:")
#         self.m.mlx_hook(self.win, 2, 1, self.handle_keys, [self])
#         self.m.mlx_loop(self.mlx)

#         def handle_keys(self, keycode, params):
#             if keycode == 65307:
#                 print("Exited with ESC ...")
#                 self.m.mlx_destroy_window(self.mlx, self.win)
#                 self.m.mlx_loop_exit(self.mlx)
#             if keycode == 65293:
#                 print("Restartint...")
#                 self.maze.generate()
#                 self.draw_maze()
#             return 0