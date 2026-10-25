"""Build the executed v3 CPU delivery from immutable checks and measured jobs."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from src.phase3.common import ROOT, digest, read_json, write_json
from src.phase3_analysis.statistics import analysis_identity
from src.phase3_v2.protocol import code_identity as parent_identity
from src.phase3_v3.development import artifact_hashes
from src.phase3_v3.protocol import DECISIONS, PROTOCOL, code_files, code_identity


def main():
    base, docs = ROOT/'results/phase3-cpu-v3', ROOT/'docs/phase3-cpu-v3'
    reports = {name: read_json(base/path) for name, path in {
        'methods': 'acceptance.json', 'integration': 'integration/acceptance.json',
        'poison_methods': 'poison-acceptance.json', 'controls': 'controls/acceptance.json',
        'recovery': 'recovery/acceptance.json', 'costs': 'cost-correction/selection.json',
        'profiling': 'profiling/jobs.json'}.items()}
    for name, report in reports.items():
        expected = 'complete' if name == 'costs' else 'passed'
        if report['status'] != expected or ('code_identity' in report and report['code_identity'] != code_identity()):
            raise ValueError('Required current evidence incomplete: '+name)
    original = read_json(base/'development/completion.json')
    selection = reports['costs']
    diagnostic_index = read_json(base/'matched-diagnostic/index.json')
    if diagnostic_index['selection_sha256'] != digest(base/'cost-correction/selection.json') or diagnostic_index['code_identity'] != code_identity():
        raise ValueError('Selected-condition diagnostic lineage changed')
    diagnostics = diagnostic_index['diagnostics']
    diagnostic_count = diagnostic_index['completed_diagnostic_rows']
    if (selection['required_matched_FT_diagnostic_rerun'] and diagnostic_index['all_clean_learners_feasible']
            and (diagnostic_index['source'] != 'cost_amended_matching_diagnostics' or diagnostic_count != 3)):
        raise ValueError('Cost-amended FT winner requires its matching poisoned diagnostic before delivery')
    cleanrows = [r for r in original['rows'] if r['group'] in ('pilot', 'tuning')]
    if len(cleanrows) != 78 or any(r['settings']['seed'] not in (101, 102, 103) for r in original['rows']):
        raise ValueError('Incomplete or undeclared seed inventory')
    receipt_checks = {}
    for row in original['rows']:
        receipt = read_json(base/'development/receipts'/f"{row['row_id']}.json")
        if receipt['row'] != row or receipt['code_identity'] != code_identity():
            raise ValueError('Row/receipt lineage differs')
        if row['physical_execution']:
            equal = artifact_hashes(base/'development/executions'/row['row_id']) == receipt['artifact_files']
            receipt_checks[row['row_id']] = equal
            if not equal:
                raise ValueError('Receipt payloads changed: '+row['row_id'])
    originals = read_json(ROOT/'results/phase3-cpu-v2/integrity/original-inputs.json')
    preserved = {name: digest(ROOT/name) == sha for name, sha in originals.items()}
    if not all(preserved.values()) or parent_identity() != '4b7561d38300b9f42dd6e9091ecc3509b5e1b2cabdddedb2b9cdd345baffa6a6':
        raise ValueError('A preserved scientific input changed')
    parent_review = ROOT/'docs/phase3-cpu-v2/evidence'
    if any(digest(parent_review/name) != sha for name, sha in read_json(parent_review/'artifact-index.json')['files'].items()):
        raise ValueError('V2 review evidence changed')
    parent_scripts = read_json(parent_review/'source-code-manifest.json')['delivery_scripts']
    if any(digest(ROOT/name) != sha for name, sha in parent_scripts.items()):
        raise ValueError('Preserved v2 delivery script changed')
    analysis = read_json(ROOT/'results/phase3-analysis-v1/acceptance.json')
    if analysis['status'] != 'passed' or analysis['analysis_identity'] != analysis_identity():
        raise ValueError('Current synthetic analysis acceptance required')
    count_audit_path = ROOT/'results/phase3-endpoint-audit-v1/audit.json'
    count_audit = read_json(count_audit_path)
    if (count_audit['status'] != 'passed' or count_audit['code_identity'] != code_identity()
            or count_audit['auditor_sha256'] != digest(ROOT/'scripts/audit_phase3_endpoints.py')
            or count_audit['valid_logical_rows_audited'] != sum(r['status'] == 'valid' for r in original['rows'])):
        raise ValueError('Current complete independent count audit required')
    write_json(base/'preservation.json', {'status': 'passed', 'parent_code_identity': parent_identity(), 'original_files': preserved,
               'physical_row_receipts_exact': receipt_checks, 'v2_review_evidence_preserved': True, 'v2_delivery_scripts_preserved': parent_scripts})
    scripts = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted((ROOT/'scripts').glob('*phase3*.py'))}
    write_json(base/'source-code-manifest.json', {'code_identity': code_identity(), 'files': code_files(), 'delivery_scripts': scripts,
               'protocol_sha256': digest(PROTOCOL), 'decisions_sha256': digest(DECISIONS), 'analysis_identity': analysis_identity(),
               'analysis_source_and_tests': {'tests/test_phase3_analysis.py': digest(ROOT/'tests/test_phase3_analysis.py')},
               'scope': 'Working-tree source and preserved dependencies; no claim these new files exist in Git HEAD'})
    rows = []
    for row in original['rows']:
        if row['status'] != 'valid':
            rows.append({'row_id': row['row_id'], 'status': row['status'], 'exception': row.get('exception'), 'message': row.get('message')})
            continue
        metric = read_json(Path(row['metrics']))
        rows.append({'row_id': row['row_id'], 'group': row['group'], 'settings': row['settings'], 'status': 'valid',
                     'alias_of': row['alias_of'], 'physical_attempts': row['physical_attempts'],
                     'metric_sha256': digest(Path(row['metrics'])), 'macro_f1_by_stage': [s['eligible_macro_f1'] for s in metric['stages']],
                     'benign_far_by_stage': [s['binary_full_seen']['benign_far'] for s in metric['stages']],
                     'eligible_class_counts': [s['eligible_classes'] for s in metric['stages']],
                     'Hulk_partitions': [s['hulk_partition'] for s in metric['stages']], 'A': metric['A'],
                     'equal_stage_ACC4': metric['equal_stage_ACC4'], 'BWT4': metric['BWT4'], 'forgetting4': metric['forgetting4']})
    write_json(base/'development-summary.json', {'rows': rows, 'selected_budget': original['selected_budget'],
               'original_selection_preserved': True, 'cost_amended_selection_sha256': digest(base/'cost-correction/selection.json')})
    feasible = all(v['selected'] is not None for v in selection['learners'].values())
    profiles = {name: read_json(base/f'profiling/{name}/profile.json') for name in ('FT', 'EI', 'DR')}
    failures = {'schema': 'phase3-cpu-failure-inventory-v3', 'invalid_declared_rows': original['invalid_rows'],
                'infeasible_learners': [k for k, v in selection['learners'].items() if v['selected'] is None],
                'unresolved_costs': selection['unresolved_costs'], 'timing_anomalies_remeasured': [r['row_id'] for r in selection['remeasurements']],
                'poison_diagnostics_completed': diagnostic_count, 'poison_diagnostics_planned': 3,
                'original_FT_diagnostic_rows_retained': original['logical_diagnostic_rows_completed'],
                'instructor_feedback': 'not supplied', 'local_graphics': 'Intel UHD Graphics; current learner runtime is CPU-only',
                'unmeasured_or_unqualified': ['Pinned actual GPU worker runtime and CPU/GPU numeric agreement',
                    'Cold dependency installation and remote/network transfer costs', 'Real infrastructure crash/disk-loss injection',
                    'Full-data poisoned EI/DR/filtered condition grid beyond tiny semantic fixtures',
                    'Optional FIFO/NoY/NoZ/oracle/external-data interventions', 'Twelve-seed final inference/statistical release'],
                'unavailable_metrics_policy': 'No favorable/zero endpoint imputation; incomplete paired analysis rows remain unavailable',
                'final_test_accessed': False, 'gpu_dispatchable': False}
    write_json(base/'failure-inventory.json', failures)
    counts = {'declared_clean_logical_rows': len(cleanrows), 'physical_clean_conditions': original['physical_clean_conditions'],
              'physical_clean_training_attempts': original['physical_clean_executions'], 'exact_clean_aliases': original['exact_clean_aliases'],
              'paired_development_seeds': 3, 'poison_diagnostics': diagnostic_count,
              'cost_amended_matching_diagnostic_trajectories': diagnostic_index['additional_physical_training_executions'],
              'extra_full_compatibility_trajectories': 1, 'extra_E1_only_compatibility_trajectories': 3,
              'extra_full_control_trajectories': 3, 'same_logical_run_recovery_suffixes': 2,
              'infrastructure_timing_full_remeasurements': selection['additional_physical_training_executions'],
              'full_profile_verification_trajectories': 3, 'extra_independent_research_replicates_from_verification': 0}
    diagnostics_ready = not feasible or diagnostic_count == 3
    completion = {'status': 'CPU_v3_implemented_verified_and_profiled' if diagnostics_ready else 'CPU_v3_diagnostic_failures_retained',
                  'code_identity': code_identity(), 'counts': counts,
                  'focused_v3_test_groups': reports['methods']['tests_run'], 'extended_poison_fixture_groups': reports['poison_methods']['tests_run'],
                  'real_data_compatibility_checks': len(reports['integration']['checks']), 'full_control_checks': len(reports['controls']['checks']),
                  'recovery_and_prediction_checks': len(reports['recovery']['checks']), 'synthetic_analysis_tests': analysis['tests_run'],
                  'independently_audited_development_count_rows': count_audit['valid_logical_rows_audited'],
                  'count_artifact_rejection_checks': len(count_audit['rejection_checks']),
                  'clean_development_feasible': feasible, 'invalid_rows': original['invalid_rows'], 'selected_budget': original['selected_budget'],
                  'final_test_accessed': False, 'gpu_dispatchable': False,
                  'remaining_gates': ([] if feasible else ['Prospective clean-feasibility revision'])+
                      ([] if diagnostics_ready else ['Resolve required diagnostic execution failures'])+
                      ['Actual pinned/confirmed GPU runtime and full worker costs', 'Final scope/code/data/analysis freeze', 'Complete validated final matrix before final analysis']}
    write_json(base/'completion.json', completion)
    mapping = [
        ('Preserved data/source and distinct study identity', 'protocol.py; train.py; immutable ../phase3_v2/data.py', 'test_version_budget_scope_and_parent_unchanged', 'preservation.json; source-code-manifest.json; integration/acceptance.json'),
        ('Exact old-budget numerical parity', 'train.py -> immutable ../phase3_v2/train.py::Simulator', 'test_exact_old_budget_parity_all_six_pipelines', 'acceptance.json; integration/acceptance.json'),
        ('Extended passes, inactive sites, first-pass insertion, EI commit and recovery', 'protocol.py; immutable ../phase3_v2/learning.py/checkpoint.py', 'test_extended_updates_proposals_importance_and_exact_recovery_all_methods', 'acceptance.json; recovery/acceptance.json'),
        ('Poisoned extended-budget state and matched-volume interactions', 'immutable ../phase3_v2/prepare.py/learning.py', 'tests/test_phase3_v3_poison.py', 'poison-acceptance.json; controls/acceptance.json; controls/*-exposure.json'),
        ('Writer lock, immutable receipts, alias costs and interruption attempts', 'development.py', 'test_single_live_orchestrator_lock; test_completed_receipts_resume_exact_alias_cost_and_corruption_rejected; test_interrupted_condition_retained_and_same_identity_retried; test_unreceipted_import_requires_physical_measured_cost', 'acceptance.json; development/receipts/*.json'),
        ('Exact declared grid, gates and selection', 'development.py; immutable ../phase3_v2/development.py', 'test_frozen_grid_numeric_ties_and_no_old_budget_selection', 'development/procedure-lock.json; development/tuning-selection.json; cost-correction/selection.json'),
        ('Independent development banks and full active heads', 'evaluate.py; immutable ../phase3_v2/evaluate.py::stage_counts', 'test_cross_revision_resume_and_v2_evaluation_rejected; parent33 count fixtures', 'integration/acceptance.json; controls/*-evaluation/metrics.json; recovery/acceptance.json'),
        ('Prospective infrastructure timing disposition', '../../scripts/remeasure_phase3_v3.py', 'tests/test_phase3_costs.py', 'cost-correction/acceptance.json; cost-correction/selection.json'),
        ('Complete measured CPU jobs, memory, latency and logical serialization', '../../scripts/profile_phase3_v3.py', 'tests/test_phase3_profile.py', 'profiling/acceptance.json; profiling/jobs.json; profiling/*/profile.json; profiling/*/communication.json'),
        ('Fixed29 exact paired analysis with unavailable endpoints', '../phase3_analysis/statistics.py', 'tests/test_phase3_analysis.py', '../phase3-analysis-v1/acceptance.json; ../phase3-analysis-v1/synthetic-family-example.json'),
        ('Independent count arithmetic and development endpoints', '../../scripts/audit_phase3_endpoints.py', 'Eight corrupted-count rejection fixtures', '../phase3-endpoint-audit-v1/audit.json'),
        ('Final/GPU seals and remaining qualification', 'protocol.py; evaluate.py; configs/phase3/cpu-v3.json', 'test_version_budget_scope_and_parent_unchanged; test_cross_revision_resume_and_v2_evaluation_rejected', 'completion.json; failure-inventory.json')]
    write_json(docs/'requirements-to-evidence.json', {'rows': [{'requirement': a, 'code_under_src_phase3_v3_unless_qualified': b,
               'tests': c, 'evidence_under_results_phase3_cpu_v3_unless_qualified': d} for a, b, c, d in mapping]})
    review = docs/'evidence'
    review.mkdir(exist_ok=False)
    import shutil
    paths = [base/'completion.json', base/'failure-inventory.json', base/'preservation.json', base/'source-code-manifest.json',
             base/'development-summary.json', base/'acceptance.json', base/'poison-acceptance.json',
             base/'integration/acceptance.json', base/'development/procedure-lock.json', base/'development/synchronization-selection.json',
             base/'development/tuning-selection.json', base/'cost-correction/selection.json', base/'cost-correction/acceptance.json',
             base/'matched-diagnostic/index.json', base/'controls/acceptance.json',
             base/'recovery/acceptance.json', base/'profiling/jobs.json', base/'profiling/acceptance.json', ROOT/'results/phase3-analysis-v1/acceptance.json', count_audit_path]
    for path in paths:
        prefix = path.parent.name+'-' if path.name in ('acceptance.json', 'selection.json', 'index.json') else ''
        target = review/(prefix+path.name)
        shutil.copyfile(path, target)
    for learner in profiles:
        shutil.copyfile(base/f'profiling/{learner}/profile.json', review/f'{learner}-CPU-profile.json')
        shutil.copyfile(base/f'profiling/{learner}/communication.json', review/f'{learner}-communication.json')
    write_json(review/'artifact-index.json', {'files': {p.name: digest(p) for p in sorted(review.glob('*.json'))}})
    lines = [f'# Executed v3 CPU implementation report — {datetime.now(UTC).astimezone().date().isoformat()}', '',
             f"The budget revision is implemented and verified. Clean development feasibility: {feasible}. Selected common budget: {original['selected_budget']} (rounds,epochs).",
             '', (f"{len(cleanrows)} logical clean rows, {original['physical_clean_conditions']} physical clean conditions, "
                  f"{original['physical_clean_executions']} actual clean attempts and {original['exact_clean_aliases']} exact aliases across three development seeds. "
                  f"Completed selected-condition FT poison diagnostics: {diagnostic_count}/3. No final-test inference or GPU dispatch occurred."), '',
             '## Selected clean settings and acquisition gates', '',
             '| Learner | Settings | Feasible candidates | Mean E1 FTP | Mean E1 SSH | Mean E2 Hulk | Selected mean four-stage macro-F1 |', '|---|---|---:|---:|---:|---:|---:|']
    for learner, detail in selection['learners'].items():
        selected = detail['selected']
        feasible_count = sum(c['feasible'] for c in detail['candidates'])
        if selected is None:
            lines.append(f'| {learner} | None | {feasible_count}/{len(detail["candidates"])} | — | — | — | — |')
        else:
            cfg = selected['settings_without_seed']
            text = f"LR={cfg['learning_rate']}"+ (f", lambda_E={cfg['lambda_E']}" if learner == 'EI' else f", lambda_z={cfg['lambda_z']}, lambda_y={cfg['lambda_y']}" if learner == 'DR' else '')
            recalls = [c['mean_recall'] for c in selected['gates']['cells']]
            lines.append(f"| {learner} | {text} | {feasible_count}/{len(detail['candidates'])} | "+' | '.join(f'{v:.4f}' for v in recalls)+f" | {selected['score']:.4f} |")
    lines.extend(['', ('All per-seed counts, failed/infeasible settings and stage outcomes remain in the indexed evidence. Mean gates were not changed into per-seed exclusions. '
                  'Exact score ties use the documented infrastructure-cost disposition and then the original numeric order.'), '',
                  '## Controlled corruption diagnostic', ''])
    for diagnostic in diagnostics:
        if diagnostic['status'] != 'valid':
            lines.append(f"Seed{diagnostic['seed']}: unavailable ({diagnostic['status']}).")
            continue
        points = ', '.join(f"E{r['stage']}: {r['difference']:+.4f}" for r in diagnostic['partitions'])
        lines.append(f"- Seed{diagnostic['seed']}, poisoned-minus-clean Hulk-to-benign error: {points}.")
    if count_audit['paired_FT_diagnostics']:
        lines.extend(['', '| Seed | Persistent excess Hulk-to-benign H | E2 source-recall change |', '|---|---:|---:|'])
        for point in count_audit['paired_FT_diagnostics']:
            lines.append(f"| {point['seed']} | {point['H']['value']:+.4f} | {point['source_recall_change_E2']['value']:+.4f} |")
    lines.extend(['', ('These are paired maximum-dose development diagnostics, not final security estimates or a trigger-conditioned backdoor test. Weak/negative effects are retained. '
                  'The full poisoned EI/DR/filter grid has not been executed.'), '', '## Matched clean controls', '',
                  '| Arm | E1 macro-F1 | E2 | E3 | E4 | E4 benign FAR |', '|---|---:|---:|---:|---:|---:|'])
    for arm, values in reports['controls']['stage_macro_f1'].items():
        lines.append('| '+arm+' | '+' | '.join(f'{v:.4f}' for v in values)+f" | {100*reports['controls']['stage_benign_far'][arm][-1]:.2f}% |")
    lines.extend(['', 'One paired engineering seed101; settings source: '+reports['controls']['settings_source']+'. All adverse outcomes remain valid. '
                  'Matched current counts, aggregation weights and named-stream positions do not imply identical retained IDs or later learned models.', '',
                  '## CPU worker costs', '', '| Learner | Process total s | Training loop s | Eval s | Peak process MiB | Batch1 median ms | Batch256 median ms | Local bundle MiB |',
                  '|---|---:|---:|---:|---:|---:|---:|---:|'])
    for job in reports['profiling']['jobs']:
        profile = profiles[job['learner']]
        memory = profile['peak_after_all_probes']
        peak = f"{memory['peak_working_set_bytes']/1024**2:.1f}" if memory['status'] == 'measured' else 'unavailable'
        latency = profile['inference_latency']
        lines.append(f"| {job['learner']} | {job['process_end_to_end_seconds']:.2f} | {profile['training_loop_seconds']:.2f} | {profile['evaluation_seconds']:.2f} | {peak} | "
                     f"{1000*latency[0]['median_seconds']:.4f} | {1000*latency[1]['median_seconds']:.4f} | {profile['local_bundle_bytes']/1024**2:.2f} |")
    lines.extend(['', ('Fresh CPU processes include imports, validation, training/checkpointing, independent development evaluation, state verification, latency/serialization probes and local export. '
                  'Process peaks include native-library allocations and verification. These are measured local worker jobs, not GPU forecasts; dependency installation and remote transfers are unmeasured. '
                  'Communication tables distinguish raw parameters and concrete model-template serialization from actual network transport, which the sequential simulator does not implement.'), '',
                  '## Verification and disposition', '',
                  (f"Passed {reports['methods']['tests_run']} v3 test groups, {reports['poison_methods']['tests_run']} extended-poison groups, "
                  f"{len(reports['integration']['checks'])} full-data compatibility checks, {len(reports['controls']['checks'])} full-data matched-control checks, "
                  f"and {len(reports['recovery']['checks'])} fresh-process recovery/prediction checks. The separate fixed29 analysis implementation passed {analysis['tests_run']} synthetic fixtures; it read no final endpoint."), '',
                  (f"Infrastructure timing remeasurements: {len(selection['remeasurements'])}. Original wall-clock records remain immutable. "
                  'Exact replay state/ledger checks qualify replacement logical costs; the derived selector records whether any exact-score tie changed. '
                  'Profiling repetitions, recovered suffixes and cached aliases add no independent research replicate.'), '',
                  (f"An independent count-only audit reconstructed endpoints for {count_audit['valid_logical_rows_audited']} valid logical development rows "
                   'and the three matched engineering controls, retaining registered rare prediction columns and the fixed full-seen FAR bank. '
                   'Eight deliberately corrupted count artifacts were rejected. This checks count arithmetic and lineage; it does not repeat model inference.'), '',
                  ('V1/v2 source/evidence and the E1 diagnostic remain preserved. The original v2 clean failure and all v3 outcomes are part of development history. '
                  +('The revised budget meets all clean development gates. ' if feasible else 'The revised budget still fails at least one clean development gate. ')
                  +'These results do not establish a poisoning defense, novel attack-technique acquisition, deployment validity or publication acceptance.'), '',
                  ('Remaining gates: '+ '; '.join(completion['remaining_gates'])+'. Instructor feedback is still unavailable. '
                  'All registered rare outputs stay active, binary/full-seen and eligible multiclass banks remain separate, and the fixed cross-period benign union is not a deployment prevalence forecast.'), '',
                  ('[Commands](README.md), [decisions](decisions-2026-10-24.md), [amendments](defects-and-amendments.md), '
                  '[timing disposition](cost-amendment-2026-10-24.md), [requirements map](requirements-to-evidence.json) and '
                  '[evidence index](evidence/artifact-index.json).')])
    (docs/'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(completion)


if __name__ == '__main__':
    main()
