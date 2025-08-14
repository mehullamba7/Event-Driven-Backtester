SHELL := /bin/bash

PY=python
PKG=backtester

.PHONY: setup lint test coverage bench run-exp reproduce-exp-001

setup:
	pip install -r requirements.txt
	pre-commit install

lint:
	ruff check src
	black --check src tests

test:
	pytest -q --disable-warnings

coverage:
	pytest --cov=src --cov-report=term-missing

bench:
	$(PY) -m backtester.bench

run-exp:
	@CONFIG?=configs/example_pairs.json
	@EXP_NAME?=exp
	MLFLOW_TRACKING_URI=mlruns $(PY) scripts/run_backtest.py --config $(CONFIG) --exp-name $(EXP_NAME)

reproduce-exp-001:
	MLFLOW_TRACKING_URI=mlruns $(PY) scripts/run_backtest.py --config configs/example_pairs.json --exp-name reproduce-exp-001 --seed 42
