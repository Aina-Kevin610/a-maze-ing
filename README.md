*This project has been created as part of the 42 curriculum by airandri.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python 3. Given a configuration file,
it generates a maze (optionally perfect, with a single path between entry and
exit), saves it to a file in hexadecimal wall format, and displays it visually
in a graphical window using the MLX library. The maze always contains a visible
"42" pattern drawn by fully closed cells.

Supported generation algorithms: DFS/Backtracking, Hunt & Kill, Prim's.

## Instructions

### Requirements

- Python 3.10 or later
- The `mlx` wheel is bundled in the repository (`mlx-2.2-py3-none-any.whl`)

### Installation and run

```bash
make install   # create venv + install deps
make run       # run with default config.txt
```

Or manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 a_maze_ing.py config.txt
```

### Other Makefile targets

```bash
make debug       # run under pdb
make lint        # flake8 + mypy
make lint-strict # flake8 + mypy --strict
make build       # build the mazegen wheel
make clean       # remove __pycache__ and .mypy_cache
make fclean      # clean + remove .venv, dist, build, maze.txt
```

## Configuration file format

One `KEY=VALUE` pair per line. Lines starting with `#` are comments.

| Key | Required | Description | Example |
|---|---|---|---|
| `WIDTH` | yes | Maze width in cells | `WIDTH=30` |
| `HEIGHT` | yes | Maze height in cells | `HEIGHT=25` |
| `ENTRY` | yes | Entry coordinates x,y | `ENTRY=0,0` |
| `EXIT` | yes | Exit coordinates x,y | `EXIT=19,19` |
| `OUTPUT_FILE` | yes | Output filename (`.txt`) | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | yes | Single path between entry/exit | `PERFECT=False` |
| `ALGO` | no | Generation algorithm | `ALGO=DFS` |
| `SEED` | no | RNG seed for reproducibility | `SEED=42` |
| `SPEED` | no | Animation speed (frames/step, ≥1) | `SPEED=100` |
| `PATTERN` | no | Pattern to embed (uppercase/digit) | `PATTERN=42` |

Available algorithms: `DFS`, `backtracking`, `hunt_and_kill`, `prim`.

Default config file (`config.txt`) is included in the repository.

## Output file format

```
<hex row 0>
<hex row 1>
...
<hex row HEIGHT-1>

<entry_x>,<entry_y>
<exit_x>,<exit_y>
<path as NESW letters>
```

Each hex digit encodes walls: bit0=North, bit1=East, bit2=South, bit3=West.
1 = wall closed, 0 = wall open.

## Maze generation algorithm

The default algorithm is **DFS Recursive Backtracking**:

1. Start from a random unprotected cell.
2. Push it on a stack and mark it visited.
3. While the stack is not empty: pick the top cell, choose a random unvisited
   neighbour, remove the wall between them, push the neighbour.
4. If no unvisited neighbour exists, pop the stack (backtrack).

**Why DFS?** It produces mazes with long winding corridors and a single
solution path (perfect maze), which makes the path visually satisfying and
easy to verify. It is also straightforward to implement step-by-step for
animation purposes. Hunt & Kill and Prim are included as bonuses for variety.

## Graphical controls

| Key | Action |
|---|---|
| `P` | Show / hide solution path |
| `Enter` | Regenerate a new maze |
| `Space` | Cycle wall colour |
| `ESC` | Quit |

## Reusable module — mazegen

The `maze_generator/` package contains the standalone `MazeGenerator` class
(via `Maze`) that can be installed and imported independently.

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Usage

```python
from maze_generator.maze_gen import Maze

# Basic usage with a config file
maze = Maze(filename="config.txt")
maze.backtracking()          # generate
maze.solve()                 # find shortest path
print(maze.path)             # list of (x, y) tuples
print(maze.hexa_maze())      # hex grid ready to save
```

### Custom parameters

Pass a different config file or set `pattern_`:

```python
maze = Maze(pattern_="AB", filename="my_config.txt")
```

Seeds are controlled via the config file (`SEED=42`) for reproducibility.

### Accessible attributes after generation

| Attribute | Type | Description |
|---|---|---|
| `maze.grid` | `list[list[int]]` | Raw wall bitfield grid |
| `maze.path` | `list[tuple[int,int]]` | BFS solution path |
| `maze.protected` | `set[tuple[int,int]]` | Pattern cell coordinates |
| `maze.width`, `maze.height` | `int` | Dimensions |
| `maze.entry`, `maze.exit` | `tuple[str,str]` | Coordinates |

### Rebuilding the package

```bash
pip install build
python3 -m build --wheel
# output: dist/mazegen-1.0.0-py3-none-any.whl
```

Or via the Makefile: `make build`.

## Bonuses implemented

1. Multiple generation algorithms (DFS, Hunt & Kill, Prim)
2. Step-by-step animated generation via MLX loop hook
3. Configurable animation speed (`SPEED` key)
4. Custom pattern support (any uppercase letter or digit string)
5. Colour cycling for walls

## Team and project management

**Team:** solo project (airandri).

**Roles:** full stack — parsing, generation algorithms, MLX rendering,
packaging, README.

**Planning:** the project was split into four phases:
1. Config parsing and validation (day 1)
2. Maze generation algorithms (days 2–3)
3. MLX rendering and keyboard interactions (day 4)
4. Packaging, README, and polish (day 5)

The animation step took longer than expected because the loop hook required
careful step-by-step refactoring of each algorithm.

**What worked well:** separating the generation logic into a standalone module
early made packaging straightforward. The BFS solver was easy to add once the
grid encoding was stable.

**What could be improved:** the open-area constraint (no 3×3 empty zone) is
not enforced programmatically; it would require a post-generation checker.

**Tools used:** Python 3.13, Neovim + Pyright + mypy, flake8, git.

## Resources

- Wilson, D. B. (1996). *Generating random spanning trees more quickly than
  the cover time.* STOC.
- Jamis Buck — [Maze Generation algorithms](https://weblog.jamisbuck.org/2011/1/17/maze-generation-aldous-broder-algorithm)
- Python docs: `collections.deque`, `random.Random`
- MLX Python bindings documentation: bundled in `.venv/lib/.../mlx/docs/`

**AI usage:** Claude was used to review the project structure, identify bugs
in wall-bit encoding and the double `__init_42()` call, and generate the
corrected versions of `maze_gen.py`, `parsing.py`, `utils.py`, and this
README. All generated code was read, understood, and validated manually before
inclusion.
