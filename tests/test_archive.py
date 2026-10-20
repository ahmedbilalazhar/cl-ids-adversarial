"""Archive moves are hash-verified; partial state is always described."""
import json

import pytest

from scripts import archive_artifacts


def _files(directory, n=2):
    paths = []
    for i in range(n):
        path = directory / f"artifact_{i}.txt"
        path.write_text(f"payload-{i}", encoding="utf-8")
        paths.append(path)
    return paths


def _records(paths):
    return [{"source": p.name, "file": p.name,
             "sha256": archive_artifacts.sha256(p)} for p in paths]


def test_move_verified_happy_path(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()
    paths = _files(src)
    moved = archive_artifacts.move_verified(paths, _records(paths), dest)
    assert len(moved) == 2
    assert [p.name for p in sorted(dest.iterdir())] == ["artifact_0.txt", "artifact_1.txt"]
    assert list(src.iterdir()) == []


def test_partial_move_described_not_silent(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()
    paths = _files(src)
    records = _records(paths)
    real_move = archive_artifacts.shutil.move

    def flaky_move(source, target):
        if str(target).endswith("artifact_1.txt"):
            raise OSError("synthetic disk failure")
        return real_move(source, target)

    monkeypatch.setattr(archive_artifacts.shutil, "move", flaky_move)
    with pytest.raises(OSError, match="synthetic disk failure"):
        archive_artifacts.move_verified(paths, records, dest)
    # First file landed intact and verified; second never left the source.
    assert (dest / "artifact_0.txt").is_file()
    assert (src / "artifact_1.txt").is_file()
    archive_artifacts.write_manifest(dest, reason="probe", commit="abc",
                                     moved=records[:1], complete=False,
                                     error="OSError: synthetic disk failure")
    manifest = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["complete"] is False
    assert manifest["n_files"] == 1
    assert "synthetic disk failure" in manifest["error"]
