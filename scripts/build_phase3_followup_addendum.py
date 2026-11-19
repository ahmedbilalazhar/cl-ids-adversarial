"""Build a polished, data-linked PDF addendum for Phase 3 follow-up work."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf/phase3-followup-addendum-v3.pdf"
DEV = json.loads((ROOT / "results/phase3-followup/discovery-development-replicates-summary-v1.json").read_text(encoding="utf-8"))
EXT = json.loads((ROOT / "results/phase3-followup/external-discovery-summary-v2.json").read_text(encoding="utf-8"))
EXT_RAW = json.loads((ROOT / "results/phase3-followup/external-discovery-v2.json").read_text(encoding="utf-8"))
PILOT = json.loads((ROOT / "results/phase3-followup/external-method-training-pilot-summary-v1.json").read_text(encoding="utf-8"))
GRID = json.loads((ROOT / "results/phase3-followup/discovery-development-sensitivity-v2.json").read_text(encoding="utf-8"))
ASSIGN = json.loads((ROOT / "results/phase3-followup/discovery-development-assignment-v1.json").read_text(encoding="utf-8"))
ASSIGN_SUMMARY = json.loads((ROOT / "results/phase3-followup/discovery-development-assignment-summary-v1.json").read_text(encoding="utf-8"))

INK = colors.HexColor("#172B3A")
NAVY = colors.HexColor("#24445E")
TEAL = colors.HexColor("#187C80")
GOLD = colors.HexColor("#C89234")
PALE = colors.HexColor("#EEF3F6")
LINE = colors.HexColor("#D8E0E6")
MUTED = colors.HexColor("#526575")
WHITE = colors.white


def pct(v: float) -> str:
    return f"{100*v:.2f}%"


def mean_sd(metric: dict, scale: float = 100.0, digits: int = 2) -> str:
    m, s = metric["mean"] * scale, metric["sd_across_component_partitions"] * scale
    return f"{m:.{digits}f} +/- {s:.{digits}f}"


class FollowupDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(str(filename), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                         topMargin=21*mm, bottomMargin=19*mm, title="Phase 3 Follow-up Studies")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=self.decorate)])

    def decorate(self, canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setFillColor(NAVY)
        canvas.rect(0, h-12*mm, w, 12*mm, stroke=0, fill=1)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(18*mm, h-8*mm, "PHASE 3  /  FOLLOW-UP STUDIES")
        canvas.setFillColor(TEAL)
        canvas.rect(18*mm, 13*mm, 14*mm, 1.4*mm, stroke=0, fill=1)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(36*mm, 13.2*mm, "Exploratory evidence - development and external component studies")
        canvas.drawRightString(w-18*mm, 13.2*mm, f"{doc.page}")
        canvas.restoreState()


def build() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Kicker", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8,
                              leading=11, textColor=TEAL, spaceAfter=5))
    styles.add(ParagraphStyle(name="Hero", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25,
                              leading=29, textColor=INK, alignment=TA_LEFT, spaceAfter=8))
    styles.add(ParagraphStyle(name="Deck", parent=styles["Normal"], fontName="Helvetica", fontSize=11,
                              leading=16, textColor=MUTED, spaceAfter=8))
    styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17,
                              leading=21, textColor=INK, spaceBefore=4, spaceAfter=9))
    styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11,
                              leading=14, textColor=NAVY, spaceBefore=8, spaceAfter=5))
    styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9,
                              leading=13, textColor=INK, spaceAfter=6))
    styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.5,
                              leading=10, textColor=MUTED, spaceAfter=3))
    styles.add(ParagraphStyle(name="CardTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8,
                              leading=10, textColor=MUTED, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="CardValue", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=15,
                              leading=19, textColor=INK, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Cell", parent=styles["BodyText"], fontName="Helvetica", fontSize=8,
                              leading=10, textColor=INK))
    styles.add(ParagraphStyle(name="CellHead", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8,
                              leading=10, textColor=WHITE))

    def p(text, style="Bodyx"):
        return Paragraph(text, styles[style])

    def table(rows, widths, header=True):
        t = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
        ts = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 6),
              ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 6),
              ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("GRID", (0, 0), (-1, -1), .35, LINE)]
        if header:
            ts += [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), WHITE)]
            for i, cell in enumerate(rows[0]):
                if isinstance(cell, Paragraph):
                    pass
        for r in range(1 if header else 0, len(rows)):
            if (r - (1 if header else 0)) % 2 == 1:
                ts.append(("BACKGROUND", (0, r), (-1, r), PALE))
        t.setStyle(TableStyle(ts))
        return t

    def header_row(vals):
        return [p(v, "CellHead") for v in vals]

    story = []
    story += [Spacer(1, 12*mm), p("PHASE 3  /  RESEARCH IMPLEMENTATION", "Kicker"),
              p("Follow-up studies", "Hero"),
              p("Unsupervised discovery, external dataset replication, and final-test readiness", "Deck"),
              p(f"Evidence addendum | {date.today().isoformat()} | Repository-local results", "Smallx"), Spacer(1, 7*mm)]

    card_data = [[p("DEVELOPMENT DISCOVERY", "CardTitle"), p("EXTERNAL DETECTION", "CardTitle"), p("FINAL TEST", "CardTitle")],
                 [p("90.23%", "CardValue"), p("13.30% / 23.22%", "CardValue"), p("SEALED", "CardValue")],
                 [p("attack detection", "CardTitle"), p("CICIoT / UNSW", "CardTitle"), p("0 rows exported", "CardTitle")]]
    card = Table(card_data, colWidths=[56*mm]*3, hAlign="LEFT")
    card.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("BOX", (0, 0), (-1, -1), .6, LINE),
                              ("INNERGRID", (0, 0), (-1, -1), .5, WHITE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story += [card, Spacer(1, 7*mm), p("Executive summary", "H1x"),
              p("A label-free anomaly/discovery submodule has been implemented and evaluated on three component-disjoint partitions of the permitted CICIDS2017 development bank. A threshold/candidate-cap sensitivity grid and a frozen cluster-assignment ablation were also run. Independent three-seed refits of the same discovery submodule were run on UNSW-NB15 and CICIoT2023.", "Bodyx"),
              p("These are exploratory component studies. They do not establish poisoning persistence or effectiveness of the full continual-learning defense. Cross-dataset feature transfer is undefined because input schemas have no shared names and units are undocumented. The CICIDS2017 final-test bank remains sealed and was not accessed.", "Bodyx"),
              p("Readout", "H2x"),
              p("The CIC development partitions yielded 90.23% mean attack detection at 5.31% benign false alerts, but cluster ARI remained 0.0421 despite 98.70% majority-label purity. External detection was much lower and task-dependent. The purity/ARI gap and adverse external results argue against a headline claim of reliable attack-family discovery.", "Bodyx"), PageBreak()]

    story += [p("01  /  COMPONENT-DISJOINT DEVELOPMENT STUDY", "Kicker"), p("Discovery results", "H1x"),
              p("The pinned 272,506-row development bank was mapped completely to the audited component graph. Every row belonged to the development role. Component IDs were split 60/20/20 into autoencoder/clustering, benign calibration, and held-out development evaluation partitions. The autoencoder used benign fit rows only; thresholding used a separate benign calibration subset; clustering received features without labels or poison masks.", "Bodyx")]
    metrics = DEV["metrics"]
    dev_rows = [header_row(["Metric", "Mean", "SD across partitions"]),
                [p("Attack detection rate", "Cell"), p(pct(metrics["attack_flagged_rate"]["mean"]), "Cell"), p(f"{100*metrics['attack_flagged_rate']['sd_across_component_partitions']:.2f} pp", "Cell")],
                [p("Benign false-alert rate", "Cell"), p(pct(metrics["benign_false_alert_rate"]["mean"]), "Cell"), p(f"{100*metrics['benign_false_alert_rate']['sd_across_component_partitions']:.2f} pp", "Cell")],
                [p("Cluster purity", "Cell"), p(pct(metrics["cluster_assignment_purity"]["mean"]), "Cell"), p(f"{100*metrics['cluster_assignment_purity']['sd_across_component_partitions']:.2f} pp", "Cell")],
                [p("Cluster ARI", "Cell"), p(f"{metrics['cluster_assignment_ari']['mean']:.4f}", "Cell"), p(f"{metrics['cluster_assignment_ari']['sd_across_component_partitions']:.4f}", "Cell")],
                [p("Flagged attack cluster coverage", "Cell"), p(pct(metrics["clustered_attack_rate"]["mean"]), "Cell"), p(f"{100*metrics['clustered_attack_rate']['sd_across_component_partitions']:.2f} pp", "Cell")]]
    story += [table(dev_rows, [75*mm, 35*mm, 55*mm]), Spacer(1, 4*mm),
              p("Purity counts each assigned cluster by its majority held-out label. ARI measures pairwise partition agreement and was low across all three partitions. The high purity value therefore does not imply that clusters recover attack families well. SD describes sensitivity to overlapping component partitions and initialization; it is not a confidence interval.", "Bodyx"),
              p("Threshold/cap sensitivity and assignment-rule ablation", "H2x")]
    grid_rows = [header_row(["Threshold q", "Candidate cap", "Detection", "Benign FAR", "Clusters", "ARI"])]
    for row in GRID["sensitivity_grid"]:
        m = row["metrics"]
        grid_rows.append([p(f"{row['quantile']:.2f}", "Cell"), p(f"{row['candidate_cap']:,}", "Cell"),
                          p(pct(m["attack_flagged_rate"]), "Cell"), p(pct(m["benign_false_alert_rate"]), "Cell"),
                          p(str(m["n_clusters"]), "Cell"), p(f"{m['cluster_assignment_ari']:.3f}", "Cell")])
    story += [table(grid_rows, [24*mm, 28*mm, 31*mm, 31*mm, 25*mm, 26*mm]), Spacer(1, 3*mm)]
    rad = ASSIGN_SUMMARY["policies"]["centroid_radius"]
    near = ASSIGN_SUMMARY["policies"]["nearest_centroid"]
    assign_rows = [header_row(["Assignment rule", "Novel rows assigned", "Purity", "ARI"]),
                   [p("Nearest centroid within training radius", "Cell"), p(f"{rad['n_eval_assigned']['mean']:,.0f} / {rad['n_novel_eval']['mean']:,.0f} mean", "Cell"), p(f"{100*rad['cluster_assignment_purity']['mean']:.2f}% +/- {100*rad['cluster_assignment_purity']['sd_across_partitions']:.2f} pp", "Cell"), p(f"{rad['cluster_assignment_ari']['mean']:.4f} +/- {rad['cluster_assignment_ari']['sd_across_partitions']:.4f}", "Cell")],
                   [p("Unrestricted nearest centroid", "Cell"), p(f"{near['n_eval_assigned']['mean']:,.0f} / {near['n_novel_eval']['mean']:,.0f} mean", "Cell"), p(f"{100*near['cluster_assignment_purity']['mean']:.2f}% +/- {100*near['cluster_assignment_purity']['sd_across_partitions']:.2f} pp", "Cell"), p(f"{near['cluster_assignment_ari']['mean']:.4f} +/- {near['cluster_assignment_ari']['sd_across_partitions']:.4f}", "Cell")]]
    story += [table(assign_rows, [66*mm, 43*mm, 30*mm, 25*mm]),
              p("Across three paired component partitions, unrestricted assignment increases attack coverage by 15.74 pp, reduces purity by 3.88 pp, and changes ARI by -0.0003 on average. Detection/FAR are invariant because the threshold step is unchanged.", "Smallx"), PageBreak()]

    story += [p("02  /  INDEPENDENT DATASET REFITS", "Kicker"), p("External discovery study", "H1x"),
              p("Each dataset was fitted independently using the same AE architecture, benign-only training/calibration logic, 95th-percentile threshold, HDBSCAN settings, and frozen centroid/radius assignment. Three seeds were run across four task splits per dataset. Calibration rows were excluded from clustering. No feature projection, model weights, thresholds, or clusters were transferred between datasets.", "Bodyx")]
    extrows = [header_row(["Dataset", "Features", "Attack detection", "Benign FAR", "Cluster ARI"])]
    for name in ("CICIoT2023", "UNSW-NB15"):
        d = EXT["datasets"][name]
        feature_count = EXT_RAW["datasets"][name]["feature_count"]
        v = d["equal_task_metrics"]
        extrows.append([p(name, "Cell"), p(str(feature_count), "Cell"),
                        p(f"{100*v['equal_task_attack_flagged_rate']['mean']:.2f}% +/- {100*v['equal_task_attack_flagged_rate']['sd_across_seeds']:.2f} pp", "Cell"),
                        p(f"{100*v['equal_task_benign_false_alert_rate']['mean']:.2f}% +/- {100*v['equal_task_benign_false_alert_rate']['sd_across_seeds']:.2f} pp", "Cell"),
                        p(f"{v['equal_task_cluster_assignment_ari']['mean']:.3f} +/- {v['equal_task_cluster_assignment_ari']['sd_across_seeds']:.3f}", "Cell")])
    story += [table(extrows, [34*mm, 25*mm, 43*mm, 43*mm, 33*mm]), Spacer(1, 3*mm),
              p("Rates are equal-weight means across four task-specific rates; SD is across three model/calibration seeds. No rows are pooled across seeds or datasets.", "Smallx"),
              p("Interpretation", "H2x"),
              p("The discovery submodule had weak external detection, especially on CICIoT2023. UNSW had a higher false-alert rate. Task-level rates differ materially, so these means should be read with the task-level figure in the companion readiness report. This is an adverse exploratory result for the discovery component; it does not benchmark the full Phase 3 defense or establish cross-site performance.", "Bodyx"),
              p("Data compatibility and limits", "H2x"),
              p("UNSW provides 194 input features and CICIoT2023 provides 39; their feature names have zero intersection and all units are undocumented. Their task construction differs from the adopted 74-feature, component-grouped CICIDS2017 protocol. Archived pre-v2 mirror runs are invalid for citation because the archive manifest records incorrect benign label IDs. The corrected external runs evaluate only the discovery submodule.", "Bodyx"), PageBreak()]

    story += [p("03  /  LOCKED WORK REMAINING", "Kicker"), p("Transfer and final-test gates", "H1x"),
              p("Direct cross-dataset transfer", "H2x"),
              p("Blocked until a source-reviewed semantic feature bridge defines matching quantities, units, transformations, missingness, and a frozen train-on-one/evaluate-on-the-other protocol. The current schemas support independent refits only; even those are limited to the discovery submodule unless a full-method adaptation can preserve the intervention timeline and estimand.", "Bodyx"),
              p("Full-method external replication", "H2x"),
              p(f"A train-label-only support audit selected UNSW Exploits and CICIoT DoS; an ID-only check found no task-ID reuse within either provider's train or test pool. The separate variable-input adapter then completed {PILOT['completed_arms']} train-only arms across four methods, paired clean/attacked conditions, and two datasets ({PILOT['task_stage_checkpoints']} task-stage checkpoints; {PILOT['total_successful_arm_runtime_seconds']:.1f} CPU seconds). The intervention relabeled 5,740/11,480 selected UNSW source rows and 1,120/2,240 CICIoT source rows. No test arrays or metrics were used. This verifies execution only, with one seed and synthetic clients; it does not establish attack persistence or defense effectiveness. Neither package has observed persistent owners or component/session IDs, and pool-local identifiers cannot establish cross-pool flow isolation. This remains an independent benchmark extension, not faithful replication.", "Bodyx"),
              p("CICIDS2017 final-test evaluation", "H2x"),
              p("Not ready or runnable from the prepared package: train and development manifests each report zero final-test rows, no final_test directory exists, and final evaluation is unauthorized. The reference settings remain untuned, and the only evaluator accepts development-only data. Remaining numerical/semantic, baseline/control, GPU-runtime, scope and analysis gates must close first. Then freeze the complete model/seed matrix and hashes, implement a separate final evaluator, build and audit an isolated component-disjoint package, and perform one frozen inference pass. No final-test outcomes are reported here.", "Bodyx")]
    gate = [[p("Study", "CellHead"), p("Current status", "CellHead"), p("Next evidence gate", "CellHead")],
            [p("Development discovery", "Cell"), p("3 partitions, threshold/cap grid, paired assignment ablation", "Cell"), p("More assignment controls; no poisoning claim", "Cell")],
            [p("External studies", "Cell"), p("Discovery: 3 seeds; method: 16 train-only arms", "Cell"), p("Freeze and qualify separate external evaluator", "Cell")],
            [p("Feature transfer", "Cell"), p("Blocked: no shared names or documented units", "Cell"), p("Semantic map and frozen transfer protocol", "Cell")],
            [p("CIC final test", "Cell"), p("Sealed; zero rows exported", "Cell"), p("Freeze scope and build isolated package", "Cell")]]
    story += [Spacer(1, 3*mm), table(gate, [35*mm, 63*mm, 62*mm]), Spacer(1, 6*mm),
              p("Reproducibility index", "H2x"),
              p("External discovery protocol/runner: configs/phase3/external-discovery-replication-v1.json and scripts/run_phase3_external_discovery.py. Full-method extension protocol/runner: configs/phase3/external-method-extension-v1.json and scripts/run_phase3_external_method_trainpilot.py. Pilot inventory: results/phase3-followup/external-method-training-pilot-summary-v1.json. CIC development runner: scripts/run_phase3_discovery_development.py. Readiness check: scripts/phase3_followup_preflight.py. Raw machine-readable outputs are in results/phase3-followup/. Figures and expanded interpretation are in docs/phase3-plan/.", "Bodyx"),
              p("This addendum reports exploratory evidence and implementation status. It does not claim full Phase 3 completion, a successful defense, or final-test performance.", "Smallx")]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = FollowupDoc(OUT)
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()
