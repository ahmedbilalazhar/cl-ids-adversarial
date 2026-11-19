"""Write the evidence-based remediation register; no historical artifacts edited."""
from pathlib import Path
import csv
import json
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from audit_phase3_reliability import read,write_json
OUT=ROOT/'results/phase3-rigorous-audit-v1'
DOC=ROOT/'docs/phase3-rigorous-audit-v1'


def main():
    DOC.mkdir(exist_ok=True)
    items=[]
    def issue(code,kind,severity,commitment,evidence,actual,claim,consequence,invalidates,fix,rerun,status):
        items.append(dict(id=code,classification=kind,severity=severity,commitment=commitment,implementation_and_evidence=evidence,
                          actual_behavior=actual,report_claim=claim,consequence=consequence,invalidates=invalidates,
                          smallest_fix=fix,required_reruns_and_acceptance=rerun,status=status))
    issue('R01','C','major','Weak effects must not trigger extra attackers or doses (Phase2 Step7).',
          'submissions/phase2-with-claude.tex: Step7 clean gates; original report subsection What changed from Phase2',
          'Historical submission escalated to 3/5 attackers and calls it a predeclared fallback.',
          'Pre-declared fallback and implementation of Phase2.', 'RQ1: stronger capability answers a different question.',
          'Invalidates predeclared-status claim, not descriptive measurements of the stronger attack.',
          'Remove fallback claim; label escalation retrospective exploratory; lead with single-attacker results.',
          'No training; revised abstract, methods and conclusion must agree.','Corrected in audited report; original preserved.')
    issue('R02','A','major','Client-local accumulated empirical Fisher, never FedAvg averaged.',
          'phase3-implementation/src/p3lib.py: run, lines386-391; src/phase3_v2/learning.py: commit_importance',
          'Historical engine forms weighted global importance and shares one penalty; newer engine retains local importance.',
          'Faithful Phase2 EI baseline.','RQ1: EI is a different algorithm in historical study.',
          'Historical EI cannot establish behavior of proposed local-EI; latest EI audited separately.',
          'Retain historical source; use local-EI engine for proposed-method comparisons.',
          'Latest primary matrix already complete; require semantic checks and exact representative replay, not redundant historical reruns.',
          'Implementation corrected in later engine; historical discrepancy disclosed.')
    issue('R03','A','major','Xavier initialization of appended head rows.',
          'phase3-implementation/src/p3lib.py: Net.grow lines127-135; src/phase3/model.py: initialize_rows',
          'Historical growth uses Gaussian standard deviation .01; latest growth uses Xavier uniform.',
          'Faithfulness to Phase2 head initialization.','RQ1/RQ2: acquisition/scoring can depend on untrained rows.',
          'Historical results remain valid only for their implemented initializer.',
          'Use latest Xavier engine; name the historical amendment explicitly.',
          'No new grid if current primary weights and replay verify.','Disclosed; latest engine implements prescribed initialization.')
    issue('R04','B','critical','Independent complete seeded trajectories and one 29-test family.',
          'original report Statistics and Limits; phase3-implementation/src/p3lib.py: Cfg.rep; historical-run-inventory.json',
          '696 distinct configurations share three ownership partitions; submitted inference treats 12 training units as independent and uses separate 30/17 families.',
          'Confirmatory significant learner/defence contrasts.','RQ1/RQ2: nominal p-values do not support original inferential claims.',
          'Invalidates original confirmatory significance claims; not raw confusion counts.',
          'Withdraw original significance claims; latest 12 ownership seeds analyzed separately with single Holm family.',
          '29 exact rational contrasts plus paired sign-test sensitivity; whole-seed intervals.','Recomputed; latest inference explicitly development-only exploratory.')
    issue('R05','B','major','H is mean E3/E4 Hulk-to-benign poisoned-minus-clean error; eligible rows with all prediction columns.',
          'original report Metrics; phase3-implementation/src/p3lib.py: stage_metrics/summarize; audit trajectory-metrics.json',
          'Historical scores mix full-bank false positives with eligible macro averaging and describe retention damage differently from prescribed H.',
          'Phase2 endpoints and whole-dataset performance.','RQ1/RQ2: estimands differ; signs and magnitudes cannot be interchanged.',
          'Original labels/interpretation require correction; saved confusion matrices can be rescored.',
          'Use independent count-derived endpoints; keep eligible and full-inventory populations separately named.',
          'No training; rational endpoints, denominators, rare-class support and excluded-column fixtures.','Latest primary and follow-up endpoints independently recomputed.')
    issue('R06','B','major','ACC/BWT/forgetting use fixed stage cohorts including disjoint benign cohorts.',
          'phase3-implementation/src/p3lib.py: summarize lines302-312; scripts/verify_phase3_cohort_metrics.py',
          'Historical continual metrics average attack-class recalls and omit required benign cohorts.',
          'ACC/BWT/forgetting as prescribed in Phase2.','RQ1/rubric: different retention metric.',
          'Historical named metrics do not estimate prescribed quantities.',
          'Label historical recall-based measures; reconstruct fixed-cohort metrics from clean latest checkpoints.',
          '60 clean trajectories, four checkpoints each; compare regenerated confusion matrices exactly.','Checkpoint reevaluation executed separately; see cohort-metrics.json.')
    issue('R07','G','major','Immutable source identities must match executed source.',
          'results/phase3-overnight/identity.json; source-verification.json; recovered executed-source/scripts/run_phase3_overnight.py',
          'Current runner changed reserve from 1.5h to .75h; exact old bytes recovered by SHA256.',
          'Current source directly reproduces frozen identity.','All RQs: hash drift breaks ordinary reproduction even when scheduling-only.',
          'Does not by itself invalidate learning outputs; difference inspected and representative execution checked.',
          'Preserve frozen source; record explicit diff; verify every source/input before replay.',
          'Exact stage/model/memory/ledger/oracle reproduction in pinned environment.','Recovered; no frozen identity rewritten.')
    issue('R08','B','moderate','Unique trajectories, copies and continuations must be counted separately.',
          'result-catalog.json; results/phase3-followup-ablation/runs/runs; completion-followup.json',
          '963 physical files collapse to 417 configurations; 546 identical copies; 24 oracle suffixes are embedded branches.',
          'Summed directory counts represent experiment replication.','Rubric and RQ inference: counts inflate apparent independent evidence.',
          'Invalidates inflated counts only; no conflicting duplicate payload found.',
          'Catalog by study identity + full settings; reject differing payloads for one identity.',
          '417 unique = 9 clean confirmations + 240 primary + 24 DQ + 48 loss + 96 quota; 24 suffixes separately.','Corrected catalog, report and package inventory.')
    issue('R09','E','major','Separate qualified sealed final-test evaluator after full freeze.',
          'data/processed/phase3-reference74-v1/development/manifest.json; docs/phase3-plan/final-test-readiness.md',
          'Zero final-test rows exported; latest results use same historical development bank.',
          'Any independent final-test or confirmatory effectiveness claim.','All RQs: repeated development exposure limits generalization/inference.',
          'Development evidence valid conditionally; independent final effectiveness unestablished.',
          'Label all current outcomes development-only; freeze then qualify isolated evaluator before any test extraction.',
          'Deferred: role-enforced evaluator, source/split/checkpoint/analysis freeze and one-shot predictions.','Not executed; sealed outcomes remain untouched.')
    issue('R10','D','moderate','Original 76 features/15 labels and source release.',
          'configs/phase3/reference74-v1.json; taxonomy-v1.json; docs/phase3-reference/adoption.json; data-audit.json',
          'Corrected source; two header-length fields removed; Infiltration-Portscan added; widths3/8/13/16.',
          'Unamended original methodology.','RQ2: E3 acquisition concerns one supported annotated scenario, not certified novel technique.',
          'Does not invalidate amended study; prevents drop-in comparison to original release.',
          'Document release/schema/taxonomy amendments and support by class; no retrospective editing of Phase2.',
          'Independent role/content/T0/transform checks and exact feature list.','Documented and exported inputs independently verified.')
    issue('R11','F','major','Honest clean acquisition and operational false alarms.',
          'core-summary.json; comparisons-29.json; clean-gates.json',
          'DC has lower mean A at all four doses and higher clean FAR than DM. Clean FTP recall is zero for pilot103 despite passing prescribed mean gate.',
          'Retention of every new-label row establishes improved acquisition or operational safety.',
          'RQ2: retention count is construction, not learning; high FAR undermines operational utility.',
          'No implementation invalidation; invalidates broad superiority/safety interpretation.',
          'Report adverse trade-off, per-seed gates and absolute errors; do not silently discard or retune weak seeds.',
          'No training; paired A/FAR effects, sign-test sensitivity and raw seed values.','Adverse results retained.')
    issue('R12','F','major','Weak attacks are valid; poison survival alone does not identify causation.',
          'core-summary.json; oracle-repair.json; 24 exact E2 clone controls',
          'Replay has small average single-attacker immediate damage; repair effects are conditional on retained labels and earlier poisoned state.',
          'Strong general persistence or replay-causes-all-damage claim.','RQ1/RQ3: forgetting, remaining headroom and earlier damage matter.',
          'No; limits claim strength.',
          'Report absolute clean/attacked errors and conditional intervention effects; keep original threat.',
          'No escalation; retain zero-effect repairs; report sign/size without causal overreach.','Claims narrowed; repair results recomputed.')
    issue('R13','E','moderate','Meaningful eviction ablations if eviction mechanism claims remain.',
          'latest unique_blocks; Phase2 Step10; historical FIFO source/results',
          'Latest single-attacker study has loss/quota/DQ controls but lacks FIFO and specified class-balanced eviction.',
          'Eviction rule explains latest single-attacker persistence.','RQ3: mechanism attribution incomplete.',
          'Does not invalidate primary comparisons; invalidates unsupported eviction attribution.',
          'Remove eviction attribution from latest conclusions; preregister complete matched controls before running.',
          '96 full DC trajectories: 2 eviction variants x 2 doses x12 seeds, original500 slots; run only if conservative estimate plus reserve fits six hours.','Unexecuted; exact experiment card in remediation-plan.md.')
    issue('R14','B','moderate','Costs separate training/admission/importance/evaluation, actual allocations and transmitted bytes.',
          'phase3-implementation/src/p3lib.py: Buffer.bytes and run cost; latest elapsed_seconds and latency fields',
          'Historical memory is a formula, communication counts raw weights only; latest elapsed time includes evaluation and, for some runs, oracle continuation.',
          'Measured end-to-end deployment/communication cost or fair training-only timing.','RQ3: overhead ratios and absolute budgets otherwise misleading.',
          'Invalidates resource interpretation, not accuracy.',
          'Instrument observational replay; distinguish measured stage categories from analytic payload estimates and unmeasured serialization.',
          'Representative matched runtime rows; batch1/256 warmup10/trials100; no edge/network/energy claim.','Representative timings measured in replay; full cross-seed cost characterization remains open.')
    issue('R15','A','minor','All-zero signed-rank effect convention is zero.',
          'scripts/phase3_evidence.py: signed_rank_enumeration; tests/test_phase3_cpu_supplement.py',
          'Shared helper returned None for all-zero rank-biserial effect.',
          'Phase2 all-zero convention.','Inference/reporting: null effects inconsistently represented.',
          'No change to p=1 or any nonzero contrast.',
          'Return0.0; update meaningful zero-case assertion and independent rational fixture.',
          'Focused helper tests; regenerate audited analyses.','Patched and tested; frozen training sources unchanged.')
    issue('R16','G','major','Independent source-session/content construction and release authentication.',
          'data-audit.json; source/input hashes; src/phase3/prepare.py docstring; corrected input manifest',
          'This audit verifies saved source graph, split, T0 and all exported transforms; it has not rebuilt full session links directly from all CSVs.',
          'Fully independent raw-capture/session validation.','All RQs: upstream session semantics/provenance not proven by downstream hash checks.',
          'No demonstrated overlap defect; full raw reconstruction assurance remains unresolved.',
          'State audit boundary; keep upstream evidence with exact identities; independently rebuild graph before claiming complete isolation certification.',
          'Source CSV census,120s graph and60/300s sensitivity, exclusion and closure parity; compare full component membership.','Unresolved, explicitly limits reliability assessment.')
    issue('R17','E','major','External replication needs independent data/schema/taxonomy/isolation and full method.',
          'results/phase3-followup/external-method-training-pilot-summary-v1.json; external-id-isolation-audit-v1.json',
          '16 train-only pilot arms on two datasets, one seed, differing feature schemas; discovery is a submodule.',
          'External full-method effectiveness or deployment generalization.','All RQs/external validity: no qualified external outcome evidence.',
          'Only efficacy extrapolation invalid; execution pilot remains evidence of running.',
          'Describe train-only pilot and discovery separately; do not pool or infer effectiveness.',
          'Separate verified external evaluator, paired repeated seeds, support and semantic-map audit before held-out scoring.','Deferred; no external held-out outcomes opened.')
    issue('R18','G','moderate','Genuine instructor feedback only.',
          'docs/instructor_note.md; submissions/phase3-methodology-amendment.md; amendment-register.md: Instructor feedback',
          'Found draft note and explicit statement that feedback was not supplied.',
          'Instructor-approved amendments.','Rubric: actual feedback compliance cannot be demonstrated.',
          'Approval claims unsupported, not experimental values.',
          'Record unavailable; do not send the draft or invent approval.',
          'Actual instructor comments required to close.','Missing external evidence; independent work completed.')
    issue('R19','A','moderate','Completed evidence must be independently reproducible without overwriting history.',
          'scripts/finalize_phase3_overnight.py: main early guard lines60-65; reproduce_phase3_overnight.py: materialize before validation',
          'Existing finalizer refuses completed manifest before reanalysis, and replay assumes current runner hash and mutating materialization.',
          'Ordinary command reproduces final completed study.','Reproducibility rubric: completed archive cannot be independently regenerated with stated path.',
          'No accuracy invalidation; reproduction instructions broken for frozen evidence.',
          'New read-only catalog/scorer plus strict frozen-source replay into new output, exclusive lock and atomic audit outputs.',
          'Read-only input hashes unchanged, conflicting duplicate rejection, pinned representative replay and package self-contained source snapshot.','New audit/replay commands supplied; original finalizer preserved.')
    issue('R20','A','major','Importing one engine must not change another engine admission contract.',
          'scripts/run_phase3_overnight.py: module-level L.choose_admission assignment; pinned-tests.log eight failures',
          'Import replaced shared v2 chooser with quota adapter requiring settings.q; v2/v3 Settings lack that field.',
          'Engines can be composed/tested independently without import-order effects.',
          'Reproducibility: mixed engine use fails; isolated archived overnight worker uses compatible settings.',
          'Does not invalidate isolated historical overnight jobs; breaks mixed imports and shared tests.',
          'Scope quota adapter to admission call and restore original function in finally.',
          'Run combined v2/v3/overnight suite plus import-isolation regression; source amendment recorded, frozen snapshot retained.',
          'Patched current runner; archived-source reproduction kept separate.')
    issue('R21','F','major','Disclose sensitivity of operational session grouping at60/120/300 seconds.',
          'scripts/verify_phase3_component_graph.py; component-reconstruction.json',
          'Independent120s graph and T0 closure match exactly. The60s graph has no frozen-split overlap;300s grouping joins8982 train/dev,9056 train/test and3444 dev/test components.',
          'Session isolation is invariant to plausible session-gap choices.',
          'Data validity/generalization: isolation is conditional on the declared120s operational grouping.',
          'Does not invalidate the predeclared120s contract; invalidates a threshold-invariant isolation claim.',
          'Report sensitivity and shared source-parser boundary; do not choose the gap using model outcomes.',
          '60/120/300 metadata-based graph reconstructions executed; any300s study needs new split/support/T0 closure and complete matched retraining.',
          'Disclosed; no threshold change or outcome-driven rerun.')
    issue('R22','G','major','Checkpoint weights, archived source and reported metrics must agree.',
          'Original Phase3_Submission ZIP member inventory; historical-run-inventory.json; checkpoint-audit.json',
          'Original archive contains no saved .pt/.pth/.npz weights. Its p3lib.py differs only in line-ending bytes from the inspected historical engine; normalized text is equal. Latest1668 weights are present and verified.',
          'All696 historical GPU metrics can be independently re-evaluated from saved weights.',
          'Historical reproducibility: raw696 result records can be checked/rescored, but their prediction/weight linkage cannot be independently replayed from missing checkpoints.',
          'No proof of fabricated metrics; limits assurance of the historical GPU study and makes missing weights explicit.',
          'Preserve historical evidence and state this boundary; use qualified latest checkpoints for weight-linked claims.',
          'Supply original GPU weights/runtime/source bundle to close historical linkage; otherwise do not claim checkpoint re-evaluation of696 GPU runs.',
          'Unresolved historical artifact absence; latest primary checkpoints verified.')
    write_json(OUT/'gap-register.json',items)
    with (DOC/'gap-register.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
    lines=['# Severity-ranked evidence register','',
           'A implementation defect; B experimental/analysis defect; C unsupported claim; D amendment; E incomplete experiment; F legitimate limitation; G unresolved evidence concern.',
           '', 'Historical defects are scoped to their engine. A verified later implementation does not repair historical outputs retrospectively.','']
    order={'critical':0,'major':1,'moderate':2,'minor':3}
    for r in sorted(items,key=lambda x:(order[x['severity']],x['id'])):
        lines.extend([f"## {r['id']} - {r['severity']} / {r['classification']}",''])
        for key,value in r.items():
            if key not in ('id','severity','classification'):lines.extend([f"**{key.replace('_',' ').capitalize()}:** {value}",''])
    (DOC/'gap-register.md').write_text('\n'.join(lines),encoding='utf-8')
    (DOC/'traceability-matrix.md').write_text('# Phase 2 traceability\n\n| Commitment | Implementation and executed evidence | Report discrepancy | Consequence | Fix / acceptance |\n|---|---|---|---|---|\n'+'\n'.join('| '+' | '.join(str(r[k]).replace('|','/') for k in ['commitment','implementation_and_evidence','report_claim','consequence','required_reruns_and_acceptance'])+' |' for r in items),encoding='utf-8')
    print('Wrote',len(items),'classified findings')


if __name__=='__main__':main()
