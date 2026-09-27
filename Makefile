.PHONY: setup smoke data experiment tables figures reproduce test lint clean

setup:
	pip install -r requirements.txt

smoke:
	python scripts/smoke_test.py

data:
	python scripts/download_cicids.py
	python -m src.data.clean --raw data/raw --out data/processed
	python -m src.data.sequence --processed data/processed --out data/processed/tasks.npz --scenario cii

experiment:
	python -m src.run_experiment --config configs/baselines/e1_clean.yaml

tables:
	python -m src.run_experiment --rebuild-table
	python scripts/stats_summary.py

figures:
	python scripts/make_figures.py

reproduce:
	bash scripts/reproduce.sh c_e1

test:
	python -m pytest tests/ -q

lint:
	python -m ruff check src scripts tests || true

clean:
	python -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in list(pathlib.Path('.').rglob('__pycache__'))]"
