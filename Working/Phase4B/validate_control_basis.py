import numpy as np,json,itertools,hashlib
from pathlib import Path
from geometry_tools import nearest_distances
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B';srcpath=P/'Working/Phase4A/Unrigged_geometry.json';src=json.loads(srcpath.read_text());v=np.array(src['vertex_positions_cm']);ue=np.array(json.loads((W/'phase4a_ue_vertices_readonly.json').read_text()));rows=[]
for signs in itertools.product([-1,1],repeat=3):
    dist=nearest_distances(v[::max(1,len(v)//160)]*signs,ue);rows.append({'signs':signs,'sample_count':len(dist),'max_cm':float(dist.max()),'mean_cm':float(dist.mean())})
best=min(rows,key=lambda r:r['mean_cm']);assert tuple(best['signs'])==(1,-1,1) and best['max_cm']<1e-4
(O/'manual_control_basis_validation.json').write_text(json.dumps({'read_only_phase4a_asset':'/Game/MetaHumanTo3DCharacter/Phase4A/Unrigged/Geometry/SM_Lara','dcc_geometry_sha256':hashlib.sha256(srcpath.read_bytes()).hexdigest(),'tested_axis_signs':rows,'verified_dcc_to_ue_signs':best['signs'],'max_sample_error_cm':best['max_cm'],'source_asset_modified':False},indent=2));print('CONTROL_BASIS',best)
