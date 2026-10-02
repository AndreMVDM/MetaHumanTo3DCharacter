"""Independent CPU skin-envelope estimate from DCC weights and actual UE baked bone poses."""
from pathlib import Path
import json,math,collections,csv
import numpy as np
from solver_sanity import validate_pose
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase3B';W=P/'Working/Phase3B'
def load(n):return json.loads((O/n).read_text())
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,allow_nan=False))
def matrix(t):
    x,y,z,w=t['rotation_xyzw'];s=np.asarray(t['scale']);m=np.eye(4)
    m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])*s[None,:]
    m[:3,3]=t['translation'];return m
candidates={(x['rig'],x['label']):x for x in load('scaled_candidates.json')}
skin={r:json.loads((W/('skin_'+r+'.json')).read_text()) for r in ['UE5','Mixamo']}
prepared={}
for r in skin:
    data=skin[r];original=candidates[r,'OriginalHeight'];names=list(original['snapshot']['bones']);lookup={n.casefold():i for i,n in enumerate(names)}
    weights=np.zeros((len(data['weights']),len(names)))
    for i,gs in enumerate(data['weights']):
        for n,w in gs:weights[i,lookup[n.casefold()]]+=w
    weights/=weights.sum(axis=1)[:,None]
    vertices=np.c_[np.asarray(data['vertices_cm']),np.ones(len(weights))]
    bone_vertex={}
    for i,n in enumerate(names):bone_vertex[n]=(np.where(weights[:,i]>0)[0],weights[weights[:,i]>0,i])
    feet={}
    for side,suff in [('Left','l'),('Right','r')]:
        group_names=['foot_'+suff,'ball_'+suff] if r=='UE5' else [side+'Foot',side+'ToeBase',side+'Toe_End']
        cols=[lookup[n.casefold()] for n in group_names]
        feet[side]=np.where(weights[:,cols].sum(axis=1)>=0.5)[0]
    prepared[r]=(vertices,names,bone_vertex,feet)
all_samples=load('runtime_samples.json')['samples']+load('control_samples.json')['samples']+load('root_motion_final_samples.json')['samples']
metrics=[];failures=[];stored_vertices={}
for sample in all_samples:
    rig,label=sample['rig'],sample['label']
    if label.startswith('Raw'):continue # Legacy scale representation intentionally fails reference preflight; evaluated separately.
    candidate=candidates.get((rig,label),candidates[rig,'Height180'])
    refs=candidate['snapshot']['bones'];factor=candidate['factor'];verts,names,bone_vertex,feet=prepared[rig]
    initial=verts.copy();initial[:,:3]*=factor
    animated={n.casefold():b for n,b in sample['bones'].items()}
    skin_out=np.zeros((len(verts),3))
    positions={n:np.asarray(animated[n.casefold()]['component']['translation']) for n in names}
    for n in names:
        indices,weights=bone_vertex[n]
        if not len(indices):continue
        m=matrix(animated[n.casefold()]['component'])@np.linalg.inv(matrix(refs[n]['component']))
        skin_out[indices]+=(initial[indices]@m.T)[:,:3]*weights[:,None]
    H=sample['requested_height_cm'];pelvis='pelvis' if rig=='UE5' else 'Hips';head='head' if rig=='UE5' else 'Head';root=names[0];rootpos=positions[root]
    folded={n.casefold():p for n,p in positions.items()}
    def at(n):return folded[n.casefold()]
    joints={}
    segments={}
    def angle(a,b,c):
        ab=at(a)-at(b);cb=at(c)-at(b)
        return math.degrees(math.acos(float(np.clip(np.dot(ab,cb)/max(np.linalg.norm(ab)*np.linalg.norm(cb),1e-9),-1,1))))
    for side,suff in [('Left','l'),('Right','r')]:
        arm=['upperarm_'+suff,'lowerarm_'+suff,'hand_'+suff] if rig=='UE5' else [side+'Arm',side+'ForeArm',side+'Hand']
        leg=['thigh_'+suff,'calf_'+suff,'foot_'+suff] if rig=='UE5' else [side+'UpLeg',side+'Leg',side+'Foot']
        joints[side+'ElbowAngleDeg']=angle(*arm);joints[side+'KneeAngleDeg']=angle(*leg)
        for a,b in zip(arm+leg,(arm+leg)[1:]):
            if (a==arm[-1]):continue
            ref_length=math.dist(refs[next(n for n in names if n.casefold()==a.casefold())]['component']['translation'],refs[next(n for n in names if n.casefold()==b.casefold())]['component']['translation'])
            actual=math.dist(at(a),at(b));segments[a+'>'+b]={'reference_cm':ref_length,'animated_cm':actual,'ratio':actual/ref_length if ref_length else 1}
    foot_metrics={}
    for side,suff in [('Left','l'),('Right','r')]:
        foot='foot_'+suff if rig=='UE5' else side+'Foot';toe='ball_'+suff if rig=='UE5' else side+'ToeBase'
        tip=side+'Toe_End' if rig=='Mixamo' else None
        direction=at(tip)-at(toe) if tip else at(toe)-at(foot)
        pitch=math.degrees(math.atan2(direction[2],np.linalg.norm(direction[:2])))
        foot_metrics[side]={'ankle_cm':at(foot).tolist(),'toe_cm':at(toe).tolist(),'terminal_cm':at(tip).tolist() if tip else None,'toe_direction_pitch_deg':pitch,'weighted_surface_min_z_cm':float(skin_out[feet[side],2].min()),'weighted_surface_max_z_cm':float(skin_out[feet[side],2].max())}
    scale_error=max(abs(x-1) for b in animated.values() for x in b['local']['scale'])
    maxradius=max(float(np.linalg.norm(p-rootpos)) for p in positions.values())
    pelvis_displacement=float(np.linalg.norm(positions[pelvis]-np.asarray(refs[pelvis]['component']['translation'])))
    maxstretch=max(abs(s['ratio']-1) for s in segments.values())
    bounds={'min_cm':skin_out.min(axis=0).tolist(),'max_cm':skin_out.max(axis=0).tolist(),'height_cm':float(np.ptp(skin_out[:,2]))}
    issues=validate_pose(H,sample['bones'],pelvis,root,refs,label.startswith('RootMotion'))
    if not np.isfinite(skin_out).all():issues.append('non_finite_skin')
    if maxradius>3*H:issues.append('bone_envelope')
    if positions[pelvis][2]<0.2*H or positions[pelvis][2]>1.5*H:issues.append('pelvis_height')
    if pelvis_displacement>H and not label.startswith('RootMotion'):issues.append('pelvis_displacement')
    if scale_error>0.001:issues.append('non_unit_bone_scale')
    if maxstretch>0.05:issues.append('limb_length_change')
    if bounds['height_cm']<0.1*H or bounds['height_cm']>2*H:issues.append('skin_height_envelope')
    metric={k:sample[k] for k in ['rig','label','state','animation_role','time_s','frame_fraction','requested_height_cm']}
    metric.update({'pelvis_cm':positions[pelvis].tolist(),'head_cm':positions[head].tolist(),'root_cm':rootpos.tolist(),'hand_left_cm':at('hand_l' if rig=='UE5' else 'LeftHand').tolist(),'hand_right_cm':at('hand_r' if rig=='UE5' else 'RightHand').tolist(),'max_bone_radius_from_root_cm':maxradius,'pelvis_displacement_from_reference_cm':pelvis_displacement,'max_bone_scale_error':scale_error,'max_limb_length_relative_error':maxstretch,'joints':joints,'segments':segments,'feet':foot_metrics,'cpu_skin_bounds':bounds,'sanity_pass':not issues,'sanity_failures':sorted(set(issues))})
    metrics.append(metric)
    if issues:failures.append({k:metric[k] for k in ['rig','label','state','animation_role','time_s','sanity_failures']})
    if ((label=='Height180' and sample['state'] in ['FK','Full']) or 'RootMapped' in label or 'RootUnmapped' in label) and sample['animation_role'] in ['run','idle','walk','reach'] and sample['frame_fraction'] in [0,0.25,0.5,0.75]:
        key='|'.join([rig,label,sample['state'],sample['animation_role'],str(sample['frame_fraction'])]);stored_vertices[key]=skin_out.tolist()
save('quantitative_metrics.json',{'method':'CPU linear blend skinning estimate from original DCC weights, normalised per vertex, and actual UE evaluated component transforms. Does not include UE weight quantisation, cloth, morphs, GPU rendering, physics or material effects.','samples':metrics,'failed_samples':failures})
(W/'visual_skin_samples.json').write_text(json.dumps(stored_vertices))
groups=collections.defaultdict(list)
for m in metrics:groups[m['rig'],m['label'],m['state'],m['animation_role']].append(m)
summary=[]
for (rig,label,state,role),ms in groups.items():
    d={'rig':rig,'label':label,'state':state,'animation_role':role,'samples':len(ms),'sanity_pass':all(m['sanity_pass'] for m in ms),'pelvis_z_range_cm':[min(m['pelvis_cm'][2] for m in ms),max(m['pelvis_cm'][2] for m in ms)],'head_z_range_cm':[min(m['head_cm'][2] for m in ms),max(m['head_cm'][2] for m in ms)],'skin_height_range_cm':[min(m['cpu_skin_bounds']['height_cm'] for m in ms),max(m['cpu_skin_bounds']['height_cm'] for m in ms)],'max_limb_relative_error':max(m['max_limb_length_relative_error'] for m in ms),'joints':{k:[min(m['joints'][k] for m in ms),max(m['joints'][k] for m in ms)] for k in ms[0]['joints']},'feet':{}}
    for side in ['Left','Right']:
        clearance=[m['feet'][side]['weighted_surface_min_z_cm'] for m in ms];pitch=[m['feet'][side]['toe_direction_pitch_deg'] for m in ms]
        contact=[(a,b) for a,b in zip(ms,ms[1:]) if a['feet'][side]['weighted_surface_min_z_cm']<=0.01*a['requested_height_cm'] and b['feet'][side]['weighted_surface_min_z_cm']<=0.01*b['requested_height_cm']]
        slips=[math.dist(a['feet'][side]['toe_cm'][:2],b['feet'][side]['toe_cm'][:2]) for a,b in contact]
        d['feet'][side]={'surface_floor_range_cm':[min(clearance),max(clearance)],'toe_pitch_range_deg':[min(pitch),max(pitch)],'penetrating_samples':sum(z<-0.01*ms[0]['requested_height_cm'] for z in clearance),'contact_pairs':len(contact),'max_contact_pair_horizontal_displacement_cm':max(slips) if slips else None,'sum_contact_horizontal_displacement_cm':sum(slips),'contact_metric_limit':'In-place sole-height proxy, 25 samples; moving gait foot is expected to travel rearward under a stationary character. This is not a world-speed foot-sliding verdict.'}
    summary.append(d)
save('quantitative_summary.json',summary)
print('QUANTIFIED',len(metrics),'failed',len(failures))
print([(m['rig'],m['label'],m['state'],m['feet']) for m in summary if ('RootMapped' in m['label'] or 'RootUnmapped' in m['label']) and m['animation_role']=='run'])
