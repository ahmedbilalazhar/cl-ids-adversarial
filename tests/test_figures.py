"""Figure pipeline never renders unvalidated or partial data silently."""
import csv

import numpy as np
import pytest

import scripts.make_figures as figures


def _write_stats_csv(directory, rows):
    fields = ["name", "device", "n_seeds", "acc_mean", "acc_std"]
    with open(directory / "stats_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def test_r_matrix_requires_validated_files(tmp_path, monkeypatch):
    monkeypatch.setattr(figures, "RUNS", tmp_path / "runs")
    monkeypatch.setattr(figures, "RESULTS", tmp_path)
    (tmp_path / "runs").mkdir()
    np.savetxt(tmp_path / "runs" / "e1_clean_R_seed1.csv", np.eye(2), delimiter=",")
    assert figures._validated_r_files("e1_clean_R_seed*.csv") == []
    with pytest.raises(ValueError, match="no manifest-validated"):
        figures.fig_r_matrix()


def test_load_stats_prefers_cpu_device(tmp_path, monkeypatch):
    monkeypatch.setattr(figures, "RESULTS", tmp_path)
    _write_stats_csv(tmp_path, [
        {"name": "e1_clean", "device": "cuda", "n_seeds": 2,
         "acc_mean": "0.9", "acc_std": "0.1"},
        {"name": "e1_clean", "device": "cpu", "n_seeds": 3,
         "acc_mean": "0.5", "acc_std": "0.05"},
    ])
    stats = figures.load_stats()
    assert stats["e1_clean"]["device"] == "cpu"
    assert stats["e1_clean"]["acc_mean"] == "0.5"


def test_e5_missing_outputs_raise_loudly(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(figures, "RESULTS", tmp_path)
    monkeypatch.setattr(figures, "FIGS", tmp_path)
    with pytest.raises(FileNotFoundError, match="archived"):
        figures.fig_e5()
