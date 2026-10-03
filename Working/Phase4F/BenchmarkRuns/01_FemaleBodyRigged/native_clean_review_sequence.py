"""Source-free continuous destination evidence at frozen speeds; camera tracking is diagnostic only."""
import unreal,json,gzip,math,traceback,sys,bisect
from pathlib import Path
sys.dont_write_bytecode=True;R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';B='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged';r=dict(status='running',source_free=True,segments=[],quality_approval_inferred=False)
try:
    assert 'CleanProject' in unreal.Paths.get_project_file_path();assert unreal.EditorLevelLibrary.load_level(B+'/Smoke/L_DestinationSmoke');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.SkeletalMeshActor));c=a.skeletal_mesh_component;mesh=c.get_skeletal_mesh_asset();camera=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.CameraActor));camera.camera_component.set_field_of_view(45)
    # Own reference helper is an evidence reset, never a common motion/retarget replacement.
    fac=unreal.AnimSequenceFactory();fac.set_editor_property('target_skeleton',mesh.skeleton);helper=unreal.AssetToolsHelpers.get_asset_tools().create_asset('P00_OwnReferenceEvidence',B+'/Smoke',unreal.AnimSequence,fac);ctl=helper.get_editor_property('controller');ctl.open_bracket('Own imported reference evidence',False);ctl.set_frame_rate(unreal.FrameRate(60,1),False);ctl.set_number_of_frames(unreal.FrameNumber(60),False);ref=mesh.skeleton.get_reference_pose()
    for n in ref.get_bone_names():
        t=ref.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL);ctl.add_bone_track(n,False);assert ctl.set_bone_track_keys(n,[t.translation]*61,[t.rotation]*61,[t.scale3d]*61,False)
    ctl.close_bracket(False);helper.set_preview_skeletal_mesh(mesh);assert unreal.EditorAssetLibrary.save_loaded_asset(helper,False)
    seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset('S_SourceFreeContinuous',B+'/Smoke',unreal.LevelSequence,unreal.LevelSequenceFactoryNew());seq.set_display_rate(unreal.FrameRate(30,1));bind=seq.add_possessable(a);track=bind.add_track(unreal.MovieSceneSkeletalAnimationTrack);cb=seq.add_possessable(camera);camera_sec=cb.add_track(unreal.MovieScene3DTransformTrack).add_section();channels=camera_sec.get_all_channels();cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',cb.get_id());cut.set_camera_binding_id(bid)
    poses={x['task_id']:x['pose_data'] for x in json.load(gzip.open(O/'native_live_samples.json.gz','rt')) if x['variant']=='Final'};clips={x['task_id']:x for x in json.loads((O/'native_bake.json').read_text())['clips'] if x['variant']=='Final'};tasks={x['id']:x for x in json.loads((R/'Documentation/Phase4F/Benchmark/MotionQualityProtocol/protocol.json').read_text())['motion_set']};height=json.loads((O/'native_reload.json').read_text())['bounds']['height_cm'];frame=0
    for view,ids in [('body',[f'P{i:02}' for i in range(15)]),('left_hand',['P11','P12','P13']),('right_hand',['P11','P12','P13'])]:
      for speed in [1,.25]:
       for id in ids:
        anim=helper if id=='P00' else unreal.load_asset(clips[id]['path']);duration=anim.get_play_length();cycles=tasks[id]['cycles'] if view=='body' else 1;count=math.ceil(duration*cycles/speed*30);sec=track.add_section();sec.set_range(frame,frame+count);params=sec.get_editor_property('params');params.set_editor_property('animation',anim);params.set_editor_property('play_rate',unreal.MovieSceneTimeWarpExtensions.make_time_warp(float(speed)));sec.set_editor_property('params',params)
        for k in range(count+1):
            tm=min(duration*cycles,k/30*speed)%duration
            if id=='P00':target=unreal.Vector(0,0,height*.52)
            else:
                pose=poses[id];times=[x[0] for x in pose['frames']];i=min(len(times)-1,bisect.bisect_left(times,tm));bone='pelvis' if view=='body' else 'middle_01_'+('l' if view=='left_hand' else 'r');target=unreal.Vector(*pose['frames'][i][1][pose['bones'].index(bone)][1][0])
            offset=unreal.Vector(0,1.5*height,.12*height) if view=='body' else unreal.Vector(0,.18*height,.10*height);loc=target+offset;rot=unreal.MathLibrary.find_look_at_rotation(loc,target)
            for ch,value in zip(channels,[loc.x,loc.y,loc.z,rot.roll,rot.pitch,rot.yaw,1,1,1]):ch.add_key(unreal.FrameNumber(frame+k),float(value),interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
        r['segments'].append(dict(task_id=id,view=view,speed=speed,start_frame=frame,end_frame_exclusive=frame+count,duration_s=count/30,cycles=cycles,animation=anim.get_path_name()));frame+=count
    for s in [camera_sec,cut]:s.set_range(0,frame)
    seq.set_playback_start(0);seq.set_playback_end(frame);assert unreal.EditorAssetLibrary.save_loaded_asset(seq,False)
    for la in E.get_all_level_actors():
        if isinstance(la,unreal.LevelSequenceActor):la.set_sequence(seq)
    assert unreal.EditorLevelLibrary.save_current_level();r.update(status='passed',map=B+'/Smoke/L_DestinationSmoke',sequence=seq.get_path_name(),frame_count=frame,duration_s=frame/30,frame_rate=[30,1],actor_translation='Zero. Root-extracted P14 shown root-relative; no world root-motion/contact acceptance claimed',floor_z_cm=0,camera='Diagnostic follow of measured native pelvis/hands with constant normalised offset; necessary because failed retarget places mesh tens of metres above fixed floor. Standard fixed camera midpoint captures retained separately',own_reference_helper=helper.get_path_name())
except Exception:r.update(status='failed',error=traceback.format_exc())
(O/'source_free_sequence.json').write_text(json.dumps(r,indent=2));print('SOURCE_FREE_SEQUENCE',r['status'],r.get('error',''))
