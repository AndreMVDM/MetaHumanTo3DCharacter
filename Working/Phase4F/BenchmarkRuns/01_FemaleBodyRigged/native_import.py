"""Existing Unreal import/inspection APIs, isolated Benchmark 1 assets only."""
import unreal,json,traceback,sys,hashlib,math,collections
from pathlib import Path
sys.dont_write_bytecode=True
R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=R/'Working/Phase4F/BenchmarkRuns/01_FemaleBodyRigged';O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';BASE='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged'
reload='-benchmark-reload' in unreal.SystemLibrary.get_command_line();r=dict(status='running',fresh_process=True,reload_only=reload,engine_version=unreal.SystemLibrary.get_engine_version(),source_mutated=False)
def v(x):return [float(x.x),float(x.y),float(x.z)]
def tr(x):return dict(translation=v(x.translation),rotation_xyzw=[x.rotation.x,x.rotation.y,x.rotation.z,x.rotation.w],scale=v(x.scale3d))
try:
    if not reload:
        assert not unreal.EditorAssetLibrary.list_assets(BASE,True,False),'refuse overwrite'
        options=unreal.FbxImportUI();options.set_editor_properties(dict(import_as_skeletal=True,mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH,import_animations=False,import_materials=False,import_textures=False,create_physics_asset=True,skeleton=None))
        task=unreal.AssetImportTask();task.set_editor_properties(dict(filename=str(next((W/'Input').glob('*.fbx'))),destination_path=BASE+'/Character',destination_name='SK_FemaleBodyRigged',automated=True,save=True,replace_existing=False,options=options))
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);r['imported_paths']=list(task.imported_object_paths)
    assets=[unreal.load_asset(p) for p in unreal.EditorAssetLibrary.list_assets(BASE+'/Character',True,False)];meshes=[x for x in assets if isinstance(x,unreal.SkeletalMesh)];assert len(meshes)==1,'expected one native skeletal mesh'
    mesh=meshes[0];sk=mesh.skeleton;assert sk,'missing skeleton';ref=sk.get_reference_pose();names=[str(n) for n in ref.get_bone_names()]
    c=unreal.new_object(unreal.SkeletalMeshComponent);c.set_skeletal_mesh_asset(mesh)
    parents={n:str(c.get_parent_bone(n)) for n in names};parents={n:None if p=='None' else p for n,p in parents.items()}
    bones={n:dict(parent=parents[n],local=tr(ref.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),component=tr(ref.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))) for n in names}
    dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL,lod_index=0))
    Q=unreal.GeometryScript_MeshQueries;BW=unreal.GeometryScript_BoneWeights;_,infos=BW.get_all_bones_info(dm);bone_indices={b.index:str(b.name) for b in infos};vertices=[];weights=[];triangles=[];invalid=[];hist=collections.Counter()
    for i in range(Q.get_num_vertex_i_ds(dm)):
        x,ok=Q.get_vertex_position(dm,i);assert ok;vertices.append(v(x));_,ws,ok=BW.get_vertex_bone_weights(dm,i);assert ok
        pairs=[[bone_indices[w.bone_index],float(w.weight)] for w in ws if w.weight>0];weights.append(pairs);hist[len(pairs)]+=1
        if not pairs or any(n not in names or not math.isfinite(w) or w<0 for n,w in pairs) or abs(sum(w for _,w in pairs)-1)>.001:invalid.append(i)
    for i in range(Q.get_num_triangle_i_ds(dm)):
        x,ok=Q.get_triangle_indices(dm,i);assert ok;triangles.append([x.x,x.y,x.z])
    bounds=mesh.get_bounds();r.update(status='passed',mesh=mesh.get_path_name(),skeleton=sk.get_path_name(),asset_inventory=[dict(path=x.get_path_name(),type=x.get_class().get_name()) for x in assets],bones=bones,bone_count=len(names),root_names=[n for n,p in parents.items() if p is None],bounds=dict(origin=v(bounds.origin),extent=v(bounds.box_extent),height_cm=2*bounds.box_extent.z),native_geometry=dict(vertices_cm=vertices,triangles=triangles,weights=weights,bone_index_names=bone_indices),vertex_count=len(vertices),triangle_count=len(triangles),weight_summary=dict(histogram=dict(hist),invalid_vertices=invalid,maximum_weight_sum_error=max(abs(sum(w for _,w in ws)-1) for ws in weights)),finite_geometry=all(math.isfinite(x) for p in vertices for x in p),hierarchy_bind_sha256=hashlib.sha256(json.dumps(bones,sort_keys=True).encode()).hexdigest(),geometry_skin_sha256=hashlib.sha256(json.dumps([vertices,triangles,weights],sort_keys=True).encode()).hexdigest(),skeleton_rebuilt=False)
except Exception:r.update(status='failed',error=traceback.format_exc())
(O/('native_reload.json' if reload else 'native_import.json')).write_text(json.dumps(r,indent=2));print('BENCHMARK_IMPORT',r['status'],r.get('error',''),{k:r.get(k) for k in ['mesh','skeleton','bone_count','root_names','vertex_count','triangle_count','bounds','weight_summary']})
