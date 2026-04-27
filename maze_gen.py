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
        if self.algo == "DFS":
            self.dfs()


    @staticmethod
    def bin_to_dec(bin:  int, pow: int = 0, result = 0) -> int:
            if pow == 4:
                return result
            result += (bin % 10) * (2**pow)
            return bin_to_dec(bin // 10, pow + 1, result)
    

    @staticmethod
    def dec_to_hex(dec: int, result: str = []) -> str:
        base = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
        if dec >= 16:
            dec_to_hex(dec // 16, result)       
        result += base[dec % 16]
        return str(result)

    def print_maze(self, grid, visited):
        print("=== MAZE ===")
        for row in grid:
            print (row)
        print("=== VISITED MAZE ===")
        for row in visited:
            print (row)


    def init_visited(self) -> list[list[bool]]:
        return [[False for _ in range(self.width)] for _ in range(self.height)]

    def draw_42(self) -> None:
        print("42 drawn")


    def direction(self) -> int:
        direction = {
            "N" : 0b0001,
            "E" : 0b0010,
            "S" : 0b0100,
            "W" : 0b1000
        }
        return random.choice(list(direction.values()))
    

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
        self.print_maze(grid, visited)
        return xn, yn


    def get_neighbors(self, visited, x, y):
        way = [
            ( 0, -1),  # Haut
            ( 1,  0),  # Droite
            ( 0,  1),  # Bas
            (-1,  0)   # Gauche
        ]
        neighbors = []
        for dx, dy in way:
            xn, yn = dx + x, dy + y
            if 0 <= xn < self.width and 0 <= yn < self.height and not visited[yn][xn]:
                neighbors.append([xn, yn])
        return neighbors[0], neighbors[1]


    def dfs(self) -> None:
        grid = self.__init_grid()
        visited: list[list[bool]] = self.init_visited()
        x, y = random.randint(0, self.width), random.randint(0, self.height)
        while not visited[y - 1][x - 1]:
            xn, yn = self.get_neighbors(visited, x, y)
            x, y = self.remove_wall(grid, visited, x, y, xn, yn)
        print(x, y)