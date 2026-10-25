"""Revalidate preserved v1 evidence without changing any historical artifact."""
import subprocess
import sys

from src.phase3.common import ROOT, digest, identity, read_json, write_json


def main():
    output = ROOT / 'results/phase3-cpu-v2/integrity'
    output.mkdir(parents=True, exist_ok=False)
    checks = []

    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise RuntimeError(name)

    evidence = ROOT / 'docs/phase3-reference/evidence'
    source = read_json(evidence / 'source-code-manifest.json')
    for name, expected in source['files'].items():
        check('v1 source: ' + name, digest(ROOT / name) == expected)
    current = {p.name: digest(p) for p in sorted((ROOT / 'src/phase3').glob('*.py'))}
    check('v1 directory identity', identity(current) == source['code_identity'])
    for name, expected in read_json(evidence / 'artifact-index.json')['files'].items():
        check('review evidence: ' + name, digest(evidence / name) == expected)
    adoption = read_json(ROOT / 'docs/phase3-reference/adoption.json')
    check('protocol', digest(ROOT / adoption['protocol']) == adoption['protocol_sha256'])
    check('taxonomy', digest(ROOT / 'configs/phase3/taxonomy-v1.json') == adoption['taxonomy_sha256'])
    prepared = ROOT / 'data/processed/phase3-reference74-v1'
    rebuilt = ROOT / 'data/processed/phase3-reference74-v1-rebuild'
    for name, expected in read_json(evidence / 'preparation-rebuild.json')['files'].items():
        check('26-file preparation identity: ' + name,
              digest(prepared / name) == digest(rebuilt / name) == expected)
    for name, expected in adoption['data_preparation']['source_assets'].items():
        check('audited source asset: ' + name, digest(ROOT / name) == expected)
    protocol = read_json(ROOT / adoption['protocol'])
    check('source archive', digest(ROOT / 'data/raw/phase3-feasibility-corrected/CICIDS2017_improved.zip')
          == protocol['data']['archive_sha256'])
    for name, expected in protocol['data_evidence'].items():
        check('data contract: ' + name, digest(ROOT / name) == expected)
    for folder, copy in [('reference', 'reference-run.json'), ('recovered', 'recovered-run.json')]:
        run_dir = ROOT / 'results/phase3-reference74-v1' / folder
        check('run manifest: ' + folder, digest(run_dir / 'run.json') == digest(evidence / copy))
        for row in read_json(run_dir / 'run.json')['checkpoints']:
            check('checkpoint: ' + folder + '/' + row['file'], digest(run_dir / row['file']) == row['file_sha256'])
    command = [sys.executable, '-m', 'src.phase3.accept_reference', '--run',
               'results/phase3-reference74-v1/reference', '--recovered',
               'results/phase3-reference74-v1/recovered', '--output', str(output / 'acceptance-v1.json')]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    check('174 bounded checks re-executed', result.returncode == 0 and
          len(read_json(output / 'acceptance-v1.json')['checks']) == 174)
    # Snapshot original project inputs, including untracked scientific material.
    folders = ['src/phase3', 'docs/phase3-reference', 'docs/phase3-plan', 'configs/phase3']
    original = {p.relative_to(ROOT).as_posix(): digest(p) for folder in folders
                for p in (ROOT / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    for p in (ROOT / 'submissions').glob('*.tex'):
        original[p.relative_to(ROOT).as_posix()] = digest(p)
    write_json(output / 'original-inputs.json', original)
    write_json(output / 'audit.json', {'status': 'passed', 'checks': checks,
               'v1_code_identity': source['code_identity'], 'reconstruction': 'audited-cache reuse, not fresh CSV reconstruction',
               'working_tree': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
               'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'final_test_predictions_accessed': False})
    print(f'{len(checks)} integrity checks and 174 reference checks passed')


if __name__ == '__main__':
    main()
