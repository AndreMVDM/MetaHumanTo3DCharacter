"""Generic native mannequin discovery/bake utilities; destination is profile-bound."""
import unreal, math, json, hashlib,struct
from pathlib import Path
VERSION='phase4f.animation-library/1.0.0'

def detach_source_editor_links(anim):
    """Derived bakes must not keep the source Sequencer editing relationship."""
    removed=[]
    for property_name in ['asset_user_data']:
        items=list(anim.get_editor_property(property_name));kept=[]
        for item in items:
            if isinstance(item,unreal.AnimSequenceLevelSequenceLink):
                removed.append(dict(property=property_name,type=path(item.get_class()),source_sequence=str(item.get_editor_property('path_to_level_sequence'))))
            else:kept.append(item)
        if len(kept)!=len(items):anim.set_editor_property(property_name,kept)
    return removed
def require(ok,message):
    if not ok: raise ValueError(message)
def path(obj):return obj.get_path_name() if obj else None
def vector(v):return [float(v.x),float(v.y),float(v.z)]
def finite(t):return all(math.isfinite(x) for x in vector(t.translation)+vector(t.scale3d)+[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w])
def metadata(anim):
    m=anim.get_editor_property('data_model_interface');rate=m.get_frame_rate();L=unreal.AnimationLibrary
    curves={str(t):[str(x) for x in L.get_animation_curve_names(anim,t)] for t in [unreal.RawCurveTrackTypes.RCT_FLOAT,unreal.RawCurveTrackTypes.RCT_TRANSFORM]}
    notifies=[dict(name=str(x.notify_name),notify_class=path(x.notify.get_class()) if x.notify else None,state_class=path(x.notify_state_class.get_class()) if x.notify_state_class else None,timing='Not exposed by installed Python struct API; native batch duplication retains event') for x in L.get_animation_notify_events(anim)]
    markers=[dict(name=str(x.marker_name),time=x.time) for x in L.get_animation_sync_markers(anim)]
    return dict(skeleton=path(anim.get_editor_property('skeleton')),duration_s=anim.get_play_length(),rate=[rate.numerator,rate.denominator],frames=m.get_number_of_frames(),keys=m.get_number_of_keys(),tracks=[str(x) for x in m.get_bone_track_names()],additive=str(anim.get_editor_property('additive_anim_type')),root_flags={k:str(anim.get_editor_property(k)) for k in ['enable_root_motion','force_root_lock','root_motion_root_lock','use_normalized_root_motion_scale']},retarget_source=str(anim.get_editor_property('retarget_source')),retarget_source_asset=path(anim.get_retarget_source_asset()),curves=curves,notifies=notifies,sync_markers=markers,metadata_classes=[path(x.get_class()) for x in anim.get_editor_property('meta_data')])
def motion_fingerprint(anim):
    """Exact native evaluated-frame/metadata equivalence; distinct motion is retained."""
    m=anim.get_editor_property('data_model_interface');h=hashlib.sha256();rate=m.get_frame_rate();h.update(struct.pack('<iii',rate.numerator,rate.denominator,m.get_number_of_keys()));names=m.get_bone_track_names()
    for n in names:h.update(str(n).encode())
    for frame in range(m.get_number_of_keys()):
        transforms=unreal.AnimationLibrary.get_bone_poses_for_frame(anim,names,frame,False)
        require(len(transforms)==len(names),'fingerprint native pose count')
        for t in transforms:h.update(struct.pack('<10d',*(vector(t.translation)+[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w]+vector(t.scale3d))))
    md=metadata(anim)
    h.update(json.dumps({k:md[k] for k in ['additive','root_flags','curves','notifies','sync_markers','metadata_classes']},sort_keys=True).encode())
    # Never infer curve-value equivalence from just curve names.
    if any(md['curves'].values()) or md['notifies']:h.update(path(anim).encode())
    return h.hexdigest()
def category(name):
    n=name.casefold()
    if any(x in n for x in ['jump','fall','land']):return 'Jump'
    if 'crouch' in n:return 'Crouch'
    if any(x in n for x in ['turn','pivot']):return 'Turns'
    if any(x in n for x in ['idle','walk','run','jog','sprint','strafe','start','stop']):return 'Locomotion'
    return 'Actions'
def root_trajectory(anim,mesh,root):
    m=anim.get_editor_property('data_model_interface');rate=m.get_frame_rate();options=unreal.AnimPoseEvaluationOptions(optional_skeletal_mesh=mesh,should_retarget=False,incorporate_root_motion_into_pose=True)
    points=[]
    for frame in range(m.get_number_of_keys()):
        pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,min(anim.get_play_length(),frame*rate.denominator/rate.numerator),options);t=pose.get_bone_pose(root,unreal.AnimPoseSpaces.LOCAL);require(finite(t),'nonfinite source trajectory');points.append(vector(t.translation))
    return points
def validate(anim,mesh,root,expected_root_deltas=None):
    require(anim.get_editor_property('skeleton')==mesh.skeleton,'wrong destination Skeleton')
    require(math.isfinite(anim.get_play_length()) and anim.get_play_length()>0,'invalid duration')
    height=2*mesh.get_bounds().box_extent.z;m=anim.get_editor_property('data_model_interface');count=0;max_local=0;root_positions=[]
    names=m.get_bone_track_names()
    raw_options=unreal.AnimPoseEvaluationOptions(optional_skeletal_mesh=mesh,should_retarget=False,incorporate_root_motion_into_pose=True)
    rate=m.get_frame_rate()
    for frame in range(m.get_number_of_keys()):
        pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,min(anim.get_play_length(),frame*rate.denominator/rate.numerator),raw_options)
        transforms=[pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL) for n in names];require(len(transforms)==len(names),'native key pose count')
        for name,t in zip(names,transforms):
            require(finite(t),'nonfinite key pose');max_local=max(max_local,t.translation.length());count+=1
            if str(name).casefold()==root.casefold():root_positions.append(vector(t.translation));require(all(abs(x-1)<1e-5 for x in vector(t.scale3d)),'nonunit evaluated root scale')
            else:require(t.translation.length()<height*2,'gross non-root local translation explosion')
    require(root_positions,'missing root track')
    trajectory_error=0
    if expected_root_deltas is not None:
        require(len(expected_root_deltas)==len(root_positions),'trajectory frame count mismatch')
        for p,expected in zip(root_positions,expected_root_deltas):trajectory_error=max(trajectory_error,math.dist([p[i]-root_positions[0][i] for i in range(3)],expected))
        require(trajectory_error<.001,'source-bound root trajectory mismatch '+str(trajectory_error))
    # R2's native routine couples finite/unit-root checks to one translation cap.
    # Non-root local keys still use height*2 above. A longer root is permitted only
    # by its independent source-bound trajectory certificate, never by its length alone.
    native_limit=height*2
    if max(math.sqrt(sum(x*x for x in p)) for p in root_positions)>native_limit:
        require(expected_root_deltas is not None,'long root trajectory without independent source certificate')
        native_limit=max(math.sqrt(sum(x*x for x in p)) for p in root_positions)+.001
    if hasattr(unreal,'RiggedUnitBridgeLibrary'):require(unreal.RiggedUnitBridgeLibrary.validate_baked_tracks(anim,root,native_limit),'accepted native finite/unit-root raw-key check failed')
    options=unreal.AnimPoseEvaluationOptions(optional_skeletal_mesh=mesh,should_retarget=False,incorporate_root_motion_into_pose=True)
    samples=[]
    for fraction in [0,.25,.5,.75,1]:
        t=anim.get_play_length()*fraction;pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,t,options);names=pose.get_bone_names();require(names,'pose evaluation empty')
        root_pose=pose.get_bone_pose(root,unreal.AnimPoseSpaces.WORLD)
        for n in names:
            transform=pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD);require(finite(transform),'nonfinite evaluated pose')
            require((transform.translation-root_pose.translation).length()<height*3,'gross evaluated body displacement')
        samples.append(dict(t=t,bones=len(names),root=vector(root_pose.translation),root_scale=vector(root_pose.scale3d)))
    return dict(status='PASS',stored_key_values_checked=count,native_raw_key_verification=hasattr(unreal,'RiggedUnitBridgeLibrary'),max_local_translation_cm=max_local,root_translation_start=root_positions[0],root_translation_end=root_positions[-1],source_bound_root_deltas=expected_root_deltas,root_trajectory_error_cm=trajectory_error,pose_samples=samples)
