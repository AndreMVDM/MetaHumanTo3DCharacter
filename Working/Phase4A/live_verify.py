"""Launch in editor; start SIE, remove Manny, evaluate actual native components across four clips."""
import unreal,json,time,traceback
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase4A';B='/Game/MetaHumanTo3DCharacter/Phase4A'
def save(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
def t(v):return {'translation':[v.translation.x,v.translation.y,v.translation.z],'rotation_xyzw':[v.rotation.x,v.rotation.y,v.rotation.z,v.rotation.w],'scale':[v.scale3d.x,v.scale3d.y,v.scale3d.z]}
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.load_level(B+'/Maps/L_VerifiedNativePlayback')
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(70,-650,100),unreal.Rotator(0,90,0))
level.editor_play_simulate();stage=-1;frame=0;next_time=0;start_time=time.monotonic();data={'method':'Actual SIE AnimSingleNodeInstance native playback after destroying Manny source component','samples':[],'errors':[]};components=None
clips=[('idle','MM_Idle'),('walk','MF_Walk_Fwd'),('run','MM_Run_Fwd'),('reach','JumpingJacks')]
def tick(delta):
    global components,stage,frame,next_time,start_time
    try:
        now=time.monotonic()
        if now<next_time:return
        world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if not world:return
        if components is None:
            demo=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_actor_label()=='Phase4A Native Diagnostic Playback');components=demo.get_components_by_class(unreal.SkeletalMeshComponent);source=next(c for c in components if c.get_name()=='Manny_Source');source.destroy_component(demo);components=[c for c in components if c.get_name()!='Manny_Source'];data['manny_destroyed']=True
        if stage<0 or frame==25:
            stage+=1;frame=0
            if stage==len(clips):
                save('independence_live.json',data);unreal.unregister_slate_post_tick_callback(handle)
                for c in components:
                    if c.get_name() in ['Unrigged','MixamoRecovered']:c.play_animation(unreal.load_asset(B+'/'+c.get_name()+'/Assisted180/Diagnostics/Full/MM_Run_Fwd'),True)
                unreal.SystemLibrary.execute_console_command(world,'HighResShot 1920x1080 filename="E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4A/native_playback.png"');print('PHASE4A_LIVE_DONE');return
            role,name=clips[stage]
            for c in components:
                case=c.get_name();base=B+'/'+case+'/Assisted180/Diagnostics/Full' if case!='Phase3B_Mixamo' else '/Game/MetaHumanTo3DCharacter/Phase3B/Mixamo/Height180/Tests/InPlaceFull';c.play_animation(unreal.load_asset(base+'/'+name),True)
            start_time=now;next_time=now+0.1;return
        sample={'role':clips[stage][0],'frame':frame,'elapsed_s':now-start_time,'manny_components_remaining':[],'components':[]}
        for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor):
            for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
                m=c.get_skeletal_mesh_asset()
                if m and 'SKM_Manny' in m.get_name():sample['manny_components_remaining'].append(c.get_name())
        for c in components:
            m=c.get_skeletal_mesh_asset();names=m.skeleton.get_reference_pose().get_bone_names();sample['components'].append({'name':c.get_name(),'anim_instance_class':str(c.get_anim_instance().get_class()),'world_transform':t(c.get_world_transform()),'bones':{str(n):{'component':t(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT)),'world':t(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_WORLD))} for n in names}})
        data['samples'].append(sample);frame+=1;next_time=now+0.08;save('independence_live.json',data)
    except Exception:data['errors'].append(traceback.format_exc());save('independence_live.json',data);unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick);print('PHASE4A_LIVE_REGISTERED')
