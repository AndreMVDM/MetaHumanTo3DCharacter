"""Fresh native representative single-node playback, without source actors."""
import unreal,json,time,math,traceback,os
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');C=json.loads((Path(__file__).parent/'profile.json').read_text());O=R/C['evidence_directory'];M=json.loads((O/'animation_library_manifest.json').read_text());B=C['output_namespace']
U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LE=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
D=dict(status='RUNNING',pid=os.getpid(),fresh_main_project=True,bridge_loaded=hasattr(unreal,'RiggedUnitBridgeLibrary'),phases=[])
def write():(O/'native_library.json').write_text(json.dumps(D,indent=2)+'\n')
def require(ok,msg):
    if not ok:raise ValueError(msg)
def vec(v):return [float(v.x),float(v.y),float(v.z)]
def choose(name):
    rows=[r for r in M['entries'] if r['name']==name and r.get('bake_result')=='PASS' and '/Sources/InstalledMannequins/Anims/Unarmed/' in r['source_path']]
    if not rows:rows=[r for r in M['entries'] if r['name']==name and r.get('bake_result')=='PASS' and '/InPlace/' in r['source_path']]
    require(len(rows)==1,'representative selection '+name);return rows[0]
try:
    require(not D['bridge_loaded'],'authoring bridge present')
    clips=[choose(n) for n in ['MM_Idle','MF_Unarmed_Walk_Fwd','MF_Unarmed_Jog_Fwd','MM_Jump','MM_Fall_Loop','MM_Land','MF_Unarmed_Walk_Right','MM_Attack_01']]
    mesh=unreal.load_asset(C['destination_mesh']);height=2*mesh.get_bounds().box_extent.z;names=[str(x) for x in mesh.skeleton.get_reference_pose().get_bone_names()]
    ref=mesh.skeleton.get_reference_pose();hierarchy=unreal.new_object(unreal.SkeletalMeshComponent);hierarchy.set_skeletal_mesh_asset(mesh);parents={n:str(hierarchy.get_parent_bone(n)) for n in names}
    reference={n:vec(ref.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD).translation) for n in names}
    level=B+'/Playback/L_LibraryProof';require(unreal.EditorLevelLibrary.new_level(level),'new proof map')
    actor=E.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector());comp=actor.skeletal_mesh_component;comp.set_skeletal_mesh_asset(mesh);comp.set_forced_lod(1);comp.set_update_animation_in_editor(True);comp.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES);comp.play_animation(unreal.load_asset(clips[0]['destination_path']),True)
    floor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-5));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(30,30,.1));E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,250),unreal.Rotator(pitch=-45,yaw=-45));E.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,250));require(unreal.EditorLevelLibrary.save_current_level(),'save proof');require(unreal.EditorLevelLibrary.load_level(level),'fresh map reload')
    eye=unreal.Vector(0,height*1.7,height*.65);U.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(0,0,height*.5)));LE.editor_set_game_view(True);unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
    D.update(level=level,height_cm=height,source_actor_count=0,live_retarget=False,playback_mode='Destination AnimSingleNodeInstance, play rate 1; original per-clip root flags preserved')
    unreal.EditorPythonScripting.set_keep_python_script_alive(True);LE.editor_play_simulate()
except Exception:D.update(status='FAIL',error=traceback.format_exc());write();unreal.SystemLibrary.quit_editor();raise
i=0;phase=False;rows=[];advanced=0;last=None;settle=0;shots=set();started=time.perf_counter();busy=False
def tick(delta):
    global i,phase,rows,advanced,last,settle,shots,busy,comp
    if busy:return
    busy=True
    try:
        require(time.perf_counter()-started<300,'native representative timeout');world=U.get_game_world()
        if not world:return
        actors=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor);require(len(actors)==1,'unexpected character/source actor');comp=actors[0].skeletal_mesh_component
        row=clips[i]
        if not phase:
            comp.play_animation(unreal.load_asset(row['destination_path']),True);comp.set_play_rate(1);comp.set_position(0,False);phase=True;rows=[];advanced=0;last=None;settle=3;shots=set();return
        if settle:settle-=1;return
        p=comp.get_position()
        if last is not None:
            d=p-last
            if d<-row['duration_s']*.5:d+=row['duration_s']
            if d>0:advanced+=d
        last=p
        transforms={n:comp.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT) for n in names};points={n:vec(t.translation) for n,t in transforms.items()}
        require(all(math.isfinite(x) for t in transforms.values() for x in vec(t.translation)+vec(t.scale3d)+[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w]),'nonfinite pose')
        require(max(abs(x-1) for x in vec(transforms[C['root_bone']].scale3d)+vec(comp.get_world_transform().scale3d)+vec(actors[0].get_actor_scale3d()))<1e-4,'scale regression')
        err=max(abs(math.dist(points[n],points[parent])-math.dist(reference[n],reference[parent])) for n,parent in parents.items() if parent in names and parent!=C['root_bone'])
        require(err<.01,'limb length regression');require(max(math.dist(p,points[C['root_bone']]) for p in points.values())<height*3,'body explosion');require(abs(actors[0].get_actor_location().z)<.01,'actor elevation')
        require(comp.get_anim_instance().get_class().get_name()=='AnimSingleNodeInstance','live animation source');rows.append(dict(position_s=p,advance_s=advanced,root=points[C['root_bone']],pelvis=points[C['pelvis_bone']],hands={n:points[n] for n in ['hand_l','hand_r']},max_limb_error_cm=err))
        for f in [.25,.65]:
            if advanced>=f*row['duration_s'] and f not in shots:unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(O/(row['name']+'_'+str(f)+'.png')));shots.add(f)
        if advanced<row['duration_s']:return
        require(len(rows)>2,'insufficient native samples');D['phases'].append(dict(name=row['name'],path=row['destination_path'],status='PASS',advance_s=advanced,samples=len(rows),max_limb_error_cm=max(r['max_limb_error_cm'] for r in rows),observations=rows));write();i+=1;phase=False
        if i==len(clips):D['status']='PASS';write();LE.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
    except Exception:D.update(status='FAIL',error=traceback.format_exc());write();LE.editor_request_end_play();unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
    finally:busy=False
handle=unreal.register_slate_post_tick_callback(tick);write()
