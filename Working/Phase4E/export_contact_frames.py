"""Read evaluated frames for a native post-bake; keeps UE evaluation as source."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ue_common import *
data={'status':'running','clips':{},'samples':[]}
try:
    mesh=unreal.load_asset(B+'/Character/Candidates/SK_Lara_Refined');opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_properties({'optional_skeletal_mesh':mesh,'incorporate_root_motion_into_pose':True})
    for role,name in [('idle','MM_Idle'),('walk','MF_Walk_Fwd'),('run','MM_Run_Fwd')]:
        anim=unreal.load_asset(B+'/Character/NativeAnimations/'+name);frames=round(anim.get_play_length()*60);data['clips'][role]={'name':name,'frames':frames,'fps':60}
        for f in range(frames+1):
            pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,f/60,opts);data['samples'].append({'role':role,'frame':f,'time_s':f/60,'bones':{str(n):{'component':tr(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD)),'local':tr(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL))} for n in pose.get_bone_names()}})
    data['status']='passed'
except Exception:data.update(status='failed',error=traceback.format_exc())
save('native_contact_frame_export.json',data)
