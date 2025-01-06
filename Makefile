# Use bash as the shell
SHELL := /bin/bash

# Define the name of the virtual environment directory
VENV_DIR = .venv

# Define the Python executable
PYTHON = python3

# Define the command to activate the virtual environment
ACTIVATE = source $(VENV_DIR)/bin/activate

# Target to create the virtual environment if it doesn't exist
$(VENV_DIR)/bin/activate: $(VENV_DIR)/bin/python

$(VENV_DIR)/bin/python:
	$(PYTHON) -m venv $(VENV_DIR)

# Target to set up the environment and install dependencies
setup: $(VENV_DIR)/bin/activate
	$(ACTIVATE) && pip install -r requirements.txt

# Target to run tests
test: $(VENV_DIR)/bin/activate
	pytest -s --log-cli-level=DEBUG tests\tests_webserver.py


.PHONY: setup