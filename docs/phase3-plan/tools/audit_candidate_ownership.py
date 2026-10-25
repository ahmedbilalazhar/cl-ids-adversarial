"""Data-only benign-pool, ownership and realized-dose feasibility census.

Uses the exact proposed component heuristic, not a model or admission scorer.
No final data/protocol selection or performance evaluation is implied.
"""
from __future__ import annotations
import argparse
import json
import time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
DOCS=ROOT/"docs/phase3-plan"
WORK=ROOT/"data/raw/phase3-feasibility-original"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release",choices=["original","corrected"],default="original")
    parser.add_argument("--benign-policy",choices=["mandatory-all-rows","benign-subset-by-component"],default="mandatory-all-rows")
    parser.add_argument("--domain-checked",action="store_true")
    parser.add_argument("--profile",choices=["default","no-headers-74"],default="default")
    args=parser.parse_args()
    work=ROOT/f"data/raw/phase3-feasibility-{args.release}"
    candidate_prefix=args.release+("-domain-checked" if args.domain_checked else "")
    if args.profile!="default":
        if args.release!="corrected" or args.domain_checked:raise ValueError("74-feature profile is a separate corrected candidate")
        candidate_prefix="corrected-no-headers-74"
        work=work/"no-headers-74"
    if args.domain_checked:
        work=work/"domain-checked"
    prefix="" if candidate_prefix=="original" else candidate_prefix+"-"
    split_name=f"{prefix}candidate-split-feasibility.json"
    suffix="" if args.benign_policy=="mandatory-all-rows" else "-benign-subset"
    started=time.monotonic()
    split_report=json.loads((DOCS/split_name).read_text())
    if split_report.get("audit_version")!=2:
        raise RuntimeError("Requires canonical-component-ID split v2")
    parent=json.loads((DOCS/f"{candidate_prefix}-component-feasibility.json").read_text())
    names=[row["family"] for row in next(g for g in parent["gap_sensitivities"] if g["gap_seconds"]==120)["families"]]
    code={name:i for i,name in enumerate(names)}
    source_census=json.loads((DOCS/("original-full-census.json" if args.release=="original" else "corrected-component-input-manifest.json")).read_text())
    stage_by_file={row["file_index"]:(0 if "monday" in row["name"].lower() else 1 if "tuesday" in row["name"].lower() else 2 if "wednesday" in row["name"].lower() else 3 if "thursday" in row["name"].lower() else 4) for row in source_census["files"]}
    state=np.load(work/"conditional-components-120.npz",allow_pickle=False)
    split=np.load(work/"conditional-candidate-split.npz",allow_pickle=False)
    positions=split["source_positions"][split["roles"]==0]
    all_roots=state["roots"]
    all_row_ids=state["row_ids"]
    canonical=np.full(len(all_roots),np.iinfo(np.uint64).max,dtype=np.uint64)
    np.minimum.at(canonical,all_roots,all_row_ids)
    group_ids=canonical[all_roots[positions]]
    components,inverse=np.unique(group_ids,return_inverse=True)
    labels=state["labels"][positions]
    stages=np.array([stage_by_file[int(f)] for f in state["file_index"][positions]],dtype=np.int8)
    if not np.all((stages>=1)&(stages<=4)):
        raise RuntimeError("T0 or unknown stage entered candidate training pool")
    counts=np.zeros((len(components),len(names)),dtype=np.int64)
    np.add.at(counts,(inverse,labels),1)
    benign_counts=np.zeros((len(components),4),dtype=np.int64)
    benign=labels==code["Benign"]
    np.add.at(benign_counts,(inverse[benign],stages[benign]-1),1)
    attacks=counts.sum(axis=1)-counts[:,code["Benign"]]
    mandatory=attacks>0
    mandatory_B=benign_counts[mandatory].sum(axis=0)
    benign_selected=mandatory.copy() if args.benign_policy=="mandatory-all-rows" else np.zeros(len(components),dtype=bool)
    B=benign_counts[benign_selected].sum(axis=0)
    candidates=np.flatnonzero((~mandatory) if args.benign_policy=="mandatory-all-rows" else (benign_counts.sum(axis=1)>0))
    builder_rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence(2027)))
    for group in builder_rng.permutation(candidates):
        increment=benign_counts[group]
        change=int(2*np.dot(increment,B-3500)+np.dot(increment,increment))
        if change<0:
            benign_selected[group]=True
            B+=increment
    selected=mandatory|benign_selected
    selected_rows=(labels!=code["Benign"])|benign_selected[inverse]
    chosen_positions=positions[selected_rows]
    chosen_component_ids=group_ids[selected_rows]
    chosen_labels=labels[selected_rows]
    chosen_stages=stages[selected_rows]
    selected_components=components[selected]
    vectors=counts[selected].copy()
    vectors[:,code["Benign"]]=np.where(benign_selected[selected],vectors[:,code["Benign"]],0)
    sizes=vectors.sum(axis=1)
    order=np.lexsort((selected_components,-sizes))
    totals=vectors.sum(axis=0)
    present=totals>0
    denominators=np.where(present,totals,1).astype(np.float64)
    seed_rows=[]
    for seed in list(range(1,12))+[42]:
        ownership_rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence([1,1,seed])))
        shares=np.zeros((5,len(names)),dtype=np.float64)
        for family in range(len(names)):
            if present[family]:
                shares[:,family]=ownership_rng.dirichlet(np.full(5,.5))
        targets=shares*totals
        assigned=np.zeros_like(targets)
        owners=np.full(len(selected_components),-1,dtype=np.int8)
        for group in order:
            vector=vectors[group]
            delta=((assigned+vector-targets)/denominators)**2-((assigned-targets)/denominators)**2
            losses=delta[:,present].sum(axis=1)
            client=int(np.argmin(losses))
            owners[group]=client
            assigned[client]+=vector
        row_component=np.searchsorted(selected_components,chosen_component_ids)
        row_owner=owners[row_component]
        E2=chosen_stages==2
        source=(chosen_labels==code["DoS Hulk"])&E2
        honest_benign=(chosen_labels==code["Benign"])&E2
        h=np.bincount(row_owner[source],minlength=5)
        b=np.bincount(row_owner[honest_benign],minlength=5)
        current=np.bincount(row_owner[E2],minlength=5)
        eligible=np.flatnonzero(h>=10)
        if not len(eligible):
            raise RuntimeError("No eligible candidate attacked client")
        attacker_rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence([1,2,seed])))
        attacker=int(attacker_rng.choice(eligible))
        dose_rows=[]
        for numerator,denominator in [(0,1),(1,10),(3,10),(1,2)]:
            q=numerator*int(h[attacker])//denominator
            group_b=int(b[attacker])+q
            quota=group_b if group_b<20 else (3*group_b+3)//4
            admitted=current.copy()
            # Only recurring benign is quota-filtered in this schedule.
            for client in range(5):
                supplied_b=int(b[client])+(q if client==attacker else 0)
                K=supplied_b if supplied_b<20 else (3*supplied_b+3)//4
                admitted[client]-=supplied_b-K
            dose_rows.append({"dose_fraction":[numerator,denominator],"flipped_count":q,
                "local_raw_poison_fraction":q/int(current[attacker]),"global_raw_poison_fraction":q/int(current.sum()),
                "attacked_supplied_benign_count":group_b,"attacked_benign_quota":quota,
                "minimum_retained_poison":max(0,quota-int(b[attacker])),
                "DQ_expected_retained_poison":q*quota/group_b if group_b else None,
                "DC_DM_DQ_admitted_counts":admitted.tolist(),
                "attacker_FedAvg_weight_filtered":int(admitted[attacker])/int(admitted.sum())})
        np.savez(work/f"conditional-ownership{suffix}-seed-{seed}.npz",source_positions=chosen_positions,row_owner=row_owner,
            component_ids=selected_components,component_owner=owners,Dirichlet_targets=targets,Dirichlet_realized=assigned)
        seed_rows.append({"seed":seed,"eligible_attackers":eligible.tolist(),"attacker":attacker,
            "E2_source_counts":h.tolist(),"E2_honest_benign_counts":b.tolist(),"E2_current_counts":current.tolist(),
            "normalized_allocation_objective":float((((assigned-targets)/denominators)[:,present]**2).sum()),"doses":dose_rows,
            "stage_client_rows":{str(stage):np.bincount(row_owner[chosen_stages==stage],minlength=5).tolist() for stage in range(1,5)}})
        print(json.dumps({"seed":seed,"attacker":attacker,"source_rows":int(h[attacker]),"benign_rows":int(b[attacker]),"global_max_dose":dose_rows[-1]["global_raw_poison_fraction"],"elapsed_seconds":round(time.monotonic()-started,2)}),flush=True)
    stage_counts={str(stage):int((chosen_stages==stage).sum()) for stage in range(1,5)}
    result={"status":"conditional_data_only_ownership_and_dose_audit_not_final_protocol_lock","completed_utc":datetime.now(timezone.utc).isoformat(),
        "parent_split":split_name,"release_candidate":candidate_prefix,"benign_policy":args.benign_policy,"requires_split_audit_version":2,
        "ownership_seed_key":"SeedSequence([namespace_version=1,namespace_id=1,training_seed]); PCG64","attacker_seed_key":"SeedSequence([namespace_version=1,namespace_id=2,training_seed]); PCG64",
        "builder_benign_seed":2027,"algorithm":"protocol-closure-spec.md deterministic normalized squared-error greedy allocator",
        "preselection_training_rows":len(positions),"selected_training_rows":len(chosen_positions),"selected_training_components":len(selected_components),
        "mandatory_benign_stage_counts":mandatory_B.tolist(),"selected_benign_stage_counts":B.tolist(),"all_stages_have_benign":bool((B>0).all()),
        "stage_total_rows":stage_counts,"family_training_rows":{name:int(totals[i]) for i,name in enumerate(names)},"seeds":seed_rows,
        "elapsed_seconds":round(time.monotonic()-started,3),"models_fitted":0,
        "limits":["Data/release/clock/graph/allocator choices remain conditional","Admitted poison is a quota bound/expectation, not a score-selected observed count","No gradients, learned models, accuracy or GPU runtime were measured","No final scope or methodological amendment was approved by this audit"]}
    (DOCS/f"{prefix}candidate-ownership-dose-audit{suffix}.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"selected_rows":len(chosen_positions),"benign_by_stage":B.tolist(),"stage_rows":stage_counts,"elapsed_seconds":result["elapsed_seconds"]}),flush=True)


if __name__=="__main__":
    main()
