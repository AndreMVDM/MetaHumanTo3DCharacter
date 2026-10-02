import sys,traceback,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common import *
B='/Game/MetaHumanTo3DCharacter/Phase4A';out={'errors':[]};T=unreal.AssetToolsHelpers.get_asset_tools()
try:
    static=unreal.load_asset(B+'/Unrigged/Geometry/SM_Lara');dm=copy_static(static);Q=unreal.GeometryScript_MeshQueries;U=unreal.GeometryScript_UVs;uv=[]
    for tid in range(dm.get_triangle_count()):
        _,ids,ok=U.get_mesh_triangle_uv_element_i_ds(dm,0,tid)
        if ok:
            for i in [ids.x,ids.y,ids.z]:
                _,p,valid=U.get_mesh_uv_element_position(dm,0,i)
                if valid:uv.append([p.x,p.y])
    original=json.loads((W/'Unrigged_geometry.json').read_text())['uv_loops'];norm=lambda pairs:{(round(u,5),round(v,5)) for u,v in pairs};a=norm(original);b=norm(uv);flipped=[(u,1-v) for u,v in original];flip=norm(flipped);buckets={}
    for u,v in uv:buckets.setdefault((int(u*1e5),int(v*1e5)),[]).append((u,v))
    distances=[]
    for u,v in flipped:
        key=(int(u*1e5),int(v*1e5));near=[p for dx in [-1,0,1] for dy in [-1,0,1] for p in buckets.get((key[0]+dx,key[1]+dy),[])];assert near;distances.append(min(math.dist((u,v),p) for p in near))
    out['uv_import_comparison']={'source_unique_round5':len(a),'ue_unique_round5':len(b),'direct_set_equal':a==b,'v_flipped_set_equal':flip==b,'difference_count_after_v_flip':len(flip^b),'max_source_to_ue_coordinate_error_after_v_flip':max(distances),'source_values_within_1e_6':all(d<1e-6 for d in distances),'note':'UV coordinate set comparison, not corner attachment proof. Within-UE triangle/corner hashes and unchanged mesh states prove no subsequent rigging UV change; before/after rendering validates attachment visually.'}
except Exception:out['errors'].append(traceback.format_exc())
save('uv_import_validation.json',out);print('PRESERVATION_DONE',out)
