import random
import sys
from typing import Any
from mlx import Mlx
from render_terminal import print_box
from maze_generator.maze_gen import Maze
from utils import *


class DrawingMaze:

    """
        Handle graphical rendering and visualization of a maze.
        This class is responsible for:
            - Creating and managing the MLX window.
            - Drawing maze walls and cells.
            - Displaying generation and solving progress.
            - Handling keyboard events.
            - Rendering entry, exit, and solution paths.
    """
    def __init__(
        self,
        maze: Maze,
        hexa_maze: Any,
        wall_color: int = 0x00FF00FF,
        bg_color: int = 0x000000FF,
    ) -> None:
        """
            Initialize the maze renderer and create the graphical window.
            Args:
                maze: Maze instance to render.
                hexa_maze: Optional hex maze representation.
                wall_color: Color used for maze walls.
                bg_color: Background color.
        """
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

        self.show_path = True
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
        """
            Draw a single pixel in the image buffer.
            Args:
                x: Horizontal pixel coordinate.
                y: Vertical pixel coordinate.
                color: RGBA color value.
        """
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

        bleu = (color >> 24) & 0xFF
        green = (color >> 16) & 0xFF
        red = (color >> 8) & 0xFF

        self.data[offset] = bleu
        self.data[offset + 1] = green
        self.data[offset + 2] = red
        self.data[offset + 3] = 0xFF

    def handle_keys(self,
                    keycode: int,
                    params: list[Any]
                    ) -> int:
        """
            Handle keyboard events.
            Supported keys:
                - Space: Change wall color.
                - P: Toggle solution path visibility.
                - Enter: Regenerate the maze.
                - Escape: Exit the application.
            Args:
                keycode: Pressed key code.
                params: Additional event parameters.
            Returns:
                Always returns 0.
        """
        _ = params

        if keycode == 32:
            loading("Changing wall color...", 0.08)
            print_box(["Wall color changed!", "Action", magenta])
            self.wall_color = random.choice(colors)
            self.draw_cell()

        if keycode == 112:
            self.show_path = not self.show_path

        if keycode == 65307:
            loading("Exiting...", 0.08)
            print_box(["Exited successfully!", "Action", magenta])
            self.m.mlx_destroy_window(self.mlx, self.win)
            self.m.mlx_loop_exit(self.mlx)

        if keycode == 65293:
            loading("Regenerating maze...", 0.08)
            print_box(["Maze regenerated", "Action", magenta])
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
        """
            Draw a horizontal line.
            Args:
                x0: Starting x coordinate.
                x1: Ending x coordinate.
                y: Line y coordinate.
                color: Line color.
        """
        for x in range(x0, x1):
            self.my_put_pixel(x, y, color)

    def draw_line_v(
        self,
        x: int,
        y0: int,
        y1: int,
        color: int,
    ) -> None:
        """
            Draw a vertical line.
            Args:
                x: Line x coordinate.
                y0: Starting y coordinate.
                y1: Ending y coordinate.
                color: Line color.
        """
        for y in range(y0, y1):
            self.my_put_pixel(x, y, color)

    def north(self, x: int, y: int) -> None:
        """
            Draw the north wall of a cell.
            Args:
                x: Cell pixel x coordinate.
                y: Cell pixel y coordinate.
        """
        self.draw_line_h(
            x,
            x + self.cell_size_w,
            y,
            self.wall_color,
        )

    def south(self, x: int, y: int) -> None:
        """
            Draw the south wall of a cell.
            Args:
                x: Cell pixel x coordinate.
                y: Cell pixel y coordinate.
        """
        self.draw_line_h(
            x,
            x + self.cell_size_w,
            y + self.cell_size_h,
            self.wall_color,
        )

    def east(self, x: int, y: int) -> None:
        """
            Draw the east wall of a cell.
            Args:
                x: Cell pixel x coordinate.
                y: Cell pixel y coordinate.
        """
        self.draw_line_v(
            x + self.cell_size_w,
            y,
            y + self.cell_size_h,
            self.wall_color,
        )

    def west(self, x: int, y: int) -> None:
        """
            Draw the west wall of a cell.
            Args:
                x: Cell pixel x coordinate.
                y: Cell pixel y coordinate.
        """
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
        """
            Fill an entire maze cell with a color.
            Args:
                x: Cell top-left pixel x coordinate.
                y: Cell top-left pixel y coordinate.
                color: Fill color.
        """
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
        """
            Draw a solution path marker using a color gradient.
            Args:
                x: Cell x coordinate.
                y: Cell y coordinate.
                index: Position in the solution path.
                total: Total number of cells in the path.
        """
        t = index / max(total - 1, 1)

        sr, sg, sb = self.path_col_start
        er, eg, eb = self.path_col_end

        red = int(sr + t * (er - sr))
        green = int(sg + t * (eg - sg))
        bleu = int(sb + t * (eb - sb))

        color = (
            (red << 24)
            | (green << 16)
            | (bleu << 8)
            | 0xFF
        )

        self.fill_circle(
            x * self.cell_size_w + self.cell_size_w // 2,
            y * self.cell_size_h + self.cell_size_h // 2,
            min(self.cell_size_w, self.cell_size_h) // 4,
            color,
        )

    def blend_color(
        self,
        color: int,
        alpha: float,
    ) -> int:
        """
            Blend a color with the background color.
            Args:
                color: Source color.
                alpha: Blend factor between 0 and 1.
            Returns:
                The resulting blended color.
        """
        bleu = (color >> 24) & 0xFF
        green = (color >> 16) & 0xFF
        red = (color >> 8) & 0xFF

        bg_bleu = (self.bg_color >> 24) & 0xFF
        bg_green = (self.bg_color >> 16) & 0xFF
        bg_red = (self.bg_color >> 8) & 0xFF

        new_bleu = int(
            bg_bleu + (bleu - bg_bleu) * alpha
        )

        new_green = int(
            bg_green + (green - bg_green) * alpha
        )

        new_red = int(
            bg_red + (red - bg_red) * alpha
        )

        return (
            (new_bleu << 24)
            | (new_green << 16)
            | (new_red << 8)
            | 0xFF
        )

    def fill_circle(
        self,
        cx: int,
        cy: int,
        r: int,
        color: int,
    ) -> None:
        """
            Draw a filled circle.
            Args:
                cx: Circle center x coordinate.
                cy: Circle center y coordinate.
                r: Circle radius.
                color: Fill color.
        """
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.my_put_pixel(x, y, color)

    def draw_cell(self) -> None:
        """
            Render the entire maze.
            Draws:
                - Explored cells.
                - Frontier cells.
                - Solution path.
                - Maze walls.
                - Entry and exit markers.
                - Current generation position.
            Updates the displayed image in the window.
        """
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

        if self.show_path:
            for i, (x, y) in enumerate(
                self.maze.path[: self.maze.path_index]
            ):
                if (x, y) not in (entry, exit_):
                    self.solve_fill_cell(x, y, i, total)

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

        if self.maze.generated:
            for x, y in self.maze.protected:
                self.fill_cell(
                    x * self.cell_size_w,
                    y * self.cell_size_h,
                    0xFFFFFFFF,
                )

        self.fill_circle(
            entry[0] * self.cell_size_w + self.cell_size_w // 2,
            entry[1] * self.cell_size_h + self.cell_size_h // 2,
            min(self.cell_size_w, self.cell_size_h) // 2 - 1,
            self.entry_color,
        )

        self.fill_circle(
            exit_[0] * self.cell_size_w + self.cell_size_w // 2,
            exit_[1] * self.cell_size_h + self.cell_size_h // 2,
            min(self.cell_size_w, self.cell_size_h) // 2 - 1,
            self.exit_color,
        )

        if self.maze.phase != "done":
            self.fill_cell(
                self.maze.current_x * self.cell_size_w,
                self.maze.current_y * self.cell_size_h,
                0xFF6600FF,
            )

        self.draw_line_h(0, self.w_win, 0, self.wall_color)
        self.draw_line_h(0, self.w_win, self.h_win - 1, self.wall_color)
        self.draw_line_v(0, 0, self.h_win, self.wall_color)
        self.draw_line_v(self.w_win - 1, 0, self.h_win, self.wall_color)

        self.m.mlx_put_image_to_window(self.mlx, self.win, self.img, 0, 0)

    def clear_image(self) -> None:
        """
            Clear the image buffer using the current background color.
        """
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
        """
            Close the application window and stop the MLX event loop.
        """
        print("Exited with ESC ...")

        self.m.mlx_destroy_window(
            self.mlx,
            self.win,
        )

        self.m.mlx_loop_exit(self.mlx)
