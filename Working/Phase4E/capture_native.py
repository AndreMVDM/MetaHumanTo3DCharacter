"""Identical cameras and times; actual native animation, no prior scene changes."""
import unreal,json,time,traceback
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4E';O=P/'Documentation/Phase4E';B='/Game/MetaHumanTo3DCharacter/Phase4E'
U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);world=U.get_game_world();assert world
demo=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_actor_label()=='Phase4E quality comparison');cs=demo.get_components_by_class(unreal.SkeletalMeshComponent);assert len(cs)==2
shots=[]
for label in ['Baseline','Refined']:
    for view,camera,rot in [('front',[0,200,105],[0,-90,0]),('side',[200,0,105],[0,180,0]),('pants_close',[0,130,96],[0,-90,0]),('shoulder_close',[0,130,136],[0,-90,0])]:
        shots.append({'label':label,'name':'native_'+label.lower()+'_'+view,'camera':camera,'rotation':rot,'clip':'JumpingJacks','fraction':.5})
stage=0;frame=0;started=time.monotonic();requested=False;requested_wall=0;data={'status':'running','captures':[]}
def tick(delta):
    global stage,frame,started,requested,requested_wall
    try:
        frame+=1;shot=shots[stage]
        if frame==1:
            for c in cs:
                is_target=shot['label'].lower() in c.get_name().lower();c.set_visibility(is_target)
                if is_target:
                    c.set_world_location(unreal.Vector(),False,False);anim=unreal.load_asset(B+'/Character/NativeAnimations/'+shot['clip']);c.play_animation(anim,True);c.set_position(anim.get_play_length()*shot['fraction'],False);c.set_play_rate(0)
            U.set_level_viewport_camera_info(unreal.Vector(*shot['camera']),unreal.Rotator(pitch=shot['rotation'][0],yaw=shot['rotation'][1],roll=shot['rotation'][2]))
        elapsed=time.monotonic()-started
        path=O/(shot['name']+'.png')
        if elapsed>1.5 and not requested:
            requested=True;requested_wall=time.time();unreal.SystemLibrary.execute_console_command(world,'HighResShot 1600x1200 filename="'+path.as_posix()+'"')
        if requested and elapsed>3.5 and path.exists() and path.stat().st_mtime>=requested_wall:
            data['captures'].append({**shot,'file':path.name,'file_verified':True});stage+=1;frame=0;started=time.monotonic();requested=False
            if stage==len(shots):
                for i,c in enumerate(cs):c.set_visibility(True);c.set_world_location(unreal.Vector(i*140,0,0),False,False);c.set_play_rate(1)
                U.set_level_viewport_camera_info(unreal.Vector(70,650,108),unreal.Rotator(pitch=0,yaw=-90,roll=0))
                data['status']='passed';(O/'native_visual_capture.json').write_text(json.dumps(data,indent=2));unreal.unregister_slate_post_tick_callback(handle);return
        elif elapsed>15:raise RuntimeError('Native screenshot did not arrive: '+str(path))
    except Exception:
        data.update(status='failed',error=traceback.format_exc());(O/'native_visual_capture.json').write_text(json.dumps(data,indent=2));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
