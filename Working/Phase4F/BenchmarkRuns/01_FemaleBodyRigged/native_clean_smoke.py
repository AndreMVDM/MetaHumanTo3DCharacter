"""Clean project fresh reload, destination-only native scene with existing animation playback."""
import unreal,json,sys,traceback,math
from pathlib import Path
sys.dont_write_bytecode=True;R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';B='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged';r=dict(status='running',source_packages_unavailable=True,existing_asset_edits=False,clips=[])
try:
    assert 'CleanProject' in unreal.Paths.get_project_file_path()
    assert not unreal.EditorAssetLibrary.does_asset_exist('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
    mesh=unreal.load_asset(B+'/Character/SK_FemaleBodyRigged');assert mesh;ref=mesh.skeleton.get_reference_pose();names=[str(n) for n in ref.get_bone_names()]
    for x in json.loads((O/'native_bake.json').read_text())['clips']:
        if x['variant']!='Final':continue
        anim=unreal.load_asset(x['path']);assert anim and anim.get_editor_property('skeleton')==mesh.skeleton
        r['clips'].append(dict(task_id=x['task_id'],path=anim.get_path_name(),duration_s=anim.get_play_length(),destination_skeleton=anim.get_editor_property('skeleton').get_path_name(),native_type=anim.get_class().get_name()))
    assert unreal.EditorLevelLibrary.new_level(B+'/Smoke/L_DestinationSmoke');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=E.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector());c=a.skeletal_mesh_component;c.set_skeletal_mesh_asset(mesh);c.set_forced_lod(1);c.set_update_animation_in_editor(True);c.play_animation(unreal.load_asset(next(x['path'] for x in r['clips'] if x['task_id']=='P05')),True)
    floor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-5));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(30,30,.1));E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,250),unreal.Rotator(pitch=-45,yaw=-45,roll=0));E.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,250))
    camera=E.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(-19,150,5212));camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),unreal.Vector(-19,28,5212)),False)
    seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset('S_DestinationSmoke',B+'/Smoke',unreal.LevelSequence,unreal.LevelSequenceFactoryNew());seq.set_display_rate(unreal.FrameRate(30,1));bind=seq.add_possessable(a);track=bind.add_track(unreal.MovieSceneSkeletalAnimationTrack);frame=0
    for x in r['clips']:
        count=math.ceil(x['duration_s']*30);sec=track.add_section();sec.set_range(frame,frame+count);params=sec.get_editor_property('params');params.set_editor_property('animation',unreal.load_asset(x['path']));sec.set_editor_property('params',params);frame+=count
    cb=seq.add_possessable(camera);cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();cut.set_range(0,frame);bid=unreal.MovieSceneObjectBindingID();bid.set_editor_property('guid',cb.get_id());cut.set_camera_binding_id(bid);seq.set_playback_start(0);seq.set_playback_end(frame);assert unreal.EditorAssetLibrary.save_loaded_asset(seq,False)
    la=E.spawn_actor_from_class(unreal.LevelSequenceActor,unreal.Vector());la.set_sequence(seq);settings=la.get_editor_property('playback_settings');settings.set_editor_property('auto_play',True);la.set_editor_property('playback_settings',settings)
    assert unreal.EditorLevelLibrary.save_current_level();r.update(status='passed',map=B+'/Smoke/L_DestinationSmoke',sequence=seq.get_path_name(),diagnostic_camera='Fixed at P05 actual raised pelvis; floor remains Z=0; no actor or pose correction',source_free_reload_count=len(r['clips']),runtime_autoplay='LevelSequenceActor auto_play, destination-native sequences only; root-motion actor integration not claimed')
except Exception:r.update(status='failed',error=traceback.format_exc())
(O/'native_clean_reload.json').write_text(json.dumps(r,indent=2));print('CLEAN_NATIVE_RELOAD',r['status'],r.get('error',''))
