"""Package only explicit project evidence, excluding local environments and raw data."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'submissions/phase3-report'


def main():
    validation=json.loads((OUT/'cpu-validation.json').read_text())
    assert validation['required_complete'] and validation['all_hashes_valid']
    pdf=json.loads((OUT/'pdf-validation.json').read_text())
    assert pdf['pages']>=4 and all(p['characters']>100 for p in pdf['page_checks'])
    paths=set()
    def include(folder):
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('preview-'):
                if 'source-review' in p.parts and p.suffix in ('.pdf','.tex'):continue
                paths.add(p)
    for folder in ('submissions/phase3-report','phase3-implementation',
                   'src','configs/phase3','docs/phase3-plan','docs/phase3-reference'):
        include(folder)
    selected=json.loads((OUT/'cpu-selected-results.json').read_text())
    for name in selected['run_hashes']:paths.add(ROOT/'results/phase3-cpu-supplement/runs'/name)
    for name in ('identity.json','environment.json'):paths.add(ROOT/'results/phase3-cpu-supplement'/name)
    completion=ROOT/'results/phase3-cpu-supplement/completion.json'
    if completion.exists() and json.loads(completion.read_text())['count']==selected['count']:paths.add(completion)
    for name in ('phase3_evidence.py','phase3_references.py','run_phase3_cpu_study.py','analyse_phase3_cpu.py',
                 'rebuild_submission_analysis.py','build_phase3_figures.py','write_phase3_report.py',
                 'export_phase3_pdf.py','export_phase3_tex.py','package_phase3_submission.py','reproduce_phase3_submission.py',
                 'build_phase3_upload.py','materialize_submission_data.py'):
        paths.add(ROOT/'scripts'/name)
    for name in ('docs/phase3-cpu-supplement-protocol.md','tests/test_phase3_cpu_supplement.py',
                 'submissions/phase3-methodology-amendment.md','submissions/phase2-with-claude.tex',
                 'requirements.txt','README.md'):
        paths.add(ROOT/name)
    # Match and include observed package manifests without duplicating >100 MB arrays.
    for seed in (101,102,103):
        paths.add(ROOT/f'data/processed/phase3-cpu-v2/s{seed}-p000/train/manifest.json')
        paths.add(ROOT/f'data/processed/phase3-cpu-v2/s{seed}-p000/preparation.json')
    paths.add(ROOT/'data/processed/phase3-reference74-v1/development/manifest.json')
    paths.add(ROOT/'data/processed/phase3-reference74-v1/preparation-report.json')
    paths.discard(OUT/'package-inventory.json')
    inventory={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError,FileNotFoundError):commit='e1abab6c2fe174774934870c698fe57fd59562f0 (source archive)'
    manifest=dict(schema='phase3-submission-inventory-v1',files=inventory,
        base_git_commit=commit,
        local_changes_included=True,final_test_included=False,cpu_runs=validation['count'])
    inv=OUT/'package-inventory.json';inv.write_text(json.dumps(manifest,indent=2));paths.add(inv)
    archive=ROOT/'submissions/phase3-submission.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(paths):z.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name,sha in inventory.items():assert hashlib.sha256(z.read(name)).hexdigest()==sha
    print('Verified',len(paths),'files;',round(archive.stat().st_size/1e6,2),'MB;',archive)


if __name__=='__main__':main()
