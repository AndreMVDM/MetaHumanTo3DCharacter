"""Native normal-PIE key-route verification, then stop PIE and leave editor open."""
import unreal,json,time,math,traceback,os
from pathlib import Path
O=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/FinalAcceptance/FemaleBodyRigged')
B='/Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/ReviewV1';MAP=B+'/L_FemaleBodyMovementReview'
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);LE=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
reference=json.loads((O/'review_build.json').read_text());height=reference['reference_height_cm'];half=reference['capsule_half_height_cm']
result=dict(status='RUNNING',pid=os.getpid(),native_normal_PIE=True,input_method='UE Input.+key / Input.-key through native PlayerController InputKey; no direct pawn manipulation',phases=[])
def write(): (O/'native_verification.json').write_text(json.dumps(result,indent=2)+'\n')
def require(ok,msg):
    if not ok:raise ValueError(msg)
def v(p):return [float(p.x),float(p.y),float(p.z)]
def finish():
    LE.editor_request_end_play()
    result['ending_PIE']=True;write()
def ready_view():
    require(unreal.EditorLevelLibrary.load_level(MAP),'load review level')
    U.set_level_viewport_camera_info(unreal.Vector(height*1.95,height*1.84,height*1.06),unreal.MathLibrary.find_look_at_rotation(unreal.Vector(height*1.95,height*1.84,height*1.06),unreal.Vector(0,0,height*.55)))
    unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
    LE.editor_set_game_view(True)
    LE.editor_set_viewport_realtime(True)
try:
    require(not LE.is_in_play_in_editor(),'startup PIE already active')
    ready_view()
    result['loaded_level']=U.get_editor_world().get_path_name()
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    unreal.SystemLibrary.execute_console_command(U.get_editor_world(),'Slate.bAllowThrottling 0')
    unreal.SystemLibrary.execute_console_command(U.get_editor_world(),'t.IdleWhenNotForeground 0')
    LE.editor_request_begin_play()
except Exception:
    result.update(status='FAIL',error=traceback.format_exc());write();raise
phases=[('Idle',{},2),('W_Walk',{'W':1},2),('Shift_W_Run',{'W':1,'LeftShift':1},2),('S_Backward',{'S':1},2),('A_Left',{'A':1},2),('D_Right',{'D':1},2),('MouseX',{'MouseX':8},1),('MouseY',{'MouseY':8},1),('Space_Jump',{'SpaceBar':1},3)]
idx=0;pc=None;phase_start=None;rows=[];held=set();busy=False;stopped=False;started=time.perf_counter()
def inject(keys):
    global held
    for k in held:unreal.SystemLibrary.execute_console_command(world,'Input.-key '+k,pc)
    held=set(keys)
    for k,value in keys.items():unreal.SystemLibrary.execute_console_command(world,'Input.+key '+k+' '+str(value),pc)
def tick(delta):
    global idx,pc,world,pawn,phase_start,rows,busy,stopped
    if busy:return
    busy=True
    try:
        require(time.perf_counter()-started<180,'verification timeout')
        if result.get('ending_PIE'):
            if LE.is_in_play_in_editor():return
            ready_view()
            require(not LE.is_in_play_in_editor(),'PIE not stopped')
            result.update(PIE_stopped=True,editor_left_open=True,review_level_loaded=U.get_editor_world().get_path_name(),ready_to_press_Play=result['status']=='PASS')
            unreal.unregister_slate_post_tick_callback(handle)
            write();stopped=True;return
        world=U.get_game_world()
        if not world:return
        if pc is None:
            pc=unreal.GameplayStatics.get_player_controller(world,0)
            if not pc or not pc.get_controlled_pawn():return
            pawn=pc.get_controlled_pawn()
            require(pawn.get_class().get_name()=='BP_FemaleBodyMovementReviewCharacter_C','wrong possessed pawn')
            characters=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Character)
            require(len(characters)==1,'unexpected character count')
            require(pawn.mesh.get_anim_instance().get_class().get_name()=='ABP_FemaleBodyMovementReview_C','wrong AnimBP')
            result.update(possession='PASS',character_count=len(characters),anim_instance=pawn.mesh.get_anim_instance().get_class().get_name(),reference_height_cm=2*pawn.mesh.get_skeletal_mesh_asset().get_bounds().box_extent.z)
            require(abs(result['reference_height_cm']-height)<.001,'stature changed')
            mr=pawn.mesh.get_editor_property('relative_rotation')
            require(abs(mr.pitch)<.001 and abs(mr.roll)<.001 and abs(mr.yaw+90)<.001,'review mesh orientation incorrect')
            anim=pawn.mesh.get_anim_instance()
            result['asset_player_lengths']={str(i):float(anim.call_method('GetInstanceAssetPlayerLength',args=(i,))) for i in range(14)}
        label,keys,duration=phases[idx]
        if phase_start is None:
            inject(keys);phase_start=unreal.GameplayStatics.get_time_seconds(world);rows=[];return
        pos=v(pawn.get_actor_location());speed=pawn.get_velocity().length();anim=pawn.mesh.get_anim_instance()
        rotation=pc.get_control_rotation()
        # Pose variation proves advancement without adding telemetry to the AnimBP.
        joints={n:v(pawn.mesh.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT).translation) for n in ['pelvis','hand_l','hand_r','ball_l','ball_r']}
        player_times={i:float(anim.call_method('GetInstanceAssetPlayerTime',args=(int(i),))) for i,length in result['asset_player_lengths'].items() if length>0}
        sample=dict(t=unreal.GameplayStatics.get_time_seconds(world)-phase_start,position=pos,speed=speed,anim_speed=float(anim.get_editor_property('Speed')),max_walk_speed=pawn.character_movement.max_walk_speed,joints=joints,player_times=player_times,camera_position=v(pc.player_camera_manager.get_camera_location()),control_rotation=[rotation.pitch,rotation.yaw,rotation.roll],vertical_velocity=pawn.get_velocity().z,airborne=bool(anim.get_editor_property('Airborne')),jump_start=bool(anim.get_editor_property('JumpStart')),landing=bool(anim.get_editor_property('Landing')),can_jump=pawn.can_jump(),jump_count=pawn.jump_current_count,jump_max=pawn.jump_max_count,jump_velocity=pawn.character_movement.jump_z_velocity,air_time=float(anim.get_editor_property('AirTime')),land_time=float(anim.get_editor_property('LandTime')),was_airborne=bool(anim.get_editor_property('WasAirborne')))
        require(all(abs(x-1)<1e-6 for x in v(pawn.get_actor_scale3d())+v(pawn.mesh.get_world_transform().scale3d)),'scene scale changed')
        root=pawn.mesh.get_socket_transform('root',unreal.RelativeTransformSpace.RTS_COMPONENT)
        require(all(abs(x-1)<1e-6 for x in v(root.scale3d)),'root scale changed')
        require(half-10<pos[2]<half+128 if label=='Space_Jump' else half-10<pos[2]<half+15,'capsule placement incorrect')
        require(all(math.isfinite(x) for j in joints.values() for x in j),'nonfinite animation')
        rows.append(sample)
        if label=='Space_Jump' and sample['t']>.5 and held:inject({})
        if sample['t']<duration:return
        steady=[x for x in rows if x['t']>.6];require(len(steady)>1,'insufficient samples')
        excursion={n:max(math.dist(x['joints'][n],steady[0]['joints'][n]) for x in steady) for n in joints}
        translation=math.dist(rows[0]['position'],rows[-1]['position'])
        peak=max(x['speed'] for x in steady)
        result['last_phase_diagnostic']=dict(name=label,translation_cm=translation,peak_speed_cm_s=peak,pose_excursion_cm=excursion,first=rows[0],last=rows[-1],samples=len(rows),observations=rows if label=='Space_Jump' else [])
        write()
        if label=='Space_Jump':
            require(max(x['position'][2] for x in rows)-min(x['position'][2] for x in rows)>30,'Space did not leave floor')
            require(any(x['airborne'] and x['jump_start'] for x in rows),'jump-start state missing')
            require(any(x['airborne'] and not x['jump_start'] and x['vertical_velocity']<0 for x in rows),'fall state missing')
            require(any(x['landing'] for x in rows),'landing state missing')
            require(not rows[-1]['airborne'] and not rows[-1]['landing'],'ground locomotion did not resume')
        elif label=='Idle':require(peak<1 and max(excursion.values())>.001,'idle static/not idle')
        elif label=='Shift_W_Run':require(peak>500 and translation>300 and max(excursion.values())>1 and max(x['anim_speed'] for x in steady)>450,'run input/state failed')
        elif label in ['W_Walk','S_Backward','A_Left','D_Right']:require(250<peak<350 and translation>100 and max(excursion.values())>1 and max(x['anim_speed'] for x in steady)>5,'walk/direction input failed')
        elif label=='MouseX':require(abs(rows[-1]['control_rotation'][1]-rows[0]['control_rotation'][1])>1,'mouse yaw failed')
        elif label=='MouseY':require(abs(rows[-1]['control_rotation'][0]-rows[0]['control_rotation'][0])>1,'mouse pitch failed')
        result['phases'].append(dict(name=label,status='PASS',keys=keys,translation_cm=translation,peak_speed_cm_s=peak,pose_excursion_cm=excursion,first=rows[0],last=rows[-1],samples=len(rows),air_observations=rows if label=='Space_Jump' else []))
        unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(O/(label+'.png')))
        write();idx+=1;phase_start=None
        if idx==len(phases):inject({});result['status']='PASS';finish()
    except Exception:
        result.update(status='FAIL',error=traceback.format_exc())
        try:
            if pc:inject({})
            finish()
        except Exception:write();unreal.unregister_slate_post_tick_callback(handle)
    finally:busy=False
handle=unreal.register_slate_post_tick_callback(tick)
write()
