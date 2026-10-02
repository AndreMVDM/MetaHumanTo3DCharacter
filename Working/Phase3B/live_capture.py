"""Run in the existing editor local console during Phase3B Simulate; samples real components."""
import sys,time,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert world
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(1300,0,130),unreal.Rotator(0,180,0))
demo=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_actor_label()=='Phase3B Live and Baked Validation')
phase3b_components=demo.get_components_by_class(unreal.SkeletalMeshComponent)
phase3b_source=next(c for c in phase3b_components if c.get_name()=='Manny_Source')
phase3b_clips=[('run','/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd'),('idle','/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/MM_Idle'),('walk','/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/MF_Walk_Fwd'),('reach','/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/JumpingJacks')]
phase3b_data={'samples':[],'errors':[],'method':'Live PIE/SIE components at actor/component scale1; source original clips with normal root lock. Simultaneous raw FK/each solver/full controls.'}
phase3b_stage=-1;phase3b_frame=0;phase3b_next=0;phase3b_start=0;phase3b_duration=0
def phase3b_capture_tick(delta):
    global phase3b_stage,phase3b_frame,phase3b_next,phase3b_start,phase3b_duration,phase3b_handle
    try:
        now=time.monotonic()
        if now<phase3b_next:return
        if phase3b_frame==25 or phase3b_stage<0:
            phase3b_stage+=1;phase3b_frame=0
            if phase3b_stage==len(phase3b_clips):
                save('live_runtime_samples.json',phase3b_data);unreal.unregister_slate_post_tick_callback(phase3b_handle);print('PHASE3B_LIVE_CAPTURE_DONE');return
            role,path=phase3b_clips[phase3b_stage];clip=unreal.load_asset(path);phase3b_duration=clip.get_editor_property('sequence_length')
            phase3b_source.play_animation(clip,True)
            for c in phase3b_components:
                if c.get_name().startswith('Baked_'):
                    rig=c.get_name().split('_')[1];name=path.rsplit('/',1)[-1];baked=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase3B/'+rig+'/Height180/Tests/InPlaceFull/'+name)
                    if baked:c.play_animation(baked,True)
            phase3b_start=now;phase3b_next=now+0.1;return
        role,path=phase3b_clips[phase3b_stage];snapshot={'animation_role':role,'source':path,'frame':phase3b_frame,'elapsed_s':now-phase3b_start,'duration_s':phase3b_duration,'actor_transform':t(demo.get_actor_transform()),'components':[]}
        for c in phase3b_components:
            mesh=c.get_skeletal_mesh_asset()
            if mesh is None:continue # Template ABP's empty root component has no mesh.
            bounds=unreal.SystemLibrary.get_component_bounds(c)
            names=[str(n) for n in mesh.skeleton.get_reference_pose().get_bone_names()]
            bones={n:{'component':t(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT)),'world':t(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_WORLD))} for n in names}
            item={'name':c.get_name(),'mesh':mesh.get_path_name(),'world_transform':t(c.get_world_transform()),'relative_transform':t(c.get_relative_transform()),'anim_instance':str(c.get_anim_instance()),'bounds':{'world_origin':v(bounds[0]),'world_extent':v(bounds[1]),'sphere_radius':bounds[2]},'bones':bones}
            snapshot['components'].append(item)
        phase3b_data['samples'].append(snapshot);phase3b_frame+=1;phase3b_next=phase3b_start+0.1+phase3b_frame*phase3b_duration/25
        save('live_runtime_samples.json',phase3b_data)
    except Exception:
        phase3b_data['errors'].append(traceback.format_exc());save('live_runtime_samples.json',phase3b_data);unreal.unregister_slate_post_tick_callback(phase3b_handle)
phase3b_handle=unreal.register_slate_post_tick_callback(phase3b_capture_tick)
print('PHASE3B_LIVE_CAPTURE_REGISTERED')
