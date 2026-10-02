import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4C';O=P/'Documentation/Phase4C'
sys.path.insert(0,str(P/'Working/Phase4B'))
from geometry_tools import body_frame
d=np.load(W/'source_geometry.npz');v=d['vertices']; t=d['triangles']
vn,frame=body_frame(v)
R=np.array(frame['rotation_columns_world']);org=np.array(frame['origin_body_coordinates_cm']);s=frame['factor']
back=(vn/s+org)@R.T
np.savez(W/'normalised_geometry.npz',vertices=vn,triangles=t)
(W/'target_geometry.json').write_text(json.dumps({'vertices_cm':vn.tolist(),'triangle_indices':t.ravel().tolist()}))
(O/'coordinate_frame.json').write_text(json.dumps(frame,indent=2))
(O/'transform_mapping.json').write_text(json.dumps({'row_vector_forward':'canonical = (source_world_cm @ R - origin) * scale','row_vector_inverse':'source_world_cm = (canonical / scale + origin) @ R.T','R':R.tolist(),'origin':org.tolist(),'scale':s,'determinant':float(np.linalg.det(R)),'round_trip_max_cm':float(np.max(np.linalg.norm(back-v,axis=1))),'height_cm':float(np.ptp(vn[:,2])),'source_geometry_changed':False,'donor_mapping_status':'pending actual solve coordinate validation'},indent=2))
print('normalised',frame['source_height_cm'],s,np.ptp(vn[:,2]),np.max(np.linalg.norm(back-v,axis=1)))
