import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
out={}
try:
    base='/Game/MetaHumanTo3DCharacter/Phase3B/UE5/Height180'
    mesh=unreal.load_asset(base+'/SK_Lara_UE5');rt=unreal.load_asset(base+'/RTG_Manny_Lara_UE5');rig=unreal.load_asset(base+'/IK_Lara_UE5')
    ctl=unreal.IKRigController.get_controller(rig)
    out['rig']=rig_snapshot(rig)
    out['skeleton_doc']=rig.__doc__
    solver=ctl.get_solver_controller(0)
    out['solver_methods']={n:getattr(solver,n).__doc__ for n in dir(solver) if 'settings' in n}
    out['solver_settings']=props(solver.get_solver_settings())
    for r in ['UE5','Mixamo']:
        rp=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase2/'+r+'/SK_Lara_'+r)
        out[r+'_import']=mesh_snapshot(rp)
    animations={}
    for name in ['MM_Idle','MF_Walk_Fwd','JumpingJacks','Manny_upperarm_r_anim','MM_Death_Front_01']:
        anim=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/'+name)
        animations[name]={'loaded':bool(anim),'skeleton':anim.get_editor_property('skeleton').get_path_name() if anim else None,'length':anim.get_editor_property('sequence_length') if anim else None,'additive':str(anim.get_editor_property('additive_anim_type')) if anim else None,'root_motion':anim.get_editor_property('enable_root_motion') if anim else None}
    out['animations']=animations
    inputs=unreal.IKRetargetBatchOperationInputs()
    inputs.set_editor_properties({'assets_to_retarget':[unreal.EditorAssetLibrary.find_asset_data('/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd')],'source_mesh':unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'),'target_mesh':mesh,'ik_retarget_asset':rt,'target_path':base+'/Tests/Full','include_referenced_assets':False,'overwrite_existing_files':False})
    assets=unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)
    out['baked']=[str(a.package_name) for a in assets]
    for a in assets:unreal.EditorAssetLibrary.save_loaded_asset(a.get_asset(),only_if_is_dirty=False)
    anim=assets[0].get_asset();opts=unreal.AnimPoseEvaluationOptions();opts.optional_skeletal_mesh=mesh
    pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,0.2,opts)
    out['pose']={n:t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD)) for n in ['root','pelvis','head','hand_l','foot_l','ball_l']}
except Exception:out['error']=traceback.format_exc()
save('batch_probe.json',out)
print('PHASE3B_BATCH_TEST_DONE')
