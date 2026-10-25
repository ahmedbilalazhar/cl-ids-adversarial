"""Read-only structural/numeric/PDF checks for the revised proposal.

Run with a Python environment containing pypdf, pdfplumber and Pillow.
These checks validate the document, not the proposed learning experiments.
"""
from pathlib import Path
import hashlib
import json
import re
from collections import Counter
from pypdf import PdfReader
import pdfplumber

root = Path(__file__).resolve().parents[3]
source = root / 'submissions/phase2-with-claude.tex'
pdf = root / 'output/pdf/phase2-with-claude.pdf'
out = Path(__file__).resolve().parent
s = source.read_text(encoding='utf-8')
log = pdf.with_suffix('.log').read_text(encoding='utf-8', errors='replace')
labels = re.findall(r'\\label\{([^}]+)\}',s)
refs = re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',s)
bib = re.findall(r'\\bibitem\{([^}]+)\}',s)
cites = [k.strip() for group in re.findall(r'\\cite\{([^}]+)\}',s) for k in group.split(',')]
reader=PdfReader(pdf)
text='\n'.join(f'PAGE {i+1}\n'+p.extract_text() for i,p in enumerate(reader.pages))
chars_outside=[]
page_summaries=[]
with pdfplumber.open(pdf) as doc:
    for i,page in enumerate(doc.pages):
        bad=[c for c in page.chars if c['x0'] < -1 or c['x1'] > page.width+1 or c['top'] < -1 or c['bottom'] > page.height+1]
        chars_outside.extend({'page':i+1,'text':c['text']} for c in bad)
        page_summaries.append({'page':i+1,'width_pt':round(page.width,2),'height_pt':round(page.height,2),'characters':len(page.chars),'rotation':page.rotation})
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
    'no_text_outside_page':not chars_outside,
    'parameter_count':76*128+128+128*64+64+64*15+15==19087,
    'fp32_payload_bytes':19087*4==76348,
    'full_trajectory_budget':18+3+60+144+144+72+192==633,
    'development_budget':18+3+60==81,
    'core_final_budget':5*4*12==240,
    'memory_continuations':2*12==24,
    'confirmatory_contrasts':3*3*2+4+3*2+1==29,
    'first_holm_resolution':2/2**11 <= .05/29 < 2/2**10,
    'no_fallback_attacker_protocol':'two attacked clients' not in s and 'fall-through' not in s,
}
report={
    'date':'2026-10-21',
    'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
    'pdf_pages':len(reader.pages),
    'bibliography_entries':len(bib),
    'labels':len(labels),
    'checks':checks,
    'page_summaries':page_summaries,
    'outside_page_characters':chars_outside,
    'compiler':'Tectonic 0.17.0, two-pass local compilation',
    'non_document_warnings':['Tectonic Fontconfig configuration notice','algorithm.sty upstream legacy-encoding comment notice','inputenc ignored by UTF-8 engine'],
    'scope':'Document validation only. No experiment outcomes or deployment feasibility are asserted.',
}
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(root/'tmp/phase2-audit/final-text.txt').write_text(text,encoding='utf-8')
print(json.dumps({'pages':report['pdf_pages'],'checks_passed':sum(checks.values()),'checks_total':len(checks),'failed':[k for k,v in checks.items() if not v]},indent=2))
if not all(checks.values()):
    raise SystemExit(1)
