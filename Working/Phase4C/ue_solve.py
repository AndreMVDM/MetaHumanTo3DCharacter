"""Isolated body-only MetaHuman donor execution. No Lara skeleton/binding."""
import unreal,json,time,traceback,hashlib,os
from pathlib import Path
P=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4C';O=P/'Documentation/Phase4C'
BASE='/Game/MetaHumanTo3DCharacter/Phase4C'
ATTEMPT=os.environ.get('PHASE4C_ATTEMPT','combined')
r={'stage':'started','solve_success':False,'temporary_only':True,'downstream_authorised':False}
def save(): (O/('solve_result_'+ATTEMPT+'.json')).write_text(json.dumps(r,indent=2),encoding='utf-8');print('PHASE4C_STAGE',r['stage'])
def xyz(v): return [v.x,v.y,v.z]
save()
try:
    sub=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
    r['subsystem']=str(sub);r['stage']='subsystem';save()
    path=BASE+'/Geometry/SM_Lara180'
    assert not unreal.EditorAssetLibrary.does_asset_exist(BASE+'/Donor/MHC_LaraDonor_'+ATTEMPT)
    mesh=unreal.load_asset(path)
    if mesh is None:mesh=unreal.EditorAssetLibrary.duplicate_asset('/Game/MetaHumanTo3DCharacter/Phase4B/Geometry/SM_Lara180',path)
    if not mesh:raise RuntimeError('Cannot create isolated target surface')
    unreal.EditorAssetLibrary.save_asset(path)
    verts,indices=sub.get_mesh_data_for_conforming(mesh)
    r['target_mesh']=path;r['target_vertex_count']=len(verts);r['target_triangles']=len(indices)//3
    (W/'ue_target_geometry.json').write_text(json.dumps({'vertices_cm':[xyz(v) for v in verts],'triangle_indices':list(indices)}))
    r['stage']='target_ready';save()
    char=unreal.AssetToolsHelpers.get_asset_tools().create_asset('MHC_LaraDonor_'+ATTEMPT,BASE+'/Donor',unreal.MetaHumanCharacter,unreal.MetaHumanCharacterFactoryNew())
    if char is None:raise RuntimeError('Character factory returned None')
    r['character']=char.get_path_name();r['stage']='character_created';save()
    if not sub.try_add_object_to_edit(char):raise RuntimeError('try_add_object_to_edit returned false')
    r['stage']='character_editable';save()
    params=unreal.ConformTargetParams()
    target=unreal.ConformTargetMesh()
    target.target_parts_type=unreal.TargetPartsType.COMBINED
    target.body_vertices=verts;target.body_vertex_indices=indices
    params.conform_target_mesh=target
    params.auto_solve=True;params.estimate_body_joints_from_mesh=True
    settings=unreal.BodyConformSolveSettings()
    settings.pipeline_name='combined';settings.face_iterations=0
    params.body_conform_solve_settings=settings
    key=unreal.MetaHumanCharacterTargetMeshKey();key.combined_mesh=mesh
    r['config']={'target_parts_type':'COMBINED','pipeline':'combined','auto_solve':True,'estimate_body_joints_from_mesh':True,'face_iterations':0,'keypoints':0,'face_tracking_curves':0,'input_space':'UE cm +X left +Y forward +Z up','settings':str(settings)}
    (O/('solve_configuration_'+ATTEMPT+'.json')).write_text(json.dumps(r['config'],indent=2))
    r['stage']='solving';save();start=time.monotonic()
    ok=sub.conform_to_target_meshes(char,key,params)
    r['solve_success']=bool(ok);r['solve_seconds']=time.monotonic()-start;r['stage']='solve_returned';save()
    if not ok:raise RuntimeError('conform_to_target_meshes returned false')
    unreal.EditorAssetLibrary.save_asset(char.get_path_name())
    exp=unreal.MetaHumanPosedDNAExportParams();exp.target_mesh_key=key
    exp.external_path=str(W/'Donor');exp.project_path='';exp.asset_name='LaraDonor_'+ATTEMPT+'_Posed';exp.overwrite_existing_assets=False
    unreal.MetaHumanCharacterExportBlueprintLibrary.export_posed_dna(char,exp)
    dna=W/('Donor/LaraDonor_'+ATTEMPT+'_Posed.dna');r['posed_dna_exists']=dna.is_file()
    r['stage']='posed_export';save()
    if dna.is_file():
        r['posed_dna_sha256']=hashlib.sha256(dna.read_bytes()).hexdigest()
        code,joints,rotations=sub.get_joints_for_body_conforming_from_dna(str(dna))
        (O/'solved_donor_joints_raw.json').write_text(json.dumps({'api':'get_joints_for_body_conforming_from_dna','error_code':str(code),'world_translations':[xyz(x) for x in joints],'rotations':[xyz(x) for x in rotations],'name_order_status':'requires DNA/name correspondence verification'},indent=2))
        r['joint_read_code']=str(code);r['joint_count']=len(joints)
    unreal.EditorAssetLibrary.save_asset(char.get_path_name())
    r['stage']='complete';save()
except Exception:
    r['error']=traceback.format_exc();r['stage']='failed';save()
