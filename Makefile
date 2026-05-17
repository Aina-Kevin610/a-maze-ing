PYTHON     = python3
VENV       = .venv
ACTIVATE   = $(VENV)/bin/activate
PIP        = $(VENV)/bin/pip
EXEC       = $(VENV)/bin/python
MAIN       = a_maze_ing.py
SRC        = a_maze_ing.py parsing.py maze_generator/maze_gen.py render.py
C          ?= "feat"
FILENAME   = "config.txt"
WHL        = maze_generator-1.0.0-py3-none-any.whl

run: install
	$(EXEC) $(MAIN) $(FILENAME)

install: $(VENV)/bin/activate

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install mlx-2.2-py3-none-any.whl

venv: install


send:
	git add .
	git commit -m "$(C)"
	git push


debug: install
	$(EXEC) -m pdb $(MAIN)

lint: install
	echo "Running flake8..."
	flake8 $(SRC)
	echo "Running mypy..."
	mypy $(SRC)

lint-strict:
	echo "Running strict linting..."
	flake8 $(SRC)
	mypy $(SRC) --strict


build: install
	$(PIP) install build
	$(EXEC) -m build --wheel
	mv dist/$(WHL) .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

fclean: clean
	rm -rf $(VENV)

re: fclean install

.PHONY: install run debug lint lint-strict clean fclean re
