"""Final evidence aggregation and focused self-review. No Unreal/Git mutations."""
import json,hashlib,math
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/ReviewFixes/RunJumpLand'
load=lambda n:json.loads((O/n).read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
baseline=load('baseline.json');audit=load('preservation_audit.json');fresh=load('fresh_validation.json');checks=[];subjects={}
def check(name,ok):
    checks.append(dict(name=name,status='PASS' if ok else 'FAIL'))
for s,folder in [('Female','FinalAcceptance/FemaleBodyRigged'),('Aegis','R4/AegisNX7')]:
    before=load(s+'_before_native.json');after=load(s+'_after_native.json');inspection=load('inspection.json')['subjects'][s];e=before['cases'][0]['touchdowns'][0]
    check(s+' unchanged baseline skid reproduced',before['status']=='PASS' and e['distance_cm']>500)
    check(s+' all fourteen native cases',after['status']=='PASS' and len(after['cases'])==14)
    check(s+' fresh reload and retained graphs',fresh['subjects'][s]['status']=='PASS')
    manifest=json.loads((R/'Documentation'/folder/'animation_library_manifest.json').read_text());library=[]
    for entry in manifest['entries']:
        if entry.get('bake_result')!='PASS':continue
        package=entry['destination_path'].split('.')[0];p=(R/'Content'/package.removeprefix('/Game/')).with_suffix('.uasset');rel=p.relative_to(R).as_posix();library.append(dict(path=package,sha256=sha(p),unchanged=sha(p)==baseline['protected'][rel]['sha256']))
    check(s+' 89 accepted library assets unchanged',len(library)==89 and all(x['unchanged'] for x in library))
    run=next(c for c in after['cases'] if c['name']=='run_jump_hold');post=[x for x in run['observations'] if run['touchdowns'][0]['touchdown']['t']+.2<x['t']<run['touchdowns'][0]['touchdown']['t']+.55]
    advance=max(x['player_times']['8'] for x in post)-min(x['player_times']['8'] for x in post);pose=max(math.dist(x['joints'][b],post[0]['joints'][b]) for x in post for b in x['joints']);check(s+' resumed run actually advances native pose',len(post)>2 and advance>.1 and pose>1)
    lands=[x for x in before['cases'][0]['observations'] if x['landing']];rootvariation=max(math.dist(x['root_component'],lands[0]['root_component']) for x in lands)
    subjects[s]=dict(before=dict(velocity_at_touchdown=e['touchdown']['velocity'],landing_delay_s=e['delay_s'],skid_distance_cm=e['distance_cm'],root_component_variation_during_landing_cm=rootvariation),after=[dict(name=c['name'],status=c['status'],states=c['states'],touchdowns=[{k:v for k,v in x.items() if k in ['delay_s','distance_cm','landing_samples']} for x in c['touchdowns']]) for c in after['cases']],post_touchdown_run=dict(native_samples=len(post),sequence_time_advance_s=advance,pose_excursion_cm=pose),CMC=after['CMC'],runtime_root_motion_mode=after['runtime_root_motion_mode'],landing_animation={label:dict(path=v['path'],duration_s=v['metadata']['duration_s'],flags=v['metadata']['root_flags'],root_excursion_cm=v['root_excursion_cm'],pelvis_excursion_cm=v['pelvis_excursion_cm']) for label,v in inspection['land'].items()},library=library,assets=fresh['subjects'][s]['assets'],runtime_closure_packages=len(fresh['subjects'][s]['runtime_closure']['packages']))
check('all 46046 protected files unchanged',audit['status']=='PASS' and not audit['changed'] and not audit['missing']);check('Git HEAD index and preexisting tracked state unchanged',audit['git_preserved'])
female=load('Female_after_native.json');check('final Female Editor native ready PIE stopped',female['PIE_stopped'] and female['editor_left_open'] and female['ready_to_press_Play'])
assets=[]
for p in (R/'Content/MetaHumanTo3DCharacter/ReviewFixes/RunJumpLand').rglob('*'):
    if p.is_file():assets.append(dict(path=p.relative_to(R).as_posix(),sha256=sha(p),bytes=p.stat().st_size))
check('exactly eight isolated UE assets',len(assets)==8)
d=dict(status='PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL',acceptance='TECHNICAL_FIX_VERIFIED_HUMAN_HANDS_ON_REVIEW_PENDING',cause_classes=['LANDING_STATE_HELD_TOO_LONG','ANIMATION_VISUAL_PLANT_VS_CONTINUED_WORLD_MOVEMENT'],fix='Original Landing predicate AND Speed<=5; existing idle/walk speed boundary and 0.1s blends preserved.',timing_caveat='Zero after values mean grounded locomotion was selected in the first observed touchdown sample. They do not mean zero blend duration. The retained air-to-ground pose blend is 0.1s; native per-player blend weights are not exposed by this harness.',subjects=subjects,checks=checks,assets=assets,animation_rebakes=0,preservation=audit['status'],final_editor_pid=female['pid'],final_map=female['map'],PIE_stopped=female['PIE_stopped'],visual_caveat='Native UE capture images and live bone poses were inspected. The desktop capture helper failed its sandbox startup, so no desktop-window capture/continuous subjective approval is claimed. Final hands-on acceptance belongs to Andre.')
(O/'result.json').write_text(json.dumps(d,indent=2)+'\n')
print(d['status'],len(checks),'checks',len(assets),'new UE assets')
