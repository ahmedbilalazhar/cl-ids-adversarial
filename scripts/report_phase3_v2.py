"""Build traceable delivery inventories from executed CPU evidence, without inference."""
from __future__ import annotations

import itertools
import statistics
from pathlib import Path

import numpy as np

from src.phase3.common import ROOT, array_identity, digest, read_json, write_json
from src.phase3_v2.checkpoint import read_transaction
from src.phase3_v2.prepare import corrupt
from src.phase3_v2.protocol import code_files, code_identity


def main():
    base = ROOT/'results/phase3-cpu-v2'
    docs = ROOT/'docs/phase3-cpu-v2'
    integrity = read_json(base/'integrity/audit.json')
    acceptance = read_json(base/'acceptance.json')
    integration = read_json(base/'integration/acceptance.json')
    development = read_json(base/'development/completion.json')
    selection = read_json(base/'development/tuning-selection.json')
    diagnostics = read_json(base/'learning-diagnostics.json')
    ei_recovery = read_json(base/'full-data-EI-recovery.json')
    dr_recovery = read_json(base/'full-data-DR-recovery.json')
    assembly = read_json(base/'recovery-assembly-acceptance.json')
    if ei_recovery['status'] != 'passed' or dr_recovery['status'] != 'passed':
        raise ValueError('Full-data fresh-process recovery did not pass')
    if assembly['status'] != 'passed':
        raise ValueError('Recovered trajectory collection verification did not pass')
    source = code_files()
    for report in (acceptance, integration):
        if report['code_identity'] != code_identity() or report['status'] != 'passed':
            raise ValueError('Current accepted code identity required')
    originals = read_json(base/'integrity/original-inputs.json')
    preserved = {name: digest(ROOT/name) == expected for name, expected in originals.items()}
    if not all(preserved.values()):
        raise ValueError('An original input changed')
    write_json(base/'preservation.json', {'status': 'passed', 'files': preserved, 'v1_code_identity': integrity['v1_code_identity']})
    write_json(base/'source-code-manifest.json', {'code_identity': code_identity(), 'files': source,
               'delivery_scripts': {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted((ROOT/'scripts').glob('*phase3_v2*.py'))},
               'scope': 'Current uncommitted source; no claim these files are present in Git HEAD'})
    corruption = []
    for seed in (101, 102, 103):
        path = ROOT/f'data/processed/phase3-cpu-v2/s{seed}-p000/train/E2'
        y, ids, owner = [np.load(path/f'{k}.npy', allow_pickle=False) for k in ('y', 'ids', 'owner')]
        original = y.copy()
        prefixes, attacked = [], []
        for dose in ((0, 1), (1, 10), (3, 10), (1, 2)):
            supplied, audit = corrupt(y, ids, owner, seed, 2, dose)
            changed = np.flatnonzero(supplied != y)
            prefixes.append(set(map(int, ids[changed])))
            attacked.append(audit['attacked_client'])
            source_count = int(np.count_nonzero((y == 4) & (owner == audit['attacked_client'])))
            num, den = dose
            # Independent integer expected count and clean-reference conservation.
            expected = (source_count*num)//den
            assert len(changed) == expected and np.array_equal(y, original)
            assert np.all((y[changed] == 4) & (supplied[changed] == 0) & (owner[changed] == audit['attacked_client']))
            corruption.append({'seed': seed, 'dose': list(dose), 'eligible_clients': audit['eligible_clients'],
                               'attacked_client': audit['attacked_client'], 'eligible_hulk': source_count,
                               'flipped': len(changed), 'prefix_ids_sha256': array_identity(ids[changed]),
                               'features': 'Identical pinned per-stage x files; corruption accepts no feature argument',
                               'clean_reference_unchanged': True})
        assert len(set(attacked)) == 1 and all(a <= b for a, b in itertools.pairwise(prefixes))
    write_json(base/'corruption-full-inventory.json', {'status': 'passed', 'records': corruption,
               'scope': 'Builder-only full selected E2 inventory at all development seeds/doses; no poisoned model-selection outcomes'})
    matched_streams = []
    for stage in range(1, 5):
        for round_id in range(1, 4):
            states = {arm: read_transaction(base/f'integration/{arm}/E{stage}-R{round_id}.npz')[:2] for arm in ('DC', 'DM', 'DQ')}
            for arm in ('DM', 'DQ'):
                for client in range(5):
                    a, aa = states['DC']
                    b, ab = states[arm]
                    fields = ('draw', 'insert', 'size', 'seen')
                    equal = all(a['clients'][client]['replay'][field] == b['clients'][client]['replay'][field] for field in fields)
                    equal = equal and np.array_equal(aa[f'client{client}.dropout'], ab[f'client{client}.dropout'])
                    assert equal, 'Matched-control named streams diverged'
                    matched_streams.append({'stage': stage, 'round': round_id, 'client': client, 'comparison': 'DC/'+arm,
                                            'replay_draw_insertion_counters_and_dropout_exact': equal})
    write_json(base/'matched-control-streams.json', {'status': 'passed', 'checks': matched_streams,
               'scope': 'Same-seed clean matched counts imply aligned stream positions, not identical retained IDs or learned models'})
    mapping = [
        ('Data identity and isolation', 'data.py; prepare.py', 'test_data_isolation_and_readonly; test_package_rejects_extras_missing_and_corruption', 'integrity/audit.json; preservation.json; data/processed/phase3-cpu-v2/*/preparation.json'),
        ('Registry and head expansion', 'train.py; unchanged ../phase3/model.py', 'test_head_initialization_independent_uniform_and_expansion; test_supplied_only_registration', 'acceptance.json; integration/acceptance.json'),
        ('Immutable broadcasts, Adam reset, inactive clients and FedAvg', 'learning.py', 'test_broadcast_and_optimizer_reset; test_inactive_client_never_updates_or_draws; test_independent_aggregation_arithmetic', 'acceptance.json; development/executions/*/train/run.json'),
        ('Matched quotas, ties, stage lock and full-pool permutation', 'learning.py', 'test_quota_rounding_ties_and_matched_controls; test_full_pool_order_then_subsequence; test_filters_off_e1_and_frozen_once', 'acceptance.json; integration/acceptance.json'),
        ('DR teacher timing, modes, means and masked widths', 'learning.py', 'test_teacher_timing_modes_and_insertion_after_update; test_teacher_values_are_pre_update; test_dark_mask_before_square_and_per_record_normalization', 'acceptance.json; integration/acceptance.json'),
        ('Algorithm R first pass and independent streams', 'learning.py; unchanged ../phase3/reference.py::insert_batch', 'test_reservoir_sequential_independent_algorithm_r; test_first_pass_only_across_epochs_and_rounds', 'acceptance.json; integration/acceptance.json'),
        ('EI per-example gradient arithmetic, anchor and stage commit', 'learning.py; checkpoint.py', 'test_ei_analytic_gradients_not_square_of_mean; test_ei_vectorized_independent_reference_tolerance; test_ei_stage_anchor_fixed_and_inactive_commit; test_ei_exact_sample_limit', 'acceptance.json; development/executions/*EI*/train/*.npz'),
        ('Corruption scope, nested rational doses, immutable reference', 'prepare.py; exposure.py', 'test_corruption_integer_nested_scope_reference_immutable; test_unfiltered_pairing_buffer_and_importance_ids_across_doses', 'acceptance.json; corruption-full-inventory.json; integration/*-exposure.json'),
        ('Strict complete transactions and exact recovery', 'checkpoint.py; train.py; ../../scripts/assemble_phase3_v2_recovery.py', 'test_exact_recovered_continuation_all_methods; test_checkpoint_incompatible_incomplete_and_corrupt_rejected; test_rng_lossless_cached_uint32_and_large_state', 'acceptance.json; integration/acceptance.json; full-data-DR-recovery.json; full-data-EI-recovery.json; recovery-assembly-acceptance.json'),
        ('Independent evaluator, rare outputs, banks and missingness', 'evaluate.py', 'test_evaluator_full_head_banks_denominators_missingness; test_evaluator_zero_prediction_precision_na_f1_zero; test_full_head_argmax_keeps_rare_outputs_and_benign_ties', 'acceptance.json; integration/*-evaluation/metrics.json; development/executions/*/evaluation/metrics.json'),
        ('Prospective selection, exact ties, all-seed acquisition gates', 'development.py; protocol.py', 'test_development_grid_and_exact_budget_ties; test_development_gates_are_per_family_and_require_three_seeds', 'development/procedure-lock.json; development/synchronization-selection.json; development/tuning-selection.json; development/completion.json'),
        ('Final-test and GPU seals; unchanged final analysis family', 'protocol.py; evaluate.py; configs/phase3/cpu-v2.json', 'test_final_seed_and_invalid_runtime_settings_sealed', 'development/completion.json; configs/phase3/cpu-v2.json'),
    ]
    write_json(docs/'requirements-to-evidence.json', {'schema': 'phase3-requirements-v2', 'code_identity': code_identity(),
               'rows': [{'requirement': r, 'code_under_src_phase3_v2': c, 'tests_in_tests_test_phase3_v2': t,
                         'evidence_under_results_phase3_cpu_v2_unless_qualified': e} for r, c, t, e in mapping]})
    physical = [r for r in development['rows'] if r['physical_execution']]
    valid = [r for r in physical if r['status'] == 'valid']
    profiles, metric_inventory = [], []
    for learner in ('FT', 'EI', 'DR'):
        runs = [read_json(Path(r['run'])/'run.json') for r in valid if r['settings']['learner'] == learner]
        if runs:
            profiles.append({'learner': learner, 'physical_clean_executions': len(runs),
                             'training_loop_seconds_min': min(r['elapsed_seconds'] for r in runs),
                             'training_loop_seconds_median': statistics.median(r['elapsed_seconds'] for r in runs),
                             'training_loop_seconds_max': max(r['elapsed_seconds'] for r in runs),
                             'training_seconds': sum(t.get('training_seconds', 0) for r in runs for t in r['timings']),
                             'admission_seconds': sum(t.get('admission_seconds', 0) for r in runs for t in r['timings']),
                             'importance_seconds': sum(t.get('importance_seconds', 0) for r in runs for t in r['timings']),
                             'checkpoint_seconds': sum(t.get('checkpoint_seconds', 0) for r in runs for t in r['timings']),
                             'evaluation_seconds': sum(read_json(Path(row['metrics']))['evaluation_seconds'] for row in valid if row['settings']['learner'] == learner)})
    for row in development['rows']:
        if row['status'] != 'valid':
            continue
        metric = read_json(Path(row['metrics']))
        metric_inventory.append({'row_id': row['row_id'], 'alias_of': row['alias_of'], 'settings': row['settings'],
                                 'macro_f1_by_stage': [s['eligible_macro_f1'] for s in metric['stages']],
                                 'benign_far_by_stage': [s['binary_full_seen']['benign_far'] for s in metric['stages']],
                                 'eligible_recall_by_stage': [{str(c['code']): c['recall'] for c in s['eligible_classes']} for s in metric['stages']],
                                 'A': metric['A'], 'metrics_sha256': digest(Path(row['metrics']))})
    write_json(base/'development-summary.json', {'status': development['status'], 'rows': metric_inventory})
    write_json(base/'cpu-profile.json', {'profiles': profiles, 'physical_clean_seconds': sum(r['logical_training_seconds'] for r in valid),
               'scope': 'Sequential, CPU single-thread complete clean trajectories, no GPU estimate; per-loop timings include scoring/importance/checkpoints and exclude setup/preparation/inference',
               'optimization_claim': 'No training-loop speed optimization or CPU/CUDA equivalence claimed; vectorized EI is checked against independent per-record arithmetic'})
    failures = {'schema': 'phase3-failure-inventory-v2', 'invalid_development_rows': development['invalid_rows'],
                'clean_infeasible_learners': [k for k, v in selection['learners'].items() if v['selected'] is None],
                'instructor_feedback': 'not supplied', 'superseded': ['Historical v1 admitted-pool-shuffle attempt',
                 'Failed tiny fixture acceptance attempt1; successful intermediate attempt2 replaced by final-code acceptance',
                 'Incomplete ownership export s101-p000-incomplete-attempt1; never used by a learner',
                 'First fresh-process DR verifier used raw NPZ ZIP bytes; preserved as full-data-DR-recovery-verifier-attempt1.json; exact typed state/ledger passed in corrected verifier'],
                'diagnostic_gate': 'Not run unless all selected unfiltered learners pass clean acquisition',
                'missing_final_seeds': [1,2,3,4,5,6,7,8,9,10,11,42],
                'final_predictions': 'sealed and unexecuted', 'GPU_runtime': 'not pinned or confirmed',
                'untested_paths': ['CUDA and cross-runtime numeric agreement', 'Real infrastructure crash injection and disk loss',
                                  'Optional FIFO/NoZ/NoY/oracle interventions', 'External datasets',
                                  'Full-data poisoned DR/EI/filtered training; corruption acceptance uses tiny learner fixtures and full builder counts',
                                  'Final 12-seed grid and single 29-contrast statistical release'],
                'unmeasured_cost_gates': ['Pinned GPU complete jobs and cold setup', 'Batch-1/256 inference latency, process peak memory and serialized communication accounting'],
                'missing_metrics_policy': 'No favorable imputation, no retry counted as a replicate'}
    write_json(base/'failure-inventory.json', failures)
    completion = {'status': 'cpu_milestone_implemented_and_verified', 'code_identity': code_identity(),
                  'integrity_checks': len(integrity['checks']), 'preserved_v1_acceptance_checks': 174,
                  'focused_tests': acceptance['tests_run'], 'full_data_integration_checks': len(integration['checks']),
                  'full_data_EI_recovered_checkpoints': len(ei_recovery['checks']),
                  'full_data_DR_fresh_process_recovered_checkpoints': len(dr_recovery['checks']),
                  'recovery_collection_checks': len(assembly['checks']),
                  'logical_clean_pilot_and_tuning': len(development['rows']), 'physical_clean_executions': len(physical),
                  'exact_aliases': development['exact_clean_aliases'], 'independent_development_seeds': 3,
                  'development_status': development['status'], 'final_test_accessed': False, 'gpu_grid_dispatchable': False,
                  'remaining_gates': development['remaining_gates']}
    write_json(base/'completion.json', completion)
    # Small review evidence only. Checkpoints and feature arrays stay in their
    # immutable local run directories, referenced by hashed manifests.
    review = docs/'evidence'
    review.mkdir(exist_ok=False)
    import shutil
    for path in [base/'completion.json', base/'acceptance.json', base/'source-code-manifest.json', base/'preservation.json',
                 base/'corruption-full-inventory.json', base/'cpu-profile.json', base/'failure-inventory.json',
                 base/'development-summary.json', base/'development/synchronization-selection.json',
                 base/'development/tuning-selection.json', base/'development/procedure-lock.json',
                 base/'learning-diagnostics.json', base/'full-data-EI-recovery.json', base/'preparation-rebuild.json',
                 base/'full-data-DR-recovery.json',
                 base/'recovery-assembly-acceptance.json',
                 base/'matched-control-streams.json',
                 base/'integration/acceptance.json']:
        target = review/('integration-acceptance.json' if path == base/'integration/acceptance.json' else path.name)
        shutil.copyfile(path, target)
    write_json(review/'artifact-index.json', {'files': {p.name: digest(p) for p in sorted(review.glob('*.json'))}})
    lines = ['# Executed CPU milestone report — 24 October 2026', '',
             (f"Implemented v2 and passed {acceptance['tests_run']} focused tests, {len(integration['checks'])} full-data integration checks, "
             f"{len(integrity['checks'])} v1 integrity checks and all 174 preserved v1 bounded checks."), '',
             (f"Development: {development['status']}. Common budget: {development['selected_budget']}. "
             f"{len(development['rows'])} logical clean rows, {len(physical)} physical clean executions, "
             f"{development['exact_clean_aliases']} exact aliases; three independent development seeds. "
             f"Poisoned FT diagnostic rows completed: {development['logical_diagnostic_rows_completed']}/3."), '',
             ('Final-test inference and the GPU grid remain sealed. The twelve final seeds and one 29-contrast family are unchanged. '
             'These are development outcomes and bounded software evidence, not publication or efficacy certification.'), '',
             '## Clean tuning acquisition gates', '',
             '| Learner | Feasible configurations | Selected |', '|---|---:|---|']
    for learner, details in selection['learners'].items():
        feasible = sum(c['feasible'] for c in details['candidates'])
        selected = details['selected']
        lines.append(f"| {learner} | {feasible}/{len(details['candidates'])} | {'None: clean gate failed' if selected is None else str(selected['settings_without_seed'])} |")
    lines.extend(['', ('Every candidate and its three per-family gate cells are retained in '
                  '[tuning-selection.json](evidence/tuning-selection.json). Scores, confusion tables, exposure counts and losses '
                  'remain available for poor candidates. No candidate is silently promoted when all gates fail.'), '',
                  '## Untuned filtered controls', '',
                  '| Arm | E1 macro-F1 | E2 | E3 | E4 | E4 benign FAR |', '|---|---:|---:|---:|---:|---:|'])
    for arm, values in integration['stage_macro_f1'].items():
        lines.append('| '+arm+' | '+' | '.join(f'{v:.4f}' for v in values)+f" | {100*integration['stage_benign_far'][arm][-1]:.2f}% |")
    lines.extend(['', ('These are one-seed default-setting control checks, not separately tuned arms or independent replicates. '
                  'All registered rare logits remain active. The DC model/replay/dropout/admission state matched v1 at all 12 '
                  'checkpoints; its independent evaluator reproduced every v1 confusion count. All 10 in-process recovered suffix payloads matched exactly.'), '',
                  (f"Fresh-process DR and EI recovery each reproduced all ten strict metadata records, typed states and the full ledger exactly. "
                   f"Complete recovered collections passed {len(assembly['checks'])} additional checks, including identical "
                   'development prediction arrays and counts at all four stages and rejection of mismatched lineage/manifest. '
                   'Collections preserve prefix/suffix lineage and add no independent replicate. '
                   'See [recovery evidence](evidence/recovery-assembly-acceptance.json).'), '',
                  '## Measured CPU work', '',
                  '| Learner | Physical clean jobs | Loop median seconds | Min–max seconds |', '|---|---:|---:|---:|'])
    for profile in profiles:
        lines.append(f"| {profile['learner']} | {profile['physical_clean_executions']} | {profile['training_loop_seconds_median']:.2f} | "
                     f"{profile['training_loop_seconds_min']:.2f}–{profile['training_loop_seconds_max']:.2f} |")
    lines.extend(['', ('Component timings are in [cpu-profile.json](evidence/cpu-profile.json). These are measured CPU workloads, '
                  'not GPU-hour forecasts. No training-loop optimization has been promoted on timing alone.'), '',
                  '## Interpretation and remaining gates', '',
                  ('Observed weak learning is not a demonstrated cause. The immutable training inventory is highly skewed, '
                  'and the development bank has a different benign prevalence. Controlled learning-rate/synchronization/retention '
                  'comparisons are preserved in the full grid. Inspect actual confusion sources, stage losses and acquisition/retention '
                  'curves before proposing an objective or sampling amendment. No split, calibration, taxonomy, benign inventory, '
                  'eligibility or bank was altered to improve scores.'), '',
                  ('No CUDA/runtime agreement, optional ablation/intervention acceptance, final-test predictions or final statistical '
                  'analysis has been exercised. Clean infeasibility requires a prospective scientific revision before final testing. '
                  'The failure and completion inventories identify missing paths without imputing metrics.'), '',
                  ('Requirements map: [requirements-to-evidence.json](requirements-to-evidence.json). '
                  'Commands and identity boundaries: [README](README.md). '
                  'Corrections and amendments: [log](defects-and-amendments.md).')])
    lines.extend(['', '## E1 training/development diagnostic patterns', '',
                  ('These counts summarize physical development executions across settings and schedules; they are not independent research replicates. '
                  'A high-training/low-development cell uses recall >=0.50 on training and <0.50 on development. '
                  'Both-low uses recall <0.50 in both banks. These are descriptive diagnostics, not new selection gates.'), '',
                  '| Learner | Annotation | Physical checks | High train / low dev | Both low |', '|---|---|---:|---:|---:|'])
    for learner in ('FT', 'EI', 'DR'):
        for code, label in ((7, 'FTP-Patator'), (12, 'SSH-Patator')):
            cells = [c for row in diagnostics['physical_rows'] if row['settings']['learner'] == learner for c in row['E1_anchor_comparison'] if c['source_code'] == code]
            gap = sum(c['training_recall'] >= .5 and c['development_recall'] < .5 for c in cells)
            weak = sum(c['training_recall'] < .5 and c['development_recall'] < .5 for c in cells)
            lines.append(f'| {learner} | {label} | {len(cells)} | {gap} | {weak} |')
    ssh_cells = [c for row in diagnostics['physical_rows'] for c in row['E1_anchor_comparison'] if c['source_code'] == 12]
    train_ssh = diagnostics['training_inventory'][0]['source_counts'][12]
    dev_ssh = diagnostics['fixed_development_inventory'][12]
    lines.extend(['', ('Complete training confusion counts, held-out error destinations, round loss/exposure curves, '
                  'fixed class counts and paired learning-rate comparisons are in [learning-diagnostics.json](evidence/learning-diagnostics.json). '
                  'These observations can locate acquisition/generalization gaps; they do not by themselves identify why those gaps occur.'), '',
                  (f"The fixed E1 banks contain {train_ssh:,} SSH training records and {dev_ssh:,} SSH development records. "
                   f"All {len(ssh_cells)} physical E1 checks had SSH recall below 0.50 on both banks. "
                   'This documents weak acquisition in the fitted training population as well as the held-out bank; it does not establish a mechanism.')])
    (docs/'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(completion)


if __name__ == '__main__':
    main()
