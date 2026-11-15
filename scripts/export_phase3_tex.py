"""Export current evidence to self-contained LaTeX and compile with Tectonic."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile

import pymupdf
from phase3_references import REFERENCES

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'submissions/phase3-report'


def main():
    source=(OUT/'report.md').read_text(encoding='utf-8')
    body='\n\n'.join(source.split('\n\n')[2:])
    body=body.replace('\n## ','\n# ')
    if body.startswith('## '):body=body[1:]
    tmp=ROOT/'tmp/phase3-tex-input.md';tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(body,encoding='utf-8')
    pandoc=shutil.which('pandoc');tectonic=shutil.which('tectonic')
    if not pandoc or not tectonic:raise RuntimeError('Install Pandoc and Tectonic, or use export_phase3_pdf.py for the PDF fallback.')
    subprocess.run([pandoc,str(tmp),'--standalone','--from','markdown+autolink_bare_uris','--to','latex',
        '-V','papersize:a4','-V','geometry:margin=0.8in','-V','fontsize=10pt',
        '--metadata','title=Poisoning Persistence and Legitimate Adaptation in Federated Continual Intrusion Detection',
        '--metadata','author=Saneedullah (23I-2568) and Ahmed Bilal (23I-2581)',
        '--metadata','date=Computer Networks, Phase 3 | 15 November 2026',
        '-o',str(OUT/'phase3-report.tex')],cwd=OUT,check=True)
    tex=(OUT/'phase3-report.tex').read_text(encoding='utf-8')
    tex=re.sub(r'\\caption\{Figure \d+\. ',r'\\caption{',tex)
    # Use native vector figures in the compiled report and Overleaf source.
    def vector_figure(match):
        path=match.group(1)
        pdf_path=path[:-4]+'.pdf' if path.endswith('.png') else path
        return match.group(0).replace(path,pdf_path) if (OUT/pdf_path).exists() else match.group(0)
    tex=re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',vector_figure,tex)
    # Apply a restrained report theme while keeping the source self-contained.
    theme=r'''\usepackage{float}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{titling}
\usepackage{fancyhdr}
\usepackage{caption}
\definecolor{reportnavy}{HTML}{17324D}
\definecolor{reportteal}{HTML}{147D83}
\definecolor{reportmuted}{HTML}{5D6B78}
\AtBeginDocument{\hypersetup{colorlinks=true,linkcolor=reportteal,citecolor=reportteal,urlcolor=reportteal}}
\pretitle{\begin{center}\vspace*{0.65cm}\color{reportnavy}\Huge\bfseries}
\posttitle{\par\vspace{0.22em}\end{center}\vspace{-0.3em}}
\preauthor{\begin{center}\large\color{reportmuted}}
\postauthor{\end{center}}
\predate{\begin{center}\small\color{reportteal}}
\postdate{\end{center}\vspace{0.5em}}
\titleformat{\section}{\Large\bfseries\color{reportnavy}}{}{0pt}{}
\titleformat{\subsection}{\large\bfseries\color{reportteal}}{}{0pt}{}
\titleformat{\subsubsection}{\normalsize\bfseries\color{reportnavy}}{}{0pt}{}
\titlespacing*{\section}{0pt}{1.6em}{0.65em}
\titlespacing*{\subsection}{0pt}{1.1em}{0.35em}
\captionsetup{font=small,labelfont={bf,color=reportnavy},textfont={color=reportmuted},skip=7pt}
\setlength{\parskip}{5pt plus 1pt}
\setlength{\headheight}{15pt}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textsc{Computer Networks | Phase 3}}
\fancyhead[R]{\small\color{reportmuted}\nouppercase{\leftmark}}
\fancyfoot[L]{\small\color{reportmuted}23I-2568 | 23I-2581}
\fancyfoot[C]{\small\color{reportmuted}Research implementation and evaluation}
\fancyfoot[R]{\small\color{reportnavy}\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}'''
    tex=tex.replace(r'\usepackage{xcolor}',theme)
    tex=tex.replace('\\begin{document}',r'\floatplacement{figure}{H}'+'\n'+r'\setlength{\emergencystretch}{3em}'+'\n'+r'\setcounter{secnumdepth}{0}'+'\n'+r'\begin{document}')
    # Keep the upload self-contained: native numbered citations and bibitems,
    # with no separate BibTeX invocation or external bibliography file.
    marker=tex.index(r'\hypertarget{references}')
    body=tex[:marker]
    for number,(key,_,_) in enumerate(REFERENCES,1):
        body=body.replace('{[}'+str(number)+'{]}',r'\cite{'+key+'}')
    entries=[]
    for key,entry,url in REFERENCES:
        entry=entry.replace('&',r'\&').replace('_',r'\_').replace('%',r'\%')
        entries.append(r'\bibitem{'+key+'} '+entry+' '+r'\url{'+url+'}')
    tex=body+r'\begin{thebibliography}{99}'+'\n'+'\n\n'.join(entries)+'\n'+r'\end{thebibliography}'+'\n'+r'\end{document}'+'\n'
    (OUT/'phase3-report.tex').write_text(tex,encoding='utf-8')
    build=ROOT/'tmp/phase3-report-build';build.mkdir(parents=True,exist_ok=True)
    subprocess.run([tectonic,'phase3-report.tex','--outdir',str(build)],cwd=OUT,check=True)
    preview=ROOT/'tmp/pdfs/phase3-report';preview.mkdir(parents=True,exist_ok=True)
    compiled=build/'phase3-report.pdf'
    doc=pymupdf.open(compiled);checks=[]
    for i,page in enumerate(doc):
        assert page.get_text().strip()
        page.get_pixmap().save(str(preview/f'page-{i+1:02}.png'))
        checks.append(dict(page=i+1,characters=len(page.get_text()),width=page.rect.width,height=page.rect.height))
    (OUT/'pdf-validation.json').write_text(json.dumps(dict(pages=len(doc),engine='Tectonic/XeTeX',page_checks=checks),indent=2))
    final=ROOT/'output/pdf';final.mkdir(parents=True,exist_ok=True);shutil.copy2(compiled,final/'phase3-report-submission.pdf')
    print('Compiled and rendered current TeX report:',len(doc),'pages')


if __name__=='__main__':main()
