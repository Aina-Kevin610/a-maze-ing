PYTHON     = python3
VENV       = .venv
PIP        = $(VENV)/bin/pip
EXEC       = $(VENV)/bin/python
RUFF       = $(VENV)/bin/ruff
PYTEST     = $(VENV)/bin/pytest
MAIN       = a_maze_ing.py
SRC        = .

.DEFAULT_GOAL = help

.PHONY: help install run debug lint test clean fclean re

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  install   create venv and install dependencies"
	@echo "  run       run the project"
	@echo "  debug     run with pdb debugger"
	@echo "  lint      check code with ruff (strict)"
	@echo "  test      run tests with pytest"
	@echo "  clean     remove __pycache__ and .mypy_cache"
	@echo "  fclean    clean + remove venv"
	@echo "  re        fclean + install"

install: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: install
	$(EXEC) $(MAIN)

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