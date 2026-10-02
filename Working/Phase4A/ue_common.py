import unreal,json,math,sys,hashlib,collections
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4A';O=P/'Documentation/Phase4A'
sys.dont_write_bytecode=True;sys.path.insert(0,str(P/'Working/Phase3B'));import common
save=lambda n,x:(O/n).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
def copy_static(mesh):
    dm=unreal.DynamicMesh();opts=unreal.GeometryScriptCopyMeshFromAssetOptions();opts.set_editor_property('apply_build_settings',False)
    unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dm,opts,unreal.GeometryScriptMeshReadLOD());return dm
def state(dm):
    Q=unreal.GeometryScript_MeshQueries;U=unreal.GeometryScript_UVs
    vertices=[];uv=[];triangles=[]
    for i in range(Q.get_num_vertex_i_ds(dm)):
        v,ok=Q.get_vertex_position(dm,i);vertices.append([v.x,v.y,v.z] if ok else None)
    for i in range(Q.get_num_triangle_i_ds(dm)):
        ids,ok=Q.get_triangle_indices(dm,i)
        if ok:triangles.append([ids.x,ids.y,ids.z])
        if Q.get_num_uv_sets(dm):
            _,uids,valid=U.get_mesh_triangle_uv_element_i_ds(dm,0,i)
            if valid:
                uv.append([[U.get_mesh_uv_element_position(dm,0,j)[1].x,U.get_mesh_uv_element_position(dm,0,j)[1].y] for j in [uids.x,uids.y,uids.z]])
    return {'vertices':vertices,'triangles':triangles,'uv_sets':Q.get_num_uv_sets(dm),'triangle_uv_sha256':hashlib.sha256(json.dumps(uv).encode()).hexdigest()}
def weights(dm):
    out=[];hist=collections.Counter();invalid=[]
    for i in range(unreal.GeometryScript_MeshQueries.get_num_vertex_i_ds(dm)):
        _,ws,valid=unreal.GeometryScript_BoneWeights.get_vertex_bone_weights(dm,i);pairs=[[w.bone_index,w.weight] for w in ws if w.weight>0];out.append(pairs);hist[len(pairs)]+=1
        if not valid or not pairs or abs(sum(w[1] for w in pairs)-1)>0.001:invalid.append(i)
    return out,{'influence_histogram':dict(hist),'invalid_or_unweighted_vertices':invalid,'max_influences':max(hist)}
