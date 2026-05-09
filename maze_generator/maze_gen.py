from parsing import parse_config
from collections import deque
import random
import os
from .pattern import Pattern


class ConfigError(Exception):
    pass


class Maze:
    def __init__(self, pattern_="42", config: dict = parse_config()) -> None:
        self.pattern_ = config.get("PATTERN", pattern_) or pattern_ 
        self.width = int(config["WIDTH"])
        self.height = int(config["HEIGHT"])
        self.entry = config["ENTRY"]
        self.exit = config["EXIT"]
        self.output_file = config["OUTPUT_FILE"]
        self.perfect = config["PERFECT"]
        self.algo = config["ALGO"]
        self.grid = self.__init_grid()
        self.visited = self.__init_visited()
        self.current_x = 0
        self.current_y = 0
        self.phase = "kill"
        self.wall = 0b1111
        self.started = False
        self.protected = set()
        self.seed = config["SEED"]
        self.path = []
        self.path_index = 0
        self.explored = set()
        self.frontier = set()
        self.solve_phase = "idle"
        self._bfs_queue = None
        self._bfs_parent = None
        self._bfs_end = None
        if (self.height >= len(self.pattern_) * 5 or self.width >= len(self.pattern_) * 5 and self.pattern_ != "42") :
            self.__init_42()
        else:
            print(f"Pattern [{self.pattern_}] cannot be contained within the maze! (10 x 10 is requiered)")
        if self.height >= 10 and self.width >= 10:
            self.__init_42()
        else:
            print(f"Pattern [{self.pattern_}] cannot be contained within the maze! (10 x 10 is requiered)")
        self.rand: random.Random = random.Random()
        if self.seed:
            self.rand = random.Random(self.seed)
        self.generated = False
        if self.exit in self.protected:
            print("Error!")
            os._exit(0)


    def __init_42(self):
        p = Pattern(self.pattern_)
        x_grid = self.width // 2
        y_grid = self.height // 2
        pat = p.create_merged()
        if not pat or not pat[0]:
            print(f"Pattern [{self.pattern_}] not recognized, skipping. (must be uppercase or number)")
            return
        offset_x = len(pat[0]) // 2
        offset_y = len(pat) // 2
        i = 0
        while i < len(pat):
            j = 0
            while j < len(pat[i]):
                if pat[i][j] == 1:
                    if self.width <= 15:
                        self.protected.add((x_grid - offset_x + j , y_grid - offset_y + i ))
                    else:
                        self.protected.add((x_grid - offset_x + j, y_grid - offset_y + i))
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
        elif self.algo == "backtracking" or self.algo == "DFS":
            return self.backtracking()
        elif self.algo == "prim":
            return self.prim()

    def hexa_maze(self) -> list[list[str]]:
        return [[format(self.grid[row][col], 'X') for col in range(self.width)] for row in range(self.height)]


    def is_all_visited(self) -> bool:
        for row in self.visited:
            if False in row:
                return False
        return True


    def __init_visited(self) -> list[list[bool]]:
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        return visited
    

    def remove_wall(self, x, y, xn, yn):
        dx, dy = xn - x, yn - y
        if dx == 1:
            dir = 0b0100
            opp = 0b0001
        elif dx == -1:
            dir = 0b0001
            opp = 0b0100
        elif dy == 1:
            dir = 0b0010
            opp = 0b1000
        elif dy == -1:
            dir = 0b1000
            opp = 0b0010
        self.grid[y][x] &= ~dir
        self.grid[yn][xn] &= ~opp
        self.visited[y][x] = True
        self.visited[yn][xn] = True
        return xn, yn, opp

    def get_neighbors(self, x, y):
        way = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        neighbors = []
        for dx, dy in way:
            xn, yn = dx + x, dy + y
            if 0 <= xn < self.width and 0 <= yn < self.height \
            and not self.visited[yn][xn] \
            and (xn, yn) not in self.protected:
                neighbors.append((xn, yn))
        return neighbors

    def get_visited_neighbors(self, x, y):
        way = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        neighbors = []
        for dx, dy in way:
            xn, yn = dx + x, dy + y
            if 0 <= xn < self.width and 0 <= yn < self.height \
            and self.visited[yn][xn] \
            and (xn, yn) not in self.protected:
                neighbors.append((xn, yn))
        return neighbors


    def init_prim(self):
        x = self.rand.randint(0, self.width - 1)
        y = self.rand.randint(0, self.height - 1)
        while (x, y) in self.protected:
            x = self.rand.randint(0, self.width - 1)
            y = self.rand.randint(0, self.height - 1)
        self.visited[y][x] = True
        self.current_x, self.current_y = x, y
        self._prim_set      = {(x, y)}
        self.prim_frontier  = [(x, y)]
        self._expand_prim(x, y)

    def _expand_prim(self, x, y):
        for dx, dy in [(0,-1),(1,0),(0,1),(-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height \
            and not self.visited[ny][nx] \
            and (nx, ny) not in self.protected \
            and (nx, ny) not in self._prim_set:
                self._prim_set.add((nx, ny))
                self.prim_frontier.append((nx, ny))

    def step_prim(self) -> bool:
        if not self.prim_frontier:
            self.phase = "done"
            self.generated = True
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

    def prim(self):
        print("=== Prim ===")
        self.init_prim()
        while self.prim_frontier:
            self.step_prim()
        grid = self.hexa_maze()
        self.save(grid)
        return grid


    def kill(self):
        neighbors = self.get_neighbors(self.current_x, self.current_y)
        if not neighbors:
            return False
        xn, yn = self.rand.choice(neighbors)
        while (xn, yn) in self.protected:
            xn, yn = self.rand.choice(neighbors)
        self.current_x, self.current_y, self.wall = self.remove_wall(self.current_x, self.current_y, xn, yn)
        return True

    def hunt(self):
        i = 0
        while i < self.height:
            j = 0
            while j < self.width:
                if not self.visited[i][j] and (j, i) not in self.protected:
                    v_neighbors = self.get_visited_neighbors(j, i)
                    if v_neighbors:
                        xn, yn = self.rand.choice(v_neighbors)
                        self.remove_wall(j, i, xn, yn)
                        return j, i 
                j += 1
            i += 1
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

    def init_backtracking(self):
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

    def backtracking(self):
        stack = []
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
        grid = self.hexa_maze()
        self.save(grid)
        return grid

    def save(self, grid) -> None:
        print("Saving maze in", self.output_file,"...")
        try:
            with open(self.output_file, "w") as f:
                for x in grid:
                    f.write(str(x).replace("[", "").replace("]", "")
                                .replace(",", "").replace("'", "")
                                .replace(" ", "") + "\n")
                entry = str(self.entry).replace("(", "").replace(")", "").replace("'", "")
                exit_ = str(self.exit).replace("(", "").replace(")", "").replace("'", "")
                f.write(f"\n{entry}")
                f.write(f"\n{exit_}")
                if self.path:
                    directions = self.path_to_directions()
                    f.write(f"\n{''.join(directions)}")
        except Exception:
            print(f"Error - {self.output_file} not created !")

    def path_to_directions(self):
        directions = []
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
    
    def solve(self):
        start = (int(self.entry[0]), int(self.entry[1]))
        end   = (int(self.exit[0]),  int(self.exit[1]))
        queue  = deque([start])
        parent = {start: None}
        while queue:
            cur = queue.popleft()
            if cur == end:
                node, path = cur, []
                while node is not None:
                    path.append(node)
                    node = parent[node]
                self.path = list(reversed(path))
                return
            x, y = cur
            cell = self.grid[y][x]
            for nx, ny, walled in [
                (x-1, y,   cell & 1),
                (x,   y+1, (cell >> 1) & 1),
                (x+1, y,   (cell >> 2) & 1),
                (x,   y-1, (cell >> 3) & 1),
            ]:
                nb = (nx, ny)
                if not walled and nb not in parent:
                    parent[nb] = cur
                    queue.append(nb)
        self.path = []

    def init_solve(self):
        start = (int(self.entry[0]), int(self.entry[1]))
        self._bfs_end = (int(self.exit[0]), int(self.exit[1]))
        self._bfs_queue = deque([start])
        self._bfs_parent = {start: None}
        self.explored = set()
        self.frontier = {start}
        self.solve_phase = "solving"
        self.path = []
        self.path_index = 0

    def step_solve(self):
        if self.solve_phase == "tracing":
            if self.path_index < len(self.path):
                self.path_index += 1
            else:
                self.solve_phase = "done"
            return True

        if self.solve_phase != "solving" or not self._bfs_queue:
            self.solve_phase = "done"
            return False

        cur = self._bfs_queue.popleft()
        self.frontier.discard(cur)
        self.explored.add(cur)

        if cur == self._bfs_end:
            node, path = cur, []
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
            (x-1, y,   cell & 1),
            (x,   y+1, (cell >> 1) & 1),
            (x+1, y,   (cell >> 2) & 1),
            (x,   y-1, (cell >> 3) & 1),
        ]:
            nb = (nx, ny)
            if not walled and nb not in self._bfs_parent:
                self._bfs_parent[nb] = cur
                self._bfs_queue.append(nb)
                self.frontier.add(nb)
        return True