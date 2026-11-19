"""Replay verified archived trajectories without changing any scientific source.

One process, CPU only, new output directory, exclusive lock, six-hour hard limit.
Timing and trace wrappers observe existing calls without changing their values.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import time
import threading

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'scripts'))
from audit_phase3_reliability import digest,read,write_json


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=True)
    lock=output/'execution.lock'
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    # This audit command never has a reason to run beyond the agreed limit.
    timer=threading.Timer(6*3600,lambda:os._exit(124));timer.daemon=True;timer.start()
    started=time.perf_counter();outcomes=[]
    try:
        frozen=read(ROOT/'results/phase3-overnight/identity.json')
        source=ROOT/'results/phase3-rigorous-audit-v1/executed-source/scripts/run_phase3_overnight.py'
        for name,expected in frozen['source'].items():
            path=source if name=='scripts/run_phase3_overnight.py' else ROOT/name
            if digest(path)!=expected:raise ValueError('Unverified executed source: '+name)
        for name,expected in frozen['inputs'].items():
            if digest(ROOT/name)!=expected:raise ValueError('Unverified input: '+name)
        spec=importlib.util.spec_from_file_location('phase3_audit_frozen_runner',source)
        study=importlib.util.module_from_spec(spec);sys.modules[spec.name]=study;spec.loader.exec_module(study)
        study.setup();study.ROOT=ROOT;study.BASE=ROOT/'data/processed/phase3-reference74-v1';study.OUT=output
        for name in ('identity.json','ownership-source.npz'):
            target=output/name
            source_path=ROOT/'results/phase3-overnight'/name
            if target.exists() and digest(target)!=digest(source_path):raise ValueError('Output identity changed')
            if not target.exists():shutil.copy2(source_path,target)
        timings={};trace=[]
        def observe(target,name,label):
            original=getattr(target,name)
            def measured(*a,**kw):
                tick=time.perf_counter()
                try:return original(*a,**kw)
                finally:timings[label]=timings.get(label,0.)+time.perf_counter()-tick
            setattr(target,name,measured)
        for name,label in [('admit','admission_seconds'),('train_client','training_seconds'),('commit_importance','importance_seconds')]:
            observe(study.L,name,label)
        observe(study,'evaluate','evaluation_seconds')
        original_train=study.L.train_client
        def trace_train(broadcast,template,client,data,slots,settings,round_id,client_id):
            result=original_train(broadcast,template,client,data,slots,settings,round_id,client_id)
            if client_id==3 and round_id in (1,settings.rounds) and settings.learner=='DR':
                m=client.replay
                selected=[int(v) for v in data.ids[client.accepted][:1]]
                trace.append(dict(stage=data.stage,round=round_id,client=client_id,
                                  admitted_example_ids=selected,buffer_ids=[str(int(v)) for v in m['ids'][:m['size']]],
                                  buffer_labels=m['y'][:m['size']].tolist(),reservoir_seen=m['seen']))
            return result
        study.L.train_client=trace_train
        for learner,admission in [('FT','NONE'),('EI','NONE'),('DR','DC')]:
            timings.clear();s=study.Settings(learner=learner,admission=admission,seed=1,dose=(1,2))
            archived=ROOT/'results/phase3-overnight/runs'/study.name(s)/'result.json';expected=read(archived)
            actual=study.worker(study.asdict(s))
            ok=actual['stages']==expected['stages'] and actual['memory']==expected['memory'] and actual['ledger']==expected['ledger'] and actual['oracle_label_repair']==expected['oracle_label_repair']
            outcomes.append(dict(learner=learner,admission=admission,archive=archived.relative_to(ROOT).as_posix(),
                                 exact_stage_memory_ledger_oracle_match=ok,observed_timing=dict(timings),
                                 elapsed_seconds=actual['elapsed_seconds'],timing_scope='whole trajectory, including oracle suffix if present'))
            write_json(output/'verification.json',dict(outcomes=outcomes,elapsed_seconds=time.perf_counter()-started,final_test_accessed=False))
            if not ok:raise ValueError('Archived trajectory did not reproduce exactly')
        write_json(output/'replay-trace.json',trace)
    except Exception as exc:
        write_json(output/'failure.json',dict(error=repr(exc),elapsed_seconds=time.perf_counter()-started))
        raise
    finally:
        timer.cancel();lock.unlink(missing_ok=True)


if __name__=='__main__':main()
