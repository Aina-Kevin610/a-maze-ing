"""Graphical maze renderer built on MiniLibX (MLX)."""

import sys
from typing import Any
from mlx import Mlx
from mazegen import Maze


WALL_COLOR = 0xFFFFFFFF
BG_COLOR = 0x000000FF
ENTRY_COLOR = 0xFF00FF00
EXIT_COLOR = 0xFF0000FF
PATH_COLOR = 0xE0AF68FF
PROT_COLOR = 0xBB9AF7FF

WALL_COLORS = {
    1: 0xFFFFFFFF,
    2: 0x00FFFF00,
    3: 0xFF00FF00,
    4: 0xFF0000FF,
}

WIN_SIZE = 720

NORTH = 1 << 0
EAST = 1 << 1
SOUTH = 1 << 2
WEST = 1 << 3


def parse_maze(filename: str) -> tuple[
    list[list[int]],
    tuple[int, int],
    tuple[int, int],
    list[tuple[int, int]],
]:
    """
    Parse a maze.txt file following the subject's output format.

    Args:
        filename: Path to the maze output file.

    Returns:
        Tuple (grid, entry, exit, path) where grid holds per-cell
        hex-decoded wall bytes, entry/exit are (x, y) coordinates,
        and path is the list of (x, y) cells from entry to exit.
    """
    with open(filename) as f:
        lines = f.read().splitlines()

    grid_lines: list[str] = []
    rest: list[str] = []
    sep = None
    for line in lines:
        if line == "" and sep is None:
            sep = 0
        elif sep is None:
            grid_lines.append(line)
        elif line:
            rest.append(line)

    grid = [[int(c, 16) for c in row] for row in grid_lines]

    ex, ey = map(int, rest[0].split(","))
    xx, xy = map(int, rest[1].split(","))

    path: list[tuple[int, int]] = []
    if len(rest) >= 3:
        x, y = ex, ey
        for ch in rest[2]:
            path.append((x, y))
            if ch == "N":
                y -= 1
            elif ch == "S":
                y += 1
            elif ch == "E":
                x += 1
            elif ch == "W":
                x -= 1
        path.append((x, y))

    return grid, (ex, ey), (xx, xy), path


class MazeRenderer:
    """
    Render a generated maze (from maze.txt) using MiniLibX.

    Reads a static maze file and draws walls, entry, exit, and the
    solution path. No regeneration or animation, single static frame.
    """

    def __init__(
        self,
        grid: list[list[int]],
        entry: tuple[int, int],
        exit_: tuple[int, int],
        path: list[tuple[int, int]],
        protected: set[tuple[int, int]] | None = None,
        bold: bool = False,
        animation: bool = False,
        speed: int = 1,
        config_filename: str | None = None,
    ) -> None:
        """
        Initialize the renderer and create the MLX window.

        Args:
            grid: Maze grid (subject hex bit encoding per cell).
            entry: Entry coordinates (x, y).
            exit_: Exit coordinates (x, y).
            path: Ordered list of (x, y) cells from entry to exit.
        """
        self.grid = grid
        self.entry = entry
        self.exit_ = exit_
        self.path = path
        self.path_set = set(path)

        self.protected = protected or set()
        self.bold = bold
        self.animation = animation
        self.speed = max(1, speed)
        self.config_filename = config_filename
        self.show_path = True
        self.wall_color_index = 1
        self.wall_color = WALL_COLORS[self.wall_color_index]
        self.animation_tasks: list[tuple[int, int]] = []
        self.animation_index = 0

        self.height = len(grid)
        self.width = len(grid[0])

        self.w_win = WIN_SIZE
        self.h_win = WIN_SIZE
        self.cell_w = self.w_win // self.width
        self.cell_h = self.h_win // self.height
        self.w_win = self.cell_w * self.width
        self.h_win = self.cell_h * self.height

        self.m = Mlx()
        self.mlx = self.m.mlx_init()
        if not self.mlx:
            sys.exit(1)

        self.win = self.m.mlx_new_window(
            self.mlx, self.w_win, self.h_win, "A-MAZE-ING !"
        )
        if not self.win:
            sys.exit(1)

        self.img = self.m.mlx_new_image(self.mlx, self.w_win, self.h_win)
        if not self.img:
            sys.exit(1)

        (
            self.data,
            self.bpp,
            self.size_line,
            _,
        ) = self.m.mlx_get_data_addr(self.img)

        self.m.mlx_hook(self.win, 2, 1, self.handle_keys, [self])

    def put_pixel(self, x: int, y: int, color: int) -> None:
        """
        Draw a single pixel in the image buffer.

        Args:
            x: Horizontal pixel coordinate.
            y: Vertical pixel coordinate.
            color: RGBA color value.
        """
        if x < 0 or y < 0 or x >= self.w_win or y >= self.h_win:
            return
        offset = (y * self.size_line) + (x * (self.bpp // 8))
        bleu = (color >> 24) & 0xFF
        green = (color >> 16) & 0xFF
        red = (color >> 8) & 0xFF
        self.data[offset] = bleu
        self.data[offset + 1] = green
        self.data[offset + 2] = red
        self.data[offset + 3] = 0xFF

    def draw_line_h(self, x0: int, x1: int, y: int, color: int) -> None:
        """
        Draw a horizontal line.

        Args:
            x0: Starting x coordinate.
            x1: Ending x coordinate.
            y: Line y coordinate.
            color: Line color.
        """
        for x in range(x0, x1):
            self.put_pixel(x, y, color)

    def draw_line_v(self, x: int, y0: int, y1: int, color: int) -> None:
        """
        Draw a vertical line.

        Args:
            x: Line x coordinate.
            y0: Starting y coordinate.
            y1: Ending y coordinate.
            color: Line color.
        """
        for y in range(y0, y1):
            self.put_pixel(x, y, color)

    def draw_thick_line_h(self, x0: int, x1: int, y: int, color: int) -> None:
        """Draw a horizontal line, thicker if bold mode is enabled.

        Args:
            x0: Starting x coordinate.
            x1: Ending x coordinate.
            y: Line y coordinate.
            color: Line color.
        """
        thickness = 3 if self.bold else 1
        for dy in range(thickness):
            self.draw_line_h(x0, x1, y + dy, color)

    def draw_thick_line_v(self, x: int, y0: int, y1: int, color: int) -> None:
        """Draw a vertical line, thicker if bold mode is enabled.

        Args:
            x: Line x coordinate.
            y0: Starting y coordinate.
            y1: Ending y coordinate.
            color: Line color.
        """
        thickness = 3 if self.bold else 1
        for dx in range(thickness):
            self.draw_line_v(x + dx, y0, y1, color)

    def _cell_distance_to_center(self, x: int, y: int) -> float:
        center_x = (self.width - 1) / 2
        center_y = (self.height - 1) / 2
        dx = x - center_x
        dy = y - center_y
        return dx * dx + dy * dy

    def build_animation_tasks(self) -> None:
        """Build the ordered list of cells to draw during the animation.

        Cells are sorted from the center of the maze outwards, so the
        drawing animation appears to expand from the middle.
        """
        if self.animation_tasks:
            return
        cells = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
        ]
        cells.sort(
            key=lambda coord: (
                self._cell_distance_to_center(*coord),
                coord[1],
                coord[0],
            )
        )
        self.animation_tasks = cells
        self.animation_index = 0

    def draw_cell_walls(self, x: int, y: int) -> None:
        """Draw the walls of a single maze cell.

        Args:
            x: Cell column.
            y: Cell row.
        """
        cell = self.grid[y][x]
        px = x * self.cell_w
        py = y * self.cell_h

        if cell & NORTH:
            self.draw_thick_line_h(px, px + self.cell_w, py, self.wall_color)
        if cell & EAST:
            self.draw_thick_line_v(
                px + self.cell_w, py, py + self.cell_h, self.wall_color
            )
        if cell & SOUTH:
            self.draw_thick_line_h(
                px, px + self.cell_w, py + self.cell_h, self.wall_color
            )
        if cell & WEST:
            self.draw_thick_line_v(px, py, py + self.cell_h, self.wall_color)

    def draw_border(self) -> None:
        """Draw the outer border around the whole maze."""
        self.draw_thick_line_h(0, self.w_win, 0, self.wall_color)
        self.draw_thick_line_h(0, self.w_win, self.h_win - 1, self.wall_color)
        self.draw_thick_line_v(0, 0, self.h_win, self.wall_color)
        self.draw_thick_line_v(self.w_win - 1, 0, self.h_win, self.wall_color)

    def draw_cells(self) -> None:
        """Draw the walls of every cell in the maze."""
        for y in range(self.height):
            for x in range(self.width):
                self.draw_cell_walls(x, y)

    def redraw(self) -> None:
        """Clear the image and redraw the full static maze."""
        self.clear_image()
        self.draw_border()
        self.draw_cells()
        self.draw_overlays()
        self.draw_border()
        self.m.mlx_put_image_to_window(self.mlx, self.win, self.img, 0, 0)

    def next_wall_color(self) -> None:
        """Cycle to the next available wall color."""
        self.wall_color_index += 1
        if self.wall_color_index not in WALL_COLORS:
            self.wall_color_index = 1
        self.wall_color = WALL_COLORS[self.wall_color_index]

    def toggle_path(self) -> None:
        """Toggle the visibility of the solution path."""
        self.show_path = not self.show_path
        if not self.animation:
            self.redraw()

    def regenerate(self) -> None:
        """
        Regenerate the maze from the original config file and redraw it.

        If maze generation fails (bad config, algo bug producing a grid
        with wrong dimensions, etc.), the error is reported and the
        renderer keeps showing the previous maze instead of crashing the
        MLX callback.
        """
        if not self.config_filename:
            return

        try:
            maze = Maze(self.config_filename)
            maze.generate()
            maze.solve()
            maze.save(maze.grid)

            grid, entry, exit_, path = parse_maze(maze.output_file)
        except (ValueError, OSError) as e:
            print(f"Regeneration failed: {e}", file=sys.stderr)
            return

        self.grid = grid
        self.entry = entry
        self.exit_ = exit_
        self.path = path
        self.path_set = set(path)

        self.height = len(grid)
        self.width = len(grid[0])
        self.cell_w = self.w_win // self.width
        self.cell_h = self.h_win // self.height

        self.bold = maze.bold
        self.animation = maze.animation
        self.speed = maze.speed
        self.animation_tasks = []
        self.animation_index = 0

        if self.animation:
            self.clear_img()
            self.draw_border()
            self.build_animation_tasks()
            self.m.mlx_loop_hook(self.mlx, self.loop_hook, [self])
            self.m.mlx_put_image_to_window(self.mlx, self.win, self.img, 0, 0)
        else:
            self.redraw()

    def draw_overlays(self) -> None:
        """Draw protected cells, the solution path, entry and exit."""
        for x, y in self.protected:
            if (x, y) in (self.entry, self.exit_):
                continue
            if 0 <= x < self.width and 0 <= y < self.height:
                self.fill_cell(x * self.cell_w, y * self.cell_h, PROT_COLOR)

        if self.show_path:
            for x, y in self.path_set:
                if (x, y) not in (self.entry, self.exit_):
                    self.fill_cell_small(
                        x * self.cell_w, y * self.cell_h, PATH_COLOR
                    )

        ex, ey = self.entry
        self.fill_cell(ex * self.cell_w, ey * self.cell_h, ENTRY_COLOR)

        xx, xy = self.exit_
        self.fill_cell(xx * self.cell_w, xy * self.cell_h, EXIT_COLOR)

    def draw_frame(self, step_count: int) -> None:
        """Draw the next batch of cells for the build animation.

        Args:
            step_count: Number of cells to draw during this frame.
        """
        while (
            step_count > 0
            and self.animation_index < len(self.animation_tasks)
        ):
            x, y = self.animation_tasks[self.animation_index]
            self.draw_cell_walls(x, y)
            self.animation_index += 1
            step_count -= 1

        if self.animation_index >= len(self.animation_tasks):
            self.draw_overlays()
            self.draw_border()
            self.animation = False

        self.m.mlx_put_image_to_window(self.mlx, self.win, self.img, 0, 0)

    def loop_hook(self, params: list[Any]) -> None:
        """MLX loop callback that advances the build animation.

        Args:
            params: Hook parameters (unused).
        """
        _ = params
        if not self.animation:
            return
        if self.animation_index >= len(self.animation_tasks):
            return
        self.draw_frame(self.speed)

    def fill_cell(self, x: int, y: int, color: int) -> None:
        """
        Fill an entire maze cell with a color.

        Args:
            x: Cell top-left pixel x coordinate.
            y: Cell top-left pixel y coordinate.
            color: Fill color.
        """
        for i in range(y, y + self.cell_h):
            self.draw_line_h(x, x + self.cell_w, i, color)

    def fill_cell_small(self, x: int, y: int, color: int) -> None:
        """
        Fill a smaller centered rectangle inside a maze cell.

        Args:
            x: Cell top-left pixel x coordinate.
            y: Cell top-left pixel y coordinate.
            color: Fill color.
        """
        padding = min(
            max(2, min(self.cell_w, self.cell_h) // 4),
            self.cell_w // 3, self.cell_h // 3
        )
        x0 = x + padding
        y0 = y + padding
        x1 = x + self.cell_w - padding
        y1 = y + self.cell_h - padding

        if x1 <= x0 or y1 <= y0:
            self.fill_cell(x, y, color)
            return

        for i in range(y0, y1):
            self.draw_line_h(x0, x1, i, color)

    def clear_img(self) -> None:
        """Overwrite all image pixels in black before redrawing."""
        for y in range(self.h_win):
            for x in range(self.w_win):
                offset = (y * self.size_line) + (x * (self.bpp // 8))
                self.data[offset] = (BG_COLOR >> 24) & 0xFF
                self.data[offset + 1] = (BG_COLOR >> 16) & 0xFF
                self.data[offset + 2] = (BG_COLOR >> 8) & 0xFF
                self.data[offset + 3] = 0xFF

    def clear_image(self) -> None:
        """Clear the image buffer using the background color."""
        self.clear_img()

    def draw(self) -> None:
        """Render the full static maze or start the animation."""
        self.clear_image()
        self.draw_border()

        if self.animation:
            self.build_animation_tasks()
            self.m.mlx_put_image_to_window(self.mlx, self.win, self.img, 0, 0)
            return

        self.draw_cells()
        self.draw_overlays()
        self.draw_border()
        self.m.mlx_put_image_to_window(self.mlx, self.win, self.img, 0, 0)

    def handle_keys(self, keycode: int, params: list[Any]) -> int:
        """
        Handle keyboard events.

        Args:
            keycode: Pressed key code.
            params: Additional hook parameters (unused).

        Returns:
            Always 0.
        """
        _ = params
        if keycode in (65307, ord('q'), ord('Q')):
            self.m.mlx_destroy_window(self.mlx, self.win)
            self.m.mlx_loop_exit(self.mlx)
        elif keycode in (ord('h'), ord('H')):
            self.toggle_path()
            if not self.animation:
                self.redraw()
        elif keycode in (ord('c'), ord('C')):
            self.next_wall_color()
            if not self.animation:
                self.redraw()
        elif keycode in (ord('r'), ord('R')):
            if self.config_filename:
                self.regenerate()
            else:
                self.animation = True
                self.animation_tasks = []
                self.animation_index = 0
                self.draw()
        return 0

    def run(self) -> None:
        """Draw the maze once and start the MLX event loop."""
        self.draw()
        self.m.mlx_loop_hook(self.mlx, self.loop_hook, [self])
        self.m.mlx_loop(self.mlx)


def window_render(
    filename: str = "maze.txt",
    protected: set[tuple[int, int]] | None = None,
    bold: bool = False,
    animation: bool = False,
    speed: int = 1,
    config_filename: str | None = None,
) -> None:
    """Entry point: load maze.txt and display it with MLX."""
    grid, entry, exit_, path = parse_maze(filename)
    renderer = MazeRenderer(
        grid,
        entry,
        exit_,
        path,
        protected,
        bold=bold,
        animation=animation,
        speed=speed,
        config_filename=config_filename,
    )
    renderer.run()
