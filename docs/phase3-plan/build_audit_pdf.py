"""Render the data/protocol gap audit; no model experiments are run."""
import json
from reportlab.platypus import Spacer, PageBreak, Image, CondPageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from build_plan_pdf import PlanDoc, para, markdown, styles, DOCS, ROOT, MARGIN, W, H, NAVY, TEAL, INK, LINE

OUT=ROOT/"output/pdf/phase3-implementation-evaluation-gap-audit.pdf"


class AuditDoc(PlanDoc):
    def page_chrome(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Plan",8)
        canvas.setFillColor(NAVY)
        if doc.page>1:
            canvas.drawString(MARGIN,H-27,"PHASE 3 | IMPLEMENTATION AND EVALUATION GAP AUDIT")
            canvas.setStrokeColor(LINE);canvas.line(MARGIN,H-34,W-MARGIN,H-34)
        canvas.setFillColor(INK)
        canvas.drawString(MARGIN,24,"Conditional data evidence; no model results | 24 October 2026")
        canvas.drawRightString(W-MARGIN,24,str(doc.page))
        canvas.restoreState()


def main():
    story=[Spacer(1,65),para("IMPLEMENTATION AND<br/>EVALUATION GAP AUDIT","PTitle"),
        para("Evidence, protocol corrections and a concrete completion path","PSubtitle"),
        para("Computer Networks Research Project | Phase 3","PBody"),Spacer(1,15),
        para("This supplement extends the revised Phase 2 implementation plan. It contains full-source data censuses, conditional component/split/ownership evidence, proposed amendments and a severity-ranked gap register. It reports no trained-model performance.","PBody"),
        para("Read the executive audit first. The source profiles remain prospective; documented fixes still require the appropriate implementation and acceptance evidence.","PBody"),
        Spacer(1,16),para("Prepared 24 October 2026. Editable sources and machine-readable evidence are included in the companion planning package.","PSmall"),PageBreak(),para("Contents","PH1")]
    toc=TableOfContents()
    toc.levelStyles=[ParagraphStyle("AuditTOC",fontName="PlanBold",fontSize=9,leading=13,textColor=NAVY,spaceBefore=4),ParagraphStyle("AuditTOCChild",fontName="Plan",fontSize=8.5,leading=12,textColor=INK,leftIndent=12)]
    story += [toc,PageBreak()]
    sections=[
        ("Final source-semantics recommendation","feature-semantics-and-final-recommendation.md"),
        ("Executive audit","audit-executive-summary.md"),
        ("Data-release decision","data-release-decision.md"),
        ("Feature domains and precision","feature-domain-and-precision-review.md"),
        ("Population and curation","data-curation-estimand.md"),
        ("Benign sampling amendment","benign-component-selection-amendment.md"),
        ("Realized dose and quota limits","realized-dose-and-quota-limits.md"),
        ("Exact protocol closure","protocol-closure-spec.md"),
        ("Evaluation strengthening","evaluation-strengthening.md"),
        ("Components and controls","component-and-control-spec.md"),
        ("Capture context and generalization","capture-context-and-generalization.md"),
        ("Resources and messages","resource-and-message-contract.md"),
        ("Rubric and readiness","rubric-and-readiness.md"),
        ("Detailed gap register","second-audit-gap-register.md"),
    ]
    for index,(title,name) in enumerate(sections):
        if index:story.extend([CondPageBreak(190),Spacer(1,12)])
        story.append(para(title,"PH1"))
        story.extend(markdown(DOCS/name,include_toc=False))
    figures=[("candidate-support.png","Earlier 76-feature negative-screened corrected profile: support counts, not the preferred 74-feature candidate."),
             ("benign-volume.png","Original conditional candidate: proposed sampling changes workload; not a model result."),
             ("realized-dose.png","Earlier 76-feature profiles: global contamination across prescribed seeds, not attack success.")]
    available=[(ROOT/"output/figures/phase3-audit"/name,caption) for name,caption in figures if (ROOT/"output/figures/phase3-audit"/name).exists()]
    if available:
        story += [PageBreak(),para("Data-feasibility figures","PH1")]
        for path,caption in available:
            story += [Image(str(path),width=W-2*MARGIN,height=(W-2*MARGIN)*.6),para(caption,"PSmall"),Spacer(1,10)]
    doc=AuditDoc(OUT);doc.title="Phase 3 Implementation and Evaluation Gap Audit";doc.multiBuild(story)
    print(json.dumps({"pdf":str(OUT),"bytes":OUT.stat().st_size,"sections":len(sections),"figures":len(available)}))


if __name__=="__main__":
    main()
