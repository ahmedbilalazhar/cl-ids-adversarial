"""Independent, development-only Phase 3 evidence audit. Never imports a runner.

Historical inputs are read-only. Outputs are versioned and atomically installed.
Run with Python + NumPy; optional checkpoint verification uses the pinned torch.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import sys
import tempfile
from collections import Counter, defaultdict

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "results/phase3-rigorous-audit-v1"
SEEDS = list(range(1, 12)) + [42]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def score(matrix, eligible):
    """Restrict true rows, never predicted columns; retain unsupported errors."""
    raw = np.asarray(matrix)
    if raw.shape != (16, 16) or not np.issubdtype(raw.dtype, np.integer) or np.any(raw < 0):
        raise ValueError("Expected a nonnegative 16x16 integer confusion matrix")
    eligible = list(eligible)
    cm = raw.copy()
    cm[[c for c in range(16) if c not in eligible], :] = 0
    support, predictions = cm.sum(1), cm.sum(0)
    if not cm.sum() or any(support[c] == 0 for c in eligible):
        raise ValueError("Missing fixed eligible class support")
    classes = {}
    for c in eligible:
        tp = int(cm[c, c]); n = int(support[c]); predicted = int(predictions[c])
        classes[c] = dict(support=n, precision=None if not predicted else tp / predicted,
                          recall=Fraction(tp, n), f1=Fraction(2 * tp, n + predicted))
    tn, fp, fn, tp = map(int, (cm[0, 0], cm[0, 1:].sum(), cm[1:, 0].sum(), cm[1:, 1:].sum()))
    return dict(classes=classes, macro_f1=sum(v["f1"] for v in classes.values()) / len(classes),
                accuracy=Fraction(int(np.trace(cm)), int(cm.sum())), benign_far=Fraction(fp, tn + fp),
                binary_precision=Fraction(tp, tp + fp) if tp + fp else None,
                binary_recall=Fraction(tp, tp + fn) if tp + fn else None,
                binary_f1=Fraction(2 * tp, 2 * tp + fp + fn) if 2 * tp + fp + fn else None,
                hulk_recall=Fraction(int(cm[4, 4]), int(support[4])) if support[4] else None,
                hulk_asr=Fraction(int(cm[4, 0]), int(support[4])) if support[4] else None)


def signed_rank(values):
    """Exact rational ties and zeros, with conditional sign enumeration."""
    values = [Fraction(v) for v in values]
    active = [v for v in values if v]
    ordered = sorted(abs(v) for v in active)
    ranks = {v: Fraction(sum(i + 1 for i, x in enumerate(ordered) if x == v), ordered.count(v))
             for v in set(ordered)}
    weights = [ranks[abs(v)] for v in active]
    observed = abs(sum(w if v > 0 else -w for v, w in zip(active, weights)))
    extreme = sum(abs(sum(sign * rank for sign, rank in zip(signs, weights))) >= observed
                  for signs in itertools.product((-1, 1), repeat=len(active)))
    total = sum(weights)
    signed = sum(w if v > 0 else -w for v, w in zip(active, weights))
    positive = sum(v > 0 for v in active); m = len(active)
    sign_p = sum(math.comb(m, k) for k in range(m + 1) if abs(2 * k - m) >= abs(2 * positive - m)) / 2**m
    return dict(p=extreme / 2**m, rank_biserial=float(signed / total) if total else 0.,
                nonzero=m, zeros=len(values)-m, tied_groups=sum(ordered.count(v)>1 for v in ranks),
                sign_test_p=sign_p)


def holm(values):
    order = sorted(range(len(values)), key=lambda i: (values[i], i))
    out = [0.] * len(values); maximum = 0.
    for rank, i in enumerate(order):
        maximum = max(maximum, min(1., values[i] * (len(values)-rank)))
        out[i] = maximum
    return out


def record_key(result):
    return result["study_identity"], canonical(result["settings"])


def catalog(roots):
    records = {}; entries = []; conflicts = []
    for base in roots:
        for path in sorted(base.rglob("result.json")):
            result = read(path)
            if "study_identity" not in result or "settings" not in result:
                continue
            key = record_key(result); sha = digest(path)
            entries.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha,
                                experiment_key=hashlib.sha256(canonical(key).encode()).hexdigest(),
                                settings=result["settings"]))
            if key in records:
                if records[key][2] != sha:
                    conflicts.append([str(records[key][0]), str(path)])
            else:
                records[key] = path, result, sha
    return list(records.values()), entries, conflicts


def audit_data():
    base = ROOT / "data/processed/phase3-reference74-v1"
    rawbase = ROOT / "data/raw/phase3-feasibility-corrected/no-headers-74"
    result = {}
    with np.load(rawbase / "conditional-components-120.npz", allow_pickle=False) as f:
        state = {k: f[k] for k in f.files}
    with np.load(rawbase / "conditional-candidate-split.npz", allow_pickle=False) as f:
        positions, roles = f["source_positions"], f["roles"]
    groups = state["roots"]
    result["component_overlap"] = {f"{a}-{b}": int(np.intersect1d(groups[positions[roles==a]], groups[positions[roles==b]]).size)
                                   for a, b in ((0, 1), (0, 2), (1, 2))}
    result["t0_closure_in_split"] = int(state["t0_closure"][positions].sum())
    result["excluded_in_split"] = int((~state["kept"][positions]).sum())
    result["t0_rows"] = int(state["t0_fit"].sum())
    result["t0_benign_only"] = bool(np.all(state["labels"][state["t0_fit"]] == 0))
    result["t0_monday_only"] = bool(np.all(state["file_index"][state["t0_fit"]] == 1))
    # No test feature/label payload is loaded; only upstream split metadata above.
    train_ids = []; train_x = []; stage_counts = {}; stages = {}
    for stage in range(1, 5):
        folder = base / f"train/E{stage}"
        ids, x, y = [np.load(folder / f"{k}.npy", allow_pickle=False) for k in ("ids", "x", "y")]
        stages[stage] = ids, x, y
        train_ids.append(ids); train_x.append(x)
        stage_counts[stage] = np.bincount(y, minlength=16).tolist()
    ids = np.concatenate(train_ids); features = np.concatenate(train_x)
    dev_ids = np.load(base / "development/ids.npy", allow_pickle=False)
    dev_x = np.load(base / "development/x.npy", allow_pickle=False)
    dev_y = np.load(base / "development/y.npy", allow_pickle=False)
    result["train_rows"] = len(ids); result["development_rows"] = len(dev_ids)
    result["fresh_stage_duplicate_ids"] = len(ids) - len(np.unique(ids))
    result["train_development_id_overlap"] = len(np.intersect1d(ids, dev_ids))
    result["stage_counts"] = stage_counts
    result["finite_fp32"] = bool(features.dtype==np.float32 and dev_x.dtype==np.float32 and np.isfinite(features).all() and np.isfinite(dev_x).all())
    def row_hashes(array):
        return np.asarray([hashlib.sha256(row.tobytes()).digest() for row in array], dtype="V32")
    result["train_development_transformed_content_overlap"] = len(np.intersect1d(row_hashes(features), row_hashes(dev_x)))
    result["development_support"] = np.bincount(dev_y, minlength=16).tolist()
    result["final_test_rows_exported"] = read(base / "development/manifest.json")["final_test_rows_exported"]
    # Refit solely on T0 and independently reconstruct all exported arrays.
    n = len(groups)
    raw = np.memmap(rawbase / "candidate-features-fp64.raw", dtype="<f8", mode="r", shape=(n,74))
    t0 = np.flatnonzero(state["t0_fit"])
    minimum = np.full(74, np.inf); maximum = np.full(74, -np.inf)
    for start in range(0, len(t0), 16384):
        chunk = raw[t0[start:start+16384]]
        minimum = np.minimum(minimum, chunk.min(0)); maximum = np.maximum(maximum, chunk.max(0))
    denominator = maximum-minimum; denominator[denominator==0] = 1
    scaler = read(base / "builder/scaler.json")
    result["scaler_denominator_matches_T0"] = bool(np.array_equal(denominator, scaler["denominator"]))
    order = np.argsort(state["row_ids"]); source_ids = state["row_ids"][order]
    transform_errors = 0; role_errors = 0
    role_lookup = np.full(n, -1, dtype=np.int8); role_lookup[positions] = roles
    for pool_ids, pool_x, role in [(ids, features, 0), (dev_ids,dev_x,1)]:
        ix = order[np.searchsorted(source_ids,pool_ids)]
        if not np.array_equal(state["row_ids"][ix],pool_ids):raise ValueError("Record mapping failed")
        role_errors += int((role_lookup[ix]!=role).sum())
        for start in range(0,len(ix),16384):
            transformed = ((raw[ix[start:start+16384]]-minimum)/denominator).astype("<f4")
            transform_errors += int(np.count_nonzero(transformed != pool_x[start:start+16384]))
    result["exported_role_errors"] = role_errors; result["transformation_cell_mismatches"] = transform_errors
    result["audit_boundary"] = "Upstream graph/split checked, not independently rebuilt from CSV sessions. No test payload read."
    return result


def audit(output):
    output.mkdir(parents=True,exist_ok=True)
    records, entries, conflicts = catalog([ROOT/"results/phase3-overnight",ROOT/"results/phase3-followup-ablation"])
    write_json(output/"result-catalog.json", dict(files=entries,unique=len(records),copies=len(entries)-len(records),conflicts=conflicts))
    if conflicts:raise ValueError("Conflicting immutable experiment payloads; see catalog")
    frozen = read(ROOT/"results/phase3-overnight/identity.json")
    recovered = output/"executed-source/scripts/run_phase3_overnight.py"
    if not recovered.exists():
        recovered = ROOT/"tmp/phase3-portable-check/23I-2568_23I-2581/scripts/run_phase3_overnight.py"
    source = []
    for name,expected in frozen["source"].items():
        p=ROOT/name; actual=digest(p) if p.exists() else None
        row=dict(path=name,expected=expected,current=actual,match=actual==expected)
        if name=="scripts/run_phase3_overnight.py" and digest(recovered)==expected:
            target=output/"executed-source/scripts/run_phase3_overnight.py";target.parent.mkdir(parents=True,exist_ok=True)
            if target.resolve()!=recovered.resolve():target.write_bytes(recovered.read_bytes())
            row["recovered"]=str(target.relative_to(ROOT))
        source.append(row)
    write_json(output/"source-verification.json",source)
    inputs=[]
    for name,expected in frozen["inputs"].items():
        p=ROOT/name;actual=digest(p) if p.exists() else None
        inputs.append(dict(path=name,expected=expected,actual=actual,match=actual==expected))
    write_json(output/"input-verification.json",inputs)
    taxonomy=read(ROOT/"configs/phase3/taxonomy-v1.json")["classes"]
    eligible=[c["source_code"] for c in taxonomy if c["scoring_eligible"]]
    arrival={c["source_code"]:c["arrival_stage"] for c in taxonomy}
    rows=[]; endpoints={}; raw={}; errors=[]; repairs=[];families=[];populations=[]
    expected_support={}; e1=defaultdict(set); poison=defaultdict(set); quota=defaultdict(dict)
    for path,r,sha in records:
        s=r["settings"]
        if s["block"]=="smoke":continue
        method=s["learner"] if s["admission"]=="NONE" else s["admission"]
        key=(s["block"],method,s["seed"],tuple(s["dose"]),s["q"],s["lambda_y"],s["lambda_z"])
        if r["status"]!="complete" or r["final_test_accessed"] or r["study_identity"]!=frozen["sha256"]:errors.append([str(path),"status/identity mismatch"])
        metrics=[]
        for stage in r["stages"]:
            t=stage["stage"];cm=np.asarray(stage["confusion"])
            if stage["bank"]!="development":errors.append([str(path),"wrong bank"])
            support=cm.sum(1).tolist()
            if t in expected_support and support!=expected_support[t]:errors.append([str(path),"bank support mismatch"])
            expected_support[t]=support
            metrics.append(score(cm,[c for c in eligible if arrival[c]<=t]))
            for population,codes in [('eligible',[c for c in eligible if arrival[c]<=t]),('full-supported',np.flatnonzero(cm.sum(1)).tolist())]:
                m=score(cm,codes)
                for code,values in m['classes'].items():
                    families.append(dict(path=path.relative_to(ROOT).as_posix(),stage=t,population=population,code=code,
                                         precision=values['precision'],precision_defined=values['precision'] is not None,
                                         recall=float(values['recall']),f1=float(values['f1']),support=values['support']))
                populations.append(dict(path=path.relative_to(ROOT).as_posix(),stage=t,population=population,
                                        rows=int(cm[codes].sum()),**{k:float(m[k]) if m[k] is not None else None for k in ('accuracy','macro_f1','benign_far','binary_precision','binary_recall','binary_f1')}))
        a=sum(sum(metrics[t-1]["classes"][c]["f1"] for c in eligible if arrival[c]==t and c!=4)/sum(arrival[c]==t and c!=4 for c in eligible) for t in (2,3,4))/3
        end=dict(A=a,e2_recall=metrics[1]["hulk_recall"],e3_asr=metrics[2]["hulk_asr"],e4_asr=metrics[3]["hulk_asr"],
                 **{k:v for k,v in metrics[3].items() if k!="classes"})
        endpoints[key]=end;raw[key]=(path,r)
        row=dict(block=s["block"],method=method,seed=s["seed"],dose=s["dose"][0]/s["dose"][1],q=s["q"],lambda_y=s["lambda_y"],lambda_z=s["lambda_z"],path=path.relative_to(ROOT).as_posix(),sha256=sha,elapsed_seconds=r["elapsed_seconds"])
        row.update({k:float(v) if v is not None else None for k,v in end.items()});rows.append((key,row))
        if s["block"]=="core":
            e1[(s["seed"],s["learner"])].add(r["stages"][0]["model_sha256"])
            poison[(s["seed"],tuple(s["dose"]))].add(tuple(r["attack"]["poison_ids"]))
            if method in ("DM","DC"):
                quota[(s["seed"],tuple(s["dose"]))][method]=[[c["admitted"] for c in ledger["clients"]] for ledger in r["ledger"] if ledger["kind"]=="admission"]
        oracle=r.get("oracle_label_repair")
        if oracle:
            repaired=[score(st["confusion"],[c for c in eligible if arrival[c]<=st["stage"]]) for st in oracle["stages"]]
            repairs.append(dict(method=method,seed=s["seed"],changed_labels=oracle["changed_labels"],nonlabel_state_unchanged=oracle["nonlabel_state_unchanged"],
                                asr_effect=float(sum(repaired[i]["hulk_asr"]-metrics[i+2]["hulk_asr"] for i in range(2))/2)))
    for key,row in rows:
        clean=key[:3]+((0,1),)+key[4:]
        if clean not in endpoints:errors.append([row["path"],"missing clean twin"]);continue
        e=endpoints[key];c=endpoints[clean]
        e["H"]=(e["e3_asr"]-c["e3_asr"]+e["e4_asr"]-c["e4_asr"])/2
        e["delta_recall"]=e["e2_recall"]-c["e2_recall"]
        row.update(H=float(e["H"]),delta_recall=float(e["delta_recall"]))
    def core(method,seed,dose):return endpoints[("core",method,seed,tuple(dose),.75,1.,.1)]
    tests=[];spec=read(ROOT/"configs/phase3/overnight-analysis.json")
    for group in spec["family"]:
        for endpoint in group["endpoints"]:
            for left,right in group["pairs"]:
                for dose in group["doses"]:
                    rational=Fraction(str(dose));d=(rational.numerator,rational.denominator)
                    values=[core(left,s,d)[endpoint]-core(right,s,d)[endpoint] for s in SEEDS]
                    inference=signed_rank(values);v=np.array(list(map(float,values)))
                    generator=np.random.default_rng(20261116+len(tests))
                    boot=v[generator.integers(0,len(v),size=(10000,len(v)))].mean(1)
                    tests.append(dict(left=left,right=right,endpoint=endpoint,dose=dose,seeds=SEEDS,differences=[str(x) for x in values],
                                      mean=float(v.mean()),median=float(np.median(v)),ci95=np.quantile(boot,[.025,.975]).tolist(),**inference))
    if len(tests)!=29:raise ValueError("Wrong inference family")
    for row,p,signp in zip(tests,holm([r["p"] for r in tests]),holm([r["sign_test_p"] for r in tests])):
        row["holm_p"]=p;row["sign_test_holm_p"]=signp
    paired_checks=dict(E1_model_prefixes=all(len(v)==1 for v in e1.values()),same_attack_IDs=all(len(v)==1 for v in poison.values()),
                       equal_DM_DC_admitted_counts=all(v.get("DM")==v.get("DC") for v in quota.values()))
    blocks=Counter(r[1]["settings"]["block"] for r in records)
    summary=[]
    for method in ("FT","EI","DR","DM","DC"):
        for dose in (0.,.1,.3,.5):
            selected=[r for _,r in rows if r["block"]=="core" and r["method"]==method and r["dose"]==dose]
            summary.append(dict(method=method,dose=dose,n=len(selected),**{k:float(np.mean([r[k] for r in selected])) for k in ("macro_f1","A","H","delta_recall","benign_far")}))
    for name,data in [("trajectory-metrics",[r for _,r in rows]),("comparisons-29",tests),("core-summary",summary),("oracle-repair",repairs)]:
        write_json(output/(name+".json"),data)
        if data:
            with (output/(name+".csv")).open("w",newline="",encoding="utf-8") as f:
                writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    completion_checks=[]
    for folder,name in [("phase3-overnight","completion.json"),("phase3-followup-ablation","completion-followup.json")]:
        base=ROOT/"results"/folder;manifest=read(base/name)
        for rel,expected in manifest["files"].items():
            p=base/rel
            if not p.exists() or digest(p)!=expected:completion_checks.append(str(p.relative_to(ROOT)))
    write_json(output/"data-audit.json",audit_data())
    for name,values in [('family-metrics',families),('population-metrics',populations)]:
        with (output/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(values[0]));writer.writeheader();writer.writerows(values)
    validation=dict(unique_trajectories=len(rows),physical_result_files=len(entries),duplicate_copies=len(entries)-len(records),unique_blocks=dict(blocks),
                    unique_oracle_continuations=len(repairs),zero_survivor_repairs=sum(r["changed_labels"]==0 for r in repairs),
                    errors=errors,paired_checks=paired_checks,completion_hash_failures=completion_checks,source_drift=[r["path"] for r in source if not r["match"]],
                    input_hash_failures=[r["path"] for r in inputs if not r["match"]],bank_support=expected_support,
                    inference_status="exploratory: reused development bank",significant_holm=sum(t["holm_p"]<.05 for t in tests),
                    final_test_accessed=False,runtime=dict(python=platform.python_version(),numpy=np.__version__))
    write_json(output/"validation.json",validation)
    print(json.dumps(validation,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,default=DEFAULT)
    audit(parser.parse_args().output)
