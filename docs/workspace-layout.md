# Local workspace and GitHub layout

Open the repository root in your editor. The [project README](../README.md), [submission index](../submissions/README.md), and [results index](../results/README.md) work from both a local checkout and GitHub. The [agent handoff](../AGENT_HANDOFF.md) maps individual experiments to their code, records and reports.

| Location | Use |
| --- | --- |
| `src/`, `configs/`, `scripts/`, `tests/` | Source, configuration, runnable workflows and checks |
| `docs/` and `submissions/` | Research decisions, audits and report versions |
| `results/<study-version>/` | New run records, checkpoints and completion manifests for one study version. Publishable summaries belong beside the corresponding evidence. |
| `data/` | Acquisition instructions and manifests. Keep raw and generated dataset files under the documented local data paths. |
| `tmp/`, `artifacts/`, `returns/` | Local work areas for temporary builds, delivery files and returned work. Consult the runner before moving a file used by an active job. |
| `output/` | Render and export location. Previously committed deliverables remain available here. Use the submission index for current reports. |
| `submissions/_local_archive/overleaf/` | Local archive for the three superseded Overleaf ZIP exports. Git ignores this directory. |
| GitHub Releases | Download location for the large evidence archive and matching validation record. |

Keep existing run, report and dataset paths stable when an executed manifest or a reproducibility script refers to them. For new work, create a versioned run directory for a change in experiment identity. Add the completion manifest and an index link so a reader can find the evidence without searching old drafts. On a fresh clone, acquire the documented data and download the required evidence snapshot before rerunning analyses that need those inputs. [Data instructions](../data/README.md) · [Reproduction guide](phase3-rigorous-audit-v1/reproduction.md)
