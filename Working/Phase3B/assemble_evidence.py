from pathlib import Path
import json,math,csv,collections,hashlib
import numpy as np
from solver_sanity import validate_pose
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase3B'
def load(n):return json.loads((O/n).read_text())
def save(n,d):(O/n).write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
rows=load('scaled_candidates.json');dcc=load('dcc_candidates.json');baseline=load('baseline_import.json');summary=load('quantitative_summary.json');reference=load('reference_validation.json');live=load('live_runtime_samples.json')
assert len(rows)==10 and not any(r.get('error') for r in rows)
assert len(live['samples'])==100 and not live['errors']
measurements=[];transforms=[];matrix=[]
for row in rows:
    d=next(x for x in dcc if x['rig']==row['rig'] and x['label']==row['label']);snap=row['snapshot'];bones=snap['bones'];root=next(iter(bones));pelvis='pelvis' if row['rig']=='UE5' else 'Hips'
    measurements.append({k:d[k] for k in ['rig','label','requested_height_cm','measured_original_height_cm','raw_original_bounds_height_cm','factor','ground_cm','crown_cm','head_joint_cm','measurement','expected_anatomical_height_cm']}|{'imported_raw_mesh_height_cm':snap['bounds']['height_cm'],'height_error_cm':row['height_error_cm'],'tolerance_cm':0.1,'pass':abs(row['height_error_cm'])<=.1,'anatomical_estimate_limit':'Head-weighted crown region includes unsegmented hair; a repeatable semantic stature estimate, not an independently measured skull crown.'})
    transforms.append({'rig':row['rig'],'label':row['label'],'root_name':root,'root':bones[root],'pelvis_name':pelvis,'pelvis':bones[pelvis],'all_local_and_component_scales_unit':row['root_scale_unit'],'finite':row['finite']})
    ms=[x for x in summary if x['rig']==row['rig'] and x['label']==row['label']]
    fk=all(x['sanity_pass'] for x in ms if x['state']=='FK');ik=all(x['sanity_pass'] for x in ms if x['state']!='FK')
    run=next(x for x in ms if x['state']=='Full' and x['animation_role']=='run')
    walk=next(x for x in ms if x['state']=='Full' and x['animation_role']=='walk')
    foot_run=all(run['feet'][s]['penetrating_samples']==0 for s in ['Left','Right'])
    matrix.append({'Rig':row['rig'],'TargetHeightCm':d['requested_height_cm'],'MeasuredHeightCm':snap['bounds']['height_cm'],'HeightErrorCm':row['height_error_cm'],'FKStable':fk,'IKStable':ik,'Feet':'Run sole proxy pass; walk needs contact correction' if foot_run else 'Needs QA','Hands':'Finite; limb lengths preserved; contact unqualified','Notes':'Unit asset/actor/component scales; five clips FK/full and isolated FBIK run; 0.1cm stature tolerance; no world-speed foot-sliding qualification'})
save('height_measurements.json',measurements);save('root_reference_transforms.json',{'baseline':{r:{'root':next(iter(b['bones'].items())),'pelvis':b['bones']['pelvis' if r=='UE5' else 'Hips']} for r,b in baseline['variants'].items()},'final':transforms})
with (O/'height_matrix.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(matrix[0]));w.writeheader();w.writerows(matrix)
save('mixamo_foot_tests.json',{'configs':[x for x in load('control_configs.json') if x['rig']=='Mixamo' and ('Foot' in x['label'] or 'Toe' in x['label'])],'quantitative_comparison':[x for x in summary if x['rig']=='Mixamo' and ('RootMapped' in x['label'] or 'RootUnmapped' in x['label'])],'final_animation_summary':[x for x in summary if x['rig']=='Mixamo' and x['label']=='Height180'],'reference_ankle_toe_bones':{n:b for n,b in next(x for x in rows if x['rig']=='Mixamo' and x['label']=='Height180')['snapshot']['bones'].items() if any(n.startswith(s) and n.endswith(b) for s in ['Left','Right'] for b in ['Foot','ToeBase','Toe_End'])},'findings':['Match the leg endpoint and leg IK goal to ToeBase to correspond to Manny ball goals.','Unmap Root chain where Hips is also the retarget pelvis; FK Root otherwise overwrites pelvis motion.','Clear ForceRootLock on destination in-place clips because Hips is the root.','Run sole proxy improved; walk and right-foot reach retain approximately 2.3cm penetration at180cm. Contact velocity is not qualified.']})
groups=collections.defaultdict(list);failures=[]
lookup={(r['rig'],r['label']):r for r in rows}
for sample in live['samples']:
    assert sample['components'] and all(abs(s-1)<.001 for s in sample['actor_transform']['scale'])
    for c in sample['components']:
        name=c['name']
        if name=='Manny_Source':continue
        rig='Mixamo' if 'Mixamo' in name else 'UE5';pelvis='Hips' if rig=='Mixamo' else 'pelvis';root='Hips' if rig=='Mixamo' else 'root'
        if name.startswith('RawUE5'):ref=baseline['variants']['UE5']['bones'];height=baseline['variants']['UE5']['bounds']['height_cm']
        else:
            label='Height180' if name.startswith('Baked_') else name.split('_',1)[1];row=lookup[rig,label];ref=row['snapshot']['bones'];height=row['requested_height_cm']
        tr={n:{'component':b['component']} for n,b in c['bones'].items()}
        issues=validate_pose(height,tr,pelvis,root,ref)
        if any(abs(s-1)>.001 for s in c['world_transform']['scale']):issues.append('external_scale')
        pp=c['bones'][pelvis]['component']['translation'];wp=c['bones'][pelvis]['world']['translation']
        groups[name,sample['animation_role']].append({'component_pelvis':pp,'world_pelvis':wp,'issues':issues,'bounds':c['bounds']})
        if issues:failures.append({'component':name,'role':sample['animation_role'],'frame':sample['frame'],'failures':issues})
out=[]
for (name,role),ms in groups.items():
    out.append({'component':name,'animation_role':role,'samples':len(ms),'pass':not any(x['issues'] for x in ms),'pelvis_component_z_range_cm':[min(x['component_pelvis'][2] for x in ms),max(x['component_pelvis'][2] for x in ms)],'pelvis_world_z_range_cm':[min(x['world_pelvis'][2] for x in ms),max(x['world_pelvis'][2] for x in ms)],'max_bounds_sphere_radius_cm':max(x['bounds']['sphere_radius'] for x in ms)})
save('live_solver_isolation.json',{'method':'100 live SIE snapshots,17 mesh components,25 per clip. Source original clips obey engine ForceRootLock. Components have identity scales and different known Y translations. Matched raw FK/solver0/solver1/full run simultaneously; each pass is a separate retarget configuration. No engine solver instrumentation.','summary':out,'failed_samples':failures})
# Verify quaternions rather than comparing sign-sensitive components.
poses=load('pose_offsets.json');pose_stats=[]
for rig in ['UE5','Mixamo']:
    p=[x for x in poses if x['rig']==rig];original=next(x for x in p if x['label']=='OriginalHeight')['offsets_xyzw'];stats=[]
    for row in p:
        diffs={n:math.degrees(2*math.acos(float(np.clip(abs(np.dot(np.array(q)/np.linalg.norm(q),np.array(original[n])/np.linalg.norm(original[n]))),-1,1)))) for n,q in row['offsets_xyzw'].items()}
        stats.append({'label':row['label'],'max_offset_difference_from_original_deg':max(diffs.values()),'nonidentity_offset_bones':[n for n,q in row['offsets_xyzw'].items() if abs(q[3])<.999999]})
    pose_stats.append({'rig':rig,'heights':stats})
save('pose_height_comparison.json',pose_stats)
runtime=load('runtime_samples.json');runtime['live_evidence_file']='live_runtime_samples.json';runtime['live_sample_count']=len(live['samples']);runtime['live_mesh_components_per_sample']=17;save('runtime_samples.json',runtime)
before=load('protected_before.json');changed=[];missing=[]
for rel,v in before.items():
    path=P/rel
    if not path.exists():missing.append(rel)
    elif hashlib.sha256(path.read_bytes()).hexdigest()!=v['sha256']:changed.append(rel)
current=[P/'MHTo3DCharacter.uproject']
for folder in ['Characters','Config','Content','Reference','Working/Phase2','Documentation/Phase2','Documentation/Phase3']:
    current.extend(p for p in (P/folder).rglob('*') if p.is_file() and 'Phase3B' not in p.parts)
added=sorted(set(str(p.relative_to(P)) for p in current)-set(before))
reference_changed=[x['source'] for x in load('source_animation_inventory.json') if hashlib.sha256(Path(x['source']).read_bytes()).hexdigest()!=x['sha256']]
save('protected_after_verification.json',{'protected_files':len(before),'changed':changed,'missing':missing,'added_in_protected_scope':added,'reference_source_assets_changed':reference_changed,'pass':not any([changed,missing,added,reference_changed])})
assert not any([changed,missing,added,reference_changed]),(changed,missing,added,reference_changed)
print('EVIDENCE_ASSEMBLED',len(matrix),'live failed samples',len(failures))
