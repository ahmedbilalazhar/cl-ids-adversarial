# Note to instructor (ready to send this week)

Subject: Scoping decision — RF-fingerprint drift authentication listed as future work

During our correctness audit we found and fixed a data bug (three Thursday
attack families were silently dropped from every task sequence) and re-ran
the full grid (126 single-node + 126 federated runs, 7 seeds each). This put
our headline result on solid ground: in a federated class-incremental IDS
with one malicious client, EWC retains single-node performance while
fine-tuning and DER++ degrade significantly — and poisoning budgets up to 10%
move accuracy within noise in both settings.

One committed claim we are explicitly scoping out: building an
RF-fingerprint drift re-authentication system. Our novelty/discovery attacks
test a different threat model (detecting *unknown* attack classes, not
re-authenticating *known* device identities under drift), and constructing
the RF system from zero would consume the remaining writing buffer while
adding an unverified artifact. It is named as future work in our limitations
section alongside the exact reason, and nothing in the paper conflates the
two threat models. The discovery work is kept as a clearly-separated
secondary result rather than cut, since its controls (nopois baseline) are
already paid for.
