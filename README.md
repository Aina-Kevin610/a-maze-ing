*This project has been created as part of the 42 curriculum by airandri, fanilran.*

# A-Maze-ing

## Description

**A-Maze-ing** is a Python maze generator and renderer. Given a simple text
configuration file, the program builds a grid-based maze (perfect or
imperfect), solves it with a shortest-path search, and displays it either in
the terminal (ASCII) or in a graphical window (MiniLibX). The maze is also
written to an output file using a compact hexadecimal wall encoding, along
with its entry, exit, and solution path.

Beyond the generator itself, the maze-building logic is packaged as a
standalone, reusable Python module (`mazegen`) that can be installed with
`pip` and reused in other projects.

## Instructions

### Requirements

- Python 3.10+
- A virtual environment (created automatically by the `Makefile`)
- The MiniLibX Python wheel provided with the subject
  (`package/mlx-2.2-py3-none-any.whl`) if you want the graphical `WINDOW`
  render mode

### Setup and run

```bash
make install   # creates .venv and installs dependencies (flake8, mypy, mlx)
make run       # runs: python3 a_maze_ing.py config.txt
```

You can also run it directly once the dependencies are installed:

```bash
python3 a_maze_ing.py config.txt
```

`config.txt` is a plain text configuration file (see format below). Any other
filename can be passed as the single argument.

### Other Makefile targets

| Target        | Description                                                     |
|---------------|-------------------------------------------------------------------|
| `install`     | Create the virtualenv and install all dependencies                |
| `run`         | Run `a_maze_ing.py` with `config.txt`                              |
| `debug`       | Run the program under `pdb`                                       |
| `lint`        | Run `flake8` and `mypy` with the mandatory flags                  |
| `build`       | Build the `mazegen` package (`.whl`) with the `build` module      |
| `clean`       | Remove `maze.txt`, `__pycache__`, and `.mypy_cache`                |
| `fclean`      | `clean` + remove the virtualenv, `dist/`, `build/`, egg-info       |
| `re`          | `fclean` then `install`                                           |

### Interacting with the maze

When rendered in the terminal (`RENDER=ASCII`), a menu lets you:

- `R` — regenerate a new maze
- `H` — show / hide the shortest path
- `C` — change the wall color (white, yellow, magenta, blue)
- `Q` — quit

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Prim's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [Buckblog: Maze Generation series (Jamis Buck)](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
- [Python `typing` module documentation](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Python Packaging User Guide](https://packaging.python.org/)

**Use of AI**: AI assistance (Claude) was used to help debug rendering issues
in `window_render.py` (MLX loop hook registration, color byte-order
consistency, animation flag handling) and to track down an
`UnboundLocalError` in `mazegen.py`'s `solve()` function. It was also used as
a sounding board to review type-hint and docstring consistency across the
package ahead of `flake8`/`mypy` checks. All suggestions were reviewed,
tested, and understood before being kept; no code was merged without being
verified against the subject's requirements.

## Configuration file format

The configuration file uses one `KEY=VALUE` pair per line. Lines starting
with `#` are comments, and inline comments after `#` are also ignored.

```txt
# === Mandatory ===
WIDTH=3         # maze width in cells, must be >= 3
HEIGHT=3        # maze height in cells, must be >= 3
ENTRY=1,1       # entry coordinates (x,y)
EXIT=1,2        # exit coordinates (x,y)
OUTPUT_FILE=maze.txt   # must end with .txt
PERFECT=True    # True or False
SEED=12         # RNG seed, for reproducible mazes (required by the subject)

# === Bonus ===
ALGO=hunt_and_kill  # hunt_and_kill or prim (random if omitted)
PATTERN=42          # uppercase letters and/or digits, needs a 10x10 minimum maze
RENDER=WINDOW       # ASCII (default, mandatory) or WINDOW (MLX, bonus)
BOLD=True           # True or False - bold wall rendering (in progress)
ANIMATION=True      # True or False
SPEED=20            # animation speed
# LOADING           # planned: loading indicator while a maze is generated
```

| Key           | Category  | Mandatory | Description                                            |
|---------------|-----------|-----------|------------------------------------------------------------|
| `WIDTH`       | Core      | yes       | Number of columns (>= 3)                                  |
| `HEIGHT`      | Core      | yes       | Number of rows (>= 3)                                     |
| `ENTRY`       | Core      | yes       | Entry cell, `x,y`, inside the grid                        |
| `EXIT`        | Core      | yes       | Exit cell, `x,y`, inside the grid, different from `ENTRY` |
| `OUTPUT_FILE` | Core      | yes       | Output filename, must end with `.txt`                     |
| `PERFECT`     | Core      | yes       | `True` for a single-path maze, `False` to add loops       |
| `SEED`        | Core      | yes       | Integer seed, required for reproducible generation         |
| `ALGO`        | Bonus     | no        | `prim` or `hunt_and_kill` (random choice if omitted)       |
| `PATTERN`     | Bonus     | no        | Text drawn as fully-walled protected cells (default `42`) |
| `RENDER`      | Bonus     | no        | `ASCII` (default, satisfies the mandatory display requirement) or `WINDOW` (MLX, bonus) |
| `BOLD`        | Bonus     | no        | Bold wall rendering toggle *(work in progress)*            |
| `ANIMATION`   | Bonus     | no        | Enable step-by-step generation animation                  |
| `SPEED`       | Bonus     | no        | Animation speed, integer >= 1                              |
| `LOADING`     | Bonus     | no        | Loading indicator while generating *(planned)*             |

Any malformed line (missing `=`, missing mandatory key, invalid type, out of
bounds coordinates, non-boolean `PERFECT`, unknown `ALGO`, wrong file
extension, identical entry/exit...) is caught and reported with a clear error
message; the program exits cleanly instead of crashing.

## Maze generation algorithm

Two algorithms are implemented and selectable through the `ALGO` key:

- **Prim's algorithm** (`prim`): starts from a random unprotected cell and
  grows the maze by repeatedly picking a random cell on the frontier of the
  visited region, then connecting it to a random already-visited neighbor.
- **Hunt and Kill** (`hunt_and_kill`): performs a random walk, carving
  passages until it gets stuck, then "hunts" for the first unvisited cell
  adjacent to a visited one to restart the walk from there.

**Why these algorithms?** Both produce a genuine spanning tree of the grid
(a perfect maze) with an easily reproducible bias: Prim's algorithm gives a
more "branchy", short-corridor maze, while Hunt and Kill tends to produce
longer, winding corridors. Offering both lets the maze's visual character be
changed simply through the config file, and comparing their behavior was a
useful way to validate the "no wall incoherence" and "no 3x3 open area"
constraints against two different growth patterns. When `PERFECT=False`,
extra walls are randomly removed after generation to introduce loops while
respecting the open-area constraint.

## Reusable module

All maze-building logic — grid generation, solving, hex encoding, config
parsing, and the `42` pattern protection — lives in the standalone `mazegen`
package, independent from the rendering code (`render/`). It is built into
an installable wheel (`mazegen-0.1.0-py3-none-any.whl`, produced with
`make build` from `pyproject.toml`) and can be reused in any other Python
project via:

```python
from mazegen import Maze

maze = Maze("config.txt")
maze.generate()
maze.solve()
```

Full usage documentation (instantiation, custom parameters, and how to
access the generated structure and its solution) is available in
[`mazegen/README.md`](mazegen/README.md).

## Team and project management

### Roles

- **airandri** (backend): the `mazegen` package — maze generation algorithms
  (Prim, Hunt and Kill), the BFS solver, configuration parsing/validation,
  the hexadecimal output encoding, and building/packaging the `mazegen`
  wheel.
- **fanilran** (frontend): the `render` package — ASCII terminal rendering
  and its interactive menu, the MLX graphical window renderer, the `42`
  pattern module, and the project's README/documentation.

### Planning

The project started with the configuration parser and the internal grid
representation, since every other part depends on them. Algorithm
implementation (Prim, then Hunt and Kill) followed, then the BFS solver and
the hexadecimal output writer. Rendering (ASCII first, then the MLX window)
was built last and iterated on the most, since it depends on both the
internal bit encoding and the subject's output encoding matching correctly.
Packaging the reusable module was tackled once the core `mazegen` API had
stabilized.

### What worked well / what could be improved

- What worked well: keeping maze generation, solving, and rendering in
  separate modules made it straightforward to debug rendering issues
  without touching the generation logic, and to add a second algorithm with
  minimal changes elsewhere.
- What could be improved: the interactive menu (regenerate / toggle path /
  change color) is currently fully implemented for the ASCII renderer;
  bringing the same level of interactivity to the MLX window renderer is an
  area for further work.

### Tools

- `flake8` and `mypy` (with the mandatory flags) for linting and static
  typing
- `pdb` for debugging
- Git/GitHub for version control
- AI assistance (see the Resources section) for targeted debugging help

## Bonuses

- **Multiple algorithms**: two maze generation algorithms (Prim's algorithm
  and Hunt and Kill), selectable via the `ALGO` config key.
- **Custom pattern**: any uppercase text or digits can be drawn as protected,
  fully-walled cells via the `PATTERN` config key (not limited to `42`).
- **Graphical rendering**: in addition to the mandatory terminal display, a
  full MLX graphical window renderer is available via `RENDER=WINDOW`.
- **Generation animation**: step-by-step animation of the maze being built,
  controlled by the `ANIMATION` and `SPEED` config keys.
- **Bold wall rendering** (`BOLD`) and a **loading indicator** (`LOADING`)
  are planned as additional bonuses; the config keys exist but are not yet
  wired into the rendering code.