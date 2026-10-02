import json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4D';O=P/'Documentation/Phase4D'
load=lambda p:json.loads(p.read_text())
def matrix(t):
 x,y,z,w=t['rotation_xyzw'];m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]);m[:3,3]=t['translation'];return m
def angle(a,b):return math.degrees(2*math.acos(float(np.clip(abs(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))),0,1))))
d=load(W/'accepted_skin.json');names=list(d['reference']['bones']);rv=np.array(d['geometry']['vertices']);v=np.c_[rv,np.ones(len(rv))];wt=np.zeros((len(rv),len(names)))
for i,ws in enumerate(d['weights']):
 for b,w in ws:wt[i,b]+=w
refs={n:np.linalg.inv(matrix(b['component'])) for n,b in d['reference']['bones'].items()};fit=load(O/'current_proposal.json');chains=fit['finger_chains'];digits=list(chains);samples=load(O/'finger_pose_samples.json')['samples'];base=samples[0]['bones']
distances=np.stack([np.linalg.norm(rv[:,None,:]-np.array(chains[k]['path_cm'])[None,:,:],axis=2).min(axis=1) for k in digits],axis=1);nearest=distances.argmin(axis=1);groups={k:np.where((nearest==i)&(distances[:,i]<.9))[0] for i,k in enumerate(digits)}
def deform(bones):
 out=np.zeros((len(rv),3))
 for i,n in enumerate(names):
  ix=np.where(wt[:,i]>0)[0];out[ix]+=(v[ix]@(matrix(bones[n]['component'])@refs[n]).T)[:,:3]*wt[ix,i,None]
 return out
baseline_surface=deform(base);results=[];surfaces={};im=Image.new('RGB',(2000,1050),'#f7f9fc');draw=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
for sample in samples:
 active=sample['active_digit']
 if not active:continue
 bones=sample['bones'];out=deform(bones);surfaces[active]=out
 rotations={k:max(angle(base[f'{k.split("_")[0]}_0{i}_{k[-1]}']['local']['rotation_xyzw'],bones[f'{k.split("_")[0]}_0{i}_{k[-1]}']['local']['rotation_xyzw']) for i in [1,2,3]) for k in digits}
 ix=groups[active];bi=[names.index(f'{active.split("_")[0]}_0{i}_{active[-1]}') for i in [1,2,3]];ownweights=wt[ix][:,bi].sum(axis=1)
 support={};paths={}
 for k in digits:
  ns=[f'{k.split("_")[0]}_0{i}_{k[-1]}' for i in [1,2,3]];points=np.array([bones[n]['component']['translation'] for n in ns]);last=ns[-1];tip=(matrix(bones[last]['component'])@refs[last]@np.r_[chains[k]['tip_cm'],1])[:3];paths[k]=np.vstack([points,tip]);support[k]=float(np.linalg.norm(points[:,None,:]-out[groups[k]][None,:,:],axis=2).min(axis=1).max()) if len(groups[k]) else None
 collisions=[]
 for k in digits:
  if k==active or k[-1]!=active[-1]:continue
  a=paths[active];b=paths[k];sa=np.concatenate([np.linspace(x,y,21) for x,y in zip(a,a[1:])]);sb=np.concatenate([np.linspace(x,y,21) for x,y in zip(b,b[1:])]);sep=float(np.linalg.norm(sa[:,None,:]-sb[None,:,:],axis=2).min());collisions.append({'other':k,'min_sampled_bone_path_distance_cm':sep})
 results.append({'digit':active,'time_s':sample['time_s'],'local_rotation_degrees':rotations,'independent_semantic_motion_passed':rotations[active]>10 and max(v for k,v in rotations.items() if k!=active)<.1,'surface_vertices':len(ix),'own_chain_weight_mean':float(ownweights.mean()) if len(ix) else None,'surface_displacement_cm_max':float(np.linalg.norm(out[ix]-baseline_surface[ix],axis=1).max()) if len(ix) else None,'phalange_surface_support_cm':support[active],'bone_path_separation_screens':collisions,'no_sampled_chain_crossing':all(c['min_sampled_bone_path_distance_cm']>.25 for c in collisions)})
 side=0 if active[-1]=='l' else 1;col=['thumb','index','middle','ring','pinky'].index(active.split('_')[0]);origin=(col*400,50+side*500);hand_ix=np.concatenate([groups[k] for k in digits if k[-1]==active[-1]]);lo=out[hand_ix][:,[1,2]].min(axis=0);hi=out[hand_ix][:,[1,2]].max(axis=0);scale=min(350/(hi[0]-lo[0]),425/(hi[1]-lo[1]));centre=(hi+lo)/2
 def xy(p):return (origin[0]+200+(p[1]-centre[0])*scale,origin[1]+265-(p[2]-centre[1])*scale)
 draw.text((origin[0]+15,origin[1]+10),active+' isolated flex',font=font,fill='#172433')
 for k in digits:
  if k[-1]!=active[-1]:continue
  pi=paths[k]
  for p in out[groups[k]]:draw.point(xy(p),fill='#b9c2cc')
  colour='#cf3347' if k==active else '#307db8';draw.line([xy(p) for p in pi],fill=colour,width=3)
  for p in pi:
   x,y=xy(p);draw.ellipse((x-3,y-3,x+3,y+3),fill=colour)
draw.text((15,10),'Actual Lara baked finger fixture | Y/Z projections | Red: active digit; blue: other chains; grey: CPU-skinned surface',font=font,fill='#172433');im.save(O/'animated_finger_validation.png')
result={'status':'measured','semantic_independent_motion_passed':len(results)==10 and all(r['independent_semantic_motion_passed'] for r in results),'all_sampled_chain_separation_passed':all(r['no_sampled_chain_crossing'] for r in results),'all_phalange_support_passed':all(r['phalange_surface_support_cm'] is not None and r['phalange_surface_support_cm']<1.2 for r in results),'results':results,'limits':'One 45-degree diagnostic peak per digit; no exhaustive joint-range or continuous volumetric collision proof; reference digit vertices labelled by human-accepted target tracks; weight means are diagnostics, not anatomy approvals','corrections':[]}
(O/'finger_animation_validation.json').write_text(json.dumps(result,indent=2,allow_nan=False));print(json.dumps(result,indent=2))
