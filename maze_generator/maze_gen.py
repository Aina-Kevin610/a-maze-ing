import os
import sys
import random
from typing import Any, Optional
from .pattern import Pattern
from collections import deque
from parsing import parse_config


class ConfigError(Exception):
    """Exception raised when an invalid maze configuration is detected."""

    pass


class Maze:
    """
    Generate, solve, and save mazes using multiple algorithms.

    Supported generation algorithms:
        - Hunt and Kill
        - Recursive Backtracking (DFS)
        - Prim's Algorithm

    The class also supports:
        - Pattern protection zones
        - Perfect and imperfect mazes
        - Maze solving using Breadth-First Search (BFS)
        - Step-by-step generation and solving visualization
    """

    def __init__(
        self,
        pattern_: str = "42",
        filename: str = "config.txt"
    ) -> None:
        """
        Initialize a maze instance from the configuration file.

        Args:
            pattern_: Pattern to preserve inside the maze.
            filename: Path to the configuration file.
        """
        config = parse_config(filename)

        self.pattern_: str = config.get("PATTERN", pattern_) or pattern_
        self.width: int = int(config["WIDTH"])
        self.height: int = int(config["HEIGHT"])
        self.entry: tuple[str, str] = config["ENTRY"]
        self.exit: tuple[str, str] = config["EXIT"]
        self.output_file: str = config["OUTPUT_FILE"]
        self.perfect: bool = config["PERFECT"] == "True"
        self.algo: str = config["ALGO"]
        self.grid: list[list[int]] = self.__init_grid()
        self.visited: list[list[bool]] = self.__init_visited()
        self.current_x: int = 0
        self.current_y: int = 0

        speed_val = config.get("SPEED")
        self.speed: int = int(speed_val) if speed_val is not None else 1

        self.phase: str = "kill"
        self.wall: int = 0b1111
        self.started: bool = False
        self.protected: set[tuple[int, int]] = set()
        self.seed: Optional[int] = config["SEED"]
        self.path: list[tuple[int, int]] = []
        self.path_index: int = 0
        self.explored: set[tuple[int, int]] = set()
        self.frontier: set[tuple[int, int]] = set()
        self.solve_phase: str = "idle"
        self._bfs_queue: Optional[deque[tuple[int, int]]] = None
        self._bfs_parent: Optional[
            dict[tuple[int, int], Optional[tuple[int, int]]]
        ] = None
        self._bfs_end: Optional[tuple[int, int]] = None

        self._prim_set: set[tuple[int, int]] = set()
        self.prim_frontier: list[tuple[int, int]] = []

        self.stack: list[tuple[int, int]] = []

        # FIX: un seul bloc conditionnel pour __init_42
        if self.height >= 10 and self.width >= 10:
            self.__init_42()
        else:
            print(
                f"Pattern [{self.pattern_}] cannot be contained within "
                "the maze! (10 x 10 is required)"
            )

        self.rand: random.Random = random.Random()
        if self.seed is not None:
            self.rand = random.Random(self.seed)
        self.generated: bool = False

        x_e, y_e = self.entry
        if (int(x_e), int(y_e)) in self.protected:
            print("Error - Inaccessible entry!")
            sys.exit(1)

    def __init_42(self) -> None:
        """
        Initialize protected zones based on a pattern.

        Converts the pattern into forbidden coordinates inside the grid.
        """
        p = Pattern(self.pattern_)
        x_grid = self.width // 2
        y_grid = self.height // 2
        pat = p.create_merged()
        if not pat or not pat[0]:
            print(
                f"Pattern [{self.pattern_}] not recognized, skipping. "
                "(must be uppercase or number)"
            )
            return
        offset_x = len(pat[0]) // 2
        offset_y = len(pat) // 2
        for i in range(len(pat)):
            for j in range(len(pat[i])):
                if pat[i][j] == 1:
                    self.protected.add(
                        (x_grid - offset_x + j, y_grid - offset_y + i)
                    )
        x, y = self.entry
        if (int(x), int(y)) in self.protected:
            print("Error - Inaccessible entry!")
            sys.exit(1)
        x, y = self.exit
        if (int(x), int(y)) in self.protected:
            print("Error - Inaccessible exit!")
            sys.exit(1)

    def __init_grid(self) -> list[list[int]]:
        """
        Initialize the maze grid.

        Returns:
            A grid filled with walls (value 15).
        """
        return [[15 for _ in range(self.width)] for _ in range(self.height)]

    def generate(self) -> list[list[Any]]:
        """
        Generate the maze using the selected algorithm.

        Returns:
            The generated maze grid.
        """
        if self.algo == "hunt_and_kill":
            return self.hunt_and_kill()
        if self.algo in ("backtracking", "DFS"):
            return self.backtracking()
        if self.algo == "prim":
            return self.prim()
        return self.grid

    def hexa_maze(self) -> list[list[str]]:
        """
        Convert the maze grid into hexadecimal representation.

        Internal grid encoding: bit0=West, bit1=South, bit2=East, bit3=North.
        Output file encoding:   bit0=North, bit1=East, bit2=South, bit3=West.

        Returns:
            Maze grid encoded in hexadecimal format per the subject spec.
        """
        def remap(v: int) -> int:
            west = (v >> 0) & 1
            south = (v >> 1) & 1
            east = (v >> 2) & 1
            north = (v >> 3) & 1
            return (north << 0) | (east << 1) | (south << 2) | (west << 3)

        return [
            [format(remap(self.grid[row][col]), "X") for col in range(self.width)]
            for row in range(self.height)
        ]

    def is_all_visited(self) -> bool:
        """
        Check whether all cells have been visited.

        Returns:
            True if all cells are visited, otherwise False.
        """
        return all(all(row) for row in self.visited)

    def __init_visited(self) -> list[list[bool]]:
        """
        Initialize the visited cells grid.

        Returns:
            A boolean matrix initialized to False.
        """
        return [[False] * self.width for _ in range(self.height)]

    def _make_imperfect(self, rate: float = 0.15) -> None:
        """
        Randomly remove walls to create an imperfect maze.

        Args:
            rate: Probability of removing a wall.
        """
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.protected:
                    continue
                if x + 1 < self.width and (x + 1, y) not in self.protected:
                    if self.rand.random() < rate:
                        self.grid[y][x] &= ~(1 << 2)
                        self.grid[y][x + 1] &= ~(1 << 0)
                if y + 1 < self.height and (x, y + 1) not in self.protected:
                    if self.rand.random() < rate:
                        self.grid[y][x] &= ~(1 << 1)
                        self.grid[y + 1][x] &= ~(1 << 3)

    def remove_wall(
        self, x: int, y: int, xn: int, yn: int
    ) -> tuple[int, int, int]:
        """
        Remove the wall between two adjacent cells.

        Args:
            x: X coordinate of current cell.
            y: Y coordinate of current cell.
            xn: X coordinate of neighbor cell.
            yn: Y coordinate of neighbor cell.

        Returns:
            Updated position and removed wall direction.
        """
        dx, dy = xn - x, yn - y
        if dx == 1:
            direction = 0b0100
            opposite = 0b0001
        elif dx == -1:
            direction = 0b0001
            opposite = 0b0100
        elif dy == 1:
            direction = 0b0010
            opposite = 0b1000
        elif dy == -1:
            direction = 0b1000
            opposite = 0b0010
        else:
            return xn, yn, 0
        self.grid[y][x] &= ~direction
        self.grid[yn][xn] &= ~opposite
        self.visited[y][x] = True
        self.visited[yn][xn] = True
        return xn, yn, opposite

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """
        Get unvisited neighbors of a cell.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            List of valid neighbor coordinates.
        """
        way = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        neighbors: list[tuple[int, int]] = []
        for dx, dy in way:
            xn, yn = x + dx, y + dy
            if (
                0 <= xn < self.width
                and 0 <= yn < self.height
                and not self.visited[yn][xn]
                and (xn, yn) not in self.protected
            ):
                neighbors.append((xn, yn))
        return neighbors

    def get_visited_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """
        Get visited neighbors of a cell.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            List of visited neighbor coordinates.
        """
        way = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        neighbors: list[tuple[int, int]] = []
        for dx, dy in way:
            xn, yn = x + dx, y + dy
            if (
                0 <= xn < self.width
                and 0 <= yn < self.height
                and self.visited[yn][xn]
                and (xn, yn) not in self.protected
            ):
                neighbors.append((xn, yn))
        return neighbors

    def init_prim(self) -> None:
        """Initialize Prim's algorithm."""
        x = self.rand.randint(0, self.width - 1)
        y = self.rand.randint(0, self.height - 1)
        while (x, y) in self.protected:
            x = self.rand.randint(0, self.width - 1)
            y = self.rand.randint(0, self.height - 1)
        self.visited[y][x] = True
        self.current_x, self.current_y = x, y
        self._prim_set = {(x, y)}
        self.prim_frontier = [(x, y)]
        self._expand_prim(x, y)

    def _expand_prim(self, x: int, y: int) -> None:
        """
        Add valid neighboring cells of (x, y) to the Prim frontier.

        Args:
            x: X coordinate of the cell to expand from.
            y: Y coordinate of the cell to expand from.
        """
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < self.width
                and 0 <= ny < self.height
                and not self.visited[ny][nx]
                and (nx, ny) not in self.protected
                and (nx, ny) not in self._prim_set
            ):
                self._prim_set.add((nx, ny))
                self.prim_frontier.append((nx, ny))

    def step_prim(self) -> bool:
        """
        Execute one step of Prim's algorithm.

        Returns:
            True if generation continues, False if finished.
        """
        if not self.prim_frontier:
            self.phase = "done"
            self.generated = True
            if not self.perfect:
                self._make_imperfect()
            return False
        idx = self.rand.randint(0, len(self.prim_frontier) - 1)
        x, y = self.prim_frontier.pop(idx)
        self._prim_set.discard((x, y))
        self.current_x, self.current_y = x, y
        visited_nb = self.get_visited_neighbors(x, y)
        if visited_nb:
            xn, yn = self.rand.choice(visited_nb)
            self.remove_wall(x, y, xn, yn)
            self._expand_prim(x, y)
        return True

    def prim(self) -> list[list[str]]:
        """
        Generate a maze using Prim's algorithm.

        Returns:
            Generated maze grid.
        """
        self.init_prim()
        while self.prim_frontier:
            self.step_prim()
        grid = self.hexa_maze()
        self.save(grid)
        return grid

    def kill(self) -> bool:
        """
        Perform the kill phase of Hunt and Kill algorithm.

        Returns:
            True if a move was made, otherwise False.
        """
        neighbors = self.get_neighbors(self.current_x, self.current_y)
        if not neighbors:
            return False
        xn, yn = self.rand.choice(neighbors)
        while (xn, yn) in self.protected:
            xn, yn = self.rand.choice(neighbors)
        self.current_x, self.current_y, self.wall = self.remove_wall(
            self.current_x, self.current_y, xn, yn
        )
        return True

    def hunt(self) -> Optional[tuple[int, int]]:
        """
        Perform the hunt phase of Hunt and Kill algorithm.

        Returns:
            Next starting cell or None if finished.
        """
        for i in range(self.height):
            for j in range(self.width):
                if (
                    not self.visited[i][j]
                    and (j, i) not in self.protected
                ):
                    v_neighbors = self.get_visited_neighbors(j, i)
                    if v_neighbors:
                        xn, yn = self.rand.choice(v_neighbors)
                        self.remove_wall(j, i, xn, yn)
                        return j, i
        return None

    def step(self) -> bool:
        """
        Execute one generation step (Hunt and Kill).

        Returns:
            True if generation continues.
        """
        if self.phase == "done":
            return False
        if self.phase == "kill":
            again = self.kill()
            if not again:
                self.phase = "hunt"
            return True
        if self.phase == "hunt":
            result = self.hunt()
            if result is None:
                self.phase = "done"
                self.generated = True
                if not self.perfect:
                    self._make_imperfect()
                return False
            self.current_x, self.current_y = result
            self.phase = "kill"
            return True
        return False

    def hunt_and_kill(self) -> list[list[str]]:
        """
        Generate a maze using the Hunt and Kill algorithm.

        Returns:
            Generated maze grid.
        """
        while self.phase != "done":
            if not self.started:
                self.current_x = self.rand.randint(0, self.width - 1)
                self.current_y = self.rand.randint(0, self.height - 1)
                self.visited[self.current_y][self.current_x] = True
                self.started = True
            if self.phase == "kill":
                again = self.kill()
                if not again:
                    self.phase = "hunt"
            elif self.phase == "hunt":
                result = self.hunt()
                if result is None:
                    self.phase = "done"
                    self.save(self.hexa_maze())
                else:
                    self.current_x, self.current_y = result
                    self.phase = "kill"
        return self.hexa_maze()

    def init_backtracking(self) -> None:
        """Initialize the DFS backtracking algorithm."""
        x = self.rand.randint(0, self.width - 1)
        y = self.rand.randint(0, self.height - 1)
        while (x, y) in self.protected:
            x = self.rand.randint(0, self.width - 1)
            y = self.rand.randint(0, self.height - 1)
        self.visited[y][x] = True
        self.stack = [(x, y)]
        self.current_x, self.current_y = x, y

    def step_backtracking(self) -> bool:
        """
        Execute one step of DFS backtracking.

        Returns:
            True if generation continues.
        """
        if not self.stack:
            self.phase = "done"
            self.generated = True
            if not self.perfect:
                self._make_imperfect()
            return False
        x, y = self.stack[-1]
        self.current_x, self.current_y = x, y
        neighbors = self.get_neighbors(x, y)
        if neighbors:
            xn, yn = self.rand.choice(neighbors)
            self.remove_wall(x, y, xn, yn)
            self.stack.append((xn, yn))
        else:
            self.stack.pop()
        return True

    def backtracking(self) -> list[list[str]]:
        """
        Generate a maze using recursive backtracking (DFS).

        Returns:
            Generated maze grid.
        """
        stack: list[tuple[int, int]] = []
        x = self.rand.randint(0, self.width - 1)
        y = self.rand.randint(0, self.height - 1)
        while (x, y) in self.protected:
            x = self.rand.randint(0, self.width - 1)
            y = self.rand.randint(0, self.height - 1)
        self.visited[y][x] = True
        stack.append((x, y))
        while stack:
            x, y = stack[-1]
            neighbors = self.get_neighbors(x, y)
            if neighbors:
                xn, yn = self.rand.choice(neighbors)
                self.remove_wall(x, y, xn, yn)
                self.visited[yn][xn] = True
                stack.append((xn, yn))
            else:
                stack.pop()
        self.generated = True
        if not self.perfect:
            self._make_imperfect()
        grid = self.hexa_maze()
        self.save(grid)
        return grid

    def save(self, grid: list[list[str]]) -> None:
        """
        Save the maze to a file in the format required by the subject.

        Format:
            - One hex digit per cell, no separator, one row per line.
            - Empty line.
            - Entry coordinates (x,y).
            - Exit coordinates (x,y).
            - Shortest path as a string of N/E/S/W letters.

        Args:
            grid: Maze grid to save.
        """
        try:
            with open(self.output_file, "w") as f:
                for row in grid:
                    f.write("".join(row) + "\n")

                entry_x, entry_y = self.entry
                exit_x, exit_y = self.exit

                f.write("\n")
                f.write(f"{entry_x},{entry_y}\n")
                f.write(f"{exit_x},{exit_y}\n")

                if self.path:
                    directions = self.path_to_directions()
                    f.write("".join(directions) + "\n")
        except OSError as e:
            print(f"Error - {self.output_file} not created: {e}")

    def path_to_directions(self) -> list[str]:
        """
        Convert a path into cardinal directions.

        Returns:
            List of directions (N, S, E, W).
        """
        directions: list[str] = []
        for i in range(len(self.path) - 1):
            x1, y1 = self.path[i]
            x2, y2 = self.path[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            if dx == 1:
                directions.append("E")
            elif dx == -1:
                directions.append("W")
            elif dy == 1:
                directions.append("S")
            elif dy == -1:
                directions.append("N")
        return directions

    def solve(self) -> None:
        """
        Solve the maze using BFS and store the shortest path.

        Internal grid bit encoding:
            bit0=West, bit1=South, bit2=East, bit3=North.
        """
        start = (int(self.entry[0]), int(self.entry[1]))
        end = (int(self.exit[0]), int(self.exit[1]))
        queue: deque[tuple[int, int]] = deque([start])
        parent: dict[tuple[int, int], Optional[tuple[int, int]]] = {
            start: None
        }
        while queue:
            cur = queue.popleft()
            if cur == end:
                node: Optional[tuple[int, int]] = cur
                path: list[tuple[int, int]] = []
                while node is not None:
                    path.append(node)
                    node = parent[node]
                self.path = list(reversed(path))
                return
            x, y = cur
            cell = self.grid[y][x]
            # bit0=West(x-1), bit1=South(y+1), bit2=East(x+1), bit3=North(y-1)
            for nx, ny, bit in [
                (x - 1, y, 0),   # West
                (x, y + 1, 1),   # South
                (x + 1, y, 2),   # East
                (x, y - 1, 3),   # North
            ]:
                if not (cell >> bit) & 1:
                    nb = (nx, ny)
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if nb not in parent:
                            parent[nb] = cur
                            queue.append(nb)
        self.path = []

    def init_solve(self) -> None:
        """Initialize data structures for solving the maze using BFS."""
        start = (int(self.entry[0]), int(self.entry[1]))
        self._bfs_end = (int(self.exit[0]), int(self.exit[1]))
        self._bfs_queue = deque([start])
        self._bfs_parent = {start: None}
        self.explored = set()
        self.frontier = {start}
        self.solve_phase = "solving"
        self.path = []
        self.path_index = 0

    def step_solve(self) -> bool:
        """
        Execute one step of BFS solving.

        Returns:
            True if solving continues.
        """
        if self.solve_phase == "tracing":
            if self.path_index < len(self.path):
                self.path_index += 1
            else:
                self.solve_phase = "done"
            return True

        if (
            self.solve_phase != "solving"
            or self._bfs_queue is None
            or self._bfs_parent is None
        ):
            self.solve_phase = "done"
            return False

        if not self._bfs_queue:
            self.solve_phase = "done"
            return False

        cur = self._bfs_queue.popleft()
        self.frontier.discard(cur)
        self.explored.add(cur)

        if cur == self._bfs_end:
            node: Optional[tuple[int, int]] = cur
            path: list[tuple[int, int]] = []
            while node is not None:
                path.append(node)
                node = self._bfs_parent[node]
            self.path = list(reversed(path))
            self.path_index = 0
            self.solve_phase = "tracing"
            return True

        x, y = cur
        cell = self.grid[y][x]
        # bit0=West(x-1), bit1=South(y+1), bit2=East(x+1), bit3=North(y-1)
        for nx, ny, bit in [
            (x - 1, y, 0),
            (x, y + 1, 1),
            (x + 1, y, 2),
            (x, y - 1, 3),
        ]:
            if not (cell >> bit) & 1:
                nb = (nx, ny)
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if nb not in self._bfs_parent:
                        self._bfs_parent[nb] = cur
                        self._bfs_queue.append(nb)
                        self.frontier.add(nb)
        return True
