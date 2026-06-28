PYTHON     = python3
VENV       = .venv
ACTIVATE   = $(VENV)/bin/activate
PIP        = $(VENV)/bin/pip
EXEC       = $(VENV)/bin/python
MAIN       = a_maze_ing.py
SRC        = a_maze_ing.py parsing.py utils.py render.py render_terminal.py \
             maze_generator/maze_gen.py maze_generator/utils.py \
             maze_generator/pattern.py
FILENAME   = "config.txt"

run: install
	$(EXEC) $(MAIN) $(FILENAME)

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy
	$(PIP) install -r requirements.txt

debug: install
	$(EXEC) -m pdb $(MAIN)

lint: install
	$(EXEC) -m flake8 $(SRC)
	$(EXEC) -m mypy --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs $(SRC)

lint-strict: install
	$(EXEC) -m flake8 $(SRC)
	$(EXEC) -m mypy --strict $(SRC)

build: install
	$(PIP) install build
	$(EXEC) -m build --wheel

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

fclean: clean
	rm -rf $(VENV)
	rm -rf dist
	rm -rf build
	rm -f maze.txt
	rm -rf mazegen.egg-info

re: fclean install

.PHONY: install run debug lint lint-strict build clean fclean re
