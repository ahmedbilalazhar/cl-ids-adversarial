"""Exact design-resolution arithmetic on hypothetical ranks, not model tests.

No experimental measurements are read. The probability scenarios are explicitly
conditional sign models, not a power estimate for the proposed IDS study.
"""
from fractions import Fraction
from math import comb
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "statistical-resolution.json"
CUTOFF = Fraction(1, 20 * 29)


def subset_counts(ranks):
    counts = [1]
    for rank in ranks:
        counts += [0] * rank
        for score in range(len(counts) - 1, rank - 1, -1):
            counts[score] += counts[score - rank]
    return counts


def boundary(m, equal_magnitudes):
    ranks = [1] * m if equal_magnitudes else list(range(1, m + 1))
    counts = subset_counts(ranks)
    cumulative = 0
    critical = None
    for score, count in enumerate(counts):
        if score * 2 >= sum(ranks):
            break
        cumulative += count
        if Fraction(2 * cumulative, 2**m) <= CUTOFF:
            critical = score
    return ranks, critical


def probability(m, p, equal_magnitudes):
    ranks, critical = boundary(m, equal_magnitudes)
    if critical is None:
        return 0.0
    distribution = [1.0]
    for rank in ranks:
        previous = distribution
        distribution = [0.0] * (len(previous) + rank)
        for score, mass in enumerate(previous):
            distribution[score] += mass * p
            distribution[score + rank] += mass * (1-p)
    return sum(distribution[:critical+1]) + sum(distribution[-critical-1:])


result = {
    "scope": "Design arithmetic only; no model tests, data split, training or experimental endpoints.",
    "first_Holm_cutoff_exact": str(CUTOFF), "first_Holm_cutoff": float(CUTOFF),
    "probability_model": "Independent signs with common P(positive)=p, fixed nonzero absolute ranks; no missing/zero pairs.",
    "interpretation": "Probability that this hypothetical contrast passes the first-step raw-p cutoff. Not overall Holm rejection probability, not empirical power for the IDS experiment.",
    "rows": []
}
for m in [8, 10, 11, 12, 16, 20, 24]:
    for tied in [False, True]:
        ranks, critical = boundary(m, tied)
        result["rows"].append({
            "nonzero_pairs": m, "absolute_magnitudes": "all_equal" if tied else "all_distinct",
            "minimum_two_sided_p": float(Fraction(2, 2**m)),
            "maximum_minority_rank_sum_at_first_cutoff": critical,
            "rank_units": "one_per_sign; common average-rank factor cancels" if tied else "ranks_1_through_m",
            "scenarios": [{"p_positive": p, "probability_passing_first_cutoff": probability(m,p,tied)}
                          for p in [.5,.7,.8,.9,.95,.99]]
        })
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"cutoff": result["first_Holm_cutoff"], "scenarios": len(result["rows"]),
                  "m12_untied": result["rows"][6], "m16_untied": result["rows"][8]}, indent=2))
