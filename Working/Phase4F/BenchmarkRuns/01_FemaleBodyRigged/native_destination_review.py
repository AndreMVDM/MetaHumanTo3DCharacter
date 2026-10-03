"""Fresh native destination-only playback/posed geometry, no retarget/source evaluation."""
import unreal,json,sys,math,traceback,gzip
from pathlib import Path
sys.dont_write_bytecode=True;R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';VIS=O/'NativeVisual';B='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged'
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
d=json.loads((O/'native_reload.json').read_text());clips=[x for x in json.loads((O/'native_bake.json').read_text())['clips'] if x['variant']=='Final'];clips=sorted(clips,key=lambda x:x['task_id']);E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert unreal.EditorLevelLibrary.load_level(B+'/Maps/L_BenchmarkReference');a=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.SkeletalMeshActor));c=a.skeletal_mesh_component;c.set_update_animation_in_editor(True);unreal.EditorLevelLibrary.editor_set_game_view(True);unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_UNLIT)
r=dict(status='running',native=True,destination_only=True,captures=[],root_application='Native root extraction in component where enabled; actor remains zero for these root-relative stills; absolute trajectory measured separately');stage=0;wait=0;points=[]
def v(x):return [x.x,x.y,x.z]
def tick(delta):
    global stage,wait
    try:
        row=clips[stage];anim=unreal.load_asset(row['path']);tm=row['duration_s']*.5;path=VIS/(row['task_id']+'_destination_midpoint.png')
        if wait==0:
            c.play_animation(anim,False);c.set_position(tm,False);c.set_play_rate(0);c.override_animation_data(anim,False,True,tm,0);a.set_actor_location(unreal.Vector(),False,False)
            h=d['bounds']['height_cm'];loc=unreal.Vector(0,1.25*h,.52*h);U.set_level_viewport_camera_info(loc,unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(0,0,.52*h)));wait=1;return
        wait+=1
        if wait==60:assert unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(path))
        if wait<95 or not path.exists():return
        bones={n:v(c.get_socket_location(n)) for n in d['bones']};dm=unreal.DynamicMesh();opt=unreal.GeometryScriptCopyMeshFromComponentOptions();opt.set_editor_property('requested_lod',unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL,lod_index=0));_,_,ok=unreal.GeometryScript_SceneUtils.copy_mesh_from_component(c,dm,opt,False);assert ok==unreal.GeometryScriptOutcomePins.SUCCESS
        Q=unreal.GeometryScript_MeshQueries;pts=[v(Q.get_vertex_position(dm,i)[0]) for i in range(Q.get_num_vertex_i_ds(dm))];assert len(pts)==d['vertex_count'];points.append(dict(task_id=row['task_id'],time_s=tm,vertices_cm=pts,bones=bones))
        mins=[min(p[j] for p in pts) for j in range(3)];maxs=[max(p[j] for p in pts) for j in range(3)]
        r['captures'].append(dict(task_id=row['task_id'],animation=row['path'],time_s=tm,file=path.relative_to(R).as_posix(),native_bounds=[mins,maxs],native_bones=bones,root_scale=v(c.get_socket_transform('root',unreal.RelativeTransformSpace.RTS_COMPONENT).scale3d)))
        stage+=1;wait=0
        if stage==len(clips):
            with gzip.open(O/'native_destination_midpoints.json.gz','wt') as f:json.dump(points,f)
            r['status']='passed';(O/'native_destination_review.json').write_text(json.dumps(r,indent=2));unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
    except Exception:r.update(status='failed',error=traceback.format_exc());(O/'native_destination_review.json').write_text(json.dumps(r,indent=2));unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
