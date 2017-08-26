
SHELL:=/bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

.PHONY: all fresh dependencies clean

all: dependencies

fresh: clean dependencies

dependencies:
	if [ ! -d $(ROOT_DIR)/env ]; then python3 -m venv $(ROOT_DIR)/env; fi
	source $(ROOT_DIR)/env/bin/activate; yes w | python -m pip install -e .[dev]

clean:
	rm -rf $(ROOT_DIR)/*.pyc
	# Remove existing environment
	if [ -d $(ROOT_DIR)/env ]; then \
		rm -rf $(ROOT_DIR)/env; \
	fi;
