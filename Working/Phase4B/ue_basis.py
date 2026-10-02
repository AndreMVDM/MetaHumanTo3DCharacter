"""READ ONLY Phase4A static asset to verify old DCC/UE coordinate mapping for control evaluation."""
import unreal,json
from pathlib import Path
W=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4B');dm=unreal.DynamicMesh();opts=unreal.GeometryScriptCopyMeshFromAssetOptions();opts.set_editor_property('apply_build_settings',False)
unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase4A/Unrigged/Geometry/SM_Lara'),dm,opts,unreal.GeometryScriptMeshReadLOD());Q=unreal.GeometryScript_MeshQueries;rows=[]
for i in range(Q.get_num_vertex_i_ds(dm)):
    p,ok=Q.get_vertex_position(dm,i)
    if ok:rows.append([p.x,p.y,p.z])
(W/'phase4a_ue_vertices_readonly.json').write_text(json.dumps(rows));print('PHASE4B_CONTROL_BASIS_READ_ONLY',len(rows))
