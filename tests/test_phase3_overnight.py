"""Training parity and paired oracle-state acceptance tests."""
import sys
from pathlib import Path
import numpy as np
import pytest
import torch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import run_phase3_overnight as O
from src.phase3_v2.train import Simulator
from src.phase3_v2.global_filter import choose_global_low_loss

def test_reference_training_parity_and_exact_label_repair(tmp_path,monkeypatch):
    torch.set_num_threads(1)
    generator=np.random.default_rng(55);data=[];poison=[]
    groups=((0,7,12),(0,3,4,5,6,8),(0,9,10,13,14,15),(0,1,2,11))
    for stage,codes in enumerate(groups,1):
        y=np.tile(np.repeat(codes,12),5).astype('<i8')
        ids=np.arange(len(y),dtype='<u8')+stage*10000
        owner=np.repeat(np.arange(5,dtype='i1'),len(codes)*12)
        if stage==2:
            ix=np.flatnonzero((y==4)&(owner==0))[:6];poison=ids[ix];y[ix]=0
        data.append(O.StageInput(stage,generator.normal(size=(len(y),74)).astype('<f4'),y,ids,owner))
    def fake_evaluate(model,slots,stage):
        return dict(stage=stage,model_sha256=O.model_identity(model,slots))
    monkeypatch.setattr(O,'evaluate',fake_evaluate)
    for learner,admission in (('FT','NONE'),('EI','NONE'),('DR','NONE'),('DR','DC')):
        settings=O.Settings(learner=learner,admission=admission,rounds=1,dose=(1,2))
        reference=Simulator(settings,lambda stage:data[stage-1],{}).execute(tmp_path/f'reference-{learner}-{admission}')
        folder=tmp_path/f'new-{learner}-{admission}';folder.mkdir()
        actual=O.train_suffix(None,[O.L.client_state(settings,i) for i in range(5)],[],data,settings,1,folder,poison)
        assert actual[0][-1]['model_sha256']==reference['final_model_sha256']
        if learner=='DR':
            assert actual[3]['changed_labels']>0
            assert actual[3]['nonlabel_state_unchanged']
            assert [r['stage'] for r in actual[3]['stages']]==[3,4]

def test_zero_repair_keeps_every_state_field_identical():
    s=O.Settings();model=O.ReferenceMLP(3,101)
    clients=[O.L.client_state(s,i) for i in range(5)]
    from copy import deepcopy
    clone=deepcopy(clients)
    assert O.state_hash(model,clients,[0,7,12])==O.state_hash(model,clone,[0,7,12])

def test_eviction_checkpoint_roundtrip_preserves_policy_and_insertion_order(tmp_path):
    from src.phase3_v2.checkpoint import read_transaction, unpack

    generator=np.random.default_rng(812)
    groups=((0,7,12),(0,3,4,5,6,8),(0,9,10,13,14,15),(0,1,2,11))
    data={}
    for stage,codes in enumerate(groups,1):
        y=np.tile(np.repeat(codes,4),5).astype('<i8')
        ids=np.arange(len(y),dtype='<u8')+stage*10000
        owner=np.repeat(np.arange(5,dtype='i1'),len(codes)*4)
        data[stage]=O.StageInput(stage,generator.normal(size=(len(y),74)).astype('<f4'),y,ids,owner)

    for policy in ('fifo','class_balanced'):
        settings=O.Settings(learner='DR',admission='DC',rounds=1,dose=(0,1),block='eviction',eviction_policy=policy)
        folder=tmp_path/policy
        result=Simulator(settings,data.__getitem__,{'fixture':'eviction-checkpoint'}).execute(folder,stop_after_commits=1)
        assert result['status']=='stopped_at_committed_boundary'
        meta,arrays,_=read_transaction(folder/'E1-R1.npz',{'fixture':'eviction-checkpoint'})
        _model,clients,_restored=unpack(meta,arrays,settings,data.__getitem__)
        for client in clients:
            memory=client.replay
            assert memory['policy']==policy
            assert memory['next_order']==memory['seen']
            assert np.array_equal(memory['order'][:memory['size']],np.arange(memory['size'],dtype='<u8'))
        assert clients[0].replay['size']>1
        corrupted={key:value.copy() for key,value in arrays.items()}
        corrupted['client0.replay.order'][1]=corrupted['client0.replay.order'][0]
        with pytest.raises(ValueError,match='Insertion order differs'):
            unpack(meta,corrupted,settings,data.__getitem__)

def test_DG_global_filter_uses_phase2_rounding_and_breaks_ties_by_id():
    from src.phase3_v2.learning import choose_admission as core_choose
    from src.phase3_v2.protocol import Settings as CoreSettings

    ids=np.arange(100,110,dtype='<u8')
    y=np.asarray([0,7,7,7,0,0,0,7,7,0],dtype='<i8')
    owner=np.asarray([0]*7+[1]*3,dtype='i1')
    x=np.zeros((10,74),dtype='<f4')
    data=O.StageInput(1,x,y,ids,owner)
    settings=O.Settings(learner='DR',admission='DG',rounds=1,dose=(0,1),block='core')
    assert settings.validate().admission=='DG'
    scores=np.asarray([.5]*10,dtype='<f4')
    accepted,rows=choose_global_low_loss(data,scores)
    assert [data.ids[ix].tolist() for ix in accepted]==[[100,101,102,103,104,105,106],[107,108,109],[],[],[]]
    assert [row['admitted'] for row in rows]==[7,3,0,0,0]
    assert all(row['filter_policy']=='bypass_e1' and row['keep_fraction']==[1,1] for row in rows)

    data=O.StageInput(2,x,y,ids,owner)
    accepted,rows=choose_global_low_loss(data,scores)
    # For n=7 and n=3, Phase 2's floor(0.75*n + 0.5) gives 5 and 2;
    # ceil(0.75*n) would incorrectly give 6 and 3.
    assert [data.ids[ix].tolist() for ix in accepted]==[[100,101,102,103,104],[107,108],[],[],[]]
    assert [row['admitted'] for row in rows]==[5,2,0,0,0]
    assert all(row['filter_policy']=='global_low_loss' and row['keep_fraction']==[3,4] for row in rows)
    assert rows[0]['class_counts']==[
        {'source_code':0,'raw':4,'admitted':2},
        {'source_code':7,'raw':3,'admitted':3},
    ]
    assert CoreSettings(learner='DR',admission='DG').validate().admission=='DG'
    generic,generic_rows=core_choose(data,scores,{0,7},CoreSettings(learner='DR',admission='DG'))
    runner,runner_rows=O.choose(data,scores,{0,7},settings)
    assert [data.ids[ix].tolist() for ix in generic]==[data.ids[ix].tolist() for ix in accepted]
    assert [data.ids[ix].tolist() for ix in runner]==[data.ids[ix].tolist() for ix in accepted]
    assert generic_rows==runner_rows==rows

def test_DG_admission_executes_through_full_synthetic_simulator(tmp_path):
    from src.phase3_v2.protocol import Settings as CoreSettings

    torch.set_num_threads(1)
    x=np.zeros((8,74),dtype='<f4')
    y=np.asarray([0,7,7,7,0,0,0,7],dtype='<i8')
    owner=np.repeat(np.arange(2,dtype='i1'),4)
    stages={}
    for stage in range(1,5):
        ids=np.arange(stage*10000,stage*10000+8,dtype='<u8')
        stages[stage]=O.StageInput(stage,x.copy(),y.copy(),ids,owner.copy())
    settings=CoreSettings(learner='DR',admission='DG',rounds=1,epochs=3)
    settings.validate()
    result=Simulator(settings,stages.__getitem__,{'fixture':'dg-synthetic'}).execute(tmp_path/'dg')
    admissions=[entry for entry in result['ledger'] if entry['kind']=='admission']
    assert result['status']=='complete' and len(admissions)==4
    assert all(row['filter_policy']==('bypass_e1' if entry['stage']==1 else 'global_low_loss')
               for entry in admissions for row in entry['clients'])
    assert [row['admitted'] for row in admissions[0]['clients']]==[4,4,0,0,0]
    assert all([row['admitted'] for row in entry['clients']]==[3,3,0,0,0] for entry in admissions[1:])
    recovered=Simulator(settings,stages.__getitem__,{'fixture':'dg-synthetic'}).execute(
        tmp_path/'dg-recovered',resume=tmp_path/'dg'/'E1-R1.npz')
    assert recovered['final_model_sha256']==result['final_model_sha256']
    assert recovered['ledger']==result['ledger']
