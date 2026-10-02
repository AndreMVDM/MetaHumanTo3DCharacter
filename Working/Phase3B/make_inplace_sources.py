import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
rows=[]
sources=['/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd']+['/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/'+n for n in ['MM_Idle','MF_Walk_Fwd','JumpingJacks','Manny_upperarm_r_anim']]
for path in sources:
    row={'source':path};rows.append(row)
    try:
        dst='/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/'+path.rsplit('/',1)[-1]
        anim=unreal.load_asset(dst) if unreal.EditorAssetLibrary.does_asset_exist(dst) else unreal.EditorAssetLibrary.duplicate_asset(path,dst)
        assert anim and '/Phase3B/' in anim.get_path_name()
        root=anim.get_editor_property('skeleton').get_reference_pose().get_bone_pose('root')
        ctl=anim.controller;ctl.open_bracket('Phase3B explicit in-place source fixture',False)
        assert ctl.set_bone_track_keys('root',[root.translation],[root.rotation],[root.scale3d],False)
        ctl.close_bracket(False)
        anim.set_editor_properties({'enable_root_motion':False,'force_root_lock':True})
        assert unreal.EditorAssetLibrary.save_loaded_asset(anim,only_if_is_dirty=False)
        row['fixture']=anim.get_path_name();row['root_track_constant_reference']=t(root);row['non_root_tracks_unchanged']=True
    except Exception:row['error']=traceback.format_exc()
save('inplace_sources.json',rows)
print('PHASE3B_FIXTURES_DONE')
