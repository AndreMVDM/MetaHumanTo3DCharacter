import unreal,json
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/R4/AegisNX7';C=json.loads((Path(__file__).parent/'profile.json').read_text());M=json.loads((O/'animation_library_manifest.json').read_text());row=next(x for x in M['entries'] if x.get('bake_result')=='FAIL');mesh=unreal.load_asset(C['destination_mesh']);srcmesh=unreal.load_asset(C['source_mesh']);rt=unreal.load_asset(row['authoring_retargeter'] if 'authoring_retargeter' in row else C['output_namespace']+'/Authoring/RTG_Library_InPlace')
inputs=unreal.IKRetargetBatchOperationInputs(assets_to_retarget=[unreal.EditorAssetLibrary.find_asset_data(row['source_path'])],source_mesh=srcmesh,target_mesh=mesh,ik_retarget_asset=rt,target_path=C['output_namespace']+'/Diagnostics',include_referenced_assets=False,overwrite_existing_files=False)
rt=unreal.load_asset(C['output_namespace']+'/Authoring/RTG_Library_RootMotion');inputs.set_editor_property('ik_retarget_asset',rt)
a=unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)[0].get_asset();m=a.get_editor_property('data_model_interface');names=m.get_bone_track_names();d=dict(source=row['source_path'],bone_tracks=[str(n) for n in names],raw_validator=unreal.RiggedUnitBridgeLibrary.validate_baked_tracks(a,C['root_bone'],2*mesh.get_bounds().box_extent.z*2),cases=[])
ctl=unreal.IKRetargeterController.get_controller(rt);d['retarget_ops']=[dict(name=str(ctl.get_op_name(i)),enabled=ctl.get_retarget_op_enabled(i),settings=str(ctl.get_op_controller(i).get_settings())) for i in range(ctl.get_num_retarget_ops())]
op=ctl.get_op_controller(ctl.get_index_of_op_by_name('Root Motion'));d['actual_root_bindings']=dict(source=str(op.get_source_root_bone()),target=str(op.get_target_root_bone()),target_pelvis=str(op.get_target_pelvis_bone()))
sys=__import__('sys');sys.path.insert(0,str(R/'Working/R4'));import animation_library as lib
d['candidate_roots']=lib.root_trajectory(a,mesh,C['root_bone']);d['source_roots']=lib.root_trajectory(unreal.load_asset(row['source_path']),srcmesh,C['root_bone'])
d['mesh_reference_pelvis']={}
for key,asset in [('source',srcmesh),('target',mesh)]:
    modifier=unreal.SkeletonModifier();modifier.set_skeletal_mesh(asset);d['mesh_reference_pelvis'][key]=str(modifier.get_bone_transform(C['pelvis_bone'],True))
for retarget in [False,True]:
    for rootmotion in [False,True]:
        opt=unreal.AnimPoseEvaluationOptions(optional_skeletal_mesh=mesh,should_retarget=retarget,incorporate_root_motion_into_pose=rootmotion);pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(a,0,opt);vals=sorted([(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL).translation.length(),str(n),str(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL))) for n in names],reverse=True);d['cases'].append(dict(retarget=retarget,rootmotion=rootmotion,maxima=vals[:4],root=str(pose.get_bone_pose(C['root_bone'],unreal.AnimPoseSpaces.LOCAL))))
(O/'failed_pose_diagnosis.json').write_text(json.dumps(d,indent=2)+'\n')
