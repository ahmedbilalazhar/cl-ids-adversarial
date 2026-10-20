"""Grid driver records per-seed failures instead of aborting the group."""
import pytest

from scripts import run_grid


def test_grid_failure_does_not_abort_group(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(run_grid, "GROUPS", {"probe": ["e1_finetune_c"]})
    monkeypatch.setattr(run_grid, "FED_GROUPS", set())
    monkeypatch.setattr(run_grid, "RUNS_DIR", tmp_path)
    monkeypatch.setattr(run_grid, "seeds_for_group", lambda group: [1, 2])
    monkeypatch.setattr(
        run_grid, "check_artifact", lambda *args, **kwargs: {"complete": False})
    calls = []

    def fake_execute(cfg, out_dir, resume=False):
        calls.append(cfg["seed"])
        if cfg["seed"] == 1:
            raise RuntimeError("synthetic boom")
        return {"summary": {"acc": 0.5, "wall_sec": 1}}

    monkeypatch.setattr(run_grid, "execute_config", fake_execute)
    monkeypatch.setattr("sys.argv", ["run_grid.py", "probe"])
    with pytest.raises(SystemExit, match="1 seed"):
        run_grid.main()
    out = capsys.readouterr().out
    assert "FAIL e1_finetune_c seed 1" in out
    assert "DONE e1_finetune_c seed 2" in out
    assert "failed 1" in out
    assert calls == [1, 2]
