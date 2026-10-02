"""Read back Phase4B debug assets and capture static proposals; no rigging or animation."""
import unreal,json,time,traceback,hashlib
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase4B';W=P/'Working/Phase4B';B='/Game/MetaHumanTo3DCharacter/Phase4B'
mesh=unreal.load_asset(B+'/Geometry/SM_Lara180');b=mesh.get_bounds();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assets=list(unreal.EditorAssetLibrary.list_assets(B,recursive=True));rows=[]
for path in assets:
    a=unreal.load_asset(path);rows.append({'path':path,'class':a.get_class().get_name()})
result={'map':U.get_editor_world().get_path_name(),'assets':rows,'skeletal_assets_authored':sum(r['class'] in ['Skeleton','SkeletalMesh','AnimSequence','IKRigDefinition','IKRetargeter'] for r in rows),'height_cm':2*b.box_extent.z,'actor_count':len(A.get_all_level_actors()),'errors':[],'proposal':'automatic_fit_v2.json','mesh':mesh.get_path_name(),'material':mesh.get_material(0).get_path_name(),'geometry_scale_baked':True,'display_mesh_actor_scales':[[a.get_actor_scale3d().x,a.get_actor_scale3d().y,a.get_actor_scale3d().z] for a in A.get_all_level_actors() if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh==mesh],'import_warnings':['Nearly zero tangents and binormals, tolerance 1e-4; debug unlit material; no shading-quality certification']}
assert result['skeletal_assets_authored']==0
assert all(s==[1.,1.,1.] for s in result['display_mesh_actor_scales'])
dm=unreal.DynamicMesh();opts=unreal.GeometryScriptCopyMeshFromAssetOptions();opts.set_editor_property('apply_build_settings',False);unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dm,opts,unreal.GeometryScriptMeshReadLOD());Q=unreal.GeometryScript_MeshQueries
result['triangles']=dm.get_triangle_count();result['uv_sets']=Q.get_num_uv_sets(dm);vertices=[]
for i in range(Q.get_num_vertex_i_ds(dm)):
    p,ok=Q.get_vertex_position(dm,i)
    if ok:vertices.append([p.x,p.y,p.z])
(W/'ue_debug_vertices.json').write_text(json.dumps(vertices));result['vertex_count']=len(vertices)
(O/'ue_debug_scene.json').write_text(json.dumps(result,indent=2));print('PHASE4B_DEBUG_READBACK',result)
raw=next(a for a in A.get_all_level_actors() if a.get_actor_label().startswith('Original textured'))
exec((W/'ue_uv.py').read_text())
exec((W/'ue_basis.py').read_text())
views=[('ue_fit_front',[0,265,90],[0,-90,0]),('ue_fit_side',[330,0,90],[0,180,0])];stage=0;start=time.monotonic()
def tick(dt):
    global stage,start
    if time.monotonic()-start<2:return
    if stage>=len(views)*2:
        raw.set_is_temporarily_hidden_in_editor(False);U.set_level_viewport_camera_info(unreal.Vector(0,265,90),unreal.Rotator(pitch=0,yaw=-90,roll=0));unreal.unregister_slate_post_tick_callback(handle);return
    name,pos,rot=views[stage//2]
    if stage%2==0:
        raw.set_is_temporarily_hidden_in_editor(stage//2==1);U.set_level_viewport_camera_info(unreal.Vector(*pos),unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]))
    else:unreal.SystemLibrary.execute_console_command(U.get_editor_world(),'HighResShot 1920x1080 filename="'+str(O/(name+'.png')).replace('\\','/')+'"')
    stage+=1;start=time.monotonic()
handle=unreal.register_slate_post_tick_callback(tick)
