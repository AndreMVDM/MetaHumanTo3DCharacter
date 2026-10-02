"""Rigidly reorient source geometry to test frame inference without FBX axes."""
import numpy as np,json,math
from pathlib import Path
from geometry_tools import body_frame
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B';v=np.load(W/'source_geometry.npz')['vertices'];reference=np.load(W/'normalised_geometry.npz')['vertices'];rows=[]
def rot(axis,deg):
    a=np.eye(3)[axis];x,y,z=a;t=math.radians(deg);K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]]);return np.eye(3)*math.cos(t)+(1-math.cos(t))*np.outer(a,a)+math.sin(t)*K
for name,M in [('yaw90',rot(2,90)),('oblique',rot(2,83)@rot(1,22)@rot(0,13)),('upside_down',rot(0,180))]:
    transformed=v@M.T+np.array([37.,-19.,62.]);got,frame=body_frame(transformed);delta=np.linalg.norm(got-reference,axis=1);rows.append({'case':name,'max_corresponding_vertex_difference_cm':float(delta.max()),'mean_cm':float(delta.mean()),'pass':bool(delta.max()<.1),'inferred_height_cm':float(np.ptp(got[:,2]))});print(name,rows[-1],flush=True)
(O/'coordinate_frame_validation.json').write_text(json.dumps({'rigid_reorientation_tests':rows,'tolerance_cm':.1,'passed':all(r['pass'] for r in rows),'limit':'Same Lara topology/pose only; no additional humanoid generalisation or guarantee under scale/pose/accessory changes.'},indent=2))
