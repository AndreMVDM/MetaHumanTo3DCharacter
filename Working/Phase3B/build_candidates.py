import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
T=unreal.AssetToolsHelpers.get_asset_tools();source=unreal.load_asset('/Game/Characters/Mannequins/Rigs/IK_Mannequin');source_mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
source_chains={str(c.chain_name) for c in unreal.IKRigController.get_controller(source).get_retarget_chains()}
results=[];rigs=[];rets=[];poses=[]
for item in json.loads((O/'dcc_candidates.json').read_text()):
    rig=item['rig'];label=item['label'];base='/Game/MetaHumanTo3DCharacter/Phase3B/'+rig+'/'+label
    row={'rig':rig,'label':label,'requested_height_cm':item['requested_height_cm'],'factor':item['factor']};results.append(row)
    try:
        mesh=unreal.load_asset(base+'/SK_Lara_'+rig) if unreal.EditorAssetLibrary.does_asset_exist(base+'/SK_Lara_'+rig) else None
        if not mesh or not mesh.skeleton or (P/'Working/Phase3B/reimport_required.flag').exists():
            options=unreal.FbxImportUI();options.set_editor_properties({'import_as_skeletal':True,'mesh_type_to_import':unreal.FBXImportType.FBXIT_SKELETAL_MESH,'import_animations':False,'import_materials':True,'import_textures':False,'create_physics_asset':False,'skeleton':None})
            imp=options.skeletal_mesh_import_data;imp.set_editor_properties({'convert_scene':True,'convert_scene_unit':True,'import_uniform_scale':1.0,'import_translation':unreal.Vector(),'import_rotation':unreal.Rotator(),'use_t0_as_ref_pose':False,'update_skeleton_reference_pose':False})
            task=unreal.AssetImportTask();task.set_editor_properties({'filename':item['fbx'],'destination_path':base,'destination_name':'SK_Lara_'+rig,'automated':True,'save':True,'replace_existing':True,'options':options,'factory':unreal.FbxFactory()})
            T.import_asset_tasks([task]);mesh=next(unreal.load_asset(p) for p in task.imported_object_paths if isinstance(unreal.load_asset(p),unreal.SkeletalMesh))
        assert mesh.skeleton
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh.skeleton,only_if_is_dirty=False)
        for slot in mesh.get_editor_property('materials'):
            material=slot.get_editor_property('material_interface')
            if material and '/Phase3B/' in material.get_path_name():unreal.EditorAssetLibrary.save_loaded_asset(material,only_if_is_dirty=False)
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
        row['snapshot']=mesh_snapshot(mesh)
        names=set(row['snapshot']['bones']);expected_names={n.removeprefix('mixamorig:') for n in item['hierarchy']}
        row['bone_names_match']=names==expected_names
        row['height_error_cm']=row['snapshot']['bounds']['height_cm']-item['requested_height_cm']
        row['root_scale_unit']=all(abs(s-1)<0.0001 for b in row['snapshot']['bones'].values() for s in b['local']['scale'])
        row['finite']=all(math.isfinite(x) for b in row['snapshot']['bones'].values() for space in ['local','component'] for values in b[space].values() for x in values)
        assert row['bone_names_match'] and row['root_scale_unit'] and row['finite'] and abs(row['height_error_cm'])<0.1,row
        ik_path=base+'/IK_Lara_'+rig
        ik=unreal.load_asset(ik_path) if unreal.EditorAssetLibrary.does_asset_exist(ik_path) else T.create_asset('IK_Lara_'+rig,base,unreal.IKRigDefinition,unreal.IKRigDefinitionFactory())
        ctl=unreal.IKRigController.get_controller(ik);assert ctl.set_skeletal_mesh(mesh)
        for i in reversed(range(ctl.get_num_solvers())):ctl.remove_solver(i)
        assert ctl.apply_auto_generated_retarget_definition();assert ctl.apply_auto_fbik()
        generated=rig_snapshot(ik)
        pelvis='pelvis' if rig=='UE5' else 'Hips';root='root' if rig=='UE5' else 'Hips'
        ctl.set_retarget_root(pelvis);ctl.set_root_motion_bone(root)
        if not any(str(c.chain_name)=='Root' for c in ctl.get_retarget_chains()):ctl.add_retarget_chain('Root',root,root,'')
        for side,suffix in [('Left','l'),('Right','r')]:
            ctl.set_retarget_chain_end_bone(side+'Leg','ball_'+suffix if rig=='UE5' else side+'ToeBase')
            assert ctl.set_goal_bone(ctl.get_retarget_chain_goal(side+'Leg'),'ball_'+suffix if rig=='UE5' else side+'ToeBase')
        final=rig_snapshot(ik)
        lengths={}
        for chain in final['chains']:
            folded={n.casefold():b for n,b in row['snapshot']['bones'].items()}
            a=folded[chain['start'].casefold()]['component']['translation'];b=folded[chain['end'].casefold()]['component']['translation']
            lengths[chain['name']]=math.dist(a,b)
        row['ik_rig']=ik.get_path_name();rigs.append({'rig':rig,'label':label,'generated':generated,'final':final,'chain_endpoint_distance_cm':lengths,'asset_doc':ik.__doc__})
        unreal.EditorAssetLibrary.save_loaded_asset(ik)
        rt_path=base+'/RTG_Manny_Lara_'+rig
        rt=unreal.load_asset(rt_path) if unreal.EditorAssetLibrary.does_asset_exist(rt_path) else T.create_asset('RTG_Manny_Lara_'+rig,base,unreal.IKRetargeter,unreal.IKRetargetFactory())
        rc=unreal.IKRetargeterController.get_controller(rt);rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE,source);rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET,ik)
        rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE,source_mesh);rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET,mesh)
        rc.remove_all_ops();rc.add_default_ops();rc.auto_map_chains(unreal.AutoMapChainType.EXACT,True)
        if rig=='Mixamo':assert rc.set_source_chain('','Root')
        mapping={c['name']:str(rc.get_source_chain(c['name'])) for c in final['chains']}
        assert all(mapping[n]==n for n in mapping if n in source_chains and not (rig=='Mixamo' and n=='Root')),mapping
        for i in range(rc.get_num_retarget_ops()):
            if str(rc.get_op_name(i)) in ['Root Motion','Speed Plant IK Goals','Stride Warp IK Goals']:rc.set_retarget_op_enabled(i,False)
        rc.reset_retarget_pose(rc.get_current_retarget_pose_name(unreal.RetargetSourceOrTarget.TARGET),[],unreal.RetargetSourceOrTarget.TARGET)
        rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
        snapshot=ret_snapshot(rt,names);row['retargeter']=rt.get_path_name()
        rets.append({'rig':rig,'label':label,'mapping':mapping,'snapshot':snapshot});poses.append({'rig':rig,'label':label,'manual_edits':[],'offsets_xyzw':snapshot['pose_offsets']})
        unreal.EditorAssetLibrary.save_loaded_asset(rt)
    except Exception:row['error']=traceback.format_exc()
    save('scaled_candidates.json',results);save('ik_rig_results.json',rigs);save('retargeter_results.json',rets);save('pose_offsets.json',poses)
print('PHASE3B_CANDIDATES_DONE',len(results))
