# Continual Learning for Network Security

Computer Networks research by Saneedullah (23I-2568) and Ahmed Bilal (23I-2581). The project studies retention and adaptation in an offline federated intrusion-detection simulation.

| If you want to… | Start here |
| --- | --- |
| Understand or review the whole project | [Agent handoff and experiment inventory](AGENT_HANDOFF.md) |
| Read the original methodology and deadline submission | [Submission index](submissions/README.md) |
| Read the latest audited report and rebuild its PDF | [Audited report](submissions/phase3-audited-report/phase3-report.pdf) · [Build guide](submissions/phase3-audited-report/BUILD.md) |
| Find raw runs, checkpoints, summaries and open work | [Results index](results/README.md) · [Scientific audit](docs/phase3-rigorous-audit-v1/README.md) |
| Download the full evidence snapshot | [Phase 3 evidence release](https://github.com/ahmedbilalazhar/cl-ids-adversarial/releases/tag/phase3-evidence-v28) |

## Project layout

| Folder | What belongs there |
| --- | --- |
| [`src/`](src/) | Model, training, data preparation and evaluation code |
| [`configs/`](configs/) | Protocol, taxonomy, experiment settings and environment locks |
| [`scripts/`](scripts/) and [`tests/`](tests/) | Runners, audits, plotting, packaging and implementation checks |
| [`data/`](data/) | Data documentation and manifests, with raw and prepared payloads kept locally |
| [`results/`](results/) | Versioned runs, checkpoints, derived tables and verification records |
| [`submissions/`](submissions/) | Phase 1–3 documents, the exact deadline archive and the audited revision |
| [`docs/`](docs/) | Methods, decisions, audits and reproduction guidance |
| [`phase3-implementation/`](phase3-implementation/) | Historical Phase 3 implementation, notebook and original run exports |
| [`phase3_delivery/`](phase3_delivery/) and [`kaggle_worker/`](kaggle_worker/) | Experiment delivery, worker and verification tooling |
| [`reports/`](reports/), [`research_figures/`](research_figures/) and [`notebooks/`](notebooks/) | Earlier course materials, figures and notebook work |

The audited CPU study contains 417 unique full trajectories and 24 paired oracle continuations. The later DG, DR eviction and DC eviction blocks add 48, 48 and 24 trajectories respectively, bringing the adopted CPU total to 537. The v28 release predates those three blocks. The real final-test bank remains sealed. [Evidence status and remaining work](AGENT_HANDOFF.md#evidence-status-and-interpretation)

## Local and GitHub copies

A clone provides the tracked code, reports and evidence inventory. Local data, Python environments, temporary output and archived exports use the paths described in the [workspace guide](docs/workspace-layout.md). Run commands from the repository root. Use the [scientific reproduction guide](docs/phase3-rigorous-audit-v1/reproduction.md) for the inputs and runtime needed for each step.

For earlier status snapshots, commands and Kaggle qualification history, see [Project history](docs/project-history.md).
