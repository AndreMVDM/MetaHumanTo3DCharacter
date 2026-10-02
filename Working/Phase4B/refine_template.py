"""Second method: bilateral semantic-template consensus, evaluated independently of manual control."""
import json,copy,math,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase4B';W=P/'Working/Phase4B'
fit=json.loads((O/'automatic_fit.json').read_text());j={r['role']:r for r in fit['joints']};changes=[]
for role in ['clavicle','upperarm','lowerarm','thigh','calf','foot','ball','hand']:
    a=j[role+'_l'];b=j[role+'_r'];pa=np.array(a['position_cm']);pb=np.array(b['position_cm']);pb[0]*=-1
    # Jointly select bend height by sum of bilateral target-curve fit costs.
    if role in ['lowerarm','calf']:
        ac=a['competing_candidates'];bc=b['competing_candidates'];pairs=[]
        for aa in ac:
            for bb in bc:
                dz=abs(aa['position_cm'][2]-bb['position_cm'][2]);pairs.append((aa['residual_cm2']+bb['residual_cm2']+8*dz**2,aa,bb))
        _,aa,bb=min(pairs,key=lambda q:q[0]);pa=np.array(aa['position_cm']);pb=np.array(bb['position_cm']);pb[0]*=-1
    mean=(pa+pb)/2
    for r,sign in [(a,1),(b,-1)]:
        old=r['position_cm'];pos=mean.copy();pos[0]*=sign;r['position_cm']=pos.tolist();r['evidence_sources'].append({'method':'Bilateral target-geometry consensus, mirrored position average; shared bend cost where available','pre_consensus_position_cm':old});changes.append({'role':r['role'],'delta_cm':float(np.linalg.norm(np.array(old)-pos))})
        if role=='foot':
            r['status']='ambiguous';r['ambiguity_flags'].append('boot_opening_narrowing_does_not_identify_internal_ankle')
# Head midpoint includes a large hair bun; position inside surface does not resolve head articulation.
j['head']['status']='ambiguous';j['head']['ambiguity_flags'].append('hair_envelope_head_centre_not_certified')
fit['method']='Second method: symmetry-constrained semantic template and joint bilateral bend-cost minimisation';fit['refinement_changes']=changes
fit['independence']='No manual-control file imported; correction count remains zero'
(O/'automatic_fit_v2.json').write_text(json.dumps(fit,indent=2))
# Track separated fingertip contour branches across neighbouring slices. Names/root articulation remain unresolved.
tracks={}
for side in ['l','r']:
    branches=[];active=[]
    for row in fit['features']['fingers_'+side]['slice_branch_evidence']:
        candidates=[c for c in row['candidates'] if c['count']>=6]
        next_active=[];used=set()
        for branch in active:
            p=np.array(branch[-1]['centre']);matches=[(float(np.linalg.norm(np.array(c['centre'])-p)),i,c) for i,c in enumerate(candidates) if i not in used]
            if matches and min(matches)[0]<2.2:
                _,idx,c=min(matches,key=lambda q:q[0]);used.add(idx);branch.append(c);next_active.append(branch)
            else:branches.append(branch)
        for i,c in enumerate(candidates):
            if i not in used:next_active.append([c])
        active=next_active
    branches.extend(active);long=[b for b in branches if len(b)>=4 and b[-1]['centre'][2]-b[0]['centre'][2]>=3]
    tracks[side]=[]
    for idx,b in enumerate(long):
        pts=np.array([c['centre'] for c in b]);ids=[len(b)-1,len(b)//2,0]
        tracks[side].append({'candidate_id':f'digit_branch_{idx+1}_{side}','sample_count':len(b),'extent_cm':float(np.linalg.norm(pts[-1]-pts[0])),'connected_joint_proposal_cm':pts[ids].tolist(),'ordered_surface_section_centres_cm':pts.tolist(),'status':'ambiguous_not_bound','unresolved':['thumb/index/middle/ring/pinky semantic identity','metacarpal root in palm','true articulation locations'],'bone_chains_accepted':0})
(O/'finger_branch_prototype.json').write_text(json.dumps({'method':'Surface section component tracking; max adjacent centroid separation 2.2cm, min4 samples; no fabricated semantic names','sides':tracks,'automatically_accepted_finger_chains':0},indent=2))
print('REFINED',len(changes),max(c['delta_cm'] for c in changes),'FINGER_BRANCHES',[(s,len(b)) for s,b in tracks.items()])
