"""Importing the downloader must not create directories (no import side effects)."""
import importlib
import os
import sys
from pathlib import Path


def test_import_has_no_filesystem_side_effects(tmp_path, monkeypatch):
    fake_root = tmp_path / "fake_root"
    monkeypatch.setenv("ARTIFACT_ROOT", str(fake_root))
    for mod in [m for m in list(sys.modules) if m.startswith(("scripts.download_cicids",))]:
        del sys.modules[mod]
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        import scripts.download_cicids as dl
        importlib.reload(dl)
        assert not (fake_root / "data" / "raw").exists()
    finally:
        if str(Path(__file__).resolve().parents[1]) in sys.path:
            sys.path.remove(str(Path(__file__).resolve().parents[1]))
        for mod in [m for m in list(sys.modules) if m.startswith(("scripts.download_cicids",))]:
            del sys.modules[mod]
        os.environ.pop("ARTIFACT_ROOT", None)
