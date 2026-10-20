"""Randomized invariant tests: partitioning, overlap counting, dedup."""
import numpy as np

from scripts.audit_tasks import content_overlap_count
from src.data.sequence import exclude_test_content_matches
from src.federated.partition import dirichlet_partition, stable_partition


def test_dirichlet_partition_invariants_randomized():
    rng = np.random.RandomState(1234)
    for trial in range(20):
        n = int(rng.randint(1, 500))
        n_classes = int(rng.randint(1, 6))
        n_clients = int(rng.randint(2, 8))
        alpha = float(rng.choice([0.1, 0.5, 1.0, 5.0]))
        seed = int(rng.randint(0, 10_000))
        y = rng.randint(0, n_classes, size=n)
        first = dirichlet_partition(y, n_clients=n_clients, alpha=alpha, seed=seed)
        second = dirichlet_partition(y, n_clients=n_clients, alpha=alpha, seed=seed)
        assert len(first) == n_clients
        for a, b in zip(first, second):
            np.testing.assert_array_equal(a, b)  # deterministic
        np.testing.assert_array_equal(np.sort(np.concatenate(first)), np.arange(n))


def test_stable_partition_invariants_randomized():
    rng = np.random.RandomState(567)
    for trial in range(20):
        n = int(rng.randint(1, 300))
        ids = rng.choice(4000, size=n, replace=False).astype(np.int64)
        if trial % 2:
            ids = ids - 2000  # include negative ids
        n_clients = int(rng.randint(2, 6))
        first = stable_partition(ids, n_clients=n_clients)
        second = stable_partition(ids, n_clients=n_clients)
        assert len(first) == n_clients
        for a, b in zip(first, second):
            np.testing.assert_array_equal(a, b)
        np.testing.assert_array_equal(np.sort(np.concatenate(first)), np.arange(n))


def test_content_overlap_counts_are_sane():
    rng = np.random.RandomState(99)
    Xtr = rng.randn(50, 4).astype(np.float32)
    ytr = np.zeros(50, dtype=np.int64)
    assert content_overlap_count(Xtr, ytr, Xtr, ytr) == 50  # self-match
    Xte = rng.randn(10, 4).astype(np.float32) + 100.0
    yte = np.zeros(10, dtype=np.int64)
    assert content_overlap_count(Xtr, ytr, Xte, yte) == 0  # disjoint
    assert content_overlap_count(Xtr, ytr, np.zeros((0, 4), dtype=np.float32),
                                 np.zeros(0, dtype=np.int64)) == 0  # empty


def test_exclude_test_matches_is_idempotent():
    rng = np.random.RandomState(7)
    X = rng.randn(40, 3).astype(np.float32)
    y = np.zeros(40, dtype=np.int64)
    tasks = [
        {"X_train": X[:30], "y_train": y[:30], "X_test": X[20:],
         "y_test": y[20:], "id_test": np.arange(20, 40)},
    ]
    first = exclude_test_content_matches(tasks)
    assert first == 10
    assert exclude_test_content_matches(tasks) == 0  # idempotent
    assert len(tasks[0]["X_test"]) == 10
