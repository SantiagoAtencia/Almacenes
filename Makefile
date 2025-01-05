# Use bash as the shell
SHELL := /bin/bash

# Define the name of the virtual environment directory
VENV_DIR = .venv

# Define the Python executable
PYTHON = python3

# Define the command to activate the virtual environment
ACTIVATE = source $(VENV_DIR)/bin/activate

# Target to create the virtual environment if it doesn't exist
create_venv: $(VENV_DIR)/bin/python

$(VENV_DIR)/bin/python:
	$(PYTHON) -m venv $(VENV_DIR)

# Target to set up the environment and install dependencies
setup: create_venv
	$(ACTIVATE) && pip install -r requirements.txt

# Target to run tests
test: setup
	$(ACTIVATE) && pytest -s --log-cli-level=DEBUG tests/tests_dataserver.py


.PHONY: setup test create_venv