"""Conditional full-input/component feasibility audit of the original mirror.

This is a data audit, not the adopted canonical builder or a model test. It uses
an explicit proposed capture-clock interpretation for minute-only strings and
retains quarantine/provenance bridges conservatively. No experiment split is
selected. All numeric features/metadata originate in the same source row.
"""
from __future__ import annotations
import hashlib
import ipaddress
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs/phase3-plan"
WORK = ROOT / "data/raw/phase3-feasibility-original"


def fingerprint_groups(x, valid, prefix):
    n = len(x)
    hashes = np.zeros(n, dtype="V16")
    indices = np.flatnonzero(valid)
    for start in range(0, len(indices), 100000):
        part = indices[start:start+100000]
        hashes[part] = [hashlib.sha256(x[int(i)]).digest()[:16] for i in part]
    unique, inverse, counts = np.unique(hashes[indices], return_inverse=True, return_counts=True)
    groups = np.full(n, -1, dtype=np.int32)
    groups[indices] = inverse
    order = np.argsort(inverse, kind="stable")
    sorted_indices = indices[order]
    offsets = np.concatenate(([0], np.cumsum(counts)))
    duplicate_groups = np.flatnonzero(counts > 1)
    for group in duplicate_groups:
        ids = sorted_indices[offsets[group]:offsets[group+1]]
        reference = np.asarray(x[int(ids[0])]).view(np.uint8)
        # Confirm canonical bytes, not only the candidate digest.
        for chunk_start in range(0, len(ids), 10000):
            rows = np.asarray(x[ids[chunk_start:chunk_start+10000]])
            if not np.all(rows.view(np.uint8).reshape(len(rows), -1) == reference):
                raise RuntimeError(f"Candidate hash collision in {prefix}; no components promoted")
    print(json.dumps({"step": prefix, "valid": len(indices), "groups": len(unique), "duplicate_groups": len(duplicate_groups)}), flush=True)
    return groups, counts, sorted_indices, offsets


def conflict_mask(groups, labels):
    active = (groups >= 0) & (labels >= 0)
    count = int(groups[active].max())+1
    low = np.full(count, np.iinfo(np.int16).max, dtype=np.int16)
    high = np.full(count, -1, dtype=np.int16)
    np.minimum.at(low, groups[active], labels[active])
    np.maximum.at(high, groups[active], labels[active])
    bad = (high >= 0) & (low != high)
    mask = np.zeros(len(groups), dtype=bool)
    mask[active] = bad[groups[active]]
    return mask, int(bad.sum())


class UnionFind:
    def __init__(self, n):
        self.parent = np.arange(n, dtype=np.int32)
        self.rank = np.zeros(n, dtype=np.uint8)
    def find(self, node):
        node = int(node)
        root = node
        while self.parent[root] != root:
            root = int(self.parent[root])
        while self.parent[node] != node:
            nxt = int(self.parent[node])
            self.parent[node] = root
            node = nxt
        return root
    def union(self, left, right):
        left, right = self.find(left), self.find(right)
        if left == right:
            return
        if self.rank[left] < self.rank[right]:
            left, right = right, left
        self.parent[right] = left
        if self.rank[left] == self.rank[right]:
            self.rank[left] += 1
    def roots(self):
        roots = self.parent.copy()
        while True:
            updated = self.parent[roots]
            if np.array_equal(updated, roots):
                return roots
            roots = updated


def add_content_links(uf, counts, sorted_indices, offsets):
    for group in np.flatnonzero(counts > 1):
        ids = sorted_indices[offsets[group]:offsets[group+1]]
        first = int(ids[0])
        for row in ids[1:]:
            uf.union(first, int(row))


def main(*, work=WORK, census_file="original-full-census.json", metadata_file="feasibility-metadata.csv", output_prefix="original", timestamp_kind="original", domain_policy="as_published", output_work=None):
    started = time.monotonic()
    census = json.loads((DOCS/census_file).read_text(encoding="utf-8"))
    n = census["total_rows"]
    names=census["numeric_feature_order"]
    dimensions=len(names)
    x = np.memmap(work/"candidate-features-fp64.raw", dtype="<f8", mode="r", shape=(n,dimensions))
    finite = np.fromfile(work/"candidate-finite.raw", dtype=np.uint8).astype(bool)
    destination=output_work or work
    destination.mkdir(parents=True,exist_ok=True)
    valid_domain=np.ones(n,dtype=bool)
    if domain_policy=="nonnegative_flow_features_with_window_sentinel_v1":
        names=census["numeric_feature_order"]
        window_columns=[i for i,name in enumerate(names) if name in {"Init_Win_bytes_forward","Init_Win_bytes_backward"}]
        nonnegative_columns=[i for i in range(dimensions) if i not in window_columns]
        for first in range(0,n,50000):
            last=min(n,first+50000)
            part=np.asarray(x[first:last])
            windows=part[:,window_columns]
            valid_domain[first:last]=np.all(part[:,nonnegative_columns]>=0,axis=1)&np.all((windows==-1)|((windows>=0)&(windows<=65535)&(windows==np.trunc(windows))),axis=1)
    elif domain_policy!="as_published":
        raise ValueError("Unknown declared feature-domain policy")
    meta = pd.read_csv(work/metadata_file, dtype={"row_id":"uint64", "file_index":"uint8", "archive_row":"uint32", "src_ip":"string", "dst_ip":"string", "reference_label_raw":"string"}, low_memory=False)
    if len(meta) != n or len(finite) != n:
        raise RuntimeError("Census row alignment mismatch")
    labels_text = meta["reference_label_raw"].astype(str).str.replace("–", "-", regex=False).str.replace("—", "-", regex=False).str.replace(r"\s+", " ", regex=True)
    aliases = {"BENIGN":"Benign", "DoS slowloris":"DoS Slowloris", "DoS slowhttptest":"DoS Slowhttptest",
        "Web Attack - Brute Force":"Web Attack Brute Force", "Web Attack - XSS":"Web Attack XSS",
        "Web Attack - Sql Injection":"Web Attack Sql Injection", "Web Attack - SQL Injection":"Web Attack Sql Injection",
        "Botnet":"Bot", "Portscan":"PortScan"}
    labels_text = labels_text.replace(aliases)
    missing_annotation = meta["reference_label_raw"].isna() | labels_text.eq("nan")
    label_names = sorted(labels_text[~missing_annotation].unique())
    label_map = {name:i for i,name in enumerate(label_names)}
    labels = labels_text.map(label_map).fillna(-1).to_numpy(dtype=np.int16)
    unique_ips = pd.unique(pd.concat([meta["src_ip"].astype(str),meta["dst_ip"].astype(str)],ignore_index=True))
    ip_map, invalid_ip_strings = {}, []
    for value in unique_ips:
        try:
            ip_map[value] = int(ipaddress.IPv4Address(value))
        except ValueError:
            invalid_ip_strings.append(None if pd.isna(value) else str(value))
    src_ip = meta["src_ip"].astype(str).map(ip_map)
    dst_ip = meta["dst_ip"].astype(str).map(ip_map)
    src_port = pd.to_numeric(meta["src_port"],errors="coerce")
    dst_port = pd.to_numeric(meta["dst_port"],errors="coerce")
    protocol = pd.to_numeric(meta["protocol"],errors="coerce")
    duration = pd.to_numeric(meta["duration_us_raw"],errors="coerce")
    raw_times = meta["timestamp_raw"].astype(str)
    if timestamp_kind=="original":
        seconds = raw_times.str.count(":").eq(2)
        starts = pd.Series(pd.NaT,index=meta.index,dtype="datetime64[ns]")
        starts.loc[seconds] = pd.to_datetime(raw_times[seconds],format="%d/%m/%Y %H:%M:%S",errors="coerce")
        starts.loc[~seconds] = pd.to_datetime(raw_times[~seconds],format="%d/%m/%Y %H:%M",errors="coerce")
        pm_interpreted = starts.dt.hour.lt(8)
        starts.loc[pm_interpreted] += pd.Timedelta(hours=12)
        clock_rule="Day-first July capture date; explicit seconds/minute formats; hours below 8 interpreted as afternoon (+12h), including second-resolution Monday. No manufactured seconds or timezone."
    elif timestamp_kind=="corrected":
        starts=pd.to_datetime(raw_times,format="%Y-%m-%d %H:%M:%S.%f",errors="coerce")
        missing=starts.isna()
        starts.loc[missing]=pd.to_datetime(raw_times[missing],format="%Y-%m-%d %H:%M:%S",errors="coerce")
        pm_interpreted=pd.Series(False,index=meta.index)
        clock_rule="Authors' ISO UTC microsecond timestamps as supplied; no local-hour or AM/PM reinterpretation."
    else:
        raise ValueError("Unknown timestamp contract")
    start_us = starts.to_numpy(dtype="datetime64[us]").astype(np.int64)
    safe_duration_limit = np.iinfo(np.int64).max - np.maximum(start_us,0)
    meta_valid = (starts.notna() & src_ip.notna() & dst_ip.notna() & np.isfinite(duration)
        & duration.ge(0) & duration.mod(1).eq(0) & duration.le(safe_duration_limit)
        & src_port.between(0,65535) & src_port.mod(1).eq(0)
        & dst_port.between(0,65535) & dst_port.mod(1).eq(0)
        & protocol.between(0,255) & protocol.mod(1).eq(0) & ~missing_annotation).to_numpy()
    duration_us = duration.where(np.isfinite(duration),0).fillna(0).to_numpy(dtype=np.int64)
    row_ids = meta["row_id"].to_numpy(dtype=np.uint64)
    file_index = meta["file_index"].to_numpy(dtype=np.uint8)
    monday_index = next(f["file_index"] for f in census["files"] if "monday" in f["name"].lower())
    print(json.dumps({"step":"metadata", "rows":n,"invalid_metadata":int((~meta_valid).sum()),"pm_interpreted":int(pm_interpreted.sum()),"elapsed_seconds":round(time.monotonic()-started,2)}),flush=True)

    raw_groups, raw_counts, raw_sorted, raw_offsets = fingerprint_groups(x,finite,"pretransform_fp64_content")
    raw_conflict, raw_conflict_groups = conflict_mask(raw_groups,labels)
    # Fit eligibility uses Monday-only validity/annotation. Cross-day conflict
    # labels never select calibration records or refit the transform.
    fit = (file_index == monday_index) & (labels == label_map["Benign"]) & finite & meta_valid & valid_domain
    if not fit.any():
        raise RuntimeError("No declared valid T0 fitting rows")
    fitting = np.asarray(x[fit])
    minimum, maximum = fitting.min(axis=0), fitting.max(axis=0)
    denominator = maximum-minimum
    zero_range = denominator == 0
    denominator[zero_range] = 1
    del fitting
    transformed_path = destination/"candidate-transformed-fp32.raw"
    transformed = np.memmap(transformed_path,dtype="<f4",mode="w+",shape=(n,dimensions))
    final_finite = np.zeros(n,dtype=bool)
    out_of_range = np.zeros(dimensions,dtype=np.int64)
    final_min = np.full(dimensions,np.inf)
    final_max = np.full(dimensions,-np.inf)
    for first in range(0,n,50000):
        last=min(n,first+50000)
        with np.errstate(over="ignore",invalid="ignore"):
            values=((np.asarray(x[first:last])-minimum)/denominator).astype("<f4")
        values[values == 0] = 0
        transformed[first:last] = values
        okay=np.isfinite(values).all(axis=1) & finite[first:last]
        final_finite[first:last]=okay
        stats_okay=okay if domain_policy=="as_published" else okay&valid_domain[first:last]&meta_valid[first:last]
        if stats_okay.any():
            valid_values=values[stats_okay]
            out_of_range += ((valid_values<0)|(valid_values>1)).sum(axis=0)
            final_min=np.minimum(final_min,valid_values.min(axis=0))
            final_max=np.maximum(final_max,valid_values.max(axis=0))
    transformed.flush()
    groups,counts,sorted_ids,offsets=fingerprint_groups(transformed,final_finite,"frozen_T0_fp32_content")
    final_conflict, final_conflict_groups = conflict_mask(groups,labels)
    quarantine = raw_conflict | final_conflict
    conflicting_fitting = int((fit & final_conflict).sum())
    eligible = finite & final_finite & meta_valid & valid_domain & ~quarantine
    # Earliest parsed start, source-file order, original row; identity is opaque.
    eligible_ids = np.flatnonzero(eligible)
    ordered=eligible_ids[np.lexsort((row_ids[eligible_ids], start_us[eligible_ids]))]
    _,first_positions=np.unique(groups[ordered],return_index=True)
    survivor=np.zeros(n,dtype=bool)
    survivor[ordered[first_positions]]=True

    base=UnionFind(n)
    add_content_links(base,raw_counts,raw_sorted,raw_offsets)
    add_content_links(base,counts,sorted_ids,offsets)
    base_roots=base.roots()
    valid_ids=np.flatnonzero(meta_valid)
    src=((src_ip.fillna(0).to_numpy(dtype=np.uint64)<<np.uint64(16))|src_port.fillna(0).to_numpy(dtype=np.uint64))[valid_ids]
    dst=((dst_ip.fillna(0).to_numpy(dtype=np.uint64)<<np.uint64(16))|dst_port.fillna(0).to_numpy(dtype=np.uint64))[valid_ids]
    low,high=np.minimum(src,dst),np.maximum(src,dst)
    protocols=protocol.fillna(0).to_numpy(dtype=np.int16)[valid_ids]
    order=np.lexsort((row_ids[valid_ids],start_us[valid_ids],high,low,protocols))
    sorted_meta=valid_ids[order]
    pair_start=np.ones(len(order),dtype=bool)
    pair_start[1:]=(low[order][1:]!=low[order][:-1])|(high[order][1:]!=high[order][:-1])|(protocols[order][1:]!=protocols[order][:-1])
    pair_ids=np.cumsum(pair_start)-1
    end=start_us[sorted_meta]+duration_us[sorted_meta]
    running_max=pd.Series(end).groupby(pair_ids,sort=False).cummax().to_numpy()
    previous_end=np.roll(running_max,1)
    results=[]
    for gap in [60,120,300]:
        new_session=pair_start|(start_us[sorted_meta]-previous_end > gap*1000000)
        uf=UnionFind(n)
        uf.parent=base_roots.copy()
        uf.rank=np.ones(n,dtype=np.uint8)
        for position in np.flatnonzero(~new_session):
            uf.union(int(sorted_meta[position-1]),int(sorted_meta[position]))
        roots=uf.roots()
        touches=np.zeros(n,dtype=bool)
        touches[roots[fit]]=True
        t0_closure=touches[roots]
        kept=survivor & ~t0_closure
        rows_by_family=[]
        for name,code in label_map.items():
            family=(labels==code)&kept
            comp_counts=np.unique(roots[family],return_counts=True)[1]
            rows_by_family.append({"family":name,"surviving_rows":int(family.sum()),"components":len(comp_counts),
                "largest_component_rows":int(comp_counts.max()) if len(comp_counts) else 0,
                "passes_necessary_150_rows_15_components":bool(family.sum()>=150 and len(comp_counts)>=15)})
        kept_component_counts=np.unique(roots[kept],return_counts=True)[1]
        result={"gap_seconds":gap,"operational_sessions":int(new_session.sum()),
            "components_all_provenance":int(len(np.unique(roots))),"t0_closure_rows":int(t0_closure.sum()),
            "non_T0_day_rows_in_closure":int((t0_closure & (file_index!=monday_index)).sum()),
            "retained_survivor_rows":int(kept.sum()),"retained_components":len(kept_component_counts),
            "largest_retained_component":int(kept_component_counts.max()) if len(kept_component_counts) else 0,
            "families":rows_by_family}
        results.append(result)
        if gap==120:
            np.savez(destination/"conditional-components-120.npz", roots=roots, survivor=survivor, kept=kept,
                t0_fit=fit,t0_closure=t0_closure,labels=labels,start_us=start_us,row_ids=row_ids,valid_metadata=meta_valid,
                raw_conflict=raw_conflict,final_conflict=final_conflict,final_finite=final_finite,file_index=file_index,valid_domain=valid_domain)
        print(json.dumps({"step":"component_gap","gap":gap,"kept":int(kept.sum()),"components":len(kept_component_counts),"elapsed_seconds":round(time.monotonic()-started,2)}),flush=True)
    features=census["numeric_feature_order"]
    result={"status":"conditional_data_feasibility_not_approved_final_split", "audit_version":2, "completed_utc":datetime.now(timezone.utc).isoformat(),
        "source_census":census_file,"release_candidate":output_prefix,"label_code_order":label_names,"source_csv_records_including_blank":n,"invalid_metadata":int((~meta_valid).sum()),
        "feature_domain_policy":domain_policy,"finite_rows_failing_domain_policy":int((finite&~valid_domain).sum()),
        "scaled_extrema_population":"All finite published values" if domain_policy=="as_published" else "Domain/metadata-valid finite candidate records, before annotation-conflict quarantine",
        "invalid_ip_strings":invalid_ip_strings,"clock_rule":clock_rule,
        "rows_pm_interpreted":int(pm_interpreted.sum()),"missing_reference_annotation_rows":int(missing_annotation.sum()),"quarantine_links_retained":True,
        "raw_conflicting_groups":raw_conflict_groups,"raw_conflicting_rows":int(raw_conflict.sum()),
        "final_conflicting_groups":final_conflict_groups,"final_conflicting_rows":int(final_conflict.sum()),
        "T0_fitting_rows":int(fit.sum()),"T0_fitting_rows_with_final_input_conflict":conflicting_fitting,
        "calibration_policy":"Monday-only source-valid benign fitting eligibility, independent of cross-day labels; future input conflicts quarantine learning/evaluation and extend T0 exclusion closure without refitting.",
        "calibration_policy_gate_passes":bool(np.isfinite(minimum).all() and np.isfinite(maximum).all()),"nonfinite_final_rows_from_finite_raw":int((finite&~final_finite).sum()),
        "same_label_duplicate_copies_removed":int(eligible.sum()-survivor.sum()),
        "scaler_features":[{"feature":name,"minimum_T0":float(minimum[i]),"maximum_T0":float(maximum[i]),
            "denominator":float(denominator[i]),"zero_range":bool(zero_range[i]),"final_minimum":float(final_min[i]),
            "final_maximum":float(final_max[i]),"out_of_0_1_rows":int(out_of_range[i])} for i,name in enumerate(features)],
        "gap_sensitivities":results,"elapsed_seconds":round(time.monotonic()-started,3),
        "limits":["Source-specific clock/units/taxonomy choices remain prospective", "Necessary support is not actual 60/20/20 split support", "No final split or learner implementation approved", "No model training, performance evaluation or implementation tests", "Original minute precision cannot establish exact physical flow start times; corrected feature-name aliases do not establish original-feature equivalence"]}
    (DOCS/f"{output_prefix}-component-feasibility.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"calibration_policy_gate_passes":result["calibration_policy_gate_passes"],"elapsed_seconds":result["elapsed_seconds"]}),flush=True)


if __name__=="__main__":
    main()
