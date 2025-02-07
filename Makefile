RM := rm -rf
PYTHON := uv run --frozen
RUFF := uvx ruff

PKG_FILES := pyproject.toml
PKG_LOCK := uv.lock
ENV_DIR := .venv
ENV_LOCK := $(ENV_DIR)/pyvenv.cfg

.PHONY: all format lint clean purge test build publish

all: venv

format:
	$(RUFF) check --fix
	$(RUFF) format

lint:
	$(RUFF) check
	$(RUFF) format --check

clean:
	$(RM) ./dist ./build ./*.egg-info

purge: clean
	$(RM) -rf $(ENV_DIR)

test:
	$(PYTHON) -m compileall wcpan

build: clean venv
	uv build

publish: build
	uv publish

venv: $(ENV_LOCK)

$(ENV_LOCK): $(PKG_LOCK)
	uv sync --frozen
	touch $@

$(PKG_LOCK): $(PKG_FILES)
	uv lock
	touch $@
