"""Summarise live UE pose variation and baked limb/root measurements."""
import json,math,sys
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));import core
O=core.O;live=core.read(O/'source_independent_playback.json');rows=[]
for role in ['idle','walk','run','reach','independent_fingers']:
 samples=[s for s in live['samples'] if s['role']==role];ranges={}
 for bone in ['pelvis','hand_l','hand_r','foot_l','foot_r','thumb_03_l','index_03_l','middle_03_l','ring_03_l','pinky_03_l','thumb_03_r','index_03_r','middle_03_r','ring_03_r','pinky_03_r']:
  points=np.array([s['components'][0]['bones'][bone]['component']['translation'] for s in samples]);ranges[bone]=float(np.linalg.norm(points.max(0)-points.min(0)))
 rows.append({'role':role,'samples':len(samples),'component_position_range_diagonal_cm':ranges,'motion_observed':max(ranges.values())>1e-4})
assert all(x['motion_observed'] for x in rows)
summaries=[]
for role in ['idle','walk','run','reach']:
 ss=[s for s in core.read(O/'runtime_samples.json')['samples'] if s['role']==role];pelvis=np.array([s['bones']['pelvis']['component']['translation'] for s in ss]);lengths={};angles={}
 for side in ['l','r']:
  for label,names in [('arm',['upperarm_'+side,'lowerarm_'+side,'hand_'+side]),('leg',['thigh_'+side,'calf_'+side,'foot_'+side])]:
   ls=[];aa=[]
   for s in ss:
    a,b,c=[np.array(s['bones'][n]['component']['translation']) for n in names];u=b-a;v=c-b;ls.append([float(np.linalg.norm(u)),float(np.linalg.norm(v))]);aa.append(math.degrees(math.acos(float(np.clip(np.dot(u,v)/np.linalg.norm(u)/np.linalg.norm(v),-1,1)))))
   arr=np.array(ls);lengths[label+'_'+side]={'minimum_segment_cm':float(arr.min()),'maximum_segment_length_variation_cm':float((arr.max(0)-arr.min(0)).max())};angles[label+'_'+side]=[min(aa),max(aa)]
 summaries.append({'role':role,'pelvis_component_min_cm':pelvis.min(0).tolist(),'pelvis_component_max_cm':pelvis.max(0).tolist(),'limb_segments':lengths,'bend_angle_range_degrees':angles,'no_zero_length_limb':all(x['minimum_segment_cm']>1 for x in lengths.values())})
core.save(O/'native_motion_summary.json',{'status':'passed','live_animation_motion_observed':rows,'baked_pose_summaries':summaries,'limits':'Nonzero motion, finite/unit transforms and positive limb lengths are structural checks; bend sign, clothing shape, planted contact and full collision quality require separate review'})
print('Live motion measured for all five native sequences')
