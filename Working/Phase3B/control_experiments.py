import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
import evaluate_candidates as ev
T=unreal.AssetToolsHelpers.get_asset_tools();source=unreal.load_asset('/Game/Characters/Mannequins/Rigs/IK_Mannequin')
foot_only='--foot-only' in sys.argv
rows=json.loads((O/'control_results.json').read_text()) if foot_only else []
configs=json.loads((O/'control_configs.json').read_text()) if foot_only else []
if foot_only:ev.samples=json.loads((O/'control_samples.json').read_text())['samples']
def fresh_ret(mesh,ik,base,name,unmap_root=False):
    path=base+'/'+name
    rt=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else T.create_asset(name,base,unreal.IKRetargeter,unreal.IKRetargetFactory())
    rc=unreal.IKRetargeterController.get_controller(rt);rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE,source);rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET,ik)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE,ev.S);rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET,mesh)
    rc.remove_all_ops();rc.add_default_ops();rc.auto_map_chains(unreal.AutoMapChainType.EXACT,True)
    if unmap_root:assert rc.set_source_chain('','Root')
    for i in range(rc.get_num_retarget_ops()):
        if str(rc.get_op_name(i))=='Root Motion':rc.set_retarget_op_enabled(i,False)
    rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
    return rt,rc
def run(row,states,mesh,ik,rt,clips):
    ic=unreal.IKRigController.get_controller(ik);rc=unreal.IKRetargeterController.get_controller(rt);idx=rc.get_index_of_op_by_name('Run IK Rig')
    for state in states:
        suffix=state.split('_')[-1]
        rc.set_retarget_op_enabled(idx,suffix!='FK')
        for i in range(ic.get_num_solvers()):ic.set_solver_enabled(i,suffix=='Full' or suffix=='Solver'+str(i))
        r=ev.bake_and_sample(row,state,mesh,rt,clips);r['configuration']=rig_snapshot(ik);rows.append(r)
        save('control_results.json',rows);save('control_samples.json',{'samples':ev.samples})
    for i in range(ic.get_num_solvers()):ic.set_solver_enabled(i,True)
    rc.set_retarget_op_enabled(idx,True)
for rig in ([] if foot_only else ['UE5','Mixamo']):
    for route in ['Legacy','Interchange']:
        label='Raw'+route;base='/Game/MetaHumanTo3DCharacter/Phase3B/'+rig+'/'+label
        row={'rig':rig,'label':label,'requested_height_cm':99.95117}
        try:
            unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX '+('1' if route=='Interchange' else '0'))
            opt=unreal.FbxImportUI();opt.set_editor_properties({'import_as_skeletal':True,'mesh_type_to_import':unreal.FBXImportType.FBXIT_SKELETAL_MESH,'import_animations':False,'import_materials':False,'import_textures':False,'create_physics_asset':False,'skeleton':None})
            opt.skeletal_mesh_import_data.set_editor_properties({'convert_scene':True,'convert_scene_unit':True,'import_uniform_scale':1.0,'use_t0_as_ref_pose':False})
            task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(next((P/'Working/Phase2'/rig).glob('*.fbx'))),'destination_path':base,'destination_name':'SK_Lara_'+rig,'automated':True,'save':False,'replace_existing':True,'options':opt,'factory':unreal.FbxFactory()})
            T.import_asset_tasks([task]);mesh=next(unreal.load_asset(p) for p in task.imported_object_paths if isinstance(unreal.load_asset(p),unreal.SkeletalMesh))
            assert unreal.EditorAssetLibrary.save_loaded_asset(mesh.skeleton,only_if_is_dirty=False);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
            unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
            row['snapshot']=mesh_snapshot(mesh)
            ik=T.create_asset('IK_Control',base,unreal.IKRigDefinition,unreal.IKRigDefinitionFactory());ic=unreal.IKRigController.get_controller(ik);ic.set_skeletal_mesh(mesh);ic.apply_auto_generated_retarget_definition();ic.apply_auto_fbik()
            root='root' if rig=='UE5' else 'Hips';ic.set_root_motion_bone(root);ic.add_retarget_chain('Root',root,root,'')
            for side,suff in [('Left','l'),('Right','r')]:ic.set_retarget_chain_end_bone(side+'Leg','ball_'+suff if rig=='UE5' else side+'ToeBase')
            rt,rc=fresh_ret(mesh,ik,base,'RTG_Control')
            # Match the Phase2 UE5 pelvis correction on raw representations; keep Mixamo defaults.
            if rig=='UE5':
                pc=rc.get_op_controller(rc.get_index_of_op_by_name('Pelvis Motion'));settings=pc.get_settings();settings.set_editor_properties({'scale_horizontal':0.01,'scale_vertical':0.01});pc.set_settings(settings)
            configs.append({'rig':rig,'label':label,'mesh':row['snapshot'],'rig_snapshot':rig_snapshot(ik),'retargeter':ret_snapshot(rt,row['snapshot']['bones'])})
            run(row,['One_FK','One_Solver0','One_Full'],mesh,ik,rt,{'run':ev.animations['run']})
            if rig=='UE5':
                ic.apply_auto_fbik()
                run(row,['Two_Solver0','Two_Solver1','Two_Full'],mesh,ik,rt,{'run':ev.animations['run']})
            unreal.EditorAssetLibrary.save_loaded_asset(ik);unreal.EditorAssetLibrary.save_loaded_asset(rt)
        except Exception:rows.append({'rig':rig,'label':label,'error':traceback.format_exc()});save('control_results.json',rows)
        save('control_configs.json',configs)
# Unit-scale control with a deliberately repeated generator call.
try:
    if foot_only:raise StopIteration()
    original=next(r for r in json.loads((O/'scaled_candidates.json').read_text()) if r['rig']=='UE5' and r['label']=='Height180')
    mesh=unreal.load_asset(original['snapshot']['mesh']);base='/Game/MetaHumanTo3DCharacter/Phase3B/UE5/Height180/Controls'
    ik=unreal.EditorAssetLibrary.duplicate_asset(original['ik_rig'],base+'/IK_Double');ic=unreal.IKRigController.get_controller(ik);ic.apply_auto_fbik()
    rt,rc=fresh_ret(mesh,ik,base,'RTG_Double')
    row={**original,'label':'CleanDouble180'}
    run(row,['Double_Solver0','Double_Solver1','Double_Full'],mesh,ik,rt,{'run':ev.animations['run']})
    unreal.EditorAssetLibrary.save_loaded_asset(ik);unreal.EditorAssetLibrary.save_loaded_asset(rt)
except StopIteration:pass
except Exception:rows.append({'label':'CleanDouble180','error':traceback.format_exc()});save('control_results.json',rows)
# Compare Root-chain collision and Foot vs ToeBase with generated Foot goals held constant.
for endpoint in ['Foot','ToeBase']:
    for unmap in [False,True]:
        try:
            original=next(r for r in json.loads((O/'scaled_candidates.json').read_text()) if r['rig']=='Mixamo' and r['label']=='Height180')
            mesh=unreal.load_asset(original['snapshot']['mesh']);base='/Game/MetaHumanTo3DCharacter/Phase3B/Mixamo/Height180/FootTests'
            label=endpoint+('_RootUnmapped' if unmap else '_RootMapped')
            if foot_only and not unmap:continue
            ik=unreal.load_asset(base+'/IK_'+label) if unreal.EditorAssetLibrary.does_asset_exist(base+'/IK_'+label) else unreal.EditorAssetLibrary.duplicate_asset(original['ik_rig'],base+'/IK_'+label);ic=unreal.IKRigController.get_controller(ik)
            for side in ['Left','Right']:ic.set_retarget_chain_end_bone(side+'Leg',side+endpoint)
            rt,rc=fresh_ret(mesh,ik,base,'RTG_'+label,unmap)
            row={**original,'label':label}
            run(row,['Foot_FK','Foot_Full'],mesh,ik,rt,{k:ev.animations[k] for k in ['idle','walk','run','reach']})
            configs.append({'rig':'Mixamo','label':label,'rig_snapshot':rig_snapshot(ik),'retargeter':ret_snapshot(rt,row['snapshot']['bones'])})
            unreal.EditorAssetLibrary.save_loaded_asset(ik);unreal.EditorAssetLibrary.save_loaded_asset(rt)
        except Exception:rows.append({'label':label,'error':traceback.format_exc()});save('control_results.json',rows)
save('control_configs.json',configs);save('control_results.json',rows);save('control_samples.json',{'samples':ev.samples})
print('PHASE3B_CONTROL_DONE',len(ev.samples))
