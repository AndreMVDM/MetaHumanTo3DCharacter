import sys,traceback,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common import *
T=unreal.AssetToolsHelpers.get_asset_tools();source=unreal.load_asset('/Game/Characters/Mannequins/Rigs/IK_Mannequin');source_mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');rows=[];rigs=[];rets=[];samples=[]
suffix=os.environ.get('PHASE4A_EVIDENCE_SUFFIX','');assert suffix in ['', '_ball_forward']
clips={role:'/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/'+name for role,name in [('idle','MM_Idle'),('walk','MF_Walk_Fwd'),('run','MM_Run_Fwd'),('reach','JumpingJacks')]}
for candidate in json.loads((O/('assisted_candidates'+suffix+'.json')).read_text()):
    row={'case':candidate['case'],'classification':'Assisted geometry-landmark control; diagnostic animations pending deformation acceptance'};rows.append(row)
    try:
        assert not candidate.get('error');mesh=unreal.load_asset(candidate['snapshot']['mesh']);base=mesh.get_path_name().split('.')[0].rsplit('/',1)[0]
        ik=unreal.load_asset(base+'/IK_Lara') if unreal.EditorAssetLibrary.does_asset_exist(base+'/IK_Lara') else T.create_asset('IK_Lara',base,unreal.IKRigDefinition,unreal.IKRigDefinitionFactory());ic=unreal.IKRigController.get_controller(ik);assert ic.set_skeletal_mesh(mesh)
        for i in reversed(range(ic.get_num_solvers())):ic.remove_solver(i)
        row['auto_characterisation']=ic.apply_auto_generated_retarget_definition();assert row['auto_characterisation'];assert ic.apply_auto_fbik();assert ic.get_num_solvers()==1
        ic.set_retarget_root('pelvis');ic.set_root_motion_bone('root')
        if not any(str(c.chain_name)=='Root' for c in ic.get_retarget_chains()):ic.add_retarget_chain('Root','root','root','')
        for side,limb_suffix in [('Left','l'),('Right','r')]:ic.set_retarget_chain_end_bone(side+'Leg','ball_'+limb_suffix);assert ic.set_goal_bone(ic.get_retarget_chain_goal(side+'Leg'),'ball_'+limb_suffix)
        row['ik_rig']=ik.get_path_name();rigs.append({'case':row['case'],'snapshot':common.rig_snapshot(ik)})
        rt=unreal.load_asset(base+'/RTG_Manny_Lara') if unreal.EditorAssetLibrary.does_asset_exist(base+'/RTG_Manny_Lara') else T.create_asset('RTG_Manny_Lara',base,unreal.IKRetargeter,unreal.IKRetargetFactory());rc=unreal.IKRetargeterController.get_controller(rt);rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE,source);rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET,ik);rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE,source_mesh);rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET,mesh);rc.remove_all_ops();rc.add_default_ops();rc.auto_map_chains(unreal.AutoMapChainType.EXACT,True)
        for i in range(rc.get_num_retarget_ops()):
            if str(rc.get_op_name(i)) in ['Root Motion','Speed Plant IK Goals','Stride Warp IK Goals']:rc.set_retarget_op_enabled(i,False)
        rc.reset_retarget_pose(rc.get_current_retarget_pose_name(unreal.RetargetSourceOrTarget.TARGET),[],unreal.RetargetSourceOrTarget.TARGET);rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
        row['retargeter']=rt.get_path_name();rets.append({'case':row['case'],'mapping':{str(c.chain_name):str(rc.get_source_chain(c.chain_name)) for c in ic.get_retarget_chains()},'snapshot':common.ret_snapshot(rt,list(candidate['snapshot']['bones']))})
        row['clips']={};ikindex=rc.get_index_of_op_by_name('Run IK Rig')
        for mode in ['FK','Full']:
            rc.set_retarget_op_enabled(ikindex,mode=='Full')
            inp=unreal.IKRetargetBatchOperationInputs();inp.set_editor_properties({'assets_to_retarget':[unreal.EditorAssetLibrary.find_asset_data(p) for p in clips.values()],'source_mesh':source_mesh,'target_mesh':mesh,'ik_retarget_asset':rt,'target_path':base+'/Diagnostics/'+mode,'include_referenced_assets':False,'overwrite_existing_files':True});baked=unreal.IKRetargetBatchOperation.run_batch_retarget(inp);assert len(baked)==4
            paths={a.get_asset().get_name():a.get_asset() for a in baked};opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_properties({'optional_skeletal_mesh':mesh,'retrieve_additive_as_full_pose':True,'incorporate_root_motion_into_pose':True})
            for role,src in clips.items():
                anim=paths[src.rsplit('/',1)[-1]];assert anim.get_editor_property('skeleton')==mesh.skeleton;assert unreal.EditorAssetLibrary.save_loaded_asset(anim,only_if_is_dirty=False);duration=anim.get_editor_property('sequence_length');key=mode+'_'+role;row['clips'][key]={'path':anim.get_path_name(),'destination_skeleton':mesh.skeleton.get_path_name(),'samples':25,'finite':True}
                for frame in range(25):
                    pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,duration*frame/24,opts);bones={str(n):{'local':common.t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),'component':common.t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))} for n in pose.get_bone_names()};finite=all(math.isfinite(x) for b in bones.values() for values in b['component'].values() for x in values);row['clips'][key]['finite'] &= finite
                    samples.append({'case':row['case'],'mode':mode,'role':role,'animation':anim.get_path_name(),'time_s':duration*frame/24,'fraction':frame/24,'bones':bones,'space':'UE evaluated component/skeleton global space; no live actor inferred'})
        rc.set_retarget_op_enabled(ikindex,True)
        for a in [ik,rt]:assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
    except Exception:row['error']=traceback.format_exc()
    save('animation_results'+suffix+'.json',rows);save('ik_rig_results'+suffix+'.json',rigs);save('retargeter_results'+suffix+'.json',rets);save('runtime_samples'+suffix+'.json',{'method':'UE5.8 destination-native diagnostic batch bake and AnimPose evaluation','samples':samples})
print('RETARGET_DONE',len(samples),[(r['case'],r.get('error')) for r in rows])
