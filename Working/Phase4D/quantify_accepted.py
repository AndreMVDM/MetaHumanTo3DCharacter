"""CPU LBS driven by UE-evaluated baked poses. Screens are not automatic acceptance."""
import json,math,collections
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4D';O=P/'Documentation/Phase4D'
load=lambda p:json.loads(p.read_text())
def save(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False))
def matrix(t):
 x,y,z,w=t['rotation_xyzw'];m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])*np.array(t['scale'])[None,:];m[:3,3]=t['translation'];return m
d=load(W/'accepted_skin.json');names=list(d['reference']['bones']);refs=d['reference']['bones'];rv=np.array(d['geometry']['vertices']);v=np.c_[rv,np.ones(len(rv))];tris=np.array(d['geometry']['triangles']);wt=np.zeros((len(v),len(names)))
for i,ws in enumerate(d['weights']):
 for b,w in ws:wt[i,b]+=w
invref={n:np.linalg.inv(matrix(refs[n]['component'])) for n in names};idxs={n:np.where(wt[:,i]>0)[0] for i,n in enumerate(names)}
area=np.linalg.norm(np.cross(rv[tris[:,1]]-rv[tris[:,0]],rv[tris[:,2]]-rv[tris[:,0]]),axis=1);valid=area>1e-6
sole={s:np.where((rv[:,0]*sign>8)&(rv[:,2]<2))[0] for s,sign in [('l',1),('r',-1)]}
feet={s:np.where((rv[:,0]*sign>8)&(rv[:,2]<10))[0] for s,sign in [('l',1),('r',-1)]}
regions={}
for label,bns in {'shoulders':['upperarm_l','upperarm_r','clavicle_l','clavicle_r'],'elbows':['lowerarm_l','lowerarm_r'],'wrists':['hand_l','hand_r'],'pelvis_hips':['pelvis','thigh_l','thigh_r'],'knees':['calf_l','calf_r'],'ankles':['foot_l','foot_r'],'fingers':[n for n in names if any(n.startswith(k+'_0') for k in ['thumb','index','middle','ring','pinky'])]}.items():
 near=np.min(np.linalg.norm(rv[:,None,:]-np.array([refs[n]['component']['translation'] for n in bns])[None,:,:],axis=2),axis=1)<5;regions[label]=np.where(valid & np.any(near[tris],axis=1))[0]
def deform(bones):
 out=np.zeros((len(v),3))
 for i,n in enumerate(names):
  idx=idxs[n];m=matrix(bones[n]['component'])@invref[n];out[idx]+=(v[idx]@m.T)[:,:3]*wt[idx,i,None]
 return out
metrics=[];visual={}
for sample in load(O/'runtime_samples.json')['samples']:
 bones=sample['bones'];out=deform(bones);newarea=np.linalg.norm(np.cross(out[tris[:,1]]-out[tris[:,0]],out[tris[:,2]]-out[tris[:,0]]),axis=1);rat=np.divide(newarea,area,out=np.ones_like(area),where=valid);pos={n:np.array(bones[n]['component']['translation']) for n in names}
 fm={}
 for s in ['l','r']:
  ss=sole[s];fi=feet[s];foot=pos['foot_'+s];ball=pos['ball_'+s];heelidx=ss[np.argsort(rv[ss,1])[:max(1,len(ss)//5)]];ballidx=ss[np.argsort(rv[ss,1])[-max(1,len(ss)//5):]]
  fm[s]={'sole_min_z_cm':float(out[ss,2].min()),'sole_max_z_cm':float(out[ss,2].max()),'foot_surface_min_z_cm':float(out[fi,2].min()),'heel_min_z_cm':float(out[heelidx,2].min()),'toe_min_z_cm':float(out[ballidx,2].min()),'sole_centroid_xy_cm':out[ss,:2].mean(axis=0).tolist(),'ankle_cm':foot.tolist(),'ball_cm':ball.tolist(),'toe_pitch_deg':math.degrees(math.atan2((ball-foot)[2],np.linalg.norm((ball-foot)[:2])))}
 metric={k:sample[k] for k in ['role','time_s','fraction']};metric.update(finite=bool(np.isfinite(out).all()),root_cm=pos['root'].tolist(),pelvis_cm=pos['pelvis'].tolist(),max_bone_scale_error=max(abs(x-1) for b in bones.values() for x in b['local']['scale']),triangle_area_p01_median_p99=np.quantile(rat[valid],[.01,.5,.99]).tolist(),collapsed_triangles=int(((rat<.1)&valid).sum()),stretched_triangles=int(((rat>5)&valid).sum()),regions={k:{'triangles':len(ix),'collapsed':int((rat[ix]<.1).sum()),'stretched':int((rat[ix]>5).sum())} for k,ix in regions.items()},feet=fm)
 metrics.append(metric)
 if sample['fraction'] in [0,.25,.5,.75]:visual[sample['role']+'|'+str(sample['fraction'])]=out
summary=[]
for role in ['idle','walk','run','reach']:
 ms=[m for m in metrics if m['role']==role];foot_summary={}
 for s in ['l','r']:
  contacts=[(a,b) for a,b in zip(ms,ms[1:]) if abs(a['feet'][s]['sole_min_z_cm'])<=2 and abs(b['feet'][s]['sole_min_z_cm'])<=2]
  speeds=[math.dist(a['feet'][s]['sole_centroid_xy_cm'],b['feet'][s]['sole_centroid_xy_cm'])/(b['time_s']-a['time_s']) for a,b in contacts]
  foot_summary[s]={'sole_height_range_cm':[min(m['feet'][s]['sole_min_z_cm'] for m in ms),max(m['feet'][s]['sole_min_z_cm'] for m in ms)],'near_ground_interval_count':len(contacts),'near_ground_surface_slide_speed_cm_s_max':max(speeds,default=None),'toe_pitch_range_deg':[min(m['feet'][s]['toe_pitch_deg'] for m in ms),max(m['feet'][s]['toe_pitch_deg'] for m in ms)]}
 summary.append({'role':role,'samples':len(ms),'max_collapsed_triangles':max(m['collapsed_triangles'] for m in ms),'max_stretched_triangles':max(m['stretched_triangles'] for m in ms),'max_bone_scale_error':max(m['max_bone_scale_error'] for m in ms),'root_max_distance_cm':max(math.dist(m['root_cm'],[0,0,0]) for m in ms),'regions':{k:{'max_collapsed':max(m['regions'][k]['collapsed'] for m in ms),'max_stretched':max(m['regions'][k]['stretched'] for m in ms)} for k in regions},'feet':foot_summary})
save('deformation_contact_results.json',{'status':'measured_pending_visual_review','method':'CPU LBS of actual UE weights and 244 UE baked poses; 10%/5x area flags and +/-2cm contact window are explicit diagnostic screens, not anatomy gate changes','limits':'No cloth/morph/physics; static in-place actor at ground Z=0; apparent slide measured in component space with no locomotion displacement','summary':summary,'samples':metrics})
np.savez_compressed(W/'animated_surface_samples.npz',triangles=tris,reference=rv,**{k.replace('|','_'):x for k,x in visual.items()})
print(json.dumps(summary,indent=2))
