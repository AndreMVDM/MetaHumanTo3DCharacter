"""Focused review of provenance, invalidation, correction effort and isolation."""
import sys, json, ast
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F';O=P/'Documentation/Phase4F'
sys.path.insert(0,str(W));import review_core as core
results=[]
def check(name,passed):
    results.append({'name':name,'passed':bool(passed)})
    if not passed:raise AssertionError(name)
for character in ['Bill','Jill']:
    core.configure(character);s=core.rebuild(core.fresh_state());original=core.read(core.W/'session.json')
    check(character+'_no_real_user_actions',not original['events'] and not original['approvals'] and original['trial_started_at'] is None)
    s=core.command(s,{'action':'start'},provenance='agent_test')
    s=core.command(s,{'action':'review','roles':['pelvis'],'judgement':'accept','category':'synthetic_test'},provenance='agent_test')
    check(character+'_synthetic_review_not_counted',core.metrics(s)['review_commands']==0 and core.metrics(s)['currently_accepted_human_roles']==[])
    p=next(r['position_cm'] for r in s['joints'] if r['role']=='pelvis');p=core.add(p,[.2,0,0])
    s=core.command(s,{'action':'move','positions':{'pelvis':p}},provenance='agent_test')
    check(character+'_dependent_move_invalidates_review','pelvis' not in s['approvals'])
    for side in ['l','r']:
        check(character+'_'+side+'_five_actual_tracks',len(s['tracks'][side])==5)
        s=core.command(s,{'action':'assign','side':side,'digit':'index','track_id':'digit_branch_1_'+side},provenance='agent_test')
        try:core.command(s,{'action':'assign','side':side,'digit':'middle','track_id':'digit_branch_1_'+side},provenance='agent_test')
        except ValueError:blocked=True
        else:blocked=False
        check(character+'_'+side+'_duplicate_track_rejected',blocked)
        f=s['fingers']['index_'+side]
        s=core.command(s,{'action':'review','roles':['index_'+side],'judgement':'accept','category':'synthetic_test'},provenance='agent_test')
        s=core.command(s,{'action':'move','positions':{'index_'+side+':tip':core.add(f['tip_cm'],[.1,0,0])}},provenance='agent_test')
        check(character+'_'+side+'_finger_endpoint_invalidates_review','index_'+side not in s['approvals'])
    check(character+'_original_session_untouched',core.read(core.W/'session.json')==original)
for p in W.rglob('*.py'):
    if 'NativeHost' in p.parts:continue
    ast.parse(p.read_text(encoding='utf-8-sig'))
check('new_python_syntax',True)
policy=json.loads((O/'evaluation_policy.json').read_text());budget=json.loads((O/'budget_consumption.json').read_text())
check('semantic_budget_within_limits',all(n<=policy['semantic_pass_limit_per_new_character'] for ch,n in budget['semantic_passes'].items()))
check('no_skin_before_anatomy',all(v==0 for v in budget['skin_candidates'].values()))
(O/'self_review.json').write_text(json.dumps({'status':'passed','tests':results,'limitations':'Synthetic state only; no real human anatomy judgement and no synthetic event exported to real sessions. Native controls/maps verified separately.'},indent=2))
print('Self-review:',len(results),'checks passed')
