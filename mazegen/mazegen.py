"""Core Maze class: generation, solving, saving and loading of mazes."""

from __future__ import annotations

import random
from collections import deque

from .algo import hunt_and_kill, prim
from .algo.algo_utils import init_protected
from .parsing import parse_config
from render.tui_utils import print_box, red


class Maze:
    """
    Generate, solve, and save mazes from a configuration file.

    Supported generation algorithms:
        - Hunt and Kill

    The internal grid uses bit encoding:
        bit0=West, bit1=South, bit2=East, bit3=North.

    The output file uses the subject's bit encoding:
        bit0=North, bit1=East, bit2=South, bit3=West.
    """

    def __init__(self, filename: str = "config.txt") -> None:
        """
        Initialize a Maze instance from the configuration file.

        Args:
            filename: Path to the configuration file.
        """
        config = parse_config(filename)

        if "RENDER" in config.keys():
            self.render = config["RENDER"]
        else:
            self.render = "WINDOW"
        self.width: int = int(config["WIDTH"])
        self.height: int = int(config["HEIGHT"])
        self.entry: tuple[str, str] = config["ENTRY"]
        self.exit: tuple[str, str] = config["EXIT"]
        self.algo: str = config["ALGO"]
        self.perfect: bool = config["PERFECT"] == "True"
        self.output_file: str = config["OUTPUT_FILE"]
        self.seed: int | None = config["SEED"]
        self.pattern: str = config.get("PATTERN", "42") or "42"
        self.bold: bool = config["BOLD"] == "True"
        self.animation: bool = config["ANIMATION"] == "True"
        self.speed: int = config["SPEED"] if config["SPEED"] is not None else 1

        self.rand: random.Random = random.Random()
        if self.seed is not None:
            self.rand = random.Random(self.seed)

        self.protected: set[tuple[int, int]] = init_protected(
            pattern=self.pattern,
            width=self.width,
            height=self.height,
            entry=self.entry,
            exit_=self.exit,
        )

        self.grid: list[list[int]] = []
        self.path: list[tuple[int, int]] = []

    def generate(self) -> list[list[int]]:
        """
        Generate the maze using the algorithm defined in config.

        Returns:
            The generated maze grid (internal bit-encoded integers).

        Raises:
            ValueError: If the configured algorithm name is unknown, or if
                the generated grid does not match the configured width and
                height (indicates a bug in the algorithm implementation).
        """
        if self.algo == "hunt_and_kill":
            self.grid = hunt_and_kill(
                width=self.width,
                height=self.height,
                protected=self.protected,
                perfect=self.perfect,
                rand=self.rand,
            )
        elif self.algo == "prim":
            self.grid = prim(
                width=self.width,
                height=self.height,
                protected=self.protected,
                perfect=self.perfect,
                rand=self.rand,
            )
        else:
            raise ValueError(f"Unknown algo: {self.algo!r}")

        if len(self.grid) != self.height or any(
            len(row) != self.width for row in self.grid
        ):
            raise ValueError(
                f"Generated grid dimensions "
                f"({len(self.grid)}x"
                f"{len(self.grid[0]) if self.grid else 0}) "
                f"do not match configured dimensions "
                f"({self.height}x{self.width})"
            )

        return self.grid

    def solve(self) -> list[tuple[int, int]]:
        """
        Solve the maze using BFS and store the shortest path.

        Must be called after generate(). Uses the internal bit encoding
        (bit0=West, bit1=South, bit2=East, bit3=North) to traverse walls.

        Returns:
            The shortest path as a list of (x, y) coordinates from entry
            to exit, or an empty list if no path exists.
        """
        if not self.grid or not self.grid[0]:
            self.path = []
            return self.path

        grid_height = len(self.grid)
        grid_width = len(self.grid[0])

        start = (int(self.entry[0]), int(self.entry[1]))
        end = (int(self.exit[0]), int(self.exit[1]))

        def in_bounds(x: int, y: int) -> bool:
            return 0 <= x < grid_width and 0 <= y < grid_height

        if not in_bounds(*start):
            self.path = []
            return self.path

        queue: deque[tuple[int, int]] = deque([start])
        parent: dict[tuple[int, int], tuple[int, int] | None] = {
            start: None
        }

        while queue:
            cur = queue.popleft()
            if cur == end:
                self.path = self._reconstruct(parent, cur)
                return self.path

            x, y = cur
            cell = self.grid[y][x]
            for nx, ny, bit in [
                (x - 1, y, 0),
                (x, y + 1, 1),
                (x + 1, y, 2),
                (x, y - 1, 3),
            ]:
                if not in_bounds(nx, ny):
                    continue
                if not (cell >> bit) & 1:
                    nb = (nx, ny)
                    if nb not in parent:
                        parent[nb] = cur
                        queue.append(nb)

        self.path = []
        return self.path

    @staticmethod
    def _reconstruct(
        parent: dict[tuple[int, int], tuple[int, int] | None],
        end: tuple[int, int],
    ) -> list[tuple[int, int]]:
        """
        Reconstruct the path from the BFS parent map.

        Args:
            parent: Dict mapping each visited cell to its predecessor.
            end: The destination cell.

        Returns:
            Ordered list of (x, y) coordinates from start to end.
        """
        path: list[tuple[int, int]] = []
        node: tuple[int, int] | None = end
        while node is not None:
            path.append(node)
            node = parent[node]
        return list(reversed(path))

    def path_to_directions(self) -> list[str]:
        """
        Convert the stored path into cardinal direction letters.

        Returns:
            List of directions (N, S, E, W) between consecutive path cells.
        """
        directions: list[str] = []
        for i in range(len(self.path) - 1):
            x1, y1 = self.path[i]
            x2, y2 = self.path[i + 1]
            dx, dy = x2 - x1, y2 - y1
            if dx == 1:
                directions.append("E")
            elif dx == -1:
                directions.append("W")
            elif dy == 1:
                directions.append("S")
            elif dy == -1:
                directions.append("N")
        return directions

    def hexa_maze(self) -> list[list[str]]:
        """
        Convert the internal grid to the subject's hexadecimal format.

        Internal encoding: bit0=West, bit1=South, bit2=East, bit3=North.
        Output encoding:   bit0=North, bit1=East, bit2=South, bit3=West.

        Uses the actual dimensions of self.grid (rather than self.width /
        self.height) so that a grid whose real size differs from the
        configured size never raises an IndexError here.

        Returns:
            Grid where each cell is a single uppercase hex character.
        """
        def remap(v: int) -> int:
            west = (v >> 0) & 1
            south = (v >> 1) & 1
            east = (v >> 2) & 1
            north = (v >> 3) & 1
            return (north << 0) | (east << 1) | (south << 2) | (west << 3)

        return [
            [
                format(remap(self.grid[row][col]), "X")
                for col in range(len(self.grid[row]))
            ]
            for row in range(len(self.grid))
        ]

    def save(self, grid: list[list[int]]) -> None:
        """
        Convert and save the maze grid to the output file.

        Format (per subject spec):
            - One hex digit per cell, no separator, one row per line.
            - Empty line.
            - Entry coordinates (x,y).
            - Exit coordinates (x,y).
            - Shortest path as N/E/S/W letters (only if solve() was called).

        Args:
            grid: Internal integer-encoded maze grid (unused directly;
                  hexa_maze() re-reads self.grid for the conversion).
        """
        hex_grid = self.hexa_maze()
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit
        try:
            with open(self.output_file, "w") as f:
                for row in hex_grid:
                    f.write("".join(row) + "\n")
                f.write("\n")
                f.write(f"{entry_x},{entry_y}\n")
                f.write(f"{exit_x},{exit_y}\n")
                if self.path:
                    f.write("".join(self.path_to_directions()) + "\n")
        except OSError as e:
            print_box((f"{self.output_file} not created: {e}", "Error", red))
