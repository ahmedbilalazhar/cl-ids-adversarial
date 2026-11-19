"""Summarize cost observables from unique archived runs without retraining."""
from __future__ import annotations
import json, statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'results/phase3-rigorous-audit-v1/result-catalog.json'
OUTPUT=ROOT/'results/phase3-rigorous-audit-v1/measured-cost-summary.json'

def quantiles(values):
    ordered=sorted(values)
    return {'n':len(ordered),'min':ordered[0],'median':statistics.median(ordered),
            'p90_nearest_rank':ordered[max(0,(9*len(ordered)+9)//10-1)],'max':ordered[-1]}

def main():
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    unique={}
    for entry in catalog['files']: unique.setdefault(entry['experiment_key'],entry)
    groups={}
    for entry in unique.values():
        run=json.loads((ROOT/entry['path']).read_text(encoding='utf-8'))
        block=run['settings']['block']; row=groups.setdefault(block,{'elapsed_seconds':[],'weight_bytes_per_stage':[],'latency':[]})
        row['elapsed_seconds'].append(float(run['elapsed_seconds']))
        row['weight_bytes_per_stage'].append(sum(run['serialized_stage_weight_bytes'].values()))
        latency=run.get('latency') or {}
        if latency: row['latency'].append(latency)
    summary={}
    for block,row in groups.items():
        summary[block]={'unique_runs':len(row['elapsed_seconds']),
            'elapsed_seconds':quantiles(row['elapsed_seconds']),
            'serialized_four_stage_weight_bytes':quantiles(row['weight_bytes_per_stage']),
            'latency_sample_count':len(row['latency'])}
        if row['latency']:
            summary[block]['offline_latency_ms']={batch:{metric:quantiles([float(x[batch][metric]) for x in row['latency']])
                 for metric in ('median','p95')} for batch in ('1','256')}
    result={'schema':'phase3-measured-cost-summary-v1','unique_result_count':len(unique),'blocks':summary,
      'measured_scope':['runner elapsed_seconds (includes training, evaluation, serialization and any included oracle continuation)','compressed NPZ stage-weight file sizes','per-run inference latency only where latency records exist'],
      'not_measured':['separate training/admission/Fisher/aggregation/evaluation wall times in overnight results','peak RSS or allocated client state','serialized upload/download messages including labels, registry and protocol framing','network delay, edge runtime, energy'],
      'interpretation':'Archived elapsed times are observational and hardware/co-load conditions are not a controlled benchmark. Do not compare as training-only costs. Weight archive size is not communication payload size.'}
    OUTPUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(OUTPUT)
if __name__=='__main__': main()
