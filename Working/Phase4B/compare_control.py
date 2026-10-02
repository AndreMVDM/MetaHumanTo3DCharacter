"""Evaluation only: imports manual Phase4A locations AFTER automatic_fit.json exists."""
import json,numpy as np,hashlib,math,sys
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B'
suffix=sys.argv[1] if len(sys.argv)>1 else '';assert suffix in ['', '_v2']
proposalpath=O/('automatic_fit'+suffix+'.json');proposal=json.loads(proposalpath.read_text());before=hashlib.sha256(proposalpath.read_bytes()).hexdigest()
controlpath=P/'Documentation/Phase4A/assisted_candidates_ball_forward.json';control=next(r for r in json.loads(controlpath.read_text()) if r['case']=='Unrigged');frame=json.loads((O/'coordinate_frame.json').read_text())
f4a=json.loads((P/'Working/Phase4A/Unrigged_geometry.json').read_text())['uniform_factor'];R=np.array(frame['rotation_columns_world']);origin=np.array(frame['origin_body_coordinates_cm']);f=frame['factor']
manual={n:np.array(pos) for n,parent,pos in control['authored_landmarks_cm']};manual['root']=np.zeros(3)
# Phase4A saved UE surface is DCC Y negated by scene conversion. Convert UE cm -> DCC world cm -> inferred body frame.
aligned={n:((point/f4a*np.array([1,-1,1]))@R-origin)*f for n,point in manual.items()}
p={r['role']:np.array(r['position_cm']) for r in proposal['joints']};parents={r['role']:r['parent_role'] for r in proposal['joints']};mp=dict((n,parent) for n,parent,pos in control['authored_landmarks_cm']);mp['root']=None
rows=[]
for n,point in p.items():
    c=aligned[n];distance=float(np.linalg.norm(point-c));par=parents[n];angle=None
    if par:
        a=point-p[par];b=c-aligned[par];angle=math.degrees(math.acos(float(np.clip(a@b/(np.linalg.norm(a)*np.linalg.norm(b)),-1,1))))
    rows.append({'role':n,'automatic_cm':point.tolist(),'control_original_ue_cm':manual[n].tolist(),'control_in_inferred_frame_cm':c.tolist(),'absolute_difference_cm':distance,'normalised_by_height':distance/180,'parent_segment_angle_difference_deg':angle,'same_parent_role':parents[n]==mp[n]})
result={'evaluation_only':True,'automatic_proposal_unchanged_sha256':before,'control':str(controlpath),'control_sha256':hashlib.sha256(controlpath.read_bytes()).hexdigest(),'alignment':'Invert Phase4A uniform factor; Verified UE Y-only handedness conversion inversion; apply Phase4B inferred body frame and final-height factor','manual_control_limit':'Approximate authored Phase4A joints, not anatomical ground truth. Positional agreement does not prove semantic accuracy.','joint_count':len(rows),'mean_difference_cm':float(np.mean([r['absolute_difference_cm'] for r in rows])),'max_difference_cm':max(r['absolute_difference_cm'] for r in rows),'hierarchy_equivalent_for_body':all(r['same_parent_role'] for r in rows),'joints':rows}
assert before==hashlib.sha256(proposalpath.read_bytes()).hexdigest()
(O/('manual_control_comparison'+suffix+'.json')).write_text(json.dumps(result,indent=2));print('CONTROL',suffix,result['mean_difference_cm'],result['max_difference_cm'])
