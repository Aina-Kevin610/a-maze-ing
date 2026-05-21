from collections import deque
import random
import os
from typing import Optional, Any

from parsing import parse_config
from .pattern import Pattern


class ConfigError(Exception):
    pass

class Maze:

    def __init__(
        self,
        pattern_: str = "42",
    ) -> None:
        config = parse_config()

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

        if (
            self.height >= len(self.pattern_) * 5
            or (
                self.width >= len(self.pattern_) * 5
                and self.pattern_ != "42"
            )
        ):
            self.__init_42()
        else:
            print(
                f"Pattern [{self.pattern_}] cannot be contained within "
                "the maze! (10 x 10 is required)"
            )
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

        if self.exit in self.protected:
            print("Error!")
            os._exit(0)

    def __init_42(self) -> None:
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
        i = 0
        while i < len(pat):
            j = 0
            while j < len(pat[i]):
                if pat[i][j] == 1:
                    self.protected.add(
                        (x_grid - offset_x + j, y_grid - offset_y + i)
                    )
                j += 1
            i += 1
        x, y = self.entry
        if (int(x), int(y)) in self.protected:
            print("Error - Inaccessible entry!")
            os._exit(0)
        x, y = self.exit
        if (int(x), int(y)) in self.protected:
            print("Error - Inaccessible exit!")
            os._exit(0)

    def __init_grid(self) -> list[list[int]]:
        return [[15 for _ in range(self.width)] for _ in range(self.height)]

    def generate(self) -> list[list[int]]:
        if self.algo == "hunt_and_kill":
            return self.hunt_and_kill()
        if self.algo in ("backtracking", "DFS"):
            return self.backtracking()
        if self.algo == "prim":
            return self.prim()
        return self.grid

    def hexa_maze(self) -> list[list[str]]:
        def remap(v: int) -> int:
            west  = (v >> 0) & 1
            south = (v >> 1) & 1
            east  = (v >> 2) & 1
            north = (v >> 3) & 1
            return (north << 0) | (east << 1) | (south << 2) | (west << 3)

        return [
            [format(remap(self.grid[row][col]), "X") for col in range(self.width)]
            for row in range(self.height)
        ]

    def is_all_visited(self) -> bool:
        return all(all(row) for row in self.visited)

    def __init_visited(self) -> list[list[bool]]:
        return [[False for _ in range(self.width)] for _ in range(self.height)]

    def _make_imperfect(self, rate: float = 0.15) -> None:
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
        print("=== Prim ===")
        self.init_prim()
        while self.prim_frontier:
            self.step_prim()
        grid = self.hexa_maze()
        self.save(grid)
        return grid

    def kill(self) -> bool:
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
        print("=== Hunt and Kill ===")
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
        x = self.rand.randint(0, self.width - 1)
        y = self.rand.randint(0, self.height - 1)
        while (x, y) in self.protected:
            x = self.rand.randint(0, self.width - 1)
            y = self.rand.randint(0, self.height - 1)
        self.visited[y][x] = True
        self.stack = [(x, y)]
        self.current_x, self.current_y = x, y

    def step_backtracking(self) -> bool:
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
        print("Saving maze in", self.output_file, "...")
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                for row in grid:
                    line = (
                        str(row)
                        .replace("[", "")
                        .replace("]", "")
                        .replace(",", "")
                        .replace("'", "")
                        .replace(" ", "")
                    )
                    f.write(line + "\n")
                entry = (
                    str(self.entry)
                    .replace("(", "")
                    .replace(")", "")
                    .replace("'", "")
                )
                exit_ = (
                    str(self.exit)
                    .replace("(", "")
                    .replace(")", "")
                    .replace("'", "")
                )
                f.write(f"\n{entry}")
                f.write(f"\n{exit_}")
                if self.path:
                    directions = self.path_to_directions()
                    f.write(f"\n{''.join(directions)}")
        except OSError:
            print(f"Error - {self.output_file} not created !")

    def path_to_directions(self) -> list[str]:
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
            for nx, ny, walled in [
                (x - 1, y, cell & 1),
                (x, y + 1, (cell >> 1) & 1),
                (x + 1, y, (cell >> 2) & 1),
                (x, y - 1, (cell >> 3) & 1),
            ]:
                nb = (nx, ny)
                if not walled and nb not in parent:
                    parent[nb] = cur
                    queue.append(nb)
        self.path = []

    def init_solve(self) -> None:
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
        for nx, ny, walled in [
            (x - 1, y, cell & 1),
            (x, y + 1, (cell >> 1) & 1),
            (x + 1, y, (cell >> 2) & 1),
            (x, y - 1, (cell >> 3) & 1),
        ]:
            nb = (nx, ny)
            if not walled and nb not in self._bfs_parent:
                self._bfs_parent[nb] = cur
                self._bfs_queue.append(nb)
                self.frontier.add(nb)
        return True