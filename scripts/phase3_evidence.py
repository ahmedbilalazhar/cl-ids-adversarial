"""Independent confusion-matrix scoring and small-sample paired inference."""
import itertools
import numpy as np
from scipy.stats import rankdata


def confusion_metrics(confusion, eligible):
    full = np.asarray(confusion, dtype=np.int64)
    if full.shape != (16, 16) or (full < 0).any(): raise ValueError('Invalid confusion matrix')
    eligible = sorted(int(c) for c in eligible)
    bank = full.copy()
    bank[[c for c in range(16) if c not in eligible], :] = 0
    # Predictions into unsupported classes still count as errors for eligible rows.
    support = bank.sum(axis=1); predicted = bank.sum(axis=0); tp = bank.diagonal()
    precision = np.divide(tp, predicted, out=np.zeros(16, float), where=predicted > 0)
    recall = np.divide(tp, support, out=np.zeros(16, float), where=support > 0)
    f1 = np.divide(2 * tp, support + predicted, out=np.zeros(16, float), where=(support + predicted) > 0)
    active = [c for c in eligible if support[c] > 0]
    if not active or not support[0]: raise ValueError('Empty scoring bank or benign denominator')
    result = dict(macro_f1=float(f1[active].mean()), accuracy=float(tp.sum() / bank.sum()),
        macro_precision=float(precision[active].mean()), macro_recall=float(recall[active].mean()),
        benign_far=float(1 - bank[0, 0] / support[0]),
        classes={c: dict(support=int(support[c]), precision=float(precision[c]),
            precision_defined=bool(predicted[c]), recall=float(recall[c]), f1=float(f1[c])) for c in active})
    if support[4]: result.update(hulk_recall=float(recall[4]), hulk_asr=float(bank[4, 0] / support[4]))
    tn, fp, fn, binary_tp = int(bank[0,0]), int(bank[0,1:].sum()), int(bank[1:,0].sum()), int(bank[1:,1:].sum())
    result['binary'] = dict(accuracy=(tn+binary_tp)/bank.sum(),
        precision=binary_tp/(binary_tp+fp) if binary_tp+fp else 0.,
        recall=binary_tp/(binary_tp+fn) if binary_tp+fn else 0.,
        f1=2*binary_tp/(2*binary_tp+fp+fn) if 2*binary_tp+fp+fn else 0.,
        fpr=fp/(fp+tn),tp=binary_tp,fp=fp,fn=fn,tn=tn)
    return result


def signed_rank_enumeration(differences):
    """Conditional two-sided signed-rank sign enumeration, allowing ties and zeros.

    Assumes symmetric differences and exchangeable signs; no claim of independent
    captures. Intended for the three ownership-partition sensitivity analysis.
    """
    d = np.asarray(differences, float)
    if not np.isfinite(d).all(): raise ValueError('Nonfinite paired effect')
    d = d[d != 0]
    if not len(d): return dict(p=1., rank_biserial=0., nonzero=0, method='all_zero')
    if len(d) > 18: raise ValueError('Exact enumeration restricted to small samples')
    ranks = rankdata(abs(d), method='average')
    signed = float(np.dot(np.sign(d), ranks))
    outcomes = [abs(np.dot(signs, ranks)) for signs in itertools.product((-1, 1), repeat=len(d))]
    p = float(np.mean(np.asarray(outcomes) >= abs(signed) - 1e-12))
    return dict(p=p, rank_biserial=float(signed / ranks.sum()), nonzero=len(d),
                method='conditional_signed_rank_sign_enumeration')


def holm(pvalues):
    p = np.asarray(pvalues, float)
    if not np.isfinite(p).all(): raise ValueError('Nonfinite p-value')
    order = np.argsort(p); out = np.empty(len(p)); running = 0.
    for rank, i in enumerate(order):
        running = max(running, (len(p) - rank) * p[i]); out[i] = min(1., running)
    return out
