from maze_gen import Maze
from render import Drawing

def read_maze(filename: str = "maze.txt") -> str:
    try:
        with open(filename, "r") as f:
            return f.read()
    except FileNotFoundError:
        print("Error - OUTPUT_FILE not generated !")
        return ""

def to_bin(hexa: str):
    return bin(int(hexa, 16))


def main() -> None:
    maze = Maze()
    grid = maze.generate()
    maze.save(grid)
    hexa_maze = read_maze()
    hexa_maze = hexa_maze.split("\n")
    draw = Drawing(maze, 0xffffffff)

    x, y = 0, 0
    for i in range(0, maze.height):
        x = 0
        for j in range(0, maze.width):
            cell = int(hexa_maze[i][j], 16)

            if cell == 0b0001:    # 0x1 - W
                draw.west(x, y)
            elif cell == 0b0010:  # 0x2 - S
                draw.south(x, y)
            elif cell == 0b0011:  # 0x3 - S + W
                draw.south(x, y)
                draw.west(x, y)
            elif cell == 0b0100:  # 0x4 - E
                draw.east(x, y)
            elif cell == 0b0101:  # 0x5 - E + W
                draw.east(x, y)
                draw.west(x, y)
            elif cell == 0b0110:  # 0x6 - E + S
                draw.east(x, y)
                draw.south(x, y)
            elif cell == 0b0111:  # 0x7 - E + S + W
                draw.east(x, y)
                draw.south(x, y)
                draw.west(x, y)
            elif cell == 0b1000:  # 0x8 - N
                draw.north(x, y)
            elif cell == 0b1001:  # 0x9 - N + W
                draw.north(x, y)
                draw.west(x, y)
            elif cell == 0b1010:  # 0xA - N + S
                draw.north(x, y)
                draw.south(x, y)
            elif cell == 0b1011:  # 0xB - N + S + W
                draw.north(x, y)
                draw.south(x, y)
                draw.west(x, y)
            elif cell == 0b1100:  # 0xC - N + E
                draw.north(x, y)
                draw.east(x, y)
            elif cell == 0b1101:  # 0xD - N + E + W
                draw.north(x, y)
                draw.east(x, y)
                draw.west(x, y)
            elif cell == 0b1110:  # 0xE - N + E + S
                draw.north(x, y)
                draw.east(x, y)
                draw.south(x, y)
            elif cell == 0b1111:  # 0xF - tous les murs
                draw.north(x, y)
                draw.east(x, y)
                draw.south(x, y)
                draw.west(x, y)

            x += draw.cell_size_w
        y += draw.cell_size_h

    draw.m.mlx_loop(draw.mlx)


if __name__ == "__main__":
    main()