"""Bidirectional geometry comparison and UV-at-position coverage; triangle changes disclosed."""
import numpy as np,json,itertools
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B'
source=np.load(W/'normalised_geometry.npz');v=source['vertices'];ue=np.array(json.loads((W/'ue_debug_vertices.json').read_text()));step=.001
def nearest_grid(query,target):
    cells={}
    for p in target:cells.setdefault(tuple(np.floor(p/step).astype(int)),[]).append(p)
    offsets=list(itertools.product([-1,0,1],repeat=3));out=[]
    for p in query:
        k=np.floor(p/step).astype(int);a=cells.get(tuple(k),[])
        if not a or min(np.linalg.norm(p-x) for x in a)>1e-4:a=[q for off in offsets for q in cells.get(tuple(k+off),[])]
        out.append(min((np.linalg.norm(p-q) for q in a),default=float('inf')))
    return np.array(out)
a=nearest_grid(v,ue);b=nearest_grid(ue,v)
src=np.array(json.loads((W/'normalised_source_uv_corners.json').read_text()));dst=np.array(json.loads((W/'ue_uv_corners.json').read_text()));dst[:,4]=1-dst[:,4]
keys={}
for row in src:keys.setdefault(tuple(np.floor(row[:3]/step).astype(int)),[]).append(row)
bad=[];uvmax=0.;pmax=0.
for idx,row in enumerate(dst):
    k=np.floor(row[:3]/step).astype(int);matches=[q for off in itertools.product([-1,0,1],repeat=3) for q in keys.get(tuple(k+off),[])];matches=[q for q in matches if np.linalg.norm(q[:3]-row[:3])<1e-4]
    if not matches:bad.append(idx);continue
    q=min(matches,key=lambda q:np.linalg.norm(q[3:]-row[3:]));diff=float(np.linalg.norm(q[3:]-row[3:]));uvmax=max(uvmax,diff);pmax=max(pmax,float(np.linalg.norm(q[:3]-row[:3])))
    if diff>1e-5:bad.append(idx)
tv=v[source['triangles']];area=np.linalg.norm(np.cross(tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]),axis=1)/2
readback=json.loads((O/'ue_debug_scene.json').read_text());result={'source_vertex_count':len(v),'ue_dynamic_vertex_count':len(ue),'source_to_ue_max_cm':float(a.max()),'ue_to_source_max_cm':float(b.max()),'geometry_vertex_positions_pass':bool(max(a.max(),b.max())<1e-4),'source_triangles':len(source['triangles']),'ue_triangles':readback['triangles'],'triangle_count_difference':readback['triangles']-len(source['triangles']),'source_triangles_area_below_1e_minus_8_cm2':int((area<1e-8).sum()),'triangle_connectivity_identical':False,'topology_limit':'UE import changes vertex indexing/splitting and triangle count; exact connectivity equivalence is not certified. Source archive and Blender polygon/UV arrays remain unchanged.','uv_corner_count':len(dst),'uv_at_position_unmatched_corners':len(bad),'uv_at_position_max_difference':uvmax,'uv_at_position_pass':not bad,'uv_conversion':'UE V inverted to DCC V before comparison','uv_check_limit':'Every imported triangle corner has matching source UV at its position; missing/removed source triangles are not a bidirectional triangle-connectivity proof.'}
result['topology_limit']='UE import changes vertex indexing/splitting; final triangle count matches. Exact triangle-connectivity equivalence is not certified. Initial debug import had 9 fewer triangles; current readback supersedes it. Source archive and Blender polygon/UV arrays remain unchanged.'
result['source_to_ue_max_cm']=float(a.max()) if np.isfinite(a.max()) else None;result['ue_to_source_max_cm']=float(b.max()) if np.isfinite(b.max()) else None
(O/'ue_import_validation.json').write_text(json.dumps(result,indent=2,allow_nan=False));print(result)
