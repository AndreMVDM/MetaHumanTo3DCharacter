import unreal,json,traceback,hashlib
from pathlib import Path
P=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4C';O=P/'Documentation/Phase4C'
dna=W/'Donor/LaraDonor_combined_Posed.dna'
r={'posed_dna_exists':dna.is_file(),'posed_dna_sha256':hashlib.sha256(dna.read_bytes()).hexdigest(),'source':'actual solved Phase4C export'}
try:
    data=json.loads(unreal.Phase4CLibrary.inspect_posed_dna(str(dna)))
    if data.get('error'):raise RuntimeError(data['error'])
    (W/'donor_geometry_and_joints.json').write_text(json.dumps(data),encoding='utf-8')
    (O/'solved_donor_joints.json').write_text(json.dumps({k:v for k,v in data.items() if k!='meshes_lod0'},indent=2),encoding='utf-8')
    r['joint_count']=len(data['joints']);r['mesh_count']=len(data['meshes_lod0']);r['extraction_success']=True
    sub=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
    code,joints,rots=sub.get_joints_for_body_conforming_from_dna(str(dna))
    r['python_joint_api_code']=str(code);r['python_joint_count']=len(joints)
    if len(joints)==len(data['joints']):
        r['python_native_joint_max_cm']=max(sum((a-b)**2 for a,b in zip([q.x,q.y,q.z],row['world_cm']))**.5 for q,row in zip(joints,data['joints']))
    r['assets']=unreal.EditorAssetLibrary.list_assets('/Game/MetaHumanTo3DCharacter/Phase4C',recursive=True,include_folder=False)
    r['assets']=list(r['assets'])
except Exception:r['error']=traceback.format_exc()
(O/'donor_extraction.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print('PHASE4C_EXTRACTION',r)
