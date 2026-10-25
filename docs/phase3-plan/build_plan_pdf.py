"""Render the planning documents; this does not run research experiments."""
from pathlib import Path
import html
import json
import re
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    LongTable, TableStyle, Preformatted, Flowable, KeepTogether, CondPageBreak,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[2]
DOCS = Path(__file__).resolve().parent
OUT = ROOT / "output/pdf/phase3-research-implementation-plan.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)
REVISION = json.loads((DOCS / "research-status.json").read_text(encoding="utf-8"))["current_iteration"]
FONTS = Path("C:/Windows/Fonts")
for name, filename in [("Plan", "arial.ttf"), ("PlanBold", "arialbd.ttf"), ("PlanItalic", "ariali.ttf"), ("PlanMono", "consola.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONTS / filename)))
pdfmetrics.registerFontFamily("Plan", normal="Plan", bold="PlanBold", italic="PlanItalic", boldItalic="PlanBold")
pdfmetrics.registerFontFamily("PlanMono", normal="PlanMono", bold="PlanMono", italic="PlanMono", boldItalic="PlanMono")

NAVY = colors.HexColor("#19364B")
TEAL = colors.HexColor("#176B70")
INK = colors.HexColor("#23313C")
PALE = colors.HexColor("#EEF4F5")
LINE = colors.HexColor("#CCD7DB")
W, H = A4
MARGIN = 42
WIDTH = W - 2 * MARGIN

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("PBody", fontName="Plan", fontSize=9.3, leading=13.4, textColor=INK, spaceAfter=7, allowWidows=0, allowOrphans=0))
styles.add(ParagraphStyle("PBodyKeep", parent=styles["PBody"], keepWithNext=True))
styles.add(ParagraphStyle("PH1", fontName="PlanBold", fontSize=15, leading=19, textColor=NAVY, spaceBefore=14, spaceAfter=9, keepWithNext=True))
styles.add(ParagraphStyle("PH1NoTOC", parent=styles["PH1"]))
styles.add(ParagraphStyle("PH1BeforeTable", parent=styles["PH1NoTOC"], keepWithNext=False))
styles.add(ParagraphStyle("PH2", fontName="PlanBold", fontSize=11, leading=15, textColor=TEAL, spaceBefore=10, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle("PTitle", fontName="PlanBold", fontSize=28, leading=33, textColor=NAVY, spaceAfter=18))
styles.add(ParagraphStyle("PSubtitle", fontName="Plan", fontSize=13, leading=19, textColor=TEAL, spaceAfter=16))
styles.add(ParagraphStyle("PSmall", fontName="Plan", fontSize=8.3, leading=11.6, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle("PTable", fontName="Plan", fontSize=8.25, leading=11.4, textColor=INK))
styles.add(ParagraphStyle("PTableHead", parent=styles["PTable"], fontName="PlanBold", textColor=NAVY))
styles.add(ParagraphStyle("PCode", fontName="PlanMono", fontSize=7.7, leading=10.2, textColor=INK, leftIndent=7, spaceBefore=4, spaceAfter=9))
styles.add(ParagraphStyle("PBullet", parent=styles["PBody"], leftIndent=12, firstLineIndent=-9, spaceAfter=4))


def plain(s):
    for a, b in {"–": "-", "—": "-", "‑": "-", "−": "-", "“": '"', "”": '"', "‘": "'", "’": "'", "→": "->", "×": "x", "≥": ">=", "≤": "<=", "≈": "~", "…": "..."}.items():
        s = s.replace(a, b)
    return s


def inline(s):
    s = html.escape(plain(s))
    s = s.replace("&lt;br/&gt;", "<br/>")
    protected = []
    def protect(value):
        protected.append(value)
        return f"PLANINLINE{len(protected)-1}TOKEN"
    s = re.sub(r"`([^`]+)`", lambda m: protect(f'<font name="PlanMono">{m[1]}</font>'), s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: protect(f'<link href="{m[2]}" color="#176B70">{m[1]}</link>' if m[2].startswith("https://") else f'<b>{m[1]}</b>'), s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    for i in reversed(range(len(protected))):
        s = s.replace(f"PLANINLINE{i}TOKEN", protected[i])
    return s


def para(s, style="PBody"):
    return Paragraph(inline(s), styles[style])


def table(lines):
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines]
    rows = [r for r in rows if not all(re.fullmatch(r"[:\- ]+", c or " ") for c in r)]
    count = max(map(len, rows))
    weights = {2: [.31, .69], 3: [.23, .41, .36], 4: [.20, .27, .25, .28], 5: [.12, .18, .23, .23, .24], 6: [.18, .09, .09, .09, .13, .42]}.get(count, [1 / count] * count)
    cells = [[para(c, "PTableHead" if i == 0 else "PTable") for c in r + [""] * (count - len(r))] for i, r in enumerate(rows)]
    t = LongTable(cells, colWidths=[WIDTH * x for x in weights], repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("LINEBELOW", (0, 0), (-1, 0), .65, TEAL),
        ("LINEBELOW", (0, 1), (-1, -1), .25, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [t, Spacer(1, 9)]


def markdown(path, omit_title=True, include_toc=True):
    lines = path.read_text(encoding="utf-8").splitlines()
    story, i = [], 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("# "):
            if not omit_title:
                story.append(para(s[2:], "PH1"))
            i += 1
        elif s.startswith("### "):
            story.append(para(s[4:], "PH2")); i += 1
        elif s.startswith("## "):
            following=i+1
            while following<len(lines) and not lines[following].strip():following+=1
            table_follows=not include_toc and following<len(lines) and lines[following].strip().startswith("|")
            if table_follows:story.append(CondPageBreak(120))
            story.append(para(s[3:], "PH1BeforeTable" if table_follows else "PH1" if include_toc else "PH1NoTOC")); i += 1
        elif s.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                line = plain(lines[i]).expandtabs(2)
                block.extend(textwrap.wrap(line, width=104, subsequent_indent="  ", replace_whitespace=False, drop_whitespace=False) or [""])
                i += 1
            story.append(KeepTogether([Preformatted("\n".join(block), styles["PCode"])]))
            i += 1
        elif s.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i]); i += 1
            story.extend(table(block))
        elif s.startswith("- ") or re.match(r"^\d+\. ", s):
            story.append(para(s if not s.startswith("- ") else "- " + s[2:], "PBullet")); i += 1
        elif s.startswith("> "):
            story.append(para(s[2:], "PSubtitle")); i += 1
        else:
            block = [s]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||```|- |\d+\. |>)", lines[i].strip()):
                block.append(lines[i].strip()); i += 1
            next_content = i
            while next_content < len(lines) and not lines[next_content].strip():
                next_content += 1
            style = "PBodyKeep" if next_content < len(lines) and lines[next_content].strip().startswith("```") else "PBody"
            story.append(para(" ".join(block), style))
    return story


class Diagram(Flowable):
    def __init__(self, nodes, loop=None):
        Flowable.__init__(self)
        self.nodes, self.loop = nodes, loop
        self.width = WIDTH
        self.height = len(nodes) * 58 + 24

    def draw(self):
        c = self.canv
        left, boxw, boxh = 10, WIDTH - 45, 43
        centers = []
        for i, (title, body) in enumerate(self.nodes):
            y = self.height - (i + 1) * 58
            c.setStrokeColor(LINE); c.setFillColor(PALE if i % 2 == 0 else colors.white)
            c.roundRect(left, y, boxw, boxh, 4, stroke=1, fill=1)
            p = para(title, "PTableHead")
            _, ph = p.wrap(boxw - 16, 100)
            p.drawOn(c, left + 8, y + boxh - 7 - ph)
            p = para(body, "PSmall")
            _, ph = p.wrap(boxw - 16, 100)
            p.drawOn(c, left + 8, y + 6)
            centers.append((left + boxw, y + boxh / 2))
            if i:
                x = left + boxw / 2
                start = y + 58
                end = y + boxh
                c.setStrokeColor(TEAL); c.setFillColor(TEAL)
                c.line(x, start, x, end + 4)
                path = c.beginPath(); path.moveTo(x - 3, end + 6); path.lineTo(x, end + 1); path.lineTo(x + 3, end + 6); path.close()
                c.drawPath(path, fill=1, stroke=0)
        if self.loop:
            start, end = self.loop
            sx, sy = centers[start]; ex, ey = centers[end]
            rx = WIDTH - 8
            c.setStrokeColor(TEAL); c.setDash(3, 2)
            p = c.beginPath(); p.moveTo(sx, sy); p.lineTo(rx, sy); p.lineTo(rx, ey); p.lineTo(ex + 4, ey)
            c.drawPath(p); c.setDash()
            c.setFillColor(TEAL)
            p = c.beginPath(); p.moveTo(ex + 6, ey - 3); p.lineTo(ex + 1, ey); p.lineTo(ex + 6, ey + 3); p.close(); c.drawPath(p, stroke=0, fill=1)


class PlanDoc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(str(path), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=48, bottomMargin=42, title="Phase 3 Research Implementation and Experimental Evaluation Plan", author="Research planning package", allowSplitting=True)
        frame = Frame(MARGIN, 42, WIDTH, H - 90, id="normal", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id="normal", frames=frame, onPage=self.page_chrome))
        self.heading_counter = 0

    def beforeDocument(self):
        self.heading_counter = 0

    def page_chrome(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Plan", 8)
        canvas.setFillColor(NAVY)
        if doc.page > 1:
            canvas.drawString(MARGIN, H - 27, "COMPUTER NETWORKS | PHASE 3 IMPLEMENTATION PLAN")
            canvas.setStrokeColor(LINE); canvas.line(MARGIN, H - 34, W - MARGIN, H - 34)
        canvas.setFillColor(INK)
        canvas.drawString(MARGIN, 24, "Research plan | No executed Phase 3 results | 24 October 2026")
        canvas.drawRightString(W - MARGIN, 24, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "PH1":
            if flowable.getPlainText() == "Contents":
                return
            self.heading_counter += 1
            key = f"heading-{self.heading_counter}"
            text = flowable.getPlainText()
            level = 1 if re.match(r"^\d+\.", text) else 0
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level)
            self.notify("TOCEntry", (level, text, self.page, key))


def build_main():
    story = [Spacer(1, 72), para("RESEARCH IMPLEMENTATION<br/>AND EXPERIMENTAL EVALUATION", "PTitle"), para("A focused Phase 3 plan for federated continual intrusion detection", "PSubtitle"), para("Two authors. Eight individually operated compute contributors. Five simulated federated clients.", "PBody"), Spacer(1, 18)]
    story.extend(table(["| Decision | Recommendation |", "|---|---|", "| First delivery | Correct implementation, audited data, paired baselines and meaningful ablations |", "| Research starter | 441 logical full trajectories; 432 distinct with valid development aliases |", "| With audited external replication | 513 logical full trajectories; 504 distinct with valid development aliases |", "| Diagnostic | 24 logical oracle rows; 12 new E3/E4 executions with exact control aliases |", "| Compute | Profile first; no GPU runtime or quota availability is assumed |"] ))
    story += [Spacer(1, 18), para(f"Reviewed research plan, iteration {REVISION}. Prepared 24 October 2026 (Asia/Karachi).", "PBody"), para("This document is a proposed implementation and evaluation plan. It contains source audits, research evidence, derived constraints and hypothetical budgets. It does not report experiments, guarantee publication or certify deployment readiness.", "PSmall"), PageBreak(), para("Contents", "PH1")]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("TOCPlan", fontName="PlanBold", fontSize=9, leading=13, textColor=NAVY, leftIndent=0, firstLineIndent=0, spaceBefore=4), ParagraphStyle("TOCPlanChild", fontName="Plan", fontSize=9, leading=12, textColor=INK, leftIndent=12, firstLineIndent=0, spaceBefore=2)]
    story += [toc, PageBreak(), para("Executive recommendation", "PH1")]
    story.extend(markdown(DOCS / "START-HERE.md", include_toc=False))
    story += [PageBreak(), para("Complete implementation and evaluation plan", "PH1")]
    story.extend(markdown(DOCS / "plan.md"))
    story += [PageBreak(), para("Appendix A. Information boundaries", "PH1"), para("The complete editable diagrams and review are in docs/phase3-plan/methodology-diagram-review.md. Final-test outputs have no route back into training or scope selection.")]
    story.append(Diagram([
        ("1. Adopt source and own-row validity rules", "Freeze Monday-only T0 fit IDs/statistics before future-label conflicts."),
        ("2. Build representations, closure and data roles", "Raw/final-input and session links; quarantine; fixed support-audited split."),
        ("3. Develop on train and development only", "Reference engine, acceptance evidence, CPU/GPU profile and tuning."),
        ("4. Lock the complete study", "Code/data/runtime, selected matrix, seeds, endpoints and analysis."),
        ("5. Execute paired jobs on contributor workers", "Each worker simulates all five clients; preserve complete state."),
        ("6. Validate the selected output matrix", "Hash identities, parents, completeness and failure dispositions."),
        ("7. Read-only evaluation on sealed banks", "Common evaluation runtime; full active head; fixed denominators."),
        ("8. Analyze and report", "Paired effects, 29-test Holm family, figures, limitations and claim ledger."),
    ]))
    story += [PageBreak(), para("Appendix B. Stage and round lifecycle", "PH1"), para("The dashed return repeats the locked round budget. Complete state proceeds to the next stage; evaluation is a later separate consumer.")]
    story.append(Diagram([
        ("1. Supplied labels and active registry", "E2-only source-label flips; append head rows, then freeze scorer."),
        ("2. Client-local admission", "Lock accepted IDs and distinct current-row counts for this stage."),
        ("3. Immutable shared broadcast", "All active clients start from the same weights; reset local Adam."),
        ("4. Local update and retained state", "FT/EI/DER losses; first-pass-only pre-update replay insertion."),
        ("5. FedAvg", "Aggregate local models with distinct admitted-row weights."),
        ("6. Final broadcast after the last round", "EI commits per-example importance/anchor; FT and replay skip this update."),
        ("7. Commit complete checkpoint", "Model, class map, retained state, cursors and independent RNG states."),
        ("8. Next stage or training complete", "E3/E4 stop fresh corruption; retained poison can remain."),
    ], loop=(4, 2)))
    story += [PageBreak(), para("Appendix C. Primary-source ledger", "PH1"), para("Verification depth and limitations are recorded in docs/phase3-plan/sources.json. Sources support planning claims, not nonexistent experimental performance.")]
    ledger = json.loads((DOCS / "sources.json").read_text(encoding="utf-8"))
    for r in ledger["sources"]:
        story.append(KeepTogether([
            para(f'**{r["id"]}. {r["title"]}** - {r["kind"]}.', "PSmall"),
            Paragraph(f'<link href="{html.escape(r["url"])}" color="#176B70">{html.escape(r["url"])}</link>', styles["PSmall"]),
            para(r["limits"], "PSmall"), Spacer(1, 5)
        ]))

    PlanDoc(OUT).multiBuild(story)
    print(json.dumps({"pdf": str(OUT), "bytes": OUT.stat().st_size, "sources": len(ledger["sources"])}))


if __name__ == "__main__":
    build_main()
