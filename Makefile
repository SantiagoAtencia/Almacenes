# varaibles
PORT=5000
NODE_NAME=nodo1

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
	$(VENV_DIR)/bin/python -m ensurepip --upgrade
# Target to set up the environment and install dependencies
setup: create_venv 
	$(VENV_DIR)/bin/pip install -r requirements.txt

activate:
	@echo "Activating virtual environment"
	source $(VENV_DIR)/bin/activate


# Target to run tests
test: setup
	 pytest -s --log-cli-level=DEBUG tests/tests_dataserver.py

run: 
	PORT=$(PORT) NODE_NAME=$(NODE_NAME) fastapi dev  --host=0.0.0.0 --port=$(PORT) src/webserver.py
	#PORT=$(PORT) NODE_NAME=$(NODE_NAME) fastapi dev  --port=$(PORT) src/webserver.py


.PHONY: setup test create_venv run activate