import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
out={}
try:
    src=unreal.load_asset('/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd')
    out['anim_methods']={n:getattr(src,n).__doc__ for n in dir(src) if any(x in n for x in ['controller','data_model','number_of'])}
    out['source_settings']=props(src)
    opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_properties({'optional_skeletal_mesh':unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'),'incorporate_root_motion_into_pose':True})
    out['source_root']=[t(unreal.AnimPoseExtensions.get_anim_pose_at_time(src,time,opts).get_bone_pose('root',unreal.AnimPoseSpaces.WORLD)) for time in [0,src.get_editor_property('sequence_length')]]
    rt=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase3B/UE5/Height180/RTG_Manny_Lara_UE5');rc=unreal.IKRetargeterController.get_controller(rt)
    out['root_op']=props(rc.get_op_controller(rc.get_index_of_op_by_name('Root Motion')).get_settings())
    c=src.controller;out['controller_methods']={n:getattr(c,n).__doc__ for n in dir(c) if any(x in n for x in ['bone','bracket','frame','play_length'])}
    model=src.data_model;out['model_methods']={n:getattr(model,n).__doc__ for n in dir(model) if any(x in n for x in ['bone','frame','key'])}
except Exception:out['error']=traceback.format_exc()
save('fixture_probe.json',out)
