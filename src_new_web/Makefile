# Source folder:
SRC = src


# Use bash as the shell
SHELL := /bin/bash

# Define the name of the virtual environment directory
VENV_DIR = .venv

# Define the Python executable
PYTHON = python3

# Define the command to activate the virtual environment
ACTIVATE = source $(VENV_DIR)/bin/activate

# Target to create the virtual environment if it doesn't exist
$(VENV_DIR)/bin/python:
	$(PYTHON) -m venv $(VENV_DIR)

create_venv: $(VENV_DIR)/bin/python



# Target to set up the environment and install dependencies
setup: create_venv requirements.txt
	$(ACTIVATE) && pip install -r requirements.txt 


# to run the server: fastapi run myserver:app --reload
#  OJO: ejecutar MANUALMENTE make setup
#
run: 
	NODE_NAME=$(NODE_NAME) PORT=$(PORT) fastapi dev $(SRC)/myserver.py --reload --port $(PORT) --host 0.0.0.0
 
.PHONY: setup create_venv run