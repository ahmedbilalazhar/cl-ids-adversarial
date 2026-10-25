"""Read-only checks of the proposal source, arithmetic and compiled PDF.

This checks the document, not an implemented experiment or NIST certification.
Run with Python containing pypdf and pdfplumber from the project root.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
from pypdf import PdfReader
import pdfplumber

root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
source=root/'submissions/phase2-with-claude.tex'
pdf=root/'output/pdf/phase2-with-claude.pdf'
s=source.read_text(encoding='utf-8')
log=pdf.with_suffix('.log').read_text(encoding='utf-8',errors='replace')
labels=re.findall(r'\\label\{([^}]+)\}',s)
refs=re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',s)
bib=re.findall(r'\\bibitem\{([^}]+)\}',s)
cites=[k.strip() for g in re.findall(r'\\cite\{([^}]+)\}',s) for k in g.split(',')]
reader=PdfReader(pdf)
page_text=[p.extract_text() for p in reader.pages]
text='\n'.join(f'PAGE {i+1}\n{t}' for i,t in enumerate(page_text))
page_summaries=[]
outside=[]
with pdfplumber.open(pdf) as doc:
    for i,p in enumerate(doc.pages,1):
        bad=[c for c in p.chars if c['x0'] < -1 or c['x1'] > p.width+1 or c['top'] < -1 or c['bottom'] > p.height+1]
        outside.extend({'page':i,'text':c['text']} for c in bad)
        page_summaries.append({'page':i,'width_pt':round(p.width,2),'height_pt':round(p.height,2),'characters':len(p.chars),'rotation':p.rotation})

assets={}
mirror_checks={}
for name in ['phase2-workflow-reviewed.tex','phase2-framework-reviewed.tex']:
    path=root/'submissions/figures'/name
    d=path.read_text(encoding='utf-8').strip()
    marker=f'% ===== Inlined from figures/{name} (self-contained build) ====='
    start=s.index(marker)+len(marker)
    stop=s.index(r'\end{figure}',start)+len(r'\end{figure}')
    mirror_checks[name]=s[start:stop].strip()==d
    assets[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()

checks={
    'all_references_defined':not(set(refs)-set(labels)),
    'unique_labels':len(labels)==len(set(labels)),
    'all_citations_defined':not(set(cites)-set(bib)),
    'unique_bibliography_keys':len(bib)==len(set(bib)),
    'ten_additional_critical_reviews':len(re.findall(r'\\subsubsection\*\{P(?:[4-9]|1[0-3]) ',s))==10,
    'twelve_methodology_steps':len(re.findall(r'\\subsection\{Step \d+ ',s))==12,
    'no_source_control_characters':not any(ord(c)<32 and c not in '\n\r\t' for c in s),
    'no_unresolved_pdf_references':'??' not in text,
    'no_replacement_glyphs':'\ufffd' not in text,
    'no_overfull_boxes':'Overfull' not in log,
    'no_undefined_tex_references':not bool(re.search(r'(undefined references|Citation .* undefined|Reference .* undefined)',log)),
    'no_blank_pdf_pages':all(p['characters']>100 for p in page_summaries),
    'no_text_outside_page':not outside,
    'no_nearly_empty_last_page':page_summaries[-1]['characters']>700,
    'parameter_count':76*128+128+128*64+64+64*15+15==19087,
    'fp32_payload_bytes':19087*4==76348,
    'replay_slot_bytes':76*4+15*4+8+8+1==381,
    'replay_capacity_bytes':381*500==190500,
    'full_trajectory_budget':18+3+60+144+144+72+192==633,
    'development_budget':18+3+60==81,
    'core_final_budget':5*4*12==240,
    'core_plus_development':240+81==321,
    'memory_continuations':2*12==24,
    'confirmatory_contrasts':3*3*2+4+3*2+1==29,
    'first_holm_resolution':2/2**11 <= .05/29 < 2/2**10,
    'self_contained_diagrams':not bool(re.search(r'\\(?:input|includegraphics)\{figures/',s)),
    'exact_diagram_mirrors':all(mirror_checks.values()),
    'two_rendered_diagrams':all(sum(f'Figure {i}:' in t for t in page_text)==1 for i in [1,2]),
    'per_example_squared_importance_declared':r'\sum_{i\in\mathcal F_{k,t}}' in s and r'\right]^2' in s and 'before} averaging' in s,
    'initial_importance_zero_declared':r'I_{k,0}=0' in s,
    'fixed_importance_sample_size_declared':r'\min(1024,n_{k,t})' in s,
    'loss_reduction_declared':'each replay term is a separate mean over the same replay draw' in s,
    'pre_update_replay_targets_declared':r'\emph{pre-update} cache' in s,
    'bounded_insertion_guard_declared':'Only that pass proposes insertions' in s and 'A persistent counter and seen-ID set' not in s,
    'dc_schedule_limitation_disclosed':r'\textbf{What DC actually tests.}' in s and 'new-label protection under equal admitted volume' in s,
    'zero_range_scaler_declared':'For a feature with zero T0 range, use denominator one' in s,
    'benign_cohort_support_declared':r'$\ge4$ test components' in s and 'four non-empty, disjoint cohorts' in s,
    'final_test_access_contract_declared':'predictions are generated after the complete locked run set' in s,
    'industry_guidance_not_certification':'planned acceptance checks, not claims of executed certification' in s,
    'no_fallback_attacker_protocol':'two attacked clients' not in s and 'fall-through' not in s,
}
warnings=[]
if 'Underfull' in log:
    warnings.append('One underfull TikZ node paragraph (badness 1097); inspected visually, with no clipped or overlapping text.')
warnings.extend(['Tectonic Fontconfig configuration notice','Upstream algorithm.sty legacy-encoding comment notice; no replacement glyph in the output','inputenc ignored by UTF-8 engine'])
report={
    'review_started':'2026-10-21','review_completed':'2026-10-22',
    'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
    'diagram_sha256':assets,
    'pdf_pages':len(reader.pages),'bibliography_entries':len(bib),'labels':len(labels),
    'checks':checks,'checks_passed':sum(checks.values()),'checks_total':len(checks),
    'mirror_checks':mirror_checks,'page_summaries':page_summaries,
    'outside_page_characters':outside,
    'compiler':'Tectonic 0.17.0, rerun until references stabilised',
    'warnings':warnings,
    'visual_review_record':'visual_review.json',
    'scope':'Source assertions check declared rules only. Arithmetic checks are independent calculations. PDF checks concern compilation, glyphs and page bounds. No experiment, acceptance test or deployment validation is claimed.',
}
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(root/'tmp/phase2-standard-review/current-text.txt').write_text(text,encoding='utf-8')
print(json.dumps({'pages':len(reader.pages),'bibliography_entries':len(bib),'checks_passed':sum(checks.values()),'checks_total':len(checks),'failed':[k for k,v in checks.items() if not v]},indent=2))
if not all(checks.values()):
    raise SystemExit(1)
