# Contributing

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
pip install -e ".[dev]"       # optional: pytest + ruff
```

## Workflow

1. Create a config in `configs/` — every reported number must be regenerable from a config.
2. Run: `python -m src.run_experiment --config configs/baselines/<name>.yaml` (or bare `--config <name>`)
3. Rebuild tables: `python -m src.run_experiment --rebuild-table && python scripts/stats_summary.py`
4. Remake figures: `python scripts/make_figures.py`
5. Verify: `python scripts/smoke_test.py` and `python -m pytest tests/ -q`

## Rules

- Fix seeds (≥3), report mean ± std, full task-accuracy matrix, Wilcoxon signed-rank vs baselines. Never report average accuracy alone.
- Don't commit datasets (`data/raw/*`, `data/processed/*`), weights (`*.pt`), or logs (`*.log`).
- Small, focused commits; don't mix code changes with regenerated `results/` tables.
