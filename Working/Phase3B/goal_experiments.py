import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
import experiments_common as exp
exp.T=unreal.AssetToolsHelpers.get_asset_tools();exp.source=unreal.load_asset('/Game/Characters/Mannequins/Rigs/IK_Mannequin')
exp.rows=json.loads((O/'control_results.json').read_text());exp.ev.samples=json.loads((O/'control_samples.json').read_text())['samples']
configs=json.loads((O/'control_configs.json').read_text())
for rig in ['UE5','Mixamo']:
    for unmap in ([False] if rig=='UE5' else [False,True]):
        label='ToeGoal'+('_RootUnmapped' if unmap else '_RootMapped')
        try:
            row=next(r for r in json.loads((O/'scaled_candidates.json').read_text()) if r['rig']==rig and r['label']=='Height180')
            mesh=unreal.load_asset(row['snapshot']['mesh']);base='/Game/MetaHumanTo3DCharacter/Phase3B/'+rig+'/Height180/GoalTests'
            ik=unreal.EditorAssetLibrary.duplicate_asset(row['ik_rig'],base+'/IK_'+label);ic=unreal.IKRigController.get_controller(ik)
            for side,suff in [('Left','l'),('Right','r')]:
                goal=ic.get_retarget_chain_goal(side+'Leg');assert ic.set_goal_bone(goal,'ball_'+suff if rig=='UE5' else side+'ToeBase')
            rt,rc=exp.fresh_ret(mesh,ik,base,'RTG_'+label,unmap)
            testrow={**row,'label':label};exp.run(testrow,['Goal_FK','Goal_Full'],mesh,ik,rt,{k:exp.ev.animations[k] for k in ['idle','walk','run','reach']})
            configs.append({'rig':rig,'label':label,'rig_snapshot':rig_snapshot(ik),'retargeter':ret_snapshot(rt,row['snapshot']['bones'])})
            unreal.EditorAssetLibrary.save_loaded_asset(ik);unreal.EditorAssetLibrary.save_loaded_asset(rt)
        except Exception:exp.rows.append({'rig':rig,'label':label,'error':traceback.format_exc()})
# Root-motion control: use ORIGINAL MM_Run_Fwd trajectory with Root Motion enabled.
for rig in ['UE5','Mixamo']:
    try:
        row=next(r for r in json.loads((O/'scaled_candidates.json').read_text()) if r['rig']==rig and r['label']=='Height180')
        mesh=unreal.load_asset(row['snapshot']['mesh']);ik=unreal.load_asset(row['ik_rig']);base='/Game/MetaHumanTo3DCharacter/Phase3B/'+rig+'/Height180/RootMotionTest'
        rt,rc=exp.fresh_ret(mesh,ik,base,'RTG_RootMotion',False)
        rc.set_retarget_op_enabled(rc.get_index_of_op_by_name('Root Motion'),True)
        state=exp.ev.bake_and_sample({**row,'label':'RootMotion180'},'RootMotion_Full',mesh,rt,{'run_original':'/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd'})
        exp.rows.append(state);unreal.EditorAssetLibrary.save_loaded_asset(rt)
    except Exception:exp.rows.append({'rig':rig,'label':'RootMotion180','error':traceback.format_exc()})
save('control_results.json',exp.rows);save('control_samples.json',{'samples':exp.ev.samples});save('control_configs.json',configs)
print('PHASE3B_GOAL_TESTS_DONE')
