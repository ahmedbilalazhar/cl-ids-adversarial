"""Curate, hash, verify and atomically install the audited roll-number archive."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys
import zipfile
import time
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from audit_phase3_reliability import read,write_json,digest,canonical
AUDIT=ROOT/'results/phase3-rigorous-audit-v1'
REPORT=ROOT/'submissions/phase3-audited-report'
ARCHIVE=ROOT/'submissions/23I-2568_23I-2581.zip'


def main():
    validation=read(AUDIT/'validation.json');data=read(AUDIT/'data-audit.json')
    replay=read(AUDIT/'reproduction-attempt2/verification.json')
    if validation['errors'] or validation['completion_hash_failures'] or validation['input_hash_failures']:raise ValueError('Unresolved evidence failures')
    if len(replay['outcomes'])!=3 or not all(r['exact_stage_memory_ledger_oracle_match'] for r in replay['outcomes']):raise ValueError('Replay not qualified')
    if not read(AUDIT/'cohort-metrics.json')['all_completed']:raise ValueError('Incomplete clean checkpoint evaluation')
    pdf=read(REPORT/'pdf-validation.json')
    if pdf['visual_review']!='passed':raise ValueError('Report visual review is incomplete')
    original=ROOT/'submissions/Phase3_Submission_23I-2568_23I-2581.zip'
    if digest(original)!='c219925799b2fe3b1d73e4203e25d1f94987b6c401f0288290f5f0bb67a2311f':raise ValueError('Original submission changed')
    tests=[]
    for name in ('pinned-tests-after-fix.xml','supplemental-tests.xml','runner-fix-tests.xml'):
        tree=ET.parse(AUDIT/name)
        for suite in tree.findall('.//testsuite'):
            row={'file':name,**suite.attrib};tests.append(row)
            if int(row['failures']) or int(row['errors']):raise ValueError('Required test failure')
    # The backup was captured before this audit began. Never replace it on rebuild.
    backup=AUDIT/'pre-audit-23I-2568_23I-2581.zip'
    if not backup.is_file():raise ValueError('Missing pre-audit archive backup')
    claims=[
        ('417 unique newer trajectories, 24 oracle branches', 'result-catalog.json; validation.json','verified development evidence'),
        ('DC lower mean acquisition at every dose; higher clean FAR','core-summary.json; comparisons-29.json','conditional exploratory result'),
        ('Single-attacker replay immediate Hulk recall damage small','core-summary.json: DR dose.5 delta_recall','conditional negative/weak effect'),
        ('One Holm family of29 rational paired contrasts','comparisons-29.json; scripts/audit_phase3_reliability.py','exploratory due development reuse'),
        ('60 clean trajectories re-evaluated; fixed-cohort metrics','cohort-metrics.json','verified development checkpoints'),
        ('All1668 stage weights match recorded model identity','checkpoint-audit.json','artifact identity, not proof of every original execution'),
        ('T0 and exported isolation checks pass','data-audit.json','saved graph and exported arrays; raw CSV parser remains upstream'),
        ('Representative FT/EI/DC exact stage/memory/ledger/oracle replay','reproduction-attempt2/verification.json','three execution checks, not additional independent seeds'),
        ('Historical EI/head initialization differ from Phase2','gap-register.json:R02/R03; original engine source','confirmed historical implementation departures'),
        ('Original significance/fallback claims withdrawn','gap-register.json:R01/R04','corrected report claims'),
        ('Latest eviction mechanism not established','gap-register.json:R13; remediation-plan.md:E2','unexecuted; attribution removed'),
        ('No external full-method efficacy or independent final test','gap-register.json:R09/R17','not established; outcomes remain sealed')]
    write_json(AUDIT/'claim-evidence-ledger.json',[dict(claim=c,evidence=e,status=s) for c,e,s in claims])
    literature=[dict(key='lavaur',primary='https://github.com/leolavaur/cose_2025',verified='Author record and study-dependent effects; retained paper5 p23 supports single-attacker RASR<.1 but the audited report avoids incompatible numerical ranking.'),
                dict(key='der',primary='https://arxiv.org/abs/2004.07211',verified='Primary authors/title/NeurIPS2020 and logit-rehearsal method; expanding-width adaptations are ours.'),
                dict(key='liu',primary='https://intrusion-detection.distrinet-research.be/CNS2022/index.html',verified='Primary source corrected extraction/annotation and dataset-error context; no claim all remaining errors fixed.')]
    write_json(AUDIT/'primary-source-ledger.json',literature)
    write_json(AUDIT/'execution-summary.json',dict(tests=tests,replayed_trajectories=3,new_independent_research_trajectories=0,
                   replay_total_elapsed_seconds=replay['elapsed_seconds'],training_limit_seconds=21600,
                   remaining=['independent source-CSV parser reconstruction','qualified sealed evaluator and independent outcomes','external full-method validation','eviction controls if attribution restored','full serialized communication/state cost'],
                   failure_records=['initial wrong scientific runtime invocation','pinned-tests.log: import contamination before fix','reproduction/failure.json: relocated data root before training'],
                   historical_artifacts_preserved=True,final_test_accessed=False))
    files={}
    def add(path,name=None):
        if path.is_file():
            key=name or path.relative_to(ROOT).as_posix()
            if key in files and files[key]!=path:raise ValueError('Duplicate package member '+key)
            files[key]=path
    for folder in ['src','scripts','configs','tests','phase3_delivery','kaggle_worker']:
        for path in (ROOT/folder).rglob('*'):
            if path.suffix in ('.py','.json','.md','.txt','.lock','.ps1','.yaml','.yml') and '__pycache__' not in path.parts:add(path)
    for path in (ROOT/'docs/phase3-rigorous-audit-v1').rglob('*'):add(path)
    for folder in ['docs/phase3-reference','docs/phase3-plan']:
        for path in (ROOT/folder).rglob('*'):
            if path.suffix in ('.py','.json','.md','.csv'):add(path)
    for path in REPORT.rglob('*'):
        if path.suffix in ('.tex','.pdf','.json'):add(path)
    add(REPORT/'phase3-report.pdf','01_FINAL_REPORT/phase3-report.pdf')
    for path in AUDIT.rglob('*'):
        if path.is_file() and path.suffix in ('.json','.csv','.log','.xml','.md','.txt','.py','.tex','.patch') and 'reproduction-attempt2/runs' not in path.as_posix() and path.name not in ('package-inventory.json','package-validation.json','START_HERE.md'):add(path)
    add(original,'02_HISTORICAL/Phase3_Submission_23I-2568_23I-2581.zip')
    for folder in ['phase3-implementation/src','phase3-implementation/notebooks','phase3-implementation/results/final-run']:
        for path in (ROOT/folder).rglob('*'):
            if path.suffix in ('.py','.ipynb','.json','.zip','.md','.csv'):add(path)
    # Include each unique newer trajectory exactly once, with its associated weights.
    seen=set()
    for entry in read(AUDIT/'result-catalog.json')['files']:
        key=entry['experiment_key']
        if key in seen:continue
        seen.add(key);path=ROOT/entry['path']
        for source in path.parent.rglob('*'):
            if source.suffix in ('.json','.npz'):add(source,'evidence/unique-runs/'+key+'/'+source.relative_to(path.parent).as_posix())
    for folder in ['data/processed/phase3-reference74-v1/train','data/processed/phase3-reference74-v1/development','data/processed/phase3-reference74-v1/builder']:
        for path in (ROOT/folder).rglob('*'):
            if path.suffix in ('.json','.npy','.npz'):add(path)
    for name in ['README.md','requirements.txt','pyproject.toml','submissions/phase2-with-claude.tex','submissions/phase3-methodology-amendment.md','submissions/phase3-report/README.md',
                 'results/phase3-overnight/identity.json','results/phase3-overnight/completion.json','results/phase3-overnight/clean-gates.json','results/phase3-overnight/ownership-source.npz',
                 'results/phase3-followup-ablation/identity.json','results/phase3-followup-ablation/completion-followup.json',
                 'results/phase3-cpu-v3/development/tuning-selection.json',
                 'results/phase3-followup/external-method-training-pilot-summary-v1.json']:
        add(ROOT/name)
    start=AUDIT/'START_HERE.md'
    start.write_text('''# Audited Phase 3 submission\n\nOpen **01_FINAL_REPORT/phase3-report.pdf**. Editable source and vector figures are in submissions/phase3-audited-report/.\n\nRead docs/phase3-rigorous-audit-v1/README.md, gap-register.md, must-fix.md and reproduction.md for reliability, patches, executed evidence and remaining limits.\n\nThe untouched pre-deadline ZIP is in02_HISTORICAL/. It is evidence of what was submitted, not the corrected report. All current outcomes are development-only. Independent final-test and external full-method efficacy remain unestablished.\n\nThere are417 unique newer trajectories and24 oracle branches, not963 independent runs. Unique evidence files appear once under evidence/unique-runs/<experiment-key>/. Their original paths/settings/hashes remain in result-catalog.json; restore original paths from that mapping before running catalog-dependent commands. Prepared train/development arrays are supplied once; raw multi-gigabyte reconstruction caches and sealed test payloads are excluded.\n\nPACKAGE_INVENTORY.json hashes every other member. Packaging does not change the original report archive or upload any files.\n''',encoding='utf-8')
    add(start,'START_HERE.md')
    inventory={name:dict(sha256=digest(path),bytes=path.stat().st_size) for name,path in sorted(files.items())}
    manifest=AUDIT/'package-inventory.json';write_json(manifest,dict(schema='phase3-rigorous-audit-package-v1',files=inventory,unique_trajectory_count=417,oracle_continuations=24,original_submission_sha256=digest(original),final_test_payload_included=False))
    temporary=ARCHIVE.with_suffix('.audit.tmp.zip')
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,path in sorted(files.items()):z.write(path,name)
        z.write(manifest,'PACKAGE_INVENTORY.json')
    with zipfile.ZipFile(temporary) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failure')
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Duplicate ZIP names')
        for name,entry in inventory.items():
            if hashlib.sha256(z.read(name)).hexdigest()!=entry['sha256']:raise ValueError('ZIP hash failure '+name)
    # Windows indexers/scanners can briefly hold an otherwise writable target.
    # Keep the existing validated archive until an atomic replacement succeeds.
    for attempt in range(20):
        try:
            os.replace(temporary,ARCHIVE)
            break
        except PermissionError:
            if attempt==19:raise
            time.sleep(.5)
    write_json(AUDIT/'package-validation.json',dict(archive=str(ARCHIVE.relative_to(ROOT)),sha256=digest(ARCHIVE),members=len(files)+1,
               all_payload_hashes_checked=True,crc_checked=True,original_preserved=True,
               pre_audit_archive_sha256=digest(backup),bytes=ARCHIVE.stat().st_size,final_test_payload_included=False))
    print('Verified archive',ARCHIVE,'members',len(files)+1,'bytes',ARCHIVE.stat().st_size)


if __name__=='__main__':main()
