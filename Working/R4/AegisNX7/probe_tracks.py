import unreal,json
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/R4/AegisNX7';C=json.loads((Path(__file__).parent/'profile.json').read_text());M=json.loads((O/'animation_library_manifest.json').read_text());p=M['entries'][0]['destination_path'];a=unreal.load_asset(p);m=a.get_editor_property('data_model_interface')
d=dict(path=p,loaded=bool(a),model=str(m),track_names=[str(x) for x in m.get_bone_track_names()],raw=[])
for t in m.get_bone_animation_tracks()[:3]:
    raw=t.internal_track_data;d['raw'].append(dict(name=str(t.name),pos=len(raw.get_positional_keys()),rot=len(raw.get_rotational_keys()),scale=len(raw.get_scale_keys()),repr=str(t)))
d['model_methods']=[x for x in dir(m) if 'bone' in x or 'frame' in x or 'key' in x]
mesh=unreal.load_asset(C['destination_mesh']);pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(a,0,unreal.AnimPoseEvaluationOptions(optional_skeletal_mesh=mesh,incorporate_root_motion_into_pose=True));d['pose_names']=[str(x) for x in pose.get_bone_names()];d['root']=str(pose.get_bone_pose(C['root_bone'],unreal.AnimPoseSpaces.WORLD))
(O/'track_api_probe.json').write_text(json.dumps(d,indent=2)+'\n')
