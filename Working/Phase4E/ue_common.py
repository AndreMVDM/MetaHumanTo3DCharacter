import sys, json, hashlib, collections, traceback, time
from pathlib import Path
import unreal
sys.dont_write_bytecode=True
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter'); W=P/'Working/Phase4E'; O=P/'Documentation/Phase4E'
B='/Game/MetaHumanTo3DCharacter/Phase4E'; D='/Game/MetaHumanTo3DCharacter/Phase4D'
def save(n,d): (O/n).write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
def dm_from(mesh):
    dm=unreal.DynamicMesh()
    unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD())
    return dm
def state(dm):
    Q=unreal.GeometryScript_MeshQueries; U=unreal.GeometryScript_UVs
    vertices=[];triangles=[];uv=[]
    for i in range(Q.get_num_vertex_i_ds(dm)):
        p,ok=Q.get_vertex_position(dm,i);assert ok;vertices.append([p.x,p.y,p.z])
    for i in range(Q.get_num_triangle_i_ds(dm)):
        ids,ok=Q.get_triangle_indices(dm,i)
        if ok: triangles.append([ids.x,ids.y,ids.z])
        if Q.get_num_uv_sets(dm):
            _,ids,valid=U.get_mesh_triangle_uv_element_i_ds(dm,0,i)
            if valid:uv.append([[U.get_mesh_uv_element_position(dm,0,j)[1].x,U.get_mesh_uv_element_position(dm,0,j)[1].y] for j in [ids.x,ids.y,ids.z]])
    return {'vertices':vertices,'triangles':triangles,'uv_sets':Q.get_num_uv_sets(dm),'triangle_uv_sha256':hashlib.sha256(json.dumps(uv).encode()).hexdigest()}
def weights(dm):
    out=[]
    for i in range(unreal.GeometryScript_MeshQueries.get_num_vertex_i_ds(dm)):
        _,ws,ok=unreal.GeometryScript_BoneWeights.get_vertex_bone_weights(dm,i);assert ok
        out.append([[w.bone_index,w.weight] for w in ws if w.weight>0])
    return out
def stats(ws):
    return {'vertices':len(ws),'influences':dict(collections.Counter(len(w) for w in ws)),'normalisation_error_max':max(abs(sum(w for _,w in row)-1) for row in ws),'unweighted':sum(not row for row in ws)}
def tr(t):
    return {'translation':[t.translation.x,t.translation.y,t.translation.z],'rotation_xyzw':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'scale':[t.scale3d.x,t.scale3d.y,t.scale3d.z]}
def reference(mesh):
    pose=mesh.skeleton.get_reference_pose()
    return {str(n):{'local':tr(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),'component':tr(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))} for n in pose.get_bone_names()}
