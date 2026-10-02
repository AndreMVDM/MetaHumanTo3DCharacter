import unreal,json,time,traceback
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase4E';B='/Game/MetaHumanTo3DCharacter/Phase4E'
U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);world=U.get_game_world();assert world
demo=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_actor_label()=='Phase4E quality comparison');cs=demo.get_components_by_class(unreal.SkeletalMeshComponent);assert len(cs)==2
clips=['MM_Idle','MF_Walk_Fwd','MM_Run_Fwd','JumpingJacks','MannyFingerIdentity'];stage=-1;frame=0;next_time=0;data={'status':'running','samples':[]}
def tick(delta):
    global stage,frame,next_time
    try:
        now=time.monotonic()
        if now<next_time:return
        if stage<0 or frame==12:
            stage+=1;frame=0
            if stage==len(clips):
                for c in cs:c.play_animation(unreal.load_asset(B+'/Character/NativeAnimations/JumpingJacks'),True)
                data['status']='passed';data['live_component_frames']=len(data['samples'])*len(cs);(O/'source_independent_playback.json').write_text(json.dumps(data,indent=2));unreal.unregister_slate_post_tick_callback(handle);return
            for c in cs:c.play_animation(unreal.load_asset(B+'/Character/NativeAnimations/'+clips[stage]),True);c.set_play_rate(1);c.set_visibility(True)
            next_time=now+.25;return
        forbidden=[]
        for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor):
            for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
                mesh=c.get_skeletal_mesh_asset()
                if mesh and not mesh.get_path_name().startswith(B+'/'):forbidden.append(mesh.get_path_name())
        assert not forbidden
        row={'clip':clips[stage],'time':now,'foreign_meshes':forbidden,'components':[]}
        for c in cs:
            assert c.get_anim_instance().get_class().get_name()=='AnimSingleNodeInstance'
            row['components'].append({'name':c.get_name(),'animation_instance':'AnimSingleNodeInstance','bones':{str(n):[c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT).translation.x,c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT).translation.y,c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT).translation.z] for n in c.get_skeletal_mesh_asset().skeleton.get_reference_pose().get_bone_names()}})
        data['samples'].append(row);frame+=1;next_time=now+.12
    except Exception:
        data.update(status='failed',error=traceback.format_exc());(O/'source_independent_playback.json').write_text(json.dumps(data,indent=2));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
