# Realized source dose and quota-imposed limits

Data-only arithmetic on the screened corrected candidate, fixed split, proposed benign bundles and twelve prescribed ownership seeds. No admission scorer or model was run.

## Exact constraints

Let b be honest benign records at the attacked client, q the Hulk-to-benign flips and K the admitted supplied-benign quota. Then the admitted poisoned count r must obey:

`L = max(0,K-b) <= r <= U = min(q,K)`.

When the supplied benign group has at least 20 records, `K = ceil(3*(b+q)/4)`. Complete poison removal is feasible only if `K <= b`, equivalently `3*q <= b`. This is a counting constraint, independent of how accurate loss ranking is. The protected-small-class branch instead keeps the entire group.

## Observed inventory at maximum local source dose

| Seed | Honest benign b | Flipped q | Quota K | Forced minimum poison L | Minimum retained poison | Global raw E2 flips |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 616 | 19,891 | 15,381 | 14,765 | 74.2% | 18.724% |
| 2 | 589 | 9,860 | 7,837 | 7,248 | 73.5% | 9.281% |
| 3 | 1,279 | 26,767 | 21,035 | 19,756 | 73.8% | 25.197% |
| 4 | 1,223 | 13,368 | 10,944 | 9,721 | 72.7% | 12.584% |
| 5 | 746 | 470 | 912 | 166 | 35.3% | 0.442% |
| 6 | 354 | 5,767 | 4,591 | 4,237 | 73.5% | 5.429% |
| 7 | 23 | 1,850 | 1,405 | 1,382 | 74.7% | 1.741% |
| 8 | 596 | 222 | 614 | 18 | 8.1% | 0.209% |
| 9 | 1,396 | 36,801 | 28,648 | 27,252 | 74.1% | 34.642% |
| 10 | 1,356 | 16,784 | 13,605 | 12,249 | 73.0% | 15.799% |
| 11 | 845 | 280 | 844 | 0 | 0.0% | 0.264% |
| 42 | 1,067 | 302 | 1,027 | 0 | 0.0% | 0.284% |

The corrected candidate selects exactly 3,500 benign records at each stage: 183,039 total fresh training records, with E1/E2/E3/E4 totals 7,659/106,233/7,176/61,971. Maximum-dose global contamination ranges from about 0.209% to 34.642%; the source dose remains 50% of the attacked site's Hulk examples. These are distinct denominators.

The original as-published candidate with the same bundle algorithm has a much smaller retained source inventory and maximum-dose global fractions about 0.0834%-1.7266%. Different release/split/ownership populations prevent interpreting this contrast as a one-factor causal effect.

## What to measure in actual experiments

- Report q, b, K, L, U, actual r, r/q, honest-benign rejection and the global/local exposure denominators for every seed/dose. Avoid averaging away the large variation in synthetic attacker exposure.
- DQ's expected retained poison is `q*K/(b+q)`. Compare the realized DC count with the actual matched random control and its expectation, keeping downstream metrics separate.
- If U>L, `(r-L)/(U-L)` is a descriptive location in the feasible retained-poison interval: zero is the smallest possible count, one the largest. If U=L, ranking has no freedom for that count and the statistic is undefined. This diagnostic is not a new confirmatory endpoint.
- Do not attribute retention near L to poor ranking when the quota forces it. Conversely, do not infer harmful persistence merely because r is positive.
- Do not increase benign inventory after seeing final model outcomes to manufacture a favorable purification result. Any class-ratio/keep-fraction sensitivity needs its own prospective contract and budget.

A 75% quota on an overwhelmingly poisoned supplied-label group is structurally incapable of general purification. The defensible question is whether its feasible selection changes downstream susceptibility/acquisition under the stated data regime. This can yield an informative negative or conditional finding.

See [quota-feasibility-summary.json](quota-feasibility-summary.json) and [corrected-domain-checked-candidate-ownership-dose-audit-benign-subset.json](corrected-domain-checked-candidate-ownership-dose-audit-benign-subset.json).
