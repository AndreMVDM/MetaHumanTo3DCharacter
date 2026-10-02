import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
import evaluate_candidates as ev
rows=[];ev.samples=[]
for rig in ['UE5','Mixamo']:
    row=next(x for x in json.loads((O/'scaled_candidates.json').read_text()) if x['rig']==rig and x['label']=='Height180')
    try:
        mesh=unreal.load_asset(row['snapshot']['mesh']);base='/Game/MetaHumanTo3DCharacter/Phase3B/'+rig+'/Height180/RootMotionFinal'
        rt=unreal.EditorAssetLibrary.duplicate_asset(row['retargeter'],base+'/RTG_RootMotion_Final')
        rc=unreal.IKRetargeterController.get_controller(rt);idx=rc.get_index_of_op_by_name('Root Motion');op=rc.get_op_controller(idx)
        # Record generated selectors; source root must be the authored trajectory bone.
        initial={'source_root':str(op.get_source_root_bone()),'target_root':str(op.get_target_root_bone()),'target_pelvis':str(op.get_target_pelvis_bone())}
        op.set_source_root_bone('root');op.set_target_root_bone('root' if rig=='UE5' else 'Hips');op.set_target_pelvis_bone('pelvis' if rig=='UE5' else 'Hips')
        rc.set_retarget_op_enabled(idx,True)
        result=ev.bake_and_sample({**row,'label':'RootMotionFinal180'},'RootMotionFinal_Full',mesh,rt,{'run_original':'/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd'})
        for path in result['baked_paths']:
            anim=unreal.load_asset(path);anim.set_editor_properties({'enable_root_motion':True,'force_root_lock':False});unreal.EditorAssetLibrary.save_loaded_asset(anim)
        rows.append({**result,'initial_root_selectors':initial,'final_root_selectors':{'source_root':str(op.get_source_root_bone()),'target_root':str(op.get_target_root_bone()),'target_pelvis':str(op.get_target_pelvis_bone())}})
        unreal.EditorAssetLibrary.save_loaded_asset(rt)
    except Exception:rows.append({'rig':rig,'error':traceback.format_exc()})
save('root_motion_final.json',rows);save('root_motion_final_samples.json',{'samples':ev.samples})
