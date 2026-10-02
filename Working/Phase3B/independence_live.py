import sys,time,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
demo=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_actor_label()=='Phase3B Live and Baked Validation')
components=demo.get_components_by_class(unreal.SkeletalMeshComponent)
source=next(c for c in components if c.get_name()=='Manny_Source');source.destroy_component(demo)
assert not any(c.get_name()=='Manny_Source' for c in demo.get_components_by_class(unreal.SkeletalMeshComponent))
phase3b_baked=[c for c in components if c.get_name().startswith('Baked_')]
for c in phase3b_baked:
    rig=c.get_name().split('_')[1];c.play_animation(unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase3B/'+rig+'/Height180/Tests/InPlaceFull/MM_Run_Fwd'),True)
phase3b_independence={'source_component_destroyed':True,'source_live_mesh_components_remaining':[c.get_name() for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) for c in a.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_skeletal_mesh_asset() and 'SKM_Manny' in c.get_skeletal_mesh_asset().get_name()],'samples':[],'errors':[]}
phase3b_ind_frame=0;phase3b_ind_next=0
def phase3b_ind_tick(delta):
    global phase3b_ind_frame,phase3b_ind_next
    try:
        now=time.monotonic()
        if now<phase3b_ind_next:return
        sample={'frame':phase3b_ind_frame,'monotonic_s':now,'components':[]}
        for c in phase3b_baked:
            mesh=c.get_skeletal_mesh_asset();names=[str(n) for n in mesh.skeleton.get_reference_pose().get_bone_names()]
            sample['components'].append({'name':c.get_name(),'anim_instance_class':str(c.get_anim_instance().get_class()),'component_scale':v(c.get_world_transform().scale3d),'bones':{n:{'component':t(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT)),'world':t(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_WORLD))} for n in names}})
        phase3b_independence['samples'].append(sample);phase3b_ind_frame+=1;phase3b_ind_next=now+.08
        save('independence_live.json',phase3b_independence)
        if phase3b_ind_frame>=25:unreal.unregister_slate_post_tick_callback(phase3b_ind_handle);print('PHASE3B_INDEPENDENT_PLAYBACK_DONE')
    except Exception:phase3b_independence['errors'].append(traceback.format_exc());save('independence_live.json',phase3b_independence);unreal.unregister_slate_post_tick_callback(phase3b_ind_handle)
phase3b_ind_handle=unreal.register_slate_post_tick_callback(phase3b_ind_tick)
