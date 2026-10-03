"""Live editor ticks ensure native SingleNode poses have actually evaluated before sampling."""
import unreal,json,gzip,sys,math,traceback
from pathlib import Path
sys.dont_write_bytecode=True;R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';B='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged'
unreal.EditorPythonScripting.set_keep_python_script_alive(True);assert unreal.EditorLevelLibrary.load_level(B+'/Maps/L_BenchmarkReference');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.SkeletalMeshActor));c=a.skeletal_mesh_component;c.set_update_animation_in_editor(True);c.set_forced_lod(1);a.set_actor_location(unreal.Vector(),False,False)
d=json.loads((O/'native_reload.json').read_text());names=list(d['bones']);clips=json.loads((O/'native_bake.json').read_text())['clips'];captures={x['task_id']:x for x in json.loads((O/'native_destination_review.json').read_text())['captures']};rows=[];r=dict(status='running',method='Fresh native editor SingleNode playback, two Slate ticks after each requested pose before actual component transform readback',clips=[],offline_animpose_samples_authoritative=False,commandlet_component_samples_authoritative=False);stage=0;frame=0;wait=0;times=[];frames=[];anim=None
def tr(t):return [[t.translation.x,t.translation.y,t.translation.z],[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],[t.scale3d.x,t.scale3d.y,t.scale3d.z]]
def finish():
    with gzip.open(O/'native_live_samples.json.gz','wt') as f:json.dump(rows,f)
    (O/'native_live_samples.json').write_text(json.dumps(r,indent=2));unreal.unregister_slate_post_tick_callback(handle);unreal.SystemLibrary.quit_editor()
def tick(delta):
    global stage,frame,wait,times,frames,anim
    try:
        row=clips[stage]
        if anim is None:
            anim=unreal.load_asset(row['path']);model=anim.get_editor_property('data_model_interface');rate=model.get_frame_rate();hz=rate.numerator/rate.denominator;duration=anim.get_play_length();times=sorted(set([min(duration,i/60) for i in range(math.ceil(duration*60)+1)]+[min(duration,i/hz) for i in range(model.get_number_of_keys())]+[duration,duration*.5]));frames=[];frame=0;wait=0;c.play_animation(anim,False);c.set_play_rate(0)
        tm=times[frame]
        if wait==0:c.set_position(tm,False);c.override_animation_data(anim,False,True,tm,0);wait=1;return
        if wait<3:wait+=1;return
        bs=[]
        for n in names:
            component=c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT);parent=d['bones'][n]['parent'];local=unreal.MathLibrary.make_relative_transform(component,c.get_socket_transform(parent,unreal.RelativeTransformSpace.RTS_COMPONENT)) if parent else component;bs.append([tr(local),tr(component)])
        frames.append([tm,bs]);frame+=1;wait=0
        if frame==len(times):
            mid=min(frames,key=lambda x:abs(x[0]-row['duration_s']*.5));error=max(math.dist(mid[1][i][1][0],captures[row['task_id']]['native_bones'][n]) for i,n in enumerate(names)) if row['variant']=='Final' else None
            rows.append(dict(**row,pose_data=dict(bones=names,frames=frames,duration_s=row['duration_s'],sample_count=len(frames))));r['clips'].append(dict(task_id=row['task_id'],variant=row['variant'],samples=len(frames),native_editor_midpoint_repeat_error_cm=error));(O/'native_live_samples.json').write_text(json.dumps(r,indent=2));print('NATIVE_LIVE_SAMPLE',row['task_id'],row['variant'],len(frames),error);stage+=1;anim=None
            if stage==len(clips):r['status']='passed';finish()
    except Exception:r.update(status='failed',error=traceback.format_exc());finish()
handle=unreal.register_slate_post_tick_callback(tick)
