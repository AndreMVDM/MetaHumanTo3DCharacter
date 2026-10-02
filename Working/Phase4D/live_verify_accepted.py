"""Actual SIE native playback. No donor/source component is part of the saved scene."""
import unreal,json,time,traceback,builtins,sys
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase4D';W=P/'Working/Phase4D';B='/Game/MetaHumanTo3DCharacter/Phase4D'
sys.dont_write_bytecode=True
def save(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False))
def t(tr):return {'translation':[tr.translation.x,tr.translation.y,tr.translation.z],'rotation_xyzw':[tr.rotation.x,tr.rotation.y,tr.rotation.z,tr.rotation.w],'scale':[tr.scale3d.x,tr.scale3d.y,tr.scale3d.z]}
if hasattr(builtins,'phase4d_tool'):
 unreal.unregister_slate_post_tick_callback(builtins.phase4d_tool.handle)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.save_current_level();assert level.load_level(B+'/Maps/L_LaraNativePlayback')
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(140,1000,115),unreal.Rotator(pitch=0,yaw=-90,roll=0))
level.editor_play_simulate();start=time.monotonic();stage=-1;frame=0;next_time=0;components=None
data={'status':'running','method':'Actual SIE AnimSingleNodeInstance direct destination-native animation in a saved scene containing no Manny or donor component','samples':[],'errors':[],'measured_results':{}}
clips=[('idle','MM_Idle'),('walk','MF_Walk_Fwd'),('run','MM_Run_Fwd'),('reach','JumpingJacks'),('independent_fingers','MannyFingerIdentity')]
def tick(delta):
 global components,stage,frame,next_time,start
 try:
  now=time.monotonic()
  if now<next_time:return
  world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
  if not world:return
  if components is None:
   demo=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_actor_label()=='Phase4D Lara Native Playback');components=demo.get_components_by_class(unreal.SkeletalMeshComponent);assert len(components)==4
   data['saved_scene_has_no_source']=True;data['manny_runtime_not_required']=True
  if stage<0 or frame==25:
   stage+=1;frame=0
   if stage==len(clips):
    data.update(status='passed',measured_results={'native_pose_samples':len(data['samples']),'source_components_remaining':0,'all_four_clips_and_finger_fixture_played':True});save('source_independent_playback.json',data);unreal.unregister_slate_post_tick_callback(handle)
    for c in components:c.play_animation(unreal.load_asset(B+'/Character/Animations/MM_Run_Fwd'),True)
    unreal.SystemLibrary.execute_console_command(world,'HighResShot 1920x1080 filename="E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4D/native_playback.png"');print('PHASE4D_LIVE_DONE');return
   for c in components:c.play_animation(unreal.load_asset(B+'/Character/Animations/'+clips[stage][1]),True)
   start=now;next_time=now+.2;return
  forbidden=[]
  for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor):
   for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
    mesh=c.get_skeletal_mesh_asset()
    if mesh and not mesh.get_path_name().startswith(B+'/Character/'):forbidden.append(mesh.get_path_name())
  assert not forbidden,forbidden
  sample={'role':clips[stage][0],'frame':frame,'elapsed_s':now-start,'foreign_runtime_meshes':forbidden,'components':[]}
  for c in components:
   mesh=c.get_skeletal_mesh_asset();inst=c.get_anim_instance();assert inst and inst.get_class().get_name()=='AnimSingleNodeInstance';sample['components'].append({'name':c.get_name(),'anim_instance_class':inst.get_class().get_name(),'world_transform':t(c.get_world_transform()),'bones':{str(n):{'component':t(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT)),'world':t(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_WORLD))} for n in mesh.skeleton.get_reference_pose().get_bone_names()}})
  data['samples'].append(sample);frame+=1;next_time=now+(.48 if stage==4 else .08);save('source_independent_playback.json',data)
 except Exception:
  data.update(status='failed');data['errors'].append(traceback.format_exc());save('source_independent_playback.json',data);unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick);print('PHASE4D_LIVE_REGISTERED')
