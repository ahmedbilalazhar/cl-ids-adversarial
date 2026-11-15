"""One-command analysis/report reproduction; training is explicit."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--train',action='store_true')
args=p.parse_args()
steps=[]
if (ROOT/'data/submission-input-map.json').exists():steps.append('materialize_submission_data.py')
if args.train:steps.append('run_phase3_cpu_study.py')
steps+=['rebuild_submission_analysis.py','analyse_phase3_cpu.py','build_phase3_figures.py',
       'write_phase3_report.py','export_phase3_tex.py','package_phase3_submission.py','build_phase3_upload.py']
for name in steps:
    subprocess.run([sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT,check=True)
