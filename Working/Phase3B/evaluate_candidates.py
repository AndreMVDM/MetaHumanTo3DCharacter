"""Bake a small validation set, evaluate the actual UE output poses at repeatable times."""
import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
S=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
animations={role:'/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/'+name for role,name in [('idle','MM_Idle'),('walk','MF_Walk_Fwd'),('run','MM_Run_Fwd'),('reach','JumpingJacks'),('arm_sweep','Manny_upperarm_r_anim')]}
results=[];samples=[]
def bake_and_sample(row,state,mesh,rt,clips):
    dest=row['snapshot']['mesh'].split('.')[0].rsplit('/',1)[0]+'/Tests/InPlace'+state
    inp=unreal.IKRetargetBatchOperationInputs()
    inp.set_editor_properties({'assets_to_retarget':[unreal.EditorAssetLibrary.find_asset_data(p) for p in clips.values()],'source_mesh':S,'target_mesh':mesh,'ik_retarget_asset':rt,'target_path':dest,'include_referenced_assets':False,'overwrite_existing_files':True})
    baked=unreal.IKRetargetBatchOperation.run_batch_retarget(inp)
    assert len(baked)==len(clips),(len(baked),len(clips))
    paths={a.get_asset().get_name():a.get_asset() for a in baked}
    state_row={'rig':row['rig'],'label':row['label'],'state':state,'retargeter':rt.get_path_name(),'baked_paths':[str(a.package_name) for a in baked],'clips':{}}
    opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_properties({'optional_skeletal_mesh':mesh,'retrieve_additive_as_full_pose':True,'incorporate_root_motion_into_pose':True})
    for role,src in clips.items():
        anim=paths[src.rsplit('/',1)[-1]];assert anim.get_editor_property('skeleton')==mesh.skeleton
        if row['rig']=='Mixamo':anim.set_editor_property('force_root_lock',False) # Hips is the root and must retain pelvis motion.
        unreal.EditorAssetLibrary.save_loaded_asset(anim,only_if_is_dirty=False)
        duration=anim.get_editor_property('sequence_length');clip=[]
        for frame in range(25):
            time=duration*frame/24
            pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,time,opts)
            bones={str(n):{'local':t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),'component':t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))} for n in pose.get_bone_names()}
            sample={'rig':row['rig'],'label':row['label'],'requested_height_cm':row['requested_height_cm'],'state':state,'animation_role':role,'animation':anim.get_path_name(),'frame_fraction':frame/24,'time_s':time,'duration_s':duration,'component_scale':[1,1,1],'world_scale':[1,1,1],'world_transform':{'translation':[0,0,0],'rotation_xyzw':[0,0,0,1],'scale':[1,1,1]},'space_note':'AnimPose WORLD is mesh component/skeleton global space. World values coincide only under the explicit identity comparison transform; no live actor sampled.','bones':bones}
            samples.append(sample);clip.append(sample)
        positions=[b['component']['translation'] for sample in clip for b in sample['bones'].values()]
        finite=all(math.isfinite(x) for sample in clip for b in sample['bones'].values() for space in ['local','component'] for value in b[space].values() for x in value)
        max_radius=max(math.sqrt(sum(x*x for x in p)) for p in positions)
        state_row['clips'][role]={'duration_s':duration,'finite':finite,'max_bone_distance_from_origin_cm':max_radius,'samples':len(clip),'stable_envelope':finite and max_radius<3*row['requested_height_cm']}
    return state_row
for row in (json.loads((O/'scaled_candidates.json').read_text()) if __name__=='__main__' else []):
    if row.get('error'):continue
    try:
        mesh=unreal.load_asset(row['snapshot']['mesh']);rt=unreal.load_asset(row['retargeter']);ik=unreal.load_asset(row['ik_rig'])
        rc=unreal.IKRetargeterController.get_controller(rt);ic=unreal.IKRigController.get_controller(ik);ik_index=rc.get_index_of_op_by_name('Run IK Rig')
        states=['FK']+['Solver'+str(i) for i in range(ic.get_num_solvers())]+['Full']
        for state in states:
            rc.set_retarget_op_enabled(ik_index,state!='FK')
            for i in range(ic.get_num_solvers()):ic.set_solver_enabled(i,state=='Full' or state=='Solver'+str(i))
            result=bake_and_sample(row,state,mesh,rt,animations if state in ['FK','Full'] else {'run':animations['run']})
            result['solver_enabled']=[ic.get_solver_enabled(i) for i in range(ic.get_num_solvers())]
            results.append(result);save('solver_isolation.json',results);save('runtime_samples.json',{'method':'UE 5.8 RunBatchRetarget then AnimPoseExtensions full-cycle evaluation, 25 samples per clip','samples':samples})
        for i in range(ic.get_num_solvers()):ic.set_solver_enabled(i,True)
        rc.set_retarget_op_enabled(ik_index,True)
    except Exception:results.append({'rig':row['rig'],'label':row['label'],'error':traceback.format_exc()});save('solver_isolation.json',results)
print('PHASE3B_EVALUATION_DONE',len(samples))
