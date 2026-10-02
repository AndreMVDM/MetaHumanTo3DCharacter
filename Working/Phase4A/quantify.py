"""CPU LBS surface estimate driven by actual evaluated UE poses; not a GPU/contact test."""
import json, math, collections,sys
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parents[2]; O=P/'Documentation/Phase4A'; W=P/'Working/Phase4A'
suffix=sys.argv[1] if len(sys.argv)>1 else '';assert suffix in ['', '_ball_forward']
def load(p):return json.loads(p.read_text())
def save(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False))
def matrix(t):
    x,y,z,w=t['rotation_xyzw'];m=np.eye(4)
    m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])*np.array(t['scale'])[None,:]
    m[:3,3]=t['translation'];return m
prepared={}
for case in ['Unrigged','MixamoRecovered']:
    d=load(W/(case+'_assisted'+suffix+'_skin.json'));names=list(d['reference']['bones']);v=np.c_[d['geometry']['vertices'],np.ones(len(d['weights']))];wt=np.zeros((len(v),len(names)))
    for i,ws in enumerate(d['weights']):
        for b,w in ws:wt[i,b]+=w
    tris=np.array(d['geometry']['triangles']);rv=v[:,:3];area=np.linalg.norm(np.cross(rv[tris[:,1]]-rv[tris[:,0]],rv[tris[:,2]]-rv[tris[:,0]]),axis=1);valid=area>1e-6
    feet={s:np.where(wt[:,[names.index('foot_'+s),names.index('ball_'+s)]].sum(axis=1)>=.5)[0] for s in ['l','r']}
    prepared[case]=(d,names,v,wt,tris,area,valid,feet)
metrics=[];visual={}
for sample in load(O/('runtime_samples'+suffix+'.json'))['samples']:
    d,names,v,wt,tris,area,valid,feet=prepared[sample['case']];out=np.zeros((len(v),3));refs=d['reference']['bones'];bones=sample['bones'];pos={n:np.array(bones[n]['component']['translation']) for n in names}
    for i,n in enumerate(names):
        idx=np.where(wt[:,i]>0)[0];m=matrix(bones[n]['component'])@np.linalg.inv(matrix(refs[n]['component']));out[idx]+=(v[idx]@m.T)[:,:3]*wt[idx,i,None]
    newarea=np.linalg.norm(np.cross(out[tris[:,1]]-out[tris[:,0]],out[tris[:,2]]-out[tris[:,0]]),axis=1);rat=newarea[valid]/area[valid]
    fm={s:{'weighted_surface_min_z_cm':float(out[idx,2].min()),'ankle_cm':pos['foot_'+s].tolist(),'ball_cm':pos['ball_'+s].tolist(),'toe_pitch_deg':math.degrees(math.atan2((pos['ball_'+s]-pos['foot_'+s])[2],np.linalg.norm((pos['ball_'+s]-pos['foot_'+s])[:2])))} for s,idx in feet.items()}
    segments={};angles={}
    for s in ['l','r']:
        for chain in [('thigh','calf','foot'),('upperarm','lowerarm','hand')]:
            ns=[n+'_'+s for n in chain];a,b,c=[pos[n] for n in ns];u=a-b;vv=c-b;angles[chain[1]+'_'+s]=math.degrees(math.acos(float(np.clip(np.dot(u,vv)/(np.linalg.norm(u)*np.linalg.norm(vv)),-1,1))))
            for x,y in zip(ns,ns[1:]):segments[x+'>'+y]=float(np.linalg.norm(pos[x]-pos[y])/np.linalg.norm(np.array(refs[x]['component']['translation'])-np.array(refs[y]['component']['translation'])))
    metric={k:sample[k] for k in ['case','mode','role','time_s','fraction']};metric.update({'feet':fm,'joint_angles_deg':angles,'limb_length_ratios':segments,'max_bone_scale_error':max(abs(z-1) for b in bones.values() for z in b['local']['scale']),'root_cm':pos['root'].tolist(),'pelvis_cm':pos['pelvis'].tolist(),'finite':bool(np.isfinite(out).all()),'triangle_area_ratio_p01_median_p99':np.quantile(rat,[.01,.5,.99]).tolist(),'triangles_area_below_10pct':int((rat<.1).sum()),'triangles_area_above_5x':int((rat>5).sum())});metrics.append(metric)
    if sample['mode']=='Full' and sample['fraction'] in [0,.25,.5,.75]:visual['|'.join([sample['case'],sample['role'],str(sample['fraction'])])]=out.tolist()
groups=collections.defaultdict(list)
for m in metrics:groups[m['case'],m['mode'],m['role']].append(m)
summary=[]
for (case,mode,role),ms in groups.items():
    summary.append({'case':case,'mode':mode,'role':role,'samples':len(ms),'finite':all(m['finite'] for m in ms),'max_bone_scale_error':max(m['max_bone_scale_error'] for m in ms),'max_limb_length_error':max(abs(r-1) for m in ms for r in m['limb_length_ratios'].values()),'max_collapsed_triangle_count':max(m['triangles_area_below_10pct'] for m in ms),'max_stretched_triangle_count':max(m['triangles_area_above_5x'] for m in ms),'feet':{s:{'surface_floor_range_cm':[min(m['feet'][s]['weighted_surface_min_z_cm'] for m in ms),max(m['feet'][s]['weighted_surface_min_z_cm'] for m in ms)],'toe_pitch_range_deg':[min(m['feet'][s]['toe_pitch_deg'] for m in ms),max(m['feet'][s]['toe_pitch_deg'] for m in ms)]} for s in ['l','r']}})
baseline=[m for m in load(P/'Documentation/Phase3B/quantitative_metrics.json')['samples'] if m['rig']=='Mixamo' and m['label']=='Height180' and m['state']=='Full']
comparison=[]
for role in ['idle','walk','run','reach']:
    b=[m for m in baseline if m['animation_role']==role]
    comparison.append({'role':role,'Phase3B_Mixamo_min_sole_z_cm':{s:min(m['feet'][side]['weighted_surface_min_z_cm'] for m in b) for s,side in [('l','Left'),('r','Right')]},'Phase4A_assisted_min_sole_z_cm':{case:{s:min(m['feet'][s]['weighted_surface_min_z_cm'] for m in groups[case,'Full',role]) for s in ['l','r']} for case in ['Unrigged','MixamoRecovered']}})
save('deformation_metrics'+suffix+'.json',{'method':'CPU linear blend skinning of UE-generated weights and 400 actual UE AnimPose samples. Excludes GPU weight quantisation, cloth, morphs and collision. Area thresholds are screening flags, not acceptance criteria.','samples':metrics,'summary':summary})
save('foot_comparison'+suffix+'.json',{'method':'Same four in-place clips, 25 uniformly spaced poses, 180cm, weighted-foot surface minima; CPU LBS estimate. No world-speed or contact solver proof.','comparison':comparison,'summary':summary})
(W/('visual_skin_samples'+suffix+'.json')).write_text(json.dumps(visual));print(json.dumps(comparison,indent=2))
