"""Apply generic representation conversion to an isolated derived mesh, inspect invariants."""
import unreal,sys,json,traceback,math,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/UnitCorrection';O.mkdir(exist_ok=True);B='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/UnitCorrection';sys.path.insert(0,str(R/'Working/Phase4F'));from rigged_unit_canonicalisation import derive
def tr(t):return dict(translation=[t.translation.x,t.translation.y,t.translation.z],rotation_xyzw=[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],scale=[t.scale3d.x,t.scale3d.y,t.scale3d.z])
r=dict(status='running',original_assets_edited=False)
try:
    original=json.loads((O.parent/'native_reload.json').read_text());source=unreal.load_asset(original['mesh']);mesh,p=derive(unreal,source,B+'/Character','SK_Canonical','SKEL_Canonical',original['bones']);r['conversion']=p
    ref=mesh.skeleton.get_reference_pose();c=unreal.new_object(unreal.SkeletalMeshComponent);c.set_skeletal_mesh_asset(mesh);bones={str(n):dict(parent=None if str(c.get_parent_bone(n))=='None' else str(c.get_parent_bone(n)),local=tr(ref.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),component=tr(ref.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))) for n in ref.get_bone_names()};assert set(bones)==set(original['bones'])
    r['bind_position_max_error_cm']=max(math.dist(b['component']['translation'],original['bones'][n]['component']['translation']) for n,b in bones.items());r['hierarchy_preserved']=all(b['parent']==original['bones'][n]['parent'] for n,b in bones.items());r['bones']=bones
    dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL,lod_index=0));Q=unreal.GeometryScript_MeshQueries;BW=unreal.GeometryScript_BoneWeights;_,info=BW.get_all_bones_info(dm);ns={b.index:str(b.name) for b in info};vertices=[];weights=[];triangles=[]
    for i in range(Q.get_num_vertex_i_ds(dm)):
        v,_=Q.get_vertex_position(dm,i);vertices.append([v.x,v.y,v.z]);_,ws,ok=BW.get_vertex_bone_weights(dm,i);assert ok;weights.append([[ns[w.bone_index],float(w.weight)] for w in ws if w.weight>0])
    for i in range(Q.get_num_triangle_i_ds(dm)):
        t,ok=Q.get_triangle_indices(dm,i);assert ok;triangles.append([t.x,t.y,t.z])
    r['geometry_skin_sha256']=hashlib.sha256(json.dumps([vertices,triangles,weights],sort_keys=True).encode()).hexdigest();r['geometry_skin_identical']=r['geometry_skin_sha256']==original['geometry_skin_sha256'];r['bounds_height_cm']=2*mesh.get_bounds().box_extent.z
    assert r['hierarchy_preserved'] and r['geometry_skin_identical'] and r['bind_position_max_error_cm']<.001
    r.update(status='passed',mesh=mesh.get_path_name(),skeleton=mesh.skeleton.get_path_name())
except Exception:r.update(status='failed',error=traceback.format_exc())
(O/'canonicalisation.json').write_text(json.dumps(r,indent=2));print('UNIT_CANONICALISATION',r['status'],r.get('error',''))
