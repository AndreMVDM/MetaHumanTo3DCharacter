"""Profile-bound reusable native animation-library bake; accepted assets read only."""
import sys,json,hashlib,traceback,collections
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'Working/R4'))
import unreal,animation_library as lib
C=json.loads((Path(__file__).parent/'profile.json').read_text());O=R/C['evidence_directory'];I=json.loads((O/'source_inventory.json').read_text());lib.require(I['status']=='PASS','inventory incomplete')
B=C['output_namespace'];T=unreal.AssetToolsHelpers.get_asset_tools();mesh=unreal.load_asset(C['destination_mesh']);source_mesh=unreal.load_asset(C['source_mesh']);accepted=unreal.load_asset(C['accepted_retargeter'])
rows=I['assets'];counts=collections.Counter(x['name'] for x in rows if x['classification']=='BAKE_DEFAULT')
previous_manifest=json.loads((O/'animation_library_manifest.json').read_text()) if (O/'animation_library_manifest.json').exists() else None
result=dict(version=lib.VERSION,status='RUNNING',destination_mesh=mesh.get_path_name(),destination_skeleton=mesh.skeleton.get_path_name(),accepted_retargeter=accepted.get_path_name(),source_inventory_sha256=hashlib.sha256((O/'source_inventory.json').read_bytes()).hexdigest(),entries=[],authoring_copies={})
def write():
    result['totals']=dict(candidates=len(rows),default=sum(x['classification']=='BAKE_DEFAULT' for x in rows),optional=sum(x['classification']=='BAKE_OPTIONAL' for x in rows),excluded=sum(x['classification'].startswith('EXCLUDE') for x in rows),attempted=sum(x['classification']=='BAKE_DEFAULT' for x in result['entries']),succeeded=sum(x.get('bake_result')=='PASS' for x in result['entries']),failed=sum(x.get('bake_result')=='FAIL' for x in result['entries']))
    (O/'animation_library_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
try:
    rt_inplace=unreal.EditorAssetLibrary.duplicate_asset(C['accepted_retargeter'],B+'/Authoring/RTG_Library_InPlace') if not unreal.EditorAssetLibrary.does_asset_exist(B+'/Authoring/RTG_Library_InPlace') else unreal.load_asset(B+'/Authoring/RTG_Library_InPlace')
    rt_root=unreal.EditorAssetLibrary.duplicate_asset(C['accepted_retargeter'],B+'/Authoring/RTG_Library_RootMotion') if not unreal.EditorAssetLibrary.does_asset_exist(B+'/Authoring/RTG_Library_RootMotion') else unreal.load_asset(B+'/Authoring/RTG_Library_RootMotion')
    for rt,root_enabled in [(rt_inplace,False),(rt_root,True)]:
        ctl=unreal.IKRetargeterController.get_controller(rt);found=False
        for i in range(ctl.get_num_retarget_ops()):
            if str(ctl.get_op_name(i))=='Root Motion':
                lib.require(ctl.set_retarget_op_enabled(i,root_enabled),'root operation configuration');found=True
                if root_enabled:
                    op=ctl.get_op_controller(i);settings=op.get_settings();settings.set_editor_property('root_height_source',unreal.RootMotionHeightSource.COPY_HEIGHT_FROM_SOURCE);op.set_settings(settings)
                    component=unreal.new_object(unreal.SkeletalMeshComponent);component.set_skeletal_mesh_asset(source_mesh)
                    roots=[n for n in source_mesh.skeleton.get_reference_pose().get_bone_names() if component.get_bone_index(n)>=0 and str(component.get_parent_bone(n))=='None'];lib.require(len(roots)==1,'source hierarchy root ambiguous');op.set_source_root_bone(roots[0]);op.set_target_root_bone(C['root_bone'])
        lib.require(found,'accepted retargeter lacks Root Motion operation');lib.require(unreal.EditorAssetLibrary.save_loaded_asset(rt,False),'retarget copy save')
        result['authoring_copies'][str(root_enabled)]=dict(path=rt.get_path_name(),only_policy_change='Root Motion enabled; source binding corrected from retarget pelvis to detected hierarchy root; source height retained for authored 3D trajectory' if root_enabled else 'Accepted in-place operation settings unchanged')
    for original in rows:
        row=dict(original);result['entries'].append(row)
        if row['classification']!='BAKE_DEFAULT':row.update(bake_result='NOT_RUN',validation_result='NOT_RUN');write();continue
        suffix='__'+hashlib.sha256(row['source_path'].encode()).hexdigest()[:8] if counts[row['name']]>1 else ''
        dest=B+'/'+C['animation_subdirectory']+'/'+row['category']+'/'+row['name']+suffix;row['destination_path']=dest;row['root_motion_policy']='ROOT_MOTION' if row['root_flags']['enable_root_motion']=='True' else 'IN_PLACE_OR_AUTHORED_ROOT_WITH_EXTRACTION_DISABLED'
        try:
            src=unreal.load_asset(row['source_path']);source_roots=lib.root_trajectory(src,source_mesh,C['root_bone']);has_trajectory=max(__import__('math').dist(p,source_roots[0]) for p in source_roots)>.0001;rt=rt_root if src.get_editor_property('enable_root_motion') or has_trajectory else rt_inplace
            ratio=mesh.skeleton.get_reference_pose().get_bone_pose(C['pelvis_bone'],unreal.AnimPoseSpaces.WORLD).translation.z/source_mesh.skeleton.get_reference_pose().get_bone_pose(C['pelvis_bone'],unreal.AnimPoseSpaces.WORLD).translation.z
            expected=[[ (p[i]-source_roots[0][i])*ratio for i in range(3)] for p in source_roots] if rt==rt_root else [[0,0,0] for p in source_roots]
            row['root_transform_certificate']=dict(source_root_points=source_roots,pelvis_reference_height_ratio=ratio,root_operation_enabled=rt==rt_root,construction='Installed CopyRootMotionFromSourceRoot: source displacement scaled by target/source pelvis reference height; horizontal/vertical multipliers unchanged at one')
            if unreal.EditorAssetLibrary.does_asset_exist(dest):
                previous=next((x for x in previous_manifest['entries'] if x.get('destination_path','').split('.')[0]==dest and x.get('bake_result')=='PASS'),None) if previous_manifest else None
                lib.require(previous is not None,'refuse overwrite/reuse uncertified existing destination');anim=unreal.load_asset(dest)
            else:
                inputs=unreal.IKRetargetBatchOperationInputs(assets_to_retarget=[unreal.EditorAssetLibrary.find_asset_data(row['source_path'])],source_mesh=source_mesh,target_mesh=mesh,ik_retarget_asset=rt,target_path=B+'/'+C['animation_subdirectory']+'/'+row['category'],suffix=suffix,include_referenced_assets=False,overwrite_existing_files=False,use_source_path=False,retain_additive_flags=True)
                made=unreal.IKRetargetBatchOperation.run_batch_retarget(inputs);lib.require(len(made)==1,'batch output count');anim=made[0].get_asset();lib.require(anim.get_path_name().split('.')[0]==dest,'deterministic output naming failed')
            lib.require(abs(anim.get_play_length()-src.get_play_length())<1e-5,'duration changed')
            row['detached_source_editor_links']=lib.detach_source_editor_links(anim)
            validation=lib.validate(anim,mesh,C['root_bone'],expected);md=lib.metadata(anim)
            lib.require(md['root_flags']==row['root_flags'],'root flags changed')
            lib.require(unreal.EditorAssetLibrary.save_loaded_asset(anim,False),'animation save failed')
            row.update(destination_path=anim.get_path_name(),bake_result='PASS',validation_result='PASS',validation=validation,destination_metadata=md,metadata_comparison={k:md[k]==row[k] for k in ['curves','notifies','sync_markers','metadata_classes']},authoring_retargeter=rt.get_path_name())
            print('R4_BAKE_PASS',row['source_path'],anim.get_path_name())
        except Exception:row.update(bake_result='FAIL',validation_result='FAIL',failure=traceback.format_exc());print('R4_BAKE_FAIL',row['source_path'],row['failure'])
        write()
    result['status']='PASS' if not any(x.get('bake_result')=='FAIL' for x in result['entries']) else 'FAIL'
except Exception:result.update(status='FAIL',error=traceback.format_exc())
write();print('R4_BAKE',result['status'],result['totals'],result.get('error',''))
