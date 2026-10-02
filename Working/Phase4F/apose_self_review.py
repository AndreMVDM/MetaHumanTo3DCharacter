"""In-memory provenance and invalidation checks; never writes real human events."""
import sys
sys.dont_write_bytecode=True
import json, ast
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F';O=P/'Documentation/Phase4F'
sys.path.insert(0,str(W));import apose_review_core as core
results=[]
def check(name,ok):
    results.append({'name':name,'passed':bool(ok)})
    if not ok:raise AssertionError(name)
for ch in ['John','Jane']:
    core.configure(ch);original=core.read(core.W/'session.json');s=core.rebuild(core.fresh_state())
    check(ch+'_zero_real_actions',not original['events'] and not original['approvals'] and original['trial_started_at'] is None)
    s=core.command(s,{'action':'start'},provenance='agent_test')
    s=core.command(s,{'action':'review','roles':['pelvis'],'judgement':'accept','category':'synthetic_test'},provenance='agent_test')
    check(ch+'_synthetic_review_not_counted',core.metrics(s)['review_commands']==0 and not core.metrics(s)['currently_accepted_human_roles'])
    p=next(r['position_cm'] for r in s['joints'] if r['role']=='pelvis')
    s=core.command(s,{'action':'move','positions':{'pelvis':core.add(p,[.2,0,0])}},provenance='agent_test')
    check(ch+'_move_invalidates_review','pelvis' not in s['approvals'])
    for side in ['l','r']:
        check(ch+'_'+side+'_five_tracks',len(s['tracks'][side])==5)
        s=core.command(s,{'action':'assign','side':side,'digit':'index','track_id':'digit_branch_1_'+side},provenance='agent_test')
        try:core.command(s,{'action':'assign','side':side,'digit':'middle','track_id':'digit_branch_1_'+side},provenance='agent_test')
        except ValueError:blocked=True
        else:blocked=False
        check(ch+'_'+side+'_duplicate_rejected',blocked)
        f=s['fingers']['index_'+side]
        s=core.command(s,{'action':'review','roles':['index_'+side],'judgement':'accept','category':'synthetic_test'},provenance='agent_test')
        s=core.command(s,{'action':'move','positions':{'index_'+side+':tip':core.add(f['tip_cm'],[.1,0,0])}},provenance='agent_test')
        check(ch+'_'+side+'_endpoint_invalidates_review','index_'+side not in s['approvals'])
    check(ch+'_real_session_untouched',core.read(core.W/'session.json')==original)
    gate=core.read(core.O/'anatomical_validation.json')
    check(ch+'_no_downstream_before_gate',not gate['downstream_authorised'] and not list((P/'Content/MetaHumanTo3DCharacter/Phase4F'/ch).rglob('SKEL_*.uasset')))
for p in list(W.glob('apose_*.py'))+[W/'John/validate.py',W/'Jane/validate.py',W/'John/inherited_validate.py',W/'Jane/inherited_validate.py']:
    ast.parse(p.read_text(encoding='utf-8-sig'))
check('python_syntax',True)
budget=core.read(O/'APoseContinuation/budget_consumption.json');policy=core.read(O/'APoseContinuation/evaluation_policy.json')
check('budget',all(n<=policy['semantic_pass_limit_per_new_character'] for n in budget['semantic_passes'].values()))
check('zero_skin_candidates',all(n==0 for n in budget['skin_candidates'].values()))
before=O/'APoseContinuation/Before'
for name in ['Phase4FQualityGeneralisationGate.md','HumanReviewInstructions.md']:
    check(name+'_historical_prefix',(O/name).read_bytes().startswith((before/name).read_bytes()))
(O/'APoseContinuation/self_review.json').write_text(json.dumps({'status':'passed','tests':results,'scope':'Synthetic in-memory states, real zero-event invariants, gate blocking, budget, syntax and byte-preserved historical report prefixes. Native maps/readback verified separately.'},indent=2),encoding='utf-8')
print('SELF_REVIEW',len(results),'passed')
