"""Synthetic checks for causal, held-out-isolated discovery."""
import numpy as np

from src.discovery import pipeline
from src.metrics import forward_transfer, summarize


class FeatureScoreAE:
    def eval(self):
        return self

    def recon_error(self, x):
        return x[:, 0]


def test_discovery_clusters_ignore_held_out_rows(monkeypatch):
    monkeypatch.setattr(pipeline, "cluster_novel", lambda x, min_cluster_size=15: np.array([0, 0, 0, 1, 1, 1]))
    ae = FeatureScoreAE()
    train = np.array([[1., 0.], [1., 0.1], [1., -0.1],
                      [1., 10.], [1., 10.1], [1., 9.9]], dtype=np.float32)
    poison = np.array([True, True, True, False, False, False])
    fitted = pipeline.fit_discovery(ae, 0.5, train, poison)
    original_labels = fitted["train_labels"].copy()
    original_centers = {k: v.copy() for k, v in fitted["centers"].items()}
    test = np.array([[1., 0.05], [1., 10.05]], dtype=np.float32)
    y_test = np.array([1, 0])
    first = pipeline.evaluate_discovery(ae, 0.5, fitted, test, y_test)
    extended = pipeline.evaluate_discovery(
        ae, 0.5, fitted, np.concatenate([test, np.array([[1., 1000.]], dtype=np.float32)]),
        np.array([1, 0, 1]),
    )
    assert first["n_attack_absorbed"] == extended["n_attack_absorbed"] == 1
    assert first["n_attack_flagged"] == 1 and extended["n_attack_flagged"] == 2
    np.testing.assert_array_equal(fitted["train_labels"], original_labels)
    for key, center in original_centers.items():
        np.testing.assert_array_equal(fitted["centers"][key], center)
    assert pipeline.assign_clusters(test, fitted).tolist() == [0, 1]
    assert pipeline.assign_clusters(test[::-1], fitted).tolist() == [1, 0]


def test_provisional_labels_enter_classifier_training(monkeypatch):
    from src import runner

    seen = []

    class SpyMethod:
        def __init__(self, model, **kwargs):
            self.model = model

        def before_task(self, task_id, loader, class_bound):
            seen.append(("bound", class_bound))

        def train_task(self, loader, epochs):
            seen.append(("labels", loader.dataset.tensors[1].numpy().tolist()))

        def after_task(self, task_id, loader):
            pass

        def predict(self, X):
            return np.zeros(len(X), dtype=np.int64)

    X = np.vstack([np.zeros((20, 2)), np.ones((20, 2))]).astype(np.float32)
    y = np.array([0] * 20 + [1] * 20, dtype=np.int64)
    task = {"X_train": X, "y_train": y, "X_test": X.copy(), "y_test": y.copy()}
    monkeypatch.setattr(runner, "load_or_build_tasks", lambda cfg: ([task], {"Benign": 0, "Attack": 1}))
    monkeypatch.setattr(runner, "train_autoencoder", lambda *args, **kwargs: FeatureScoreAE())
    monkeypatch.setattr(pipeline, "cluster_novel", lambda x, min_cluster_size=15: np.zeros(len(x), dtype=np.int64))
    monkeypatch.setitem(runner.METHODS, "finetune", SpyMethod)
    cfg = {"name": "synthetic-discovery", "cl_method": "finetune", "seed": 1,
           "data": {"tasks": "data/processed/tasks_chrono_dedup.npz", "scenario": "cii"},
           "attack": {"type": "novelty", "budget": 0.0, "min_cluster_size": 3}}
    result = runner.run(cfg)
    assert seen[0] == ("bound", 3)
    assert 2 in seen[1][1]
    assert result["discovery_rows"][0]["n_train_relabelled_by_discovery"] == 40
    assert result["summary"]["asr_mean"] is None

    seen.clear()
    def direct_poison(*args, **kwargs):
        poisoned_y = y.copy()
        poisoned_y[0] = 99
        mask = np.zeros(len(y), dtype=bool)
        mask[0] = True
        return X.copy(), poisoned_y, {"target_label": 99, "triggered": mask}

    monkeypatch.setattr(runner, "apply_attack", direct_poison)
    control_cfg = {**cfg, "attack": {**cfg["attack"], "training_mode": "direct_label_poison"}}
    control = runner.run(control_cfg)
    assert seen[1][1].count(2) == 1
    assert control["discovery_rows"][0]["n_train_relabelled_by_discovery"] == 0


def test_cluster_fit_cap_is_seeded_and_recorded(monkeypatch):
    monkeypatch.setattr(
        pipeline, "cluster_novel",
        lambda x, min_cluster_size=3: np.zeros(len(x), dtype=np.int64),
    )
    X = np.column_stack([np.ones(30), np.linspace(0, 1, 30)]).astype(np.float32)
    poison = np.zeros(30, dtype=bool)
    first = pipeline.fit_discovery(
        FeatureScoreAE(), 0.5, X, poison, min_cluster_size=3,
        max_cluster_candidates=10, seed=7,
    )
    second = pipeline.fit_discovery(
        FeatureScoreAE(), 0.5, X, poison, min_cluster_size=3,
        max_cluster_candidates=10, seed=7,
    )
    assert first["n_fit_candidates"] == 10
    assert first["n_novel_candidates"] == 30
    np.testing.assert_array_equal(first["train_labels"], second["train_labels"])


def test_unmeasured_fwt_is_unavailable():
    R = np.eye(3)
    assert forward_transfer(R) is None
    assert summarize(R)["fwt"] is None
    R[0, 1] = 0.4
    R[1, 2] = 0.3
    assert forward_transfer(R, np.array([0.0, 0.2, 0.1])) == 0.2


def test_attack_dose_uses_actual_changed_and_retained_counts():
    from src.runner import attack_dose_row

    y = np.array([0, 0, 1, 1, 2])
    row = attack_dose_row(
        {"type": "label_flip", "mode": "targeted", "source_class": "Attack",
         "budget": 0.4, "target_class": 0},
        y, np.array([False, False, True, False, False]),
        {"Benign": 0, "Attack": 1, "Other": 2}, task=2,
        retained_mask=np.array([True, True, False, True, True]),
    )
    assert row["eligible"] == 2
    assert row["changed"] == 1
    assert row["retained_after_defense"] == 0
    assert row["realized_shard_dose"] == 0.2
