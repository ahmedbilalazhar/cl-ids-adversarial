import numpy as np


def average_accuracy(R: np.ndarray) -> float:
    T = R.shape[0]
    return float(np.mean(R[T - 1, :]))


def backward_transfer(R: np.ndarray) -> float:
    T = R.shape[0]
    if T < 2:
        return 0.0
    vals = [R[T - 1, j] - R[j, j] for j in range(T - 1)]
    return float(np.mean(vals))


def forward_transfer(R: np.ndarray, fwt_baseline: np.ndarray | None = None) -> float:
    T = R.shape[0]
    if T < 2:
        return 0.0
    if fwt_baseline is None:
        vals = [R[j - 1, j] for j in range(1, T)]
        return float(np.mean(vals))
    vals = [R[j - 1, j] - fwt_baseline[j] for j in range(1, T)]
    return float(np.mean(vals))


def forgetting(R: np.ndarray) -> float:
    T = R.shape[0]
    vals = []
    for j in range(T):
        best = float(np.max(R[j:, j]))
        vals.append(best - float(R[T - 1, j]))
    return float(np.mean(vals))


def task_accuracy_matrix_row(true: np.ndarray, pred: np.ndarray) -> float:
    if len(true) == 0:
        return 0.0
    return float(np.mean(true == pred))


def asr_backdoor(y_true: np.ndarray, y_pred: np.ndarray, triggered: np.ndarray, target_label: int) -> float:
    mask = triggered & (y_true != target_label)
    if mask.sum() == 0:
        return 0.0
    return float(np.mean(y_pred[mask] == target_label))


def asr_novelty(y_true: np.ndarray, y_pred: np.ndarray, real_attack_labels: list[int], benign_label: int = 0) -> float:
    mask = np.isin(y_true, real_attack_labels)
    if mask.sum() == 0:
        return 0.0
    return float(np.mean(y_pred[mask] == benign_label))


def summarize(R: np.ndarray) -> dict:
    return {
        "acc": average_accuracy(R),
        "bwt": backward_transfer(R),
        "fwt": forward_transfer(R),
        "forgetting": forgetting(R),
    }
