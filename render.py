import random
import sys
from typing import Any

from mlx import Mlx

from maze_generator.maze_gen import Maze


def loop_hook(param):
    draw, rand, maze = param

    if maze.algo == "hunt_and_kill":
        if draw.maze.phase != "done":
            if not draw.maze.started:
                draw.maze.current_x = rand.randint(0, draw.maze.width - 1)
                draw.maze.current_y = rand.randint(0, draw.maze.height - 1)
                draw.maze.visited[draw.maze.current_y][draw.maze.current_x] = True
                draw.maze.started = True
            alive = draw.maze.step()
            if not alive:
                draw.maze.save(draw.maze.hexa_maze())
    elif maze.algo == "prim":
        if draw.maze.phase != "done":
            if not draw.maze.started:
                draw.maze.init_prim()
                draw.maze.started = True
            alive = draw.maze.step_prim()
            if not alive:
                draw.maze.save(draw.maze.hexa_maze())
    elif maze.algo == "backtracking" or maze.algo == "DFS":
        if draw.maze.phase != "done":
            if not draw.maze.started:
                draw.maze.init_backtracking()
                draw.maze.started = True
            alive = draw.maze.step_backtracking()
            if not alive:
                draw.maze.save(draw.maze.hexa_maze())
    if draw.maze.phase == "done":
        if draw.maze.solve_phase == "idle":
            draw.maze.init_solve()
        if draw.maze.solve_phase not in ("idle", "done"):
            draw.maze.step_solve()
        if draw.maze.solve_phase == "done" and not draw.saved:
            draw.maze.solve()
            draw.maze.save(draw.maze.hexa_maze())
            draw.saved = True
    draw.draw_cell()


class DrawingMaze:

    def __init__(
        self,
        maze: Maze,
        hexa_maze: Any,
        wall_color: int = 0x00FF00FF,
        bg_color: int = 0x000000FF,
    ) -> None:
        self.h_win = 480
        self.w_win = 480

        self.cell_size_w = self.w_win // maze.width
        self.cell_size_h = self.h_win // maze.height

        if self.w_win % maze.width != 0:
            self.w_win -= (
                self.w_win - (maze.width * self.cell_size_w)
            )

        if self.h_win % maze.height != 0:
            self.h_win -= (
                self.h_win - (maze.height * self.cell_size_h)
            )

        self.m = Mlx()
        self.mlx = self.m.mlx_init()

        if not self.mlx:
            sys.exit(0)

        self.win = self.m.mlx_new_window(
            self.mlx,
            self.w_win,
            self.h_win,
            "A-MAZE-ING !",
        )

        if not self.win:
            sys.exit(0)

        self.img = self.m.mlx_new_image(
            self.mlx,
            self.w_win,
            self.h_win,
        )

        if not self.img:
            sys.exit(0)

        self.wall_color = wall_color
        self.bg_color = bg_color

        (
            self.data,
            self.bpp,
            self.size_line,
            _,
        ) = self.m.mlx_get_data_addr(self.img)

        self.maze = maze
        self.hexa_maze = hexa_maze

        self.m.mlx_hook(
            self.win,
            2,
            1,
            self.handle_keys,
            [self],
        )

        self.exit_color = 0xFFFF00FF
        self.entry_color = 0xFFFFFFFF

        self.visited_col = 0x4F07F5FF
        self.front_col = 0x00C8FFFF

        self.path_col_start = (0x00, 0xE8, 0x7F)
        self.path_col_end = (0xFF, 0x40, 0x00)

    def my_put_pixel(
        self,
        x: int,
        y: int,
        color: int,
    ) -> None:
        if (
            x < 0
            or y < 0
            or x >= self.w_win
            or y >= self.h_win
        ):
            return

        offset = (
            y * self.size_line
        ) + (x * (self.bpp // 8))

        blue = (color >> 24) & 0xFF
        green = (color >> 16) & 0xFF
        red = (color >> 8) & 0xFF

        self.data[offset] = blue
        self.data[offset + 1] = green
        self.data[offset + 2] = red
        self.data[offset + 3] = 0xFF

    def handle_keys(
        self,
        keycode: int,
        params: list[Any],
    ) -> int:
        _ = params

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
                0xB22222FF,
            ]

            print("Changing wall color...")

            self.wall_color = random.choice(colors)

            self.draw_cell()

        if keycode == 65307:
            print("Exited with ESC ...")

            self.m.mlx_destroy_window(
                self.mlx,
                self.win,
            )

            self.m.mlx_loop_exit(self.mlx)

        if keycode == 65293:
            print("Regenerating...")

            self.maze = Maze()
            self.saved = False

            self.clear_image()

            self.m.mlx_loop_hook(
                self.mlx,
                loop_hook,
                [self, self.maze.rand, self.maze],
            )

            self.m.mlx_loop(self.mlx)

        return 0

    def draw_line_h(
        self,
        x0: int,
        x1: int,
        y: int,
        color: int,
    ) -> None:
        for x in range(x0, x1):
            self.my_put_pixel(x, y, color)

    def draw_line_v(
        self,
        x: int,
        y0: int,
        y1: int,
        color: int,
    ) -> None:
        for y in range(y0, y1):
            self.my_put_pixel(x, y, color)

    def north(self, x: int, y: int) -> None:
        self.draw_line_h(
            x,
            x + self.cell_size_w,
            y,
            self.wall_color,
        )

    def south(self, x: int, y: int) -> None:
        self.draw_line_h(
            x,
            x + self.cell_size_w,
            y + self.cell_size_h,
            self.wall_color,
        )

    def east(self, x: int, y: int) -> None:
        self.draw_line_v(
            x + self.cell_size_w,
            y,
            y + self.cell_size_h,
            self.wall_color,
        )

    def west(self, x: int, y: int) -> None:
        self.draw_line_v(
            x,
            y,
            y + self.cell_size_h,
            self.wall_color,
        )

    def fill_cell(
        self,
        x: int,
        y: int,
        color: int,
    ) -> None:
        for i in range(y, y + self.cell_size_h):
            self.draw_line_h(
                x,
                x + self.cell_size_w,
                i,
                color,
            )

    def solve_fill_cell(
        self,
        x: int,
        y: int,
        index: int,
        total: int,
    ) -> None:
        t = index / max(total - 1, 1)

        sr, sg, sb = self.path_col_start
        er, eg, eb = self.path_col_end

        red = int(sr + t * (er - sr))
        green = int(sg + t * (eg - sg))
        blue = int(sb + t * (eb - sb))

        color = (
            (red << 24)
            | (green << 16)
            | (blue << 8)
            | 0xFF
        )

        self.fill_cell(
            x * self.cell_size_w,
            y * self.cell_size_h,
            color,
        )

    def blend_color(
        self,
        color: int,
        alpha: float,
    ) -> int:
        blue = (color >> 24) & 0xFF
        green = (color >> 16) & 0xFF
        red = (color >> 8) & 0xFF

        bg_blue = (self.bg_color >> 24) & 0xFF
        bg_green = (self.bg_color >> 16) & 0xFF
        bg_red = (self.bg_color >> 8) & 0xFF

        new_blue = int(
            bg_blue + (blue - bg_blue) * alpha
        )

        new_green = int(
            bg_green + (green - bg_green) * alpha
        )

        new_red = int(
            bg_red + (red - bg_red) * alpha
        )

        return (
            (new_blue << 24)
            | (new_green << 16)
            | (new_red << 8)
            | 0xFF
        )

    def draw_cell(self) -> None:
        self.clear_image()

        entry = (
            int(self.maze.entry[0]),
            int(self.maze.entry[1]),
        )

        exit_ = (
            int(self.maze.exit[0]),
            int(self.maze.exit[1]),
        )

        faded_color = self.blend_color(
            self.visited_col,
            0.15,
        )

        for x, y in self.maze.explored:
            if (x, y) not in (entry, exit_):
                self.fill_cell(
                    x * self.cell_size_w,
                    y * self.cell_size_h,
                    faded_color,
                )

        for x, y in self.maze.frontier:
            if (x, y) not in (entry, exit_):
                self.fill_cell(
                    x * self.cell_size_w,
                    y * self.cell_size_h,
                    self.front_col,
                )

        total = self.maze.path_index

        for i, (x, y) in enumerate(
            self.maze.path[: self.maze.path_index]
        ):
            if (x, y) not in (entry, exit_):
                self.solve_fill_cell(
                    x,
                    y,
                    i,
                    total,
                )

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if not self.maze.visited[y][x]:
                    continue

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

        if self.maze.phase != "done":
            self.fill_cell(
                self.maze.current_x * self.cell_size_w,
                self.maze.current_y * self.cell_size_h,
                0xFF6600FF,
            )

        if self.maze.generated:
            for x, y in self.maze.protected:
                self.fill_cell(
                    x * self.cell_size_w,
                    y * self.cell_size_h,
                    0xFFFFFFFF,
                )

        self.fill_cell(
            entry[0] * self.cell_size_w,
            entry[1] * self.cell_size_h,
            self.entry_color,
        )

        self.fill_cell(
            exit_[0] * self.cell_size_w,
            exit_[1] * self.cell_size_h,
            self.exit_color,
        )

        self.draw_line_h(
            0,
            self.w_win,
            0,
            self.wall_color,
        )

        self.draw_line_h(
            0,
            self.w_win,
            self.h_win - 1,
            self.wall_color,
        )

        self.draw_line_v(
            0,
            0,
            self.h_win,
            self.wall_color,
        )

        self.draw_line_v(
            self.w_win - 1,
            0,
            self.h_win,
            self.wall_color,
        )

        self.m.mlx_put_image_to_window(
            self.mlx,
            self.win,
            self.img,
            0,
            0,
        )
    
        self.fill_cell(
            entry[0] * self.cell_size_w,
            entry[1] * self.cell_size_h,
            self.entry_color,
        )

        self.fill_cell(
            exit_[0] * self.cell_size_w,
            exit_[1] * self.cell_size_h,
            self.exit_color,
        )

        self.draw_line_h(
            0,
            self.w_win,
            0,
            self.wall_color,
        )

        self.draw_line_h(
            0,
            self.w_win,
            self.h_win - 1,
            self.wall_color,
        )

        self.draw_line_v(
            0,
            0,
            self.h_win,
            self.wall_color,
        )

        self.draw_line_v(
            self.w_win - 1,
            0,
            self.h_win,
            self.wall_color,
        )

        self.m.mlx_put_image_to_window(
            self.mlx,
            self.win,
            self.img,
            0,
            0,
        )

    def clear_image(self) -> None:
        for y in range(self.h_win):
            for x in range(self.w_win):
                offset = (
                    y * self.size_line
                ) + (x * (self.bpp // 8))

                self.data[offset] = (
                    (self.bg_color >> 8) & 0xFF
                )

                self.data[offset + 1] = (
                    (self.bg_color >> 16) & 0xFF
                )

                self.data[offset + 2] = (
                    (self.bg_color >> 24) & 0xFF
                )

                self.data[offset + 3] = (
                    self.bg_color & 0xFF
                )

    def exit_win(self) -> None:
        print("Exited with ESC ...")

        self.m.mlx_destroy_window(
            self.mlx,
            self.win,
        )

        self.m.mlx_loop_exit(self.mlx)
