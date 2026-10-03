"""Read-only normal-PIE locomotion measurement. Never saves accepted assets."""
import unreal,json,time,math,traceback,os,re
from pathlib import Path
W=Path(__file__).parent;O=Path(json.loads((W/'fresh_profile.json').read_text())['evidence_directory'])
cmd=unreal.SystemLibrary.get_command_line();subject=re.search(r'-LocomotionCase=(\w+)',cmd).group(1);mode='after';handoff=False
C=json.loads((W/'regression_profiles.json').read_text())[subject];MAP=C['assets']['level'].split('.')[0];ABP=C['assets']['anim_blueprint'].split('.')[0];BP=C['assets']['character'].split('.')[0];settings_config=C['settings'];idle_threshold=settings_config['IdleSpeedThreshold'];run_threshold=(settings_config['WalkSpeed']+settings_config['RunSpeed'])/2
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);LE=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
D=dict(status='RUNNING',subject=subject,mode=mode,pid=os.getpid(),map=MAP,normal_native_PIE=True,input_method='native PlayerController Input.+key/Input.-key',cases=[],no_pawn_transform_or_velocity_writes=True)
def write():(O/(subject+'_'+mode+'_native.json')).write_text(json.dumps(D,indent=2)+'\n')
def require(x,msg):
    if not x:raise ValueError(msg)
def v(p):return [float(p.x),float(p.y),float(p.z)]
def state(x):return 'Jump' if x['airborne'] and x['jump_start'] else 'Fall' if x['airborne'] else 'Land' if x['landing'] else 'Run' if x['anim_speed']>run_threshold else 'Walk' if x['anim_speed']>idle_threshold else 'Idle'
def ready():
    require(unreal.EditorLevelLibrary.load_level(MAP),'load review')
    pawn=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.Character));height=2*pawn.mesh.get_skeletal_mesh_asset().get_bounds().box_extent.z
    eye=unreal.Vector(height*1.95,height*1.84,height*1.06);U.set_level_viewport_camera_info(eye,unreal.MathLibrary.find_look_at_rotation(eye,unreal.Vector(0,0,height*.55)))
    unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT);LE.editor_set_game_view(True);LE.editor_set_viewport_realtime(True)
# Each case begins with fresh PIE possession, avoiding floor bounds and any direct repositioning.
cases=[dict(name='run_jump_hold',keys={'W':1,'LeftShift':1},pre=.9,end=3.0,jumps=[0])]
if mode=='after':
    cases=[dict(name='stationary_jump',keys={},pre=.7,end=3.0,jumps=[0]),dict(name='walk_jump',keys={'W':1},pre=.9,end=2.4,jumps=[0]),cases[0],dict(name='repeat_run_jump',keys={'W':1,'LeftShift':1},pre=.7,end=2.8,jumps=[0,1.2]),dict(name='forward_held_jump',keys={'W':1},pre=.8,end=2.4,jumps=[0]),dict(name='release_forward_air',keys={'W':1,'LeftShift':1},pre=.9,end=2.8,jumps=[0],release_at=.55)]
    cases += [dict(name=n,keys=k,pre=.2,end=t,jumps=[]) for n,k,t in [('idle',{},2),('walk_W',{'W':1},2),('run_Shift_W',{'W':1,'LeftShift':1},2),('back_S',{'S':1},2),('left_A',{'A':1},2),('right_D',{'D':1},2),('camera_X',{'MouseX':8},1),('camera_Y',{'MouseY':8},1)]]
idx=0;phase='starting';pc=None;pawn=None;rows=[];held={};origin=None;busy=False;started=time.perf_counter();weights_available=True

def inject(keys):
    global held
    for k in held:
        if k not in keys:unreal.SystemLibrary.execute_console_command(world,'Input.-key '+k,pc)
    for k,val in keys.items():
        if k not in held:unreal.SystemLibrary.execute_console_command(world,'Input.+key '+k+' '+str(val),pc)
    held=dict(keys)
def summarize(case,rows):
    hits=[i for i in range(1,len(rows)) if rows[i-1]['falling'] and not rows[i]['falling']]
    events=[]
    for i in hits:
        # Select first grounded locomotion pose with landing false; also verify its native blend weight.
        j=next((j for j in range(i,len(rows)) if not rows[j]['airborne'] and not rows[j]['landing']),None)
        stable=next((j for j in range(i,len(rows)) if rows[j]['t']-rows[i]['t']>=.1 and not rows[j]['airborne'] and not rows[j]['landing'] and rows[j]['weights'].get('3',1)<.01),None) if weights_available else None
        events.append(dict(touchdown_horizontal_speed=rows[i]['horizontal_speed'],first_grounded_state=rows[i]['state'],touchdown=rows[i],touchdown_previous=rows[i-1],landing_samples=sum(1 for x in rows[i:j or len(rows)] if x['landing']),locomotion_resume=rows[j] if j is not None else None,stable_locomotion=rows[stable] if stable is not None else None,delay_s=rows[j]['t']-rows[i]['t'] if j is not None else None,distance_cm=math.dist(rows[j]['position'],rows[i]['position']) if j is not None else None,stable_delay_s=rows[stable]['t']-rows[i]['t'] if stable is not None else None,stable_distance_cm=math.dist(rows[stable]['position'],rows[i]['position']) if stable is not None else None))
    r=dict(name=case['name'],status='PASS',touchdowns=events,observations=rows,states=sorted(set(x['state'] for x in rows)),peak_horizontal_speed=max(x['horizontal_speed'] for x in rows),pose_excursions={b:max(math.dist(x['joints'][b],rows[0]['joints'][b]) for x in rows) for b in rows[0]['joints']})
    if case['jumps']:
        require(len(hits)==len(case['jumps']),'missing touchdown '+case['name']+' '+str(len(hits)))
        require('Jump' in r['states'] and 'Fall' in r['states'],'air states missing '+case['name'])
        if mode=='before':require(events[0]['distance_cm']>300,'baseline skid not reproduced')
        elif case['name']=='stationary_jump':require('Land' in r['states'] and rows[-1]['state']=='Idle','stationary land regression')
        else:
            for event in events:
                require(event['delay_s']<.1 and event['distance_cm']<settings_config['RunSpeed']*.1,'moving landing delay/skid '+case['name'])
                require(event['first_grounded_state'] in ['Walk','Run'],'incorrect first grounded state '+case['name'])
                if 'release_at' not in case:require(event['touchdown_horizontal_speed']>=.95*(settings_config['RunSpeed'] if 'LeftShift' in case['keys'] else settings_config['WalkSpeed']),'forced velocity stop '+case['name'])
            require(rows[-1]['state'] in (['Idle'] if 'release_at' in case else ['Run'] if 'LeftShift' in case['keys'] else ['Walk']),'wrong final state '+case['name'])
    elif case['name']=='idle':require(r['peak_horizontal_speed']<1 and max(r['pose_excursions'].values())>.001,'idle regression')
    elif case['name'].startswith('camera_'):
        axis=1 if case['name']=='camera_X' else 0;require(abs(rows[-1]['rotation'][axis]-rows[0]['rotation'][axis])>1,'mouse regression')
    else:require(r['peak_horizontal_speed']>(.9*settings_config['RunSpeed'] if 'Shift' in case['name'] else .9*settings_config['WalkSpeed']),'movement input regression')
    for i,x in enumerate(rows):
        require(all(abs(s-1)<1e-5 for s in x['scales']),'scale regression')
        require(all(math.isfinite(z) for values in x['joints'].values() for z in values),'nonfinite pose')
        require(x['position'][2]>D['half_height']-10 and x['position'][2]<D['half_height']+130,'placement regression')
        if i:
            dt=x['t']-rows[i-1]['t'];distance=math.dist(x['position'][:2],rows[i-1]['position'][:2]);require(distance<=(settings_config['RunSpeed']+50)*dt+3,'horizontal teleport')
    return r
try:
    require(not LE.is_in_play_in_editor(),'PIE startup already running');ready();unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    # Transient performance setting only; no SaveConfig / source modification.
    settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
    unreal.SystemLibrary.execute_console_command(U.get_editor_world(),'Slate.bAllowThrottling 0');unreal.SystemLibrary.execute_console_command(U.get_editor_world(),'t.IdleWhenNotForeground 0');LE.editor_request_begin_play()
except Exception:D.update(status='FAIL',error=traceback.format_exc());write();raise

def tick(delta):
    global idx,phase,pc,pawn,world,origin,rows,held,busy,weights_available
    if busy:return
    busy=True
    try:
        require(time.perf_counter()-started<300,'native timeout')
        if phase=='stopping':
            if LE.is_in_play_in_editor():return
            pc=None;pawn=None;held={};rows=[];origin=None
            if idx==len(cases) or D['status']=='FAIL':
                ready();D.update(PIE_stopped=True,editor_left_open=handoff,ready_to_press_Play=handoff and D['status']=='PASS',review_level_loaded=U.get_editor_world().get_path_name());write();unreal.unregister_slate_post_tick_callback(handle)
                if not handoff:unreal.SystemLibrary.quit_editor()
                return
            phase='starting';LE.editor_request_begin_play();return
        world=U.get_game_world()
        if not world:return
        if pc is None:
            pc=unreal.GameplayStatics.get_player_controller(world,0)
            if not pc or not pc.get_controlled_pawn():pc=None;return
            pawn=pc.get_controlled_pawn();require(pawn.get_class().get_name()==BP.split('/')[-1]+'_C','wrong possession');anim=pawn.mesh.get_anim_instance();require(anim.get_class().get_name()==ABP.split('/')[-1]+'_C','wrong animation instance')
            D['half_height']=pawn.capsule_component.get_unscaled_capsule_half_height();D['stature_cm']=2*pawn.mesh.get_skeletal_mesh_asset().get_bounds().box_extent.z;D['runtime_root_motion_mode']=str(anim.get_editor_property('root_motion_mode'))
            D['CMC']={k:str(pawn.character_movement.get_editor_property(k)) for k in ['max_walk_speed','braking_deceleration_walking','ground_friction','braking_friction','braking_friction_factor','use_separate_braking_friction','air_control','falling_lateral_friction','braking_deceleration_falling','jump_z_velocity']}
            D['possession']='PASS';D['authoring_bridge_loaded']=hasattr(unreal,'RiggedUnitBridgeLibrary');require(not D['authoring_bridge_loaded'],'authoring bridge loaded');
            if C.get('expected_version'):require(str(anim.get_editor_property('LocomotionTemplateVersion'))==C['expected_version'],'wrong generated version')
            D['players']={str(i):float(anim.call_method('GetInstanceAssetPlayerLength',args=(i,))) for i in range(14)}
            origin=unreal.GameplayStatics.get_time_seconds(world);phase='running'
        case=cases[idx];t=unreal.GameplayStatics.get_time_seconds(world)-origin;rel=t-case['pre'];keys=dict(case['keys'])
        if 'release_at' in case and rel>=case['release_at']:keys={}
        if any(j<=rel<j+.4 for j in case['jumps']):keys['SpaceBar']=1
        inject(keys);anim=pawn.mesh.get_anim_instance();vel=pawn.get_velocity();root=pawn.mesh.get_socket_transform('root',unreal.RelativeTransformSpace.RTS_COMPONENT);rootw=pawn.mesh.get_socket_transform('root',unreal.RelativeTransformSpace.RTS_WORLD);rotation=pc.get_control_rotation()
        weights={}
        if weights_available:
            try:weights={i:float(anim.call_method('GetInstanceAssetPlayerIndexWeight',args=(int(i),))) for i,length in D['players'].items() if length>0}
            except Exception:weights_available=False;D['native_player_weight_available']=False
        x=dict(t=t,relative_to_jump=rel,position=v(pawn.get_actor_location()),velocity=v(vel),horizontal_speed=math.hypot(vel.x,vel.y),movement_mode=str(pawn.character_movement.movement_mode),falling=pawn.character_movement.is_falling(),anim_speed=float(anim.get_editor_property(C['speed_variable'])),airborne=bool(anim.get_editor_property('Airborne')),jump_start=bool(anim.get_editor_property('JumpStart')),landing=bool(anim.get_editor_property('Landing')),land_time=float(anim.get_editor_property('LandTime')),air_time=float(anim.get_editor_property('AirTime')),root_component=v(root.translation),root_world=v(rootw.translation),mesh_world=v(pawn.mesh.get_world_transform().translation),scales=v(pawn.get_actor_scale3d())+v(pawn.mesh.get_world_transform().scale3d)+v(root.scale3d),joints={n:v(pawn.mesh.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT).translation) for n in ['pelvis','hand_l','hand_r','ball_l','ball_r']},player_times={i:float(anim.call_method('GetInstanceAssetPlayerTime',args=(int(i),))) for i,length in D['players'].items() if length>0},weights=weights,keys=keys,rotation=[rotation.pitch,rotation.yaw,rotation.roll]);x['state']=state(x);rows.append(x)
        if len(rows)>1 and rows[-2]['falling'] and not x['falling']:
            unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(O/(subject+'_'+mode+'_'+case['name']+'_touchdown.png')))
        if rel<case['end']:return
        D['last_case_samples']=rows;write();r=summarize(case,rows);D.pop('last_case_samples',None);D['cases'].append(r);write();idx+=1;inject({});phase='stopping'
        if idx==len(cases):D['status']='PASS'
        LE.editor_request_end_play()
    except Exception:
        D.update(status='FAIL',error=traceback.format_exc(),failed_case=cases[idx]['name'],last_case_samples=rows);write()
        try:
            if pc:inject({})
            phase='stopping';LE.editor_request_end_play()
        except Exception:unreal.unregister_slate_post_tick_callback(handle)
    finally:busy=False
handle=unreal.register_slate_post_tick_callback(tick);write()



