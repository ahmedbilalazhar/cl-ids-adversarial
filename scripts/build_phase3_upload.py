"""Create the single roll-number upload ZIP, with deduplicated prepared data."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
ROLLS='23I-2568_23I-2581'


def main():
    report=ROOT/'submissions/phase3-report'
    valid=json.loads((report/'cpu-validation.json').read_text())
    assert valid['required_complete'] and valid['all_hashes_valid']
    base=ROOT/'submissions/phase3-submission.zip';assert base.exists()
    output=ROOT/'submissions/phase3-final'/f'{ROLLS}.zip'
    output.parent.mkdir(parents=True,exist_ok=True)
    study=json.loads((ROOT/'results/phase3-cpu-supplement/identity.json').read_text())
    mapping={};shared={}
    for rel,expected in study['inputs'].items():
        rel=rel.replace('\\','/')
        if not rel.endswith('.npy'):continue
        assert rel.startswith('data/processed/') and 'test' not in rel.lower()
        source=ROOT/rel;actual=hashlib.sha256(source.read_bytes()).hexdigest();assert actual==expected
        name=f'data/shared/{actual}.npy';mapping[rel]=dict(shared=name,sha256=actual)
        shared[name]=source
    for source in sorted((ROOT/'data/processed/phase3-reference74-v1/train').rglob('*.npy')):
        actual=hashlib.sha256(source.read_bytes()).hexdigest();name=f'data/shared/{actual}.npy'
        mapping[source.relative_to(ROOT).as_posix()]=dict(shared=name,sha256=actual)
        shared[name]=source
    input_map=dict(schema='phase3-deduplicated-inputs-v1',files=mapping,
        final_test_included=False,unique_files=len(shared),materialize_command='python scripts/materialize_submission_data.py')
    (ROOT/'data/submission-input-map.json').write_text(json.dumps(input_map,indent=2))
    entries={}
    def write_bytes(z,name,content):
        z.writestr(f'{ROLLS}/{name}',content);entries[name]=hashlib.sha256(content).hexdigest()
    start=f'''# Computer Networks - Phase 3 submission

Saneedullah (23I-2568) and Ahmed Bilal (23I-2581)

Open **Phase3_Report.pdf** first. It is the authoritative report: 696 archived GPU
trajectories and {valid['count']} validated CPU supplement trajectories, clearly separated.
The report incorporates and corrects the supplied earlier report, with nine
regenerated figure sets and 13 relevant primary references.

- Phase3_Report.tex and figures/: self-contained XeLaTeX source with vector figures.
- submissions/phase3-report/: corrected tables, per-family metrics, validation,
  source ledgers, editable Markdown and reproduction instructions.
- phase3-implementation/: implementation, original executed notebook and raw GPU results.
- results/phase3-cpu-supplement/: selected complete CPU runs and immutable identities.
- data/shared/ and data/submission-input-map.json: prepared training/development
  inputs stored once per byte identity. No final-test features or raw 343 MB capture.
- src/, configs/, docs/: preparation source, methodology and preprocessing evidence.
- tests/: targeted scientific-invariant checks. No installed environment is bundled.

To regenerate the evidence/report after installing the observed Python dependencies,
Pandoc and Tectonic, run from this directory:

    python scripts/reproduce_phase3_submission.py

To train on the included prepared inputs:

    python scripts/materialize_submission_data.py
    python scripts/run_phase3_cpu_study.py

Completed runs are reused only when input/configuration/source/runtime identities
match. A different runtime requires a fresh --output directory, and must not be
pooled with these results. To check code invariants:

    python -m pytest tests/test_phase3_cpu_supplement.py -q

Native TeX uses XeLaTeX. The original notebook's Part C statistics and metric names
are historical; use this report and corrected CSVs. Historical methodology documents
are provenance and not claims that every Phase 2 proposal was executed.

UPLOAD_INVENTORY.json contains hashes of every supplied file. The portal ZIP is
named only with the two roll numbers. No other report drafts are upload entry points.
'''
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        with zipfile.ZipFile(base) as source:
            for info in source.infolist():
                if info.filename.endswith('package-inventory.json'):continue
                write_bytes(z,info.filename,source.read(info.filename))
        write_bytes(z,'START_HERE.md',start.encode())
        pdf_check=json.loads((report/'pdf-validation.json').read_text())
        pdf_path=report/pdf_check.get('pdf','phase3-report.pdf')
        assert hashlib.sha256(pdf_path.read_bytes()).hexdigest()==pdf_check['sha256']
        write_bytes(z,'Phase3_Report.pdf',pdf_path.read_bytes())
        write_bytes(z,'Phase3_Report.tex',(report/'phase3-report.tex').read_bytes())
        for p in sorted((report/'figures').glob('*')):
            if p.suffix in ('.pdf','.png'):write_bytes(z,'figures/'+p.name,p.read_bytes())
        write_bytes(z,'data/submission-input-map.json',json.dumps(input_map,indent=2).encode())
        for name,path in shared.items():
            z.write(path,f'{ROLLS}/{name}');entries[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        inventory=dict(schema='phase3-upload-v1',authors=ROLLS,files=entries,cpu_runs=valid['count'],
            original_gpu_runs=696,final_test_features_included=False,prepared_data_deduplicated=True)
        z.writestr(f'{ROLLS}/UPLOAD_INVENTORY.json',json.dumps(inventory,indent=2))
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        for name,expected in entries.items():assert hashlib.sha256(z.read(f'{ROLLS}/{name}')).hexdigest()==expected
    print('UPLOAD ZIP VERIFIED',output,round(output.stat().st_size/1e6,2),'MB;',len(entries),'files;',len(shared),'unique prepared arrays')


if __name__=='__main__':main()
