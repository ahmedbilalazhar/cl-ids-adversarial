"""GPU completion-manifest gate: v2 cross-machine, v3 same-machine only."""
import pytest

from scripts.import_architecture_gpu import check_completion_manifest
from src.reporting import config_hash, source_tree_hash


def _completion(cfg, version, tree=None):
    manifest = {
        "manifest_version": version, "name": cfg["name"],
        "config_name": cfg["name"], "seed": cfg["seed"],
        "config_hash": config_hash(cfg), "task_file_hash": "abc",
        "source_commit": "commit", "runner": "single-node", "device": "cuda",
        "summary_sha256": "s", "r_sha256": "r",
    }
    if tree is not None:
        manifest["source_tree_hash"] = tree
    return manifest


def test_v2_manifest_accepted_without_tree_pin():
    cfg = {"name": "ar_probe", "seed": 1, "device": "cuda"}
    check_completion_manifest(_completion(cfg, 2), cfg=cfg,
                              task_hash="abc", source_commit="commit")


def test_v3_manifest_requires_local_tree():
    cfg = {"name": "ar_probe", "seed": 1, "device": "cuda"}
    check_completion_manifest(_completion(cfg, 3, tree=source_tree_hash()),
                              cfg=cfg, task_hash="abc", source_commit="commit")
    with pytest.raises(ValueError, match="not from this machine"):
        check_completion_manifest(_completion(cfg, 3, tree="0" * 64),
                                  cfg=cfg, task_hash="abc", source_commit="commit")
    with pytest.raises(ValueError, match="not from this machine"):
        check_completion_manifest(_completion(cfg, 3),
                                  cfg=cfg, task_hash="abc", source_commit="commit")


def test_unknown_version_and_identity_mismatch_rejected():
    cfg = {"name": "ar_probe", "seed": 1, "device": "cuda"}
    with pytest.raises(ValueError, match="version"):
        check_completion_manifest(_completion(cfg, 1), cfg=cfg,
                                  task_hash="abc", source_commit="commit")
    bad = _completion(cfg, 2)
    bad["seed"] = 2
    with pytest.raises(ValueError, match="seed"):
        check_completion_manifest(bad, cfg=cfg, task_hash="abc",
                                  source_commit="commit")
