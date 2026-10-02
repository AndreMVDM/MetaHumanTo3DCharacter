import json,numpy as np
from pathlib import Path
from mathutils import kdtree
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4A';O=P/'Documentation/Phase4A'
a=json.loads((W/'MixamoRecovered_geometry.json').read_text());b=json.loads((W/'Unrigged_geometry.json').read_text())
va=np.array(a['vertex_positions_cm']);vb=np.array(b['vertex_positions_cm']);kd=kdtree.KDTree(len(vb))
for i,v in enumerate(vb):kd.insert(v,i)
kd.balance();queries=[kd.find(v) for v in va];idx=[q[1] for q in queries];d=[q[2] for q in queries]
fa=sorted(tuple(sorted(idx[i] for i in f)) for f in a['faces']);fb=sorted(tuple(sorted(f)) for f in b['faces'])
c=json.loads((O/'geometry_comparison.json').read_text());c.update(nearest_vertex_max_cm=max(d),nearest_vertex_mean_cm=sum(d)/len(d),bijective_nearest_mapping=len(set(idx))==len(idx),faces_equal_after_bijective_remap=fa==fb,uv_equivalence=False,material_equivalence=False,comparison_note='Nearest-position correspondence after independent ground alignment and uniform 180 cm scaling; face comparison ignores winding.')
(O/'geometry_comparison.json').write_text(json.dumps(c,indent=2));(W/'mixamo_to_unrigged_vertex_mapping.json').write_text(json.dumps(idx));print('GEOMETRY_COMPARISON',max(d),len(set(idx)),fa==fb)
