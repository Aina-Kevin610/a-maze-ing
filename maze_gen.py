from parsing import parse_config
import random


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


    def __init_grid(self) -> list[list[int]]:
        return [[15 for _ in range(self.width)] for _ in range(self.height)]


    def generate(self) -> None:
        if self.algo == "hunt_and_kill":
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
        way = [
            ( 0, -1), 
            ( 1,  0),
            ( 0,  1),
            (-1,  0)
        ]
        neighbors = []
        for dx, dy in way:
            xn, yn = dx + x, dy + y
            if 0 <= xn < self.width and 0 <= yn < self.height and not self.visited[yn][xn]:
                neighbors.append((xn, yn))
        return neighbors


    def get_visited_neighbors(self, x, y):
        way = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        neighbors = []
        for dx, dy in way:
            xn, yn = dx + x, dy + y
            if 0 <= xn < self.width and 0 <= yn < self.height and self.visited[yn][xn]:
                neighbors.append((xn, yn))
        return neighbors


    def kill(self):
        neighbors = self.get_neighbors(self.current_x, self.current_y)
        if not neighbors:
            return False
        xn, yn = random.choice(neighbors)
        self.current_x, self.current_y, self.wall = self.remove_wall(self.current_x, self.current_y, xn, yn)
        return True


    def hunt(self):
        i = 0
        while i < self.height:
            j = 0
            while j < self.width:
                if not self.visited[i][j]:
                    v_neighbors = self.get_visited_neighbors(j, i)
                    if v_neighbors:
                        xn, yn = random.choice(v_neighbors)
                        self.remove_wall(j, i, xn, yn)
                        return j, i 
                j += 1
            i += 1
        return None


    def hunt_and_kill(self) -> list[list[str]]:
        print("=== Hunt and Kill ===")
        self.current_x, self.current_y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        self.visited[self.current_y][self.current_x] = True
        while not self.is_all_visited():
            self.kill()
            if self.is_all_visited():
                break
            result = self.hunt()
            if result is None:
                break
            self.current_x, self.current_y = result
        self.save(self.hexa_maze())
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