"""Native reference and bind inspection in Benchmark 1's isolated scene."""
import unreal,json,sys,time,math,traceback
from pathlib import Path
sys.dont_write_bytecode=True
R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';VIS=O/'NativeVisual';VIS.mkdir(exist_ok=True);BASE='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged'
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
d=json.loads((O/'native_reload.json').read_text());assert d['status']=='passed'
assert unreal.EditorLevelLibrary.new_level(BASE+'/Maps/L_BenchmarkReference')
U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=E.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector());a.set_actor_label('Benchmark 1 original rig reference')
c=a.skeletal_mesh_component;c.set_skeletal_mesh_asset(unreal.load_asset(d['mesh']));c.set_update_animation_in_editor(True);c.set_forced_lod(1);c.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE);c.set_animation(None)
floor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-5));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(30,30,.1))
E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,250),unreal.Rotator(pitch=-45,yaw=-45,roll=0));E.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,250))
unreal.EditorLevelLibrary.save_current_level();unreal.EditorLevelLibrary.editor_set_game_view(True);unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_UNLIT)
views=['front','back','left','right'];stage=0;wait=0;r=dict(status='running',native=True,captures=[],floor_z_cm=0,original_rig_only=True)
def v(x):return [x.x,x.y,x.z]
def tick(delta):
    global stage,wait
    try:
        view=views[stage];h=d['bounds']['height_cm'];target=unreal.Vector(0,0,h*.5);offset={'front':(0,2.5*h,h*.55),'back':(0,-2.5*h,h*.55),'left':(2.5*h,0,h*.55),'right':(-2.5*h,0,h*.55)}[view]
        if wait==0:loc=unreal.Vector(*offset);U.set_level_viewport_camera_info(loc,unreal.MathLibrary.find_look_at_rotation(loc,target));wait=1;return
        wait+=1
        path=VIS/('P00_reference_'+view+'.png')
        if wait==60:assert unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(path))
        if wait<100 or not path.exists():return
        r['captures'].append(dict(view=view,file=path.relative_to(R).as_posix(),dimensions=[1920,1080]))
        if stage==0:
            r['native_bones']={n:v(c.get_socket_location(n)) for n in d['bones']};r['reference_position_max_error_cm']=max(math.dist(r['native_bones'][n],b['component']['translation']) for n,b in d['bones'].items())
            dm=unreal.DynamicMesh();opt=unreal.GeometryScriptCopyMeshFromComponentOptions();opt.set_editor_property('requested_lod',unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL,lod_index=0));_,_,outcome=unreal.GeometryScript_SceneUtils.copy_mesh_from_component(c,dm,opt,False);assert outcome==unreal.GeometryScriptOutcomePins.SUCCESS
            Q=unreal.GeometryScript_MeshQueries;r['native_reference_vertex_max_error_cm']=max(math.dist(v(Q.get_vertex_position(dm,i)[0]),p) for i,p in enumerate(d['native_geometry']['vertices_cm']))
        stage+=1;wait=0
        if stage==len(views):r['status']='passed';(O/'native_reference_review.json').write_text(json.dumps(r,indent=2));unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
    except Exception:r.update(status='failed',error=traceback.format_exc());(O/'native_reference_review.json').write_text(json.dumps(r,indent=2));unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
