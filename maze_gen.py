from parsing import parse_config
import random


DIGITS = {
    '4': [[1,0,0,1,0],
          [1,0,0,1,0],
          [1,1,1,1,0],
          [0,0,0,1,0],
          [0,0,0,1,0]],

    '2': [[1,1,1,1,0],
          [0,0,0,1,0],
          [1,1,1,1,0],
          [1,0,0,0,0],
          [1,1,1,1,0]]
}

class Maze:
    def __init__(self, config: dict = parse_config()) -> None:
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
        self.__init_42()


    def __init_42(self):
        scale_x = self.width  // 11
        scale_y = self.height // 7
        scale   = min(scale_x, scale_y) // 2

        total_w = 11 * scale
        total_h = 7  * scale
        start_x = (self.width  - total_w) // 2
        start_y = (self.height - total_h) // 2

        char_idx = 0
        for char in ['4', '2']:
            digit = DIGITS[char]
            row_i = 0
            while row_i < len(digit):
                col_i = 0
                while col_i < len(digit[row_i]):
                    if digit[row_i][col_i] == 1:
                        bx = start_x + char_idx * 6 * scale + col_i * scale
                        by = start_y + row_i * scale
                        sy = 0
                        while sy < scale:
                            sx = 0
                            while sx < scale:
                                self.protected.add((bx + sx, by + sy))
                                self.visited[by + sy][bx + sx] = True
                                sx += 1
                            sy += 1
                    col_i += 1
                row_i += 1
            char_idx += 1


    def __init_grid(self) -> list[list[int]]:
        return [[15 for _ in range(self.width)] for _ in range(self.height)]


    def generate(self) -> list[list[int]]: 
        if self.algo == "hunt_and_kill":
            self.save(self.hunt_and_kill())
        return self.grid


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


    def kill(self):
        neighbors = self.get_neighbors(self.current_x, self.current_y)
        if not neighbors:
            return False
        xn, yn = random.choice(neighbors)
        while (xn, yn) in self.protected:
            xn, yn = random.choice(neighbors)
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
                        xn, yn = random.choice(v_neighbors)
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
                return False
            self.current_x, self.current_y = result
            self.phase = "kill"
            return True
        return False


    def hunt_and_kill(self) -> list[list[str]]:
        print("=== Hunt and Kill ===")
        while self.phase != "done":
            if not self.started:
                self.current_x = random.randint(0, self.width - 1)
                self.current_y = random.randint(0, self.height - 1)
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


    def save(self, grid) -> None:
        print("Saving maze in", self.output_file,"...")
        try:
            f = open(self.output_file, "w")
            for x in grid:
                f.write(str(x).replace("[", "").replace("]", "").replace(",", "").replace("'", "").replace(" ", "") + "\n")
            f.write(f"\n{str(self.entry).replace("(", "").replace(")", "").replace("'", "")}")
            f.write(f"\n{str(self.exit).replace("(", "").replace(")", "").replace("'", "")}")
        except Exception:
            print(f"Error - {self.output_file} not created !")
        finally:
            f.close()