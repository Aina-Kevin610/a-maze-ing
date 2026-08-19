*This project has been created as part of the 42 curriculum by airandri, fanilran.*

# mazegen

`mazegen` is a standalone, installable Python package that generates,
solves, and encodes mazes. It has no dependency on the rendering code and
can be reused in any Python project.

## Installation

From the built wheel:

```bash
pip install mazegen-0.1.0-py3-none-any.whl
```

Or build it yourself from source (requires the `build` package):

```bash
python3 -m pip install build
python3 -m build --wheel
pip install dist/mazegen-0.1.0-py3-none-any.whl
```

## Basic usage

The generator is driven by a single class, `Maze`, instantiated from a
configuration file (see the main project README for the full format):

```python
from mazegen import Maze

maze = Maze("config.txt")   # parses and validates the config file
maze.generate()              # builds the maze grid with the chosen algorithm
maze.solve()                 # computes the shortest path (BFS)
maze.save(maze.grid)         # writes maze.txt in the subject's output format
```

## Custom parameters

Parameters are not passed directly to the `Maze` constructor; instead they
are read from the configuration file passed to it. This keeps a single
source of truth for maze settings. The most relevant keys for reuse are:

| Key      | Effect                                                          |
|----------|-------------------------------------------------------------------|
| `WIDTH`, `HEIGHT` | Size of the grid                                       |
| `SEED`   | Makes generation reproducible: same seed → same maze              |
| `ALGO`   | `prim` or `hunt_and_kill`                                          |
| `PERFECT`| `True` for a single-path maze, `False` to add extra loops          |
| `PATTERN`| Text of fully-walled protected cells drawn inside the maze         |

To reuse the module with different settings, simply point `Maze(...)` at a
different configuration file (or generate one programmatically before
instantiating `Maze`).

## Accessing the generated structure and the solution

```python
maze.grid          # list[list[int]]: internal bit-encoded grid
                    # bit0=West, bit1=South, bit2=East, bit3=North

maze.hexa_maze()    # list[list[str]]: grid re-encoded as single hex digits,
                    # using the subject's bit order (bit0=North, bit1=East,
                    # bit2=South, bit3=West) — this is what gets written
                    # to the output file

maze.path                 # list[tuple[int, int]]: shortest path, as (x, y)
                           # cells from entry to exit (empty if unreachable)

maze.path_to_directions()  # list[str]: the same path as 'N'/'E'/'S'/'W'
                            # letters, as written in the output file
```

Note: the structure exposed by `maze.grid` uses an internal bit order that
is convenient for the generation algorithms and the solver. It is *not* the
same bit order as the output file — use `maze.hexa_maze()` if you need the
subject's exact encoding.

## Example: generating a maze without touching disk

```python
from mazegen import Maze

maze = Maze("config.txt")
maze.generate()
maze.solve()

for row in maze.hexa_maze():
    print("".join(row))

print("Solution:", "".join(maze.path_to_directions()))
```