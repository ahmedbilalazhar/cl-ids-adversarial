"""Group queue records failures and continues instead of aborting."""
import subprocess

import pytest

from scripts import run_groups


def test_queue_continues_past_failed_group(tmp_path, monkeypatch):
    monkeypatch.setattr(run_groups, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["run_groups.py", "g1", "g2"])
    calls = []

    def fake_run(*args, **kwargs):
        calls.append(args[0][-1])
        code = 1 if args[0][-1] == "g1" else 0
        return subprocess.CompletedProcess(args[0], code)

    monkeypatch.setattr(run_groups.subprocess, "run", fake_run)
    with pytest.raises(SystemExit, match="g1"):
        run_groups.main()
    assert calls == ["g1", "g2"]
    log = (tmp_path / "results" / "run_groups.log").read_text(encoding="utf-8")
    assert "=== g1 exit=1" in log and "=== g2 exit=0" in log
