"""Isolated invocation of the existing standard UE rig/retarget recipe. No rig repair."""
import unreal,sys,json,traceback,math
from pathlib import Path
sys.dont_write_bytecode=True
R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged'
sys.path.insert(0,str(R/'Working/Phase3B'))
from common import rig_snapshot,ret_snapshot,mesh_snapshot,props
B='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged';T=unreal.AssetToolsHelpers.get_asset_tools();r={'status':'running','recipe':'Existing standard UE auto-characterisation, ball-chain endpoint and native automatic retarget alignment; no subject-specific tuning','attempt_id':'retarget-001'}
try:
    mesh=unreal.load_asset(B+'/Character/SK_FemaleBodyRigged');sm=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');original=unreal.load_asset('/Game/Characters/Mannequins/Rigs/IK_Mannequin')
    assert not unreal.EditorAssetLibrary.does_asset_exist(B+'/Retarget/IK_Target'),'refuse overwrite'
    source=T.duplicate_asset('IK_Source',B+'/Retarget',original);sc=unreal.IKRigController.get_controller(source)
    r['original_source_rig']=rig_snapshot(original)
    for side,suf in [('Left','l'),('Right','r')]:
        assert str(sc.get_retarget_chain_end_bone(side+'Leg')).lower()=='ball_'+suf
        if not any(str(c.chain_name)==side+'Foot' for c in sc.get_retarget_chains()):sc.add_retarget_chain(side+'Foot','ball_'+suf,'ball_'+suf,'')
    ik=T.create_asset('IK_Target',B+'/Retarget',unreal.IKRigDefinition,unreal.IKRigDefinitionFactory());ic=unreal.IKRigController.get_controller(ik);assert ic.set_skeletal_mesh(mesh)
    r['auto_characterisation']=ic.apply_auto_generated_retarget_definition();assert r['auto_characterisation'];assert ic.apply_auto_fbik()
    ic.set_retarget_root('pelvis');ic.set_root_motion_bone('root')
    if not any(str(c.chain_name)=='Root' for c in ic.get_retarget_chains()):ic.add_retarget_chain('Root','root','root','')
    for side,suf in [('Left','l'),('Right','r')]:
        ic.set_retarget_chain_end_bone(side+'Leg','ball_'+suf);goal=ic.get_retarget_chain_goal(side+'Leg');assert ic.set_goal_bone(goal,'ball_'+suf)
    r['source_rig']=rig_snapshot(source);r['target_rig']=rig_snapshot(ik)
    rt=T.create_asset('RTG_InPlace',B+'/Retarget',unreal.IKRetargeter,unreal.IKRetargetFactory());rc=unreal.IKRetargeterController.get_controller(rt)
    for st,rig,m in [(unreal.RetargetSourceOrTarget.SOURCE,source,sm),(unreal.RetargetSourceOrTarget.TARGET,ik,mesh)]:rc.set_ik_rig(st,rig);rc.set_preview_mesh(st,m)
    rc.remove_all_ops();rc.add_default_ops();rc.auto_map_chains(unreal.AutoMapChainType.EXACT,True)
    for i in range(rc.get_num_retarget_ops()):
        if str(rc.get_op_name(i)) in ['Root Motion','Speed Plant IK Goals','Stride Warp IK Goals']:rc.set_retarget_op_enabled(i,False)
    rc.reset_retarget_pose(rc.get_current_retarget_pose_name(unreal.RetargetSourceOrTarget.TARGET),[],unreal.RetargetSourceOrTarget.TARGET);rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
    r['mapping']={str(c.chain_name):str(rc.get_source_chain(c.chain_name)) for c in ic.get_retarget_chains()}
    r['mapping_complete']=all(k==v for k,v in r['mapping'].items())
    r['retargeter']=ret_snapshot(rt,list(mesh_snapshot(mesh)['bones']))
    r['reference_stature_ratio']=mesh.get_bounds().box_extent.z/sm.get_bounds().box_extent.z
    rm=T.duplicate_asset('RTG_RootMotion',B+'/Retarget',rt);rmc=unreal.IKRetargeterController.get_controller(rm);idx=rmc.get_index_of_op_by_name('Root Motion');op=rmc.get_op_controller(idx)
    op.set_source_root_bone('root');op.set_target_root_bone('root');op.set_target_pelvis_bone('pelvis');rmc.set_retarget_op_enabled(idx,True)
    r['root_motion']=dict(selectors={'source_root':str(op.get_source_root_bone()),'target_root':str(op.get_target_root_bone()),'target_pelvis':str(op.get_target_pelvis_bone())},settings=props(op.get_settings()),api={n:getattr(type(op),n).__doc__ for n in dir(type(op)) if 'scale' in n or 'settings' in n})
    fk=T.duplicate_asset('RTG_FKDiagnostic',B+'/Retarget',rt);fc=unreal.IKRetargeterController.get_controller(fk)
    for i in range(fc.get_num_retarget_ops()):
        if 'IK' in str(fc.get_op_name(i)):fc.set_retarget_op_enabled(i,False)
    r['fk_diagnostic']=ret_snapshot(fk,list(mesh_snapshot(mesh)['bones']))
    for a in [source,ik,rt,rm,fk]:assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
    r.update(status='passed' if r['mapping_complete'] else 'failed',assets=[a.get_path_name() for a in [source,ik,rt,rm,fk]],target_reference=mesh_snapshot(mesh)['bones'])
except Exception:r.update(status='failed',error=traceback.format_exc())
(O/'native_retarget_setup.json').write_text(json.dumps(r,indent=2));print('BENCHMARK_RETARGET_SETUP',r['status'],r.get('error',''))
