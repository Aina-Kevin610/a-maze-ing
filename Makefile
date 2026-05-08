PYTHON     = python3
VENV       = .venv
PIP        = $(VENV)/bin/pip
EXEC       = $(VENV)/bin/python
RUFF       = $(VENV)/bin/ruff
PYTEST     = $(VENV)/bin/pytest
MAIN       = a_maze_ing.py
SRC        = a_maze_ing.py parsing.py maze_gen.py render.py

run: install
	$(EXEC) $(MAIN)

install: $(VENV)/bin/activate

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r

debug: install
	$(EXEC) -m pdb $(MAIN)

lint: install
	$(RUFF) check --select ALL $(SRC)

test: install
	$(PYTEST) tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

fclean: clean
	rm -rf $(VENV)

re: fclean install

.PHONY: help install run debug lint test clean fclean re
