"""Transient SIE captures only; restore saved per-component native playback at end."""
import unreal,json,traceback
from pathlib import Path
O=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/Phase4D');B='/Game/MetaHumanTo3DCharacter/Phase4D'
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert world
demo=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_actor_label()=='Phase4D Lara Native Playback');cs=demo.get_components_by_class(unreal.SkeletalMeshComponent);by={c.get_name().lower():c for c in cs};assert len(cs)==4
data={'status':'running','captures':[],'runtime_changes_only':True};stage=0;frame=0
clips={'idle':'MM_Idle','walk':'MF_Walk_Fwd','run':'MM_Run_Fwd','reach':'JumpingJacks'}
def camera(x,y,z):unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(x,y,z),unreal.Rotator(pitch=0,yaw=-90,roll=0))
def restore():
 for c in cs:
  name=next(n for n in clips if n in c.get_name().lower());c.set_visibility(True);c.play_animation(unreal.load_asset(B+'/Character/Animations/'+clips[name]),True);c.set_play_rate(1)
 camera(140,650,105)
def setup():
 for c in cs:
  c.set_visibility(True)
  if stage:
   name=next(n for n in clips if n in c.get_name().lower());clip=unreal.load_asset(B+'/Character/Animations/'+clips[name]);c.play_animation(clip,True);c.set_position(clip.get_play_length()*.5,False);c.set_play_rate(0)
 if stage==0:
  for c in cs:
   c.set_visibility('idle' in c.get_name().lower());c.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
  camera(-70,360,95)
 elif stage==1:camera(140,650,105)
 elif stage==2:camera(420,210,132)
 elif stage==3:camera(140,130,30)
def tick(delta):
 global stage,frame
 try:
  frame+=1
  if frame==1:setup()
  if frame==10:
   name=['native_reference_pose','native_representative_poses','native_shoulders_reach','native_walk_feet'][stage];path=O/(name+'.png');unreal.SystemLibrary.execute_console_command(world,'HighResShot 1920x1080 filename="'+str(path).replace('\\','/')+'"');data['captures'].append({'file':path.name,'stage':stage,'pose':'reference' if stage==0 else 'paused native clip at 50% duration'})
   if stage==0:
    c=next(c for c in cs if 'idle' in c.get_name().lower());ref=c.get_skeletal_mesh_asset().skeleton.get_reference_pose();errors=[]
    for n in ref.get_bone_names():
     a=c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT).translation;b=ref.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD).translation;errors.append((a-b).length())
    data['reference_component_position_error_cm_max']=max(errors);assert max(errors)<1e-4
  if frame==25:
   stage+=1;frame=0
   if stage==4:
    restore();data['status']='passed';(O/'native_visual_capture.json').write_text(json.dumps(data,indent=2));unreal.unregister_slate_post_tick_callback(handle);print('PHASE4D_NATIVE_VISUAL_DONE')
 except Exception:
  data.update(status='failed',error=traceback.format_exc());restore();(O/'native_visual_capture.json').write_text(json.dumps(data,indent=2));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick);print('PHASE4D_NATIVE_VISUAL_REGISTERED')
