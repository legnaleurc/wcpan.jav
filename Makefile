RM := rm -rf
PYTHON := uv run
RUFF := $(PYTHON) ruff

PKG_FILES := pyproject.toml hatch.toml
PKG_LOCK := uv.lock
ENV_DIR := .venv
ENV_LOCK := $(ENV_DIR)/pyvenv.cfg

.PHONY: all format lint clean purge test build publish

all: venv

format: venv
	$(RUFF) check --fix
	$(RUFF) format

lint: venv
	$(RUFF) check
	$(RUFF) format --check

clean:
	$(RM) ./dist ./build ./*.egg-info

purge: clean
	$(RM) -rf $(ENV_DIR)

test:
	$(PYTHON) -m compileall src/wcpan

build: clean venv
	uv build

publish: build
	uv publish

venv: $(ENV_LOCK)

$(ENV_LOCK): $(PKG_LOCK)
	uv sync
	touch $@

$(PKG_LOCK): $(PKG_FILES)
	uv lock
	touch $@
