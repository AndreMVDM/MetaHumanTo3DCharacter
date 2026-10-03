"""Native live retarget proof for only neutral/idle/walk/run; no destination bakes."""
import unreal,json,sys,time,math,traceback
from pathlib import Path
sys.dont_write_bytecode=True;R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/UnitCorrection';VIS=O/'NativeLive';VIS.mkdir(exist_ok=True);d=json.loads((O/'canonicalisation.json').read_text());setup=json.loads((O/'live_setup.json').read_text());unreal.EditorPythonScripting.set_keep_python_script_alive(True);assert unreal.EditorLevelLibrary.load_level(setup['map']);E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);actor=next(a for a in E.get_all_level_actors() if len(a.get_components_by_class(unreal.SkeletalMeshComponent))==2);components=actor.get_components_by_class(unreal.SkeletalMeshComponent);dst=next(c for c in components if c.get_skeletal_mesh_asset().get_path_name()==d['mesh']);src=next(c for c in components if c!=dst)
src.set_visibility(False,False);dst.set_visibility(True,False)
for c in [src,dst]:c.set_update_animation_in_editor(True)
h=d['bounds_height_cm'];location=unreal.Vector(0,1.6*h,h*.55);U.set_level_viewport_camera_info(location,unreal.MathLibrary.find_look_at_rotation(location,unreal.Vector(0,0,h*.5)));unreal.EditorLevelLibrary.editor_set_game_view(True);unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_UNLIT)
VIS=O/'NativeLivePIE';VIS.mkdir(exist_ok=True);unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_play_simulate();game_ready=False
paths={'neutral':None,'idle':'/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/MM_Idle','walk':'/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/MF_Walk_Fwd','run':'/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/MM_Run_Fwd'};phases=[(n,s) for s in [1,.25] for n in paths];stage=0;start=None;last=0;rows=[];shots=set();r=dict(status='running',native_live_retarget=True,native_game_world=True,bakes_created=False,source_assets_edited=False,phases=[],floor_z_cm=0)
def v(x):return [x.x,x.y,x.z]
def tick(delta):
    global stage,start,last,rows,shots,game_ready,actor,src,dst
    try:
        if not game_ready:
            world=U.get_game_world()
            if not world:return
            actor=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if len(a.get_components_by_class(unreal.SkeletalMeshComponent))==2);components=actor.get_components_by_class(unreal.SkeletalMeshComponent);dst=next(c for c in components if c.get_skeletal_mesh_asset().get_path_name()==d['mesh']);src=next(c for c in components if c!=dst);src.set_visibility(False,False);dst.set_visibility(True,False);game_ready=True
        task,speed=phases[stage];now=time.perf_counter()
        if start is None:
            anim=unreal.load_asset(paths[task]) if paths[task] else None;duration=anim.get_play_length() if anim else 1;src.play_animation(anim,True) if anim else src.set_animation(None);src.override_animation_data(anim,True,True,0,speed);start=now;last=0;rows=[];shots=set();return
        elapsed=now-start;duration=unreal.load_asset(paths[task]).get_play_length() if paths[task] else 1;cycles=2 if task in ['walk','run'] else 1;total=duration*cycles/speed
        if elapsed>=.15 and elapsed-last>=1/60:
            last=elapsed;bounds=unreal.SystemLibrary.get_component_bounds(dst);bones={n:v(dst.get_socket_location(n)) for n in d['bones']};root=dst.get_socket_transform('root',unreal.RelativeTransformSpace.RTS_COMPONENT);finite=all(math.isfinite(x) for p in bones.values() for x in p);segments={n:math.dist(bones[n],bones[b['parent']]) for n,b in d['bones'].items() if b['parent']}
            rows.append(dict(elapsed_s=elapsed,source_position_s=src.get_position(),bones=bones,root_scale=v(root.scale3d),component_scale=v(dst.get_world_transform().scale3d),actor_location=v(actor.get_actor_location()),world_bounds_origin=v(bounds[0]),world_bounds_extent=v(bounds[1]),finite=finite,segment_lengths_cm=segments))
        for f in [.25,.5,.75]:
            if elapsed>=f*total and f not in shots:path=VIS/(task+'_'+str(speed)+'_'+str(f)+'.png');assert unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,str(path));shots.add(f)
        if elapsed>=total+.2:
            assert rows;max_scale=max(abs(x-1) for z in rows for x in z['root_scale']);pelvis_range=[min(z['bones']['pelvis'][2] for z in rows),max(z['bones']['pelvis'][2] for z in rows)];max_limb_error=max(abs(length-math.dist(d['bones'][n]['component']['translation'],d['bones'][d['bones'][n]['parent']]['component']['translation'])) for z in rows for n,length in z['segment_lengths_cm'].items());motions={n:max(math.dist(z['bones'][n],rows[0]['bones'][n]) for z in rows) for n in ['hand_l','hand_r','foot_l','foot_r']}
            carrier=next(n for n,b in d['bones'].items() if b['parent'] is None)
            max_limb_error=max(abs(length-math.dist(d['bones'][n]['component']['translation'],d['bones'][d['bones'][n]['parent']]['component']['translation'])) for z in rows for n,length in z['segment_lengths_cm'].items() if d['bones'][n]['parent']!=carrier)
            advanced=task=='neutral' or max(z['source_position_s'] for z in rows)-min(z['source_position_s'] for z in rows)>.1
            moved=task=='neutral' or max(motions.values())>.001
            passed=all(z['finite'] for z in rows) and max_scale<1e-4 and max_limb_error<.01 and 20<pelvis_range[0]<pelvis_range[1]+.01<100 and advanced and moved
            r['phases'].append(dict(task=task,speed=speed,status='PASS' if passed else 'FAIL',sample_count=len(rows),pelvis_z_range_cm=pelvis_range,max_root_scale_error=max_scale,max_segment_length_error_cm=max_limb_error,motion_excursion_cm=motions,samples=rows));(O/'native_live_proof.json').write_text(json.dumps(r));stage+=1;start=None
            if stage==len(phases):r['status']='passed' if all(x['status']=='PASS' for x in r['phases']) else 'failed';(O/'native_live_proof.json').write_text(json.dumps(r));unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
    except Exception:r.update(status='failed',error=traceback.format_exc());(O/'native_live_proof.json').write_text(json.dumps(r));unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
handle=unreal.register_slate_post_tick_callback(tick)
