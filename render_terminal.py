import sys
import time
import threading
import tty
import termios
import random
from typing import Any

from maze_generator.maze_gen import Maze



RESET       = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR       = "\033[H\033[2J"


def _fg(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


def _bg(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"


def _lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)

_BG = (0, 0, 0)

_WALL_COLORS = [
    (0,   0,   255),
    (255, 255, 255),
    (255, 0,   0),
    (0,   255, 0),
    (255, 255, 0),
    (0,   255, 255),
    (255, 0,   255),
    (139, 0,   0),
    (220, 20,  60),
    (178, 34,  34),
]

_COL_CURRENT   = _bg(0,   102, 255)
_COL_FRONTIER  = _bg(255, 200, 0)
_COL_EXPLORED  = _bg(
    _lerp(_BG[0], 245, 0.15),
    _lerp(_BG[1], 7,   0.15),
    _lerp(_BG[2], 79,  0.15),
)
_COL_ENTRY     = _bg(255, 255, 255) + _fg(0, 0, 0)
_COL_EXIT      = _bg(0,   255, 255) + _fg(0, 0, 0)
_COL_PROTECTED = _bg(180, 180, 180) + _fg(0, 0, 0)

_PATH_START = (0x7F, 0xE8, 0x00)
_PATH_END   = (0x00, 0x40, 0xFF)


def _path_bg(t: float) -> str:
    r = _lerp(_PATH_START[0], _PATH_END[0], t)
    g = _lerp(_PATH_START[1], _PATH_END[1], t)
    b = _lerp(_PATH_START[2], _PATH_END[2], t)
    return _bg(r, g, b)



class TerminalDrawingMaze:

    def __init__(self, maze: Maze) -> None:
        self.maze        = maze
        self.saved       = False
        self.regenerate  = False
        self._running    = True
        self._wall_color = _WALL_COLORS[0]
        self._path_map:  dict[tuple[int, int], int] = {}


    def _col_wall(self) -> str:
        return _fg(*self._wall_color)

    def _build_path_map(self) -> None:
        self._path_map = {
            pos: i
            for i, pos in enumerate(
                self.maze.path[: self.maze.path_index]
            )
        }

    def _cell_bg(
        self,
        x: int,
        y: int,
        entry: tuple[int, int],
        exit_: tuple[int, int],
    ) -> str:
        pos = (x, y)

        if pos == entry:
            return _COL_ENTRY
        if pos == exit_:
            return _COL_EXIT
        if (
            self.maze.phase != "done"
            and x == self.maze.current_x
            and y == self.maze.current_y
        ):
            return _COL_CURRENT
        if self.maze.generated and pos in self.maze.protected:
            return _COL_PROTECTED
        if pos in self._path_map:
            total = max(self.maze.path_index - 1, 1)
            t = self._path_map[pos] / total
            return _path_bg(t)
        if pos in self.maze.frontier:
            return _COL_FRONTIER
        if pos in self.maze.explored:
            return _COL_EXPLORED
        return ""


    def draw_cell(self) -> None:
        maze = self.maze
        W    = maze.width
        H    = maze.height

        entry = (int(maze.entry[0]), int(maze.entry[1]))
        exit_ = (int(maze.exit[0]),  int(maze.exit[1]))

        self._build_path_map()

        wall = self._col_wall()
        lines: list[str] = []

        for y in range(H):
            top = ""
            mid = ""

            for x in range(W):
                visited = maze.visited[y][x]
                cell    = maze.grid[y][x] if visited else 0b1111

                north = (cell >> 3) & 1
                west  =  cell       & 1
                bg    = self._cell_bg(x, y, entry, exit_) if visited else ""

                top += wall + "+" + ("--" if north else "  ") + RESET
                mid += wall + ("|" if west else " ") + RESET
                mid += bg + "  " + RESET

            rc   = maze.grid[y][W - 1] if maze.visited[y][W - 1] else 0b1111
            east = (rc >> 2) & 1
            top += wall + "+" + RESET
            mid += wall + ("|" if east else " ") + RESET

            lines.append(top)
            lines.append(mid)

        bot = ""
        for x in range(W):
            c     = maze.grid[H - 1][x] if maze.visited[H - 1][x] else 0b1111
            south = (c >> 1) & 1
            bot  += wall + "+" + ("--" if south else "  ") + RESET
        bot += wall + "+" + RESET
        lines.append(bot)

        sys.stdout.write(CLEAR + "\r\n".join(lines) + "\r\n")
        sys.stdout.flush()


    def _read_keys(self) -> None:
        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while self._running:
                ch = sys.stdin.read(1)
                if ch == " ":
                    self._wall_color = random.choice(_WALL_COLORS)
                elif ch == "\r":
                    if not self.regenerate:
                        self.regenerate = True
                elif ch in ("\x1b", "q"):
                    self._running = False
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


    def run(
        self,
        loop_hook: Any,
        param: list[Any],
        fps: int = 60,
    ) -> None:
        sys.stdout.write(HIDE_CURSOR)
        sys.stdout.flush()

        key_thread = threading.Thread(
            target=self._read_keys,
            daemon=True,
        )
        key_thread.start()

        delay = 1.0 / fps

        try:
            while self._running:
                loop_hook(param)
                time.sleep(delay)
        finally:
            sys.stdout.write(SHOW_CURSOR + "\r\n")
            sys.stdout.flush()