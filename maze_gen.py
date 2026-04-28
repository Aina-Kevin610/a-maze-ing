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


    def __init_grid(self) -> list[list[int]]:
        return [[15 for _ in range(self.width)] for _ in range(self.height)]


    def generate(self) -> None:
        if self.algo == "hunt_and_kill":
            return self.hunt_and_kill()


    def hexa_maze(self, grid) -> list[list[str]]:
        return [[format(grid[row][col], 'X') for row in range(self.width)] for col in range(self.height)]


    def is_all_visited(self, visited) -> bool:
        for row in visited:
            if False in row:
                return False
        return True


    def init_visited(self) -> list[list[bool]]:
        return [[False for _ in range(self.width)] for _ in range(self.height)]
    

    def remove_wall(self, grid, visited, x, y, xn, yn):
        dx, dy = xn - x, yn - y
        if dx == 1:
            dir = 0b0010
            opp = 0b1000
        elif dx == -1:
            dir = 0b1000
            opp = 0b0010
        elif dy == 1:
            dir = 0b0100
            opp = 0b0001
        elif dy == -1:
            dir = 0b0001
            opp = 0b0100
        grid[y][x] &= ~dir
        grid[yn][xn] &= ~opp
        visited[y][x] = True
        visited[yn][xn] = True
        return xn, yn


    def get_neighbors(self, visited, x, y):
        way = [
            ( 0, -1), 
            ( 1,  0),
            ( 0,  1),
            (-1,  0)
        ]
        neighbors = []
        for dx, dy in way:
            xn, yn = dx + x, dy + y
            if 0 <= xn < self.width and 0 <= yn < self.height and not visited[yn][xn]:
                neighbors.append((xn, yn))
        return neighbors


    def get_visited_neighbors(self, visited, x, y):
        way = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        neighbors = []
        for dx, dy in way:
            xn, yn = dx + x, dy + y
            if 0 <= xn < self.width and 0 <= yn < self.height and visited[yn][xn]:
                neighbors.append((xn, yn))
        return neighbors


    def kill(self, grid, visited, x, y):
        while True:
            neighbors = self.get_neighbors(visited, x, y)
            if not neighbors:
                return x, y
            xn, yn = random.choice(neighbors)
            x, y = self.remove_wall(grid, visited, x, y, xn, yn)


    def hunt(self, grid, visited):
        i = 0
        while i < self.height:
            j = 0
            while j < self.width:
                if not visited[i][j]:
                    v_neighbors = self.get_visited_neighbors(visited, j, i)
                    if v_neighbors:
                        xn, yn = random.choice(v_neighbors)
                        self.remove_wall(grid, visited, j, i, xn, yn)
                        return j, i   
                j += 1
            i += 1
        return None


    def hunt_and_kill(self) -> list[list[str]]:
        print("=== Hunt and Kill ===")
        grid = self.__init_grid()
        visited = self.init_visited()
        x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        visited[y][x] = True
        while not self.is_all_visited(visited):
            x, y = self.kill(grid, visited, x, y)
            if self.is_all_visited(visited):
                break
            result = self.hunt(grid, visited)
            if result is None:
                break
            x, y = result
        return self.hexa_maze(grid)
    

    def save(self, grid) -> None:
        print("Saving maze in", self.output_file,"...")
        try:
            f = open(self.output_file, "w")
            for x in grid:
                f.write(str(x).replace("[", "").replace("]", "").replace(",", "").replace("'", "").replace(" ", "") + "\n")
            f.write(f"\n{str(self.entry).replace("(", "").replace(")", "").replace("'", "")}")
            f.write(f"\n{str(self.exit).replace("(", "").replace(")", "").replace("'", "")}")
        except Exception:
            pass
        finally:
            f.close()