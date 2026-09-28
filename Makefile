.PHONY: setup smoke data data-primary data-legacy data-unsw data-iot experiment tables figures reproduce test lint clean

setup:
	pip install -r requirements.txt

smoke:
	python scripts/smoke_test.py

data-primary:
	python scripts/download_cicids.py
	python -m src.data.clean --raw data/raw --out data/processed
	python -m src.data.sequence --processed data/processed/cicids2017_clean.parquet --out data/processed/tasks_chrono.npz --scenario cii --split chrono --scaler frozen

data:
	python scripts/download_cicids.py
	python -m src.data.clean --raw data/raw --out data/processed
	python -m src.data.sequence --processed data/processed/cicids2017_clean.parquet --out data/processed/tasks.npz --scenario cii --split random --scaler pertask

data-unsw:
	python -m src.data.unsw --raw data/raw_unsw --out data/processed/tasks_unsw.npz

data-iot:
	python -m src.data.iot --raw data/raw_iot --out data/processed/tasks_iot.npz

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
	python -m ruff check src scripts tests

clean:
	python -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in list(pathlib.Path('.').rglob('__pycache__'))]"
