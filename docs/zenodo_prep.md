# Zenodo artifact prep (Phase-6 step 24)

Upload (owner: student, at submission time — mints the DOI cited in the paper):

1. `git archive` the repo at the submission tag (code + configs + scripts +
   docs), PLUS:
2. `data/processed/tasks_chrono.npz`, `tasks_chrono_alt.npz`,
   `tasks_chrono_rev.npz`, `tasks_frozen.npz`, `tasks_unsw.npz`,
   `tasks_iot.npz` (built task files; raw CSVs referenced by URL, not
   re-uploaded),
3. `results/baseline_table.csv`, `results/stats_summary.csv`,
   `results/wilcoxon.csv`, `results/figures/`, `results/e8_deployment.json`,
4. `Dockerfile` + `requirements.txt` (frozen versions at tag time:
   `pip freeze > requirements_frozen.txt`),
5. `docs/search_protocol.md` (+ `docs/search_exports/` once Scholar/Xplore/
   Scopus manual runs land).

Include `notebooks/architecture_colab.ipynb`, its GPU `run_manifest.json`,
and `results_prefix0/dispatch_bug_20260927/manifest.csv` with the final
artifact. Report the GPU model, PyTorch/CUDA versions, and bundle/task hashes
when citing the architecture sweep; compare its GPU runs within that sweep.

Suggested record metadata — title: "Poisoning Federated Class-Incremental
Network Intrusion Detection: code, task files, and full result tables";
authors: Saneedullah, Ahmed Bilal (+ supervisor); description: one paragraph
per docs/proposal.md §3 + the locked positioning memo; license: MIT (code)
+ CC-BY-4.0 (data artifacts); related identifiers: the paper DOI (fill at
acceptance), dataset DOIs/URLs (UNB CICIDS2017 page, UNSW-NB15 page,
HuggingFace mirrors used with row-count fingerprints).

The paper references the artifact as a first-class contribution
("all tables and figures regenerate via scripts/reproduce.sh; archived at
DOI:___"), not a footnote.
