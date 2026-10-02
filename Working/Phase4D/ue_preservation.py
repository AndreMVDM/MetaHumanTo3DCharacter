"""Read-only triangle/UV comparison and final Phase4D callback refresh."""
import unreal,sys,hashlib,json,importlib,builtins
from pathlib import Path
W=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4D');sys.path.insert(0,str(W));sys.dont_write_bytecode=True
import core
importlib.reload(core)
Q=unreal.GeometryScript_MeshQueries;UV=unreal.GeometryScript_UVs
def mesh_signature(path):
    mesh=unreal.load_asset(path);dm=unreal.DynamicMesh();opts=unreal.GeometryScriptCopyMeshFromAssetOptions();opts.set_editor_property('apply_build_settings',False)
    unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dm,opts,unreal.GeometryScriptMeshReadLOD())
    topology=hashlib.sha256();corners=hashlib.sha256();count=0
    for i in range(Q.get_num_triangle_i_ds(dm)):
        ids,valid=Q.get_triangle_indices(dm,i)
        if not valid:continue
        indices=[ids.x,ids.y,ids.z];topology.update(core.canonical(indices));count+=1
        _,uids,valid=UV.get_mesh_triangle_uv_element_i_ds(dm,0,i)
        if not valid:raise RuntimeError('missing triangle UV')
        for vi,ui in zip(indices,[uids.x,uids.y,uids.z]):
            p,ok=Q.get_vertex_position(dm,vi);assert ok
            _,uv,ok=UV.get_mesh_uv_element_position(dm,0,ui);assert ok
            corners.update(core.canonical([p.x,p.y,p.z,uv.x,uv.y]))
    return {'triangles':count,'triangle_indices_sha256':topology.hexdigest(),'position_uv_corners_sha256':corners.hexdigest(),'uv_sets':Q.get_num_uv_sets(dm),'height_cm':2*mesh.get_bounds().box_extent.z}
source=mesh_signature('/Game/MetaHumanTo3DCharacter/Phase4C/Geometry/SM_Lara180')
target=mesh_signature('/Game/MetaHumanTo3DCharacter/Phase4D/Geometry/SM_Lara180')
result={'passed':source==target,'source':source,'phase4d':target,'method':'exact ordered triangle indices and triangle-corner position/UV hash; build settings disabled','archive_sha256':core.file_sha(core.P/'Characters/Lara_UnRigged_Textured.zip'),'limit':'Normalised prior StaticMesh readback equivalence; archive/extracted source byte preservation verified separately; no skeletal mesh authored'}
core.save(core.O/'source_surface_preservation.json',result);assert result['passed']
tool=builtins.phase4d_tool
tool.state=core.rebuild(tool.state);core.export(tool.state);tool.publish('Ready for real anatomical review. Start measured trial before recording placements.')
print('PHASE4D_SOURCE_PRESERVATION',result)
