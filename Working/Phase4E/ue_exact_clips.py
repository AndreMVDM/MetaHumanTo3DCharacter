"""Copy raw tracks exactly to Phase4E skeleton and verify evaluated transforms."""
import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ue_common import *
result={'status':'running','clips':[]}
try:
    mesh=unreal.load_asset(B+'/Character/SK_Lara');source=unreal.load_asset(D+'/Character/SK_Lara')
    for name in ['MM_Idle','MF_Walk_Fwd','MM_Run_Fwd','JumpingJacks','MannyFingerIdentity']:
        src=unreal.load_asset(D+'/Character/Animations/'+name);anim=unreal.load_asset(B+'/Character/NativeAnimations/'+name);model=src.get_editor_property('controller').get_model_interface();frames=model.get_number_of_frames();fps=model.get_frame_rate();ctl=anim.get_editor_property('controller')
        ctl.open_bracket('Exact Phase4D raw animation tracks on identical Phase4E skeleton',False);ctl.remove_all_bone_tracks(False);ctl.set_frame_rate(fps,False);ctl.set_number_of_frames(unreal.FrameNumber(frames),False)
        raw_hash={}
        for n in model.get_bone_track_names():
            positions,rotations,scales=unreal.AnimationLibrary.get_raw_track_data(src,n);ctl.add_bone_track(n,False);assert ctl.set_bone_track_keys(n,positions,rotations,scales,False)
            copied=unreal.AnimationLibrary.get_raw_track_data(anim,n);assert list(positions)==list(copied[0]) and list(rotations)==list(copied[1]) and list(scales)==list(copied[2]);raw_hash[str(n)]=hashlib.sha256(str((positions,rotations,scales)).encode()).hexdigest()
        ctl.close_bracket(False);anim.set_preview_skeletal_mesh(mesh);unreal.EditorAssetLibrary.save_loaded_asset(anim,False)
        aopt=unreal.AnimPoseEvaluationOptions();aopt.set_editor_property('optional_skeletal_mesh',source);bopt=unreal.AnimPoseEvaluationOptions();bopt.set_editor_property('optional_skeletal_mesh',mesh);errs=[];rot_err=[]
        for f in range(61):
            tm=src.get_play_length()*f/60;a=unreal.AnimPoseExtensions.get_anim_pose_at_time(src,tm,aopt);b=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,tm,bopt)
            for n in a.get_bone_names():
                ta=a.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD);tb=b.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD);errs.append((ta.translation-tb.translation).length());rot_err.append(max(abs(x-y) for x,y in zip(tr(ta)['rotation_xyzw'],tr(tb)['rotation_xyzw'])))
        result['clips'].append({'name':name,'raw_tracks_identical':True,'raw_track_hashes':raw_hash,'position_error_cm_max':max(errs),'quaternion_component_error_max':max(rot_err),'fps':[fps.numerator,fps.denominator],'frames':frames})
    result['status']='passed'
except Exception:result.update(status='failed',error=traceback.format_exc())
save('exact_animation_preservation.json',result);print('EXACT_CLIPS',result['status'],result.get('error'))
