"""Synthetic mechanics only; no real session writes, approvals or skinning."""
import copy, sys, math
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import core
import tempfile
from unittest.mock import patch
results=[]
def check(name,test):
    assert test,name;results.append({'name':name,'pass':True})
def rejected(name,cmd,state):
    before=copy.deepcopy(state)
    try:core.command(state,cmd,'synthetic_test_only')
    except (ValueError,KeyError,StopIteration):check(name,state==before)
    else:raise AssertionError(name)
state=core.rebuild(core.fresh_state());base=copy.deepcopy(state)
rejected('movement_before_start',{'action':'move','positions':{'pelvis':[0,0,100]}},state)
state=core.command(state,{'action':'start'},'synthetic_test_only')
pelvis=next(r['position_cm'] for r in state['joints'] if r['role']=='pelvis')
edited=core.command(state,{'action':'move','positions':{'pelvis':core.add(pelvis,[0,1,2])}},'synthetic_test_only')
check('immutable_baseline',state['joints']==base['joints'])
check('pelvis_five_dependents',len([r for r in edited['joints'] if r.get('dependency_recomputation')])==5)
check('dependent_acceptance_invalidated',all(r['status']=='dependency_recomputed' for r in edited['joints'] if r.get('dependency_recomputation')))
check('rebuild_idempotent',core.rebuild(copy.deepcopy(edited))==core.rebuild(copy.deepcopy(edited)))
def row(s,n):return next(r for r in s['joints'] if r['role']==n)
point=core.add(row(state,'thigh_l')['position_cm'],[.1,0,0]);both={'pelvis':core.add(pelvis,[0,1,2]),'thigh_l':point}
a=core.command(state,{'action':'move','positions':both},'synthetic_test_only');b=core.command(state,{'action':'move','positions':dict(reversed(list(both.items())))},'synthetic_test_only')
check('order_independence',a['joints']==b['joints']);check('explicit_hip_overrides_pelvis',row(a,'thigh_l')['position_cm']==point)
approved=core.command(state,{'action':'review','roles':['spine_01'],'judgement':'accept','category':'synthetic fixture'},'synthetic_test_only')
changed=core.command(approved,{'action':'move','positions':{'pelvis':core.add(pelvis,[0,1,2])}},'synthetic_test_only')
check('stale_dependent_review_removed','spine_01' not in changed['approvals'])
for name,cmd in [('unknown_role',{'action':'move','positions':{'unknown':[1,2,3]}}),('nan',{'action':'move','positions':{'pelvis':[0,math.nan,1]}}),('boolean_xyz',{'action':'move','positions':{'pelvis':[0,True,1]}}),('ground_root_mutation',{'action':'move','positions':{'root':[0,0,1]}}),('zero_parent_segment',{'action':'move','positions':{'hand_l':row(state,'lowerarm_l')['position_cm']}}),('missing_judgement',{'action':'review','roles':['pelvis'],'category':'test'})]: rejected(name,cmd,state)
stale=copy.deepcopy(state);stale['baseline_sha256']='stale';rejected('stale_fit',{'action':'finish'},stale)
for side in ['l','r']:
    for digit,track in zip(core.DIGITS,state['tracks'][side]):
        state=core.command(state,{'action':'assign','side':side,'digit':digit,'track_id':track['candidate_id']},'synthetic_test_only')
check('ten_independent_digit_chains',len(state['fingers'])==10)
check('thirty_generated_phalanges',sum(len(f['phalanges_cm']) for f in state['fingers'].values())==30)
rejected('duplicate_track',{'action':'assign','side':'l','digit':'index','track_id':'digit_branch_1_l'},state)
finger=state['fingers']['thumb_l'];target=core.add(finger['root_cm'],[.2,0,.1]);moved=core.command(state,{'action':'move','positions':{'thumb_l:root':target}},'synthetic_test_only')
check('finger_root_updates_intermediates',moved['fingers']['thumb_l']['phalanges_cm']!=finger['phalanges_cm']);check('finger_tip_preserved',moved['fingers']['thumb_l']['tip_cm']==finger['tip_cm'])
check('synthetic_not_counted_as_human',core.metrics(moved)['recorded_user_commands']==0)
check('synthetic_no_downstream_authorisation',not moved['downstream_authorised'])
worldpos={};worldcols={};error=0
for r in moved['generated_joint_schema']:
    n=r['role'];parent=r['parent_role'];transform=moved['local_transforms'][n];cols=worldcols[parent] if parent else [[1,0,0],[0,1,0],[0,0,1]]
    apply=lambda v: [sum(cols[k][i]*v[k] for k in range(3)) for i in range(3)]
    p=core.add(worldpos[parent] if parent else [0,0,0],apply(transform['translation_cm']));worldpos[n]=p;worldcols[n]=[apply(c) for c in transform['rotation_matrix_columns']];error=max(error,core.norm(core.sub(p,r['position_cm'])))
check('53_joint_parent_transform_roundtrip',error<1e-9)
# Metrics regression fixtures use an isolated state and never export approvals.
fixture=copy.deepcopy(moved)
for event in fixture['events']:event['provenance']='human_editor_action'
fixture=core.command(fixture,{'action':'review','roles':['thumb_l'],'judgement':'accept','category':'isolated metrics fixture'})
check('moved_endpoint_is_not_unchanged_chain_review','thumb_l' not in core.metrics(fixture)['reviewed_without_movement'])
fixture=core.command(fixture,{'action':'review','roles':['neck_01'],'judgement':'accept','category':'isolated metrics fixture'})
check('unchanged_review_counted','neck_01' in core.metrics(fixture)['reviewed_without_movement'])
check('automatic_roles_counted',len(core.metrics(base)['automatically_accepted_roles'])==4)
finished=core.command(moved,{'action':'finish'},'synthetic_test_only')
rejected('finished_trial_rejects_edits',{'action':'move','positions':{'pelvis':pelvis}},finished)
resumed=core.command(finished,{'action':'start'},'synthetic_test_only')
check('resume_preserves_trial_origin',resumed['trial_started_at']==finished['trial_started_at'] and resumed['trial_finished_at'] is None)
with tempfile.TemporaryDirectory(prefix='mechanics_',dir=core.W) as directory:
    original_replace=Path.replace;attempts=[]
    def briefly_locked(path,target):
        attempts.append(1)
        if len(attempts)<3:raise PermissionError('synthetic short-lived Windows reader lock')
        return original_replace(path,target)
    destination=Path(directory)/'fixture.json'
    with patch.object(Path,'replace',briefly_locked):core.save(destination,{'fixture_only':True})
    check('atomic_publication_recovers_reader_lock',len(attempts)==3 and core.read(destination)=={'fixture_only':True})
core.save(core.O/'mechanics_validation.json',{'tests':results,'passed':True,'synthetic_only':True,'real_session_modified':False,'anatomical_accuracy_not_tested':True,'fixtures_do_not_prove_digit_identity':True})
print(len(results),'synthetic mechanics checks passed')
