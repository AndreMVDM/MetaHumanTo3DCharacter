import unreal,json
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4B';mesh=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase4B/Geometry/SM_Lara180');dm=unreal.DynamicMesh();opts=unreal.GeometryScriptCopyMeshFromAssetOptions();opts.set_editor_property('apply_build_settings',False);unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dm,opts,unreal.GeometryScriptMeshReadLOD());Q=unreal.GeometryScript_MeshQueries;UV=unreal.GeometryScript_UVs;rows=[]
for i in range(Q.get_num_triangle_i_ds(dm)):
    ids,valid=Q.get_triangle_indices(dm,i)
    if not valid:continue
    _,uids,valid=UV.get_mesh_triangle_uv_element_i_ds(dm,0,i)
    if not valid:raise RuntimeError('triangle has no UV')
    for vi,ui in zip([ids.x,ids.y,ids.z],[uids.x,uids.y,uids.z]):
        v,ok=Q.get_vertex_position(dm,vi);_,uv,ok=UV.get_mesh_uv_element_position(dm,0,ui);assert ok;rows.append([v.x,v.y,v.z,uv.x,uv.y])
(W/'ue_uv_corners.json').write_text(json.dumps(rows));print('PHASE4B_UV_READBACK',len(rows))
