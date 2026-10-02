"""Build only the accepted Phase4D coordinates and axes; no fitting changes."""
import sys,traceback,hashlib
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from ue_common_d import *
B='/Game/MetaHumanTo3DCharacter/Phase4D';base=B+'/Character'
row={'status':'running','measured_results':{},'coordinate_source':'SHA-bound human-reviewed current_proposal; no Phase4A landmark initialisation','weight_edits':[]}
try:
 gate=json.loads((O/'anatomical_validation.json').read_text());fit=json.loads((O/'current_proposal.json').read_text());assert gate['downstream_authorised'] and gate['passed'] and not gate['failed']
 row['proposal_sha256']=hashlib.sha256((O/'current_proposal.json').read_bytes()).hexdigest()
 for n in ['SKEL_Lara','SK_Lara_Authoring','SK_Lara']:assert not unreal.EditorAssetLibrary.does_asset_exist(base+'/'+n),n
 static=unreal.load_asset(B+'/Geometry/SM_Lara180');assert static;dm=copy_static(static);before=state(dm)
 sk=unreal.Phase4DLibrary.create_blank_skeleton(base+'/SKEL_Lara');assert sk
 unreal.GeometryScript_BoneWeights.copy_bones_from_skeleton(sk,dm);unreal.GeometryScript_BoneWeights.compute_smooth_bone_weights(dm,sk,unreal.GeometryScriptSmoothBoneWeightsOptions())
 options=unreal.GeometryScriptCreateNewSkeletalMeshAssetOptions();options.set_editor_properties({'materials':{x.material_slot_name:x.material_interface for x in static.static_materials},'use_original_vertex_order':True})
 author,outcome=unreal.GeometryScript_NewAssetUtils.create_new_skeletal_mesh_asset_from_mesh(dm,sk,base+'/SK_Lara_Authoring',options);assert author,outcome
 mod=unreal.SkeletonModifier();assert mod.set_skeletal_mesh(author)
 for r in fit['generated_joint_schema']:
  n=r['role'];local=fit['recomputed_local_transforms'][n];cols=local['rotation_matrix_columns'];rot=unreal.MathLibrary.make_rot_from_xy(unreal.Vector(*cols[0]),unreal.Vector(*cols[1]));tr=unreal.Transform(location=unreal.Vector(*local['translation_cm']),rotation=rot,scale=unreal.Vector(1,1,1))
  if n=='root':assert mod.set_bones_transforms(['root'],[tr],True)
  else:assert mod.add_bone(n,r['parent_role'],tr),n
 assert mod.commit_skeleton_to_skeletal_mesh();assert unreal.Phase4DLibrary.sync_skeleton_reference(author)
 snap=mesh_snapshot(author);parents={str(n):str(mod.get_parent_name(n)) for n in mod.get_all_bone_names()}
 errors={r['role']:math.dist(r['position_cm'],snap['bones'][r['role']]['component']['translation']) for r in fit['generated_joint_schema']};axis_errors={}
 for n,a in fit['recomputed_axes'].items():
  tr=author.skeleton.get_reference_pose().get_bone_pose(n,unreal.AnimPoseSpaces.WORLD);origin=tr.transform_location(unreal.Vector(0,0,0));axis_errors[n]=max(math.dist(v(tr.transform_location(unreal.Vector(*basis))-origin),expected) for basis,expected in zip([[1,0,0],[0,1,0],[0,0,1]],[a['aim_x'],a['y'],a['z']]))
 assert len(snap['bones'])==53 and max(errors.values())<.001 and max(axis_errors.values())<1e-5
 assert all(parents[r['role']]==r['parent_role'] for r in fit['generated_joint_schema'] if r['parent_role'])
 assert all(max(abs(x-1) for x in b['component']['scale'])<1e-6 for b in snap['bones'].values())
 save('skeleton_construction.json',{'status':'passed','assets':[author.get_path_name(),sk.get_path_name()],'measured_results':{'snapshot':snap,'parents':parents,'position_errors_cm':errors,'axis_errors':axis_errors,'bone_count':53},'proposal_sha256':row['proposal_sha256']})
 dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(author,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD())
 bind=unreal.GeometryScriptSmoothBoneWeightsOptions();bind.set_editor_properties({'distance_weighing_type':unreal.GeometryScriptSmoothBoneWeightsType.GEODESIC_VOXEL,'max_influences':5,'voxel_resolution':128,'stiffness':.2});unreal.GeometryScript_BoneWeights.compute_smooth_bone_weights(dm,author.skeleton,bind)
 after=state(dm);ws,stats=weights(dm);assert not stats['invalid_or_unweighted_vertices'] and stats['max_influences']<=5
 assert before['vertices']==after['vertices'] and before['triangles']==after['triangles'] and before['triangle_uv_sha256']==after['triangle_uv_sha256']
 options.set_editor_property('use_mesh_bone_proportions',True);final,outcome=unreal.GeometryScript_NewAssetUtils.create_new_skeletal_mesh_asset_from_mesh(dm,author.skeleton,base+'/SK_Lara',options);assert final,outcome
 final_snap=mesh_snapshot(final);assert abs(final_snap['bounds']['height_cm']-180)<.001
 for a in [author,final,final.skeleton]:assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
 (W/'accepted_skin.json').write_text(json.dumps({'geometry':after,'weights':ws,'reference':final_snap,'parents':parents},allow_nan=False))
 row.update(status='passed',assets=[final.get_path_name(),final.skeleton.get_path_name()],snapshot=final_snap,measured_results={'weight_statistics':stats,'vertices':len(after['vertices']),'triangles':len(after['triangles']),'geometry_identical':True,'uv_identical':True,'height_cm':final_snap['bounds']['height_cm'],'materials':[m.material_interface.get_path_name() if m.material_interface else None for m in final.materials]},skinning_parameters={'method':'GEODESIC_VOXEL','voxel_resolution':128,'stiffness':.2,'max_influences':5},deformation_acceptance='pending animated evaluation')
except Exception:row.update(status='failed',error=traceback.format_exc())
save('skinning_results.json',row)
print('PHASE4D_BUILD_DONE',row['status'],row.get('error'))
