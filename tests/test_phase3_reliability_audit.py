"""Adversarial evidence checks independent of the study implementation."""
import importlib.util
from pathlib import Path
from fractions import Fraction

import numpy as np
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/audit_phase3_reliability.py'
spec = importlib.util.spec_from_file_location('reliability_audit', SCRIPT)
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


def test_excluded_prediction_column_is_still_an_error():
    matrix = np.zeros((16, 16), dtype=np.int64)
    matrix[0, 0] = 8; matrix[0, 15] = 2
    matrix[4, 4] = 5; matrix[4, 0] = 5
    matrix[15, 4] = 100  # excluded true rows must not contaminate precision
    result = A.score(matrix, [0, 4])
    assert result['classes'][4]['f1'] == Fraction(2, 3)
    assert result['benign_far'] == Fraction(1, 5)
    assert result['accuracy'] == Fraction(13, 20)


def test_missing_fixed_support_fails_instead_of_changing_macro_population():
    matrix = np.zeros((16,16), dtype=np.int64); matrix[0,0] = 5
    with pytest.raises(ValueError, match='Missing fixed eligible'):
        A.score(matrix,[0,4])


def test_exact_ties_zeros_and_effect_convention():
    assert A.signed_rank([0]*12)['rank_biserial'] == 0
    assert A.signed_rank([0]*12)['p'] == 1
    result=A.signed_rank([Fraction(1,3),-Fraction(1,3),0])
    assert result['p']==1 and result['tied_groups']==1 and result['nonzero']==2
    assert A.signed_rank([1]*12)['p'] == 2/4096
    assert A.holm([.01,.04,.02]) == [.03,.04,.04]


def test_byte_deduplication_rejects_conflicting_experiments(tmp_path,monkeypatch):
    monkeypatch.setattr(A,'ROOT',tmp_path)
    row={'study_identity':'frozen','settings':{'seed':1},'value':1}
    for folder in ['one','two']:
        A.write_json(tmp_path/folder/'result.json',row)
    records,entries,conflicts=A.catalog([tmp_path])
    assert len(records)==1 and len(entries)==2 and not conflicts
    row['value']=2;A.write_json(tmp_path/'two/result.json',row)
    assert len(A.catalog([tmp_path])[2])==1


def test_runner_import_does_not_mutate_shared_learning_module():
    from src.phase3_v2 import learning
    before=learning.choose_admission
    import importlib
    import scripts.run_phase3_overnight as runner
    importlib.reload(runner)
    assert learning.choose_admission is before


def test_runner_lock_excludes_duplicate_and_preserves_owner(tmp_path,monkeypatch):
    import scripts.run_phase3_overnight as runner
    monkeypatch.setattr(runner,'OUT',tmp_path)
    with runner.execution_lock():
        with pytest.raises(FileExistsError):
            with runner.execution_lock():
                raise AssertionError('Second owner entered')
        assert (tmp_path/'execution.lock').exists()
    assert not (tmp_path/'execution.lock').exists()


def test_source_drift_rejected_before_any_worker_output(tmp_path,monkeypatch):
    import scripts.run_phase3_overnight as runner
    monkeypatch.setattr(runner,'OUT',tmp_path);monkeypatch.setattr(runner,'ROOT',tmp_path)
    A.write_json(tmp_path/'identity.json',{'source':{'missing.py':'bad-hash'}})
    with pytest.raises(RuntimeError,match='Frozen source drift'):
        runner.validate_sources()
    assert not (tmp_path/'runs').exists()
