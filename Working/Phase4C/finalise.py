"""Fail-closed aggregate gate, installed boundary inventory, and protected audit."""
import json,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4C';O=P/'Documentation/Phase4C';E=Path('D:/Epic Games/UE_5.8/Engine')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(O/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
base=read(O/'anatomical_validation_v2.json');fingers=read(O/'finger_validation.json')
extended=dict(base);extended['extension_checks']=[{'name':'finger_target_tracks_not_collapsed','pass':fingers['collision_screen_passed'],'measured':fingers['checks']},
 {'name':'finger_chains_anatomically_resolved','pass':fingers['named_chains_accepted_for_lara']==10,'measured':fingers['named_chains_accepted_for_lara'],'threshold':'10/10 independently accepted chains'}]
extended['failed']=base['failed']+[q['name'] for q in extended['extension_checks'] if not q['pass']];extended['passed']=not extended['failed'];extended['downstream_authorised']=extended['passed']
extended['clavicle_sign_limit']='Existing 4B side-sign screen fails right clavicle root X=+0.069cm. This is a convention-sensitive central root, not proof that actual arms crossed. Review rather than weaken the gate silently.'
save('anatomical_validation.json',extended)
status={'status':'not_run_anatomy_rejected','anatomical_gate_passed':extended['passed'],'authorised':extended['downstream_authorised'],'created_assets':[],
 'reason':'19 unresolved body articulations, strict clavicle side screen, collapsed digit mapping. No donor geometry or skin weights used as final Lara.'}
for n in ['skinning_results.json','ik_retarget_configuration.json','animation_bake_results.json','source_independent_playback.json']:save(n,status)
boundary_files=[
 'Plugins/MetaHuman/MetaHumanCharacter/MetaHumanCharacter.uplugin',
 'Plugins/MetaHuman/MetaHumanCoreTechLib/MetaHumanCoreTech.uplugin',
 'Plugins/Animation/RigLogic/RigLogic.uplugin',
 'Plugins/MetaHuman/MetaHumanCharacter/Source/MetaHumanCharacterEditor/Public/MetaHumanCharacterEditorSubsystem.h',
 'Plugins/MetaHuman/MetaHumanCharacter/Source/MetaHumanCharacterEditor/Public/MetaHumanCharacterExportBlueprintLibrary.h',
 'Plugins/MetaHuman/MetaHumanCoreTechLib/Source/MetaHumanCoreTechLib/Public/MetaHumanCoreTechMeshUtils.h',
 'Plugins/MetaHuman/MetaHumanCoreTechLib/Source/MetaHumanCoreTechLib/Public/MetaHumanConformTargetParams.h',
 'Plugins/Animation/RigLogic/Source/RigLogicModule/Public/DNAUtils.h',
 'Plugins/Animation/RigLogic/Source/RigLogicModule/Public/DNAReader.h']
inventory=[]
for n in boundary_files:
    p=E/n;row={'path':str(p),'exists':p.is_file()}
    if p.is_file():row.update(sha256=sha(p),bytes=p.stat().st_size)
    if p.suffix=='.uplugin' and p.is_file():row['descriptor']=read(p)
    inventory.append(row)
models=[]
for n in ['body_model.dna','skin_model.binary','rbf_model.binary','pipeline_presets.json']:
    p=E/'Plugins/MetaHuman/MetaHumanCharacter/Content/Body/IdentityTemplate'/n;models.append({'path':str(p),'exists':p.is_file(),'bytes':p.stat().st_size if p.is_file() else None,'copied':False,'reverse_engineered':False})
save('semantic_api_inventory.json',{'engine':read(O/'python_api_probe.json')['engine'],'installed_public_boundaries':inventory,'installed_model_resources':models,
 'explicit_plugin_loads':['MetaHumanCharacter','Phase4CTools (extraction only)'],'helper_dependencies':['RigLogicModule','MetaHumanCoreTechLib'],
 'project_configuration_changes':[],'engine_source_changes':[],'python_execution':'PythonScriptPlugin already enabled in unchanged project',
 'access':{'python':'executed conform_to_target_meshes and joint readback','blueprint':'public reflected Blueprint-callable export/subsystem declarations inspected; graph not executed','cpp':'compiled public DNA reader and world joint helper executed'},
 'private_boundary_policy':'Installed implementation inspected to understand basis/pipeline. No private source copied, no model matrices read directly, no binary reverse engineering.'})
save('web_sources.json',{'checked_date':'2026-10-01','sources':[
 {'url':'https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-custom-mesh-tool-in-unreal-engine','purpose':'combined/body-only input modes, custom pose export, keypoints and input limits'},
 {'url':'https://www.metahuman.com/license','purpose':'standard Unreal Engine licence scope; no inferred redistribution permission'},
 {'url':'https://www.unrealengine.com/eula/unreal','purpose':'Engine Tools, redistribution, seats and MetaHuman ML restrictions; professional review required'}]})
before=read(O/'protected_before.json')['files'];changed=[];missing=[]
for n,row in before.items():
    p=P/n
    if not p.is_file():missing.append(n)
    elif sha(p)!=row['sha256']:changed.append(n)
new=[]
for root in ['Characters','Config','Content','Reference','Documentation','Working']:
    for p in (P/root).rglob('*'):
        if not p.is_file() or any(n in p.parts for n in ['Intermediate','Saved','Binaries','DerivedDataCache','__pycache__']):continue
        n=str(p.relative_to(P))
        if n not in before and 'Phase4C' not in p.parts:new.append(n)
audit={'protected_file_count':len(before),'changed':changed,'missing':missing,'new_authored_files_outside_phase4c':new,
 'passed':not changed and not missing and not new,'archive_sha256_after':sha(P/'Characters/Lara_UnRigged_Textured.zip'),
 'archive_sha256_before':read(O/'input_inventory.json')['archive_sha256'],
 'scope':read(O/'protected_before.json')['scope'],'configuration_byte_identical':not any(n.startswith('Config') or n.endswith('.uproject') for n in changed),
 'engine_reference_limit':'Engine/reference locations were never write targets; project Reference authored files hashed. No pre-run exhaustive external Engine hash baseline, so no blanket cryptographic proof for the entire installation.',
 'expected_execution_caches':'UE Saved/Intermediate/DDC, NativeHost Binaries/Intermediate and external standard UE process caches are outside authored preservation scope.',
 'git_actions':'No Git repository; no stage, commit, push, branch or config change attempted'}
audit['archive_byte_identical']=audit['archive_sha256_after']==audit['archive_sha256_before'];save('protected_file_audit.json',audit)
save('experiment_result.json',{'solve_executed':True,'public_extraction_proven':True,'joint_count':342,'target_height_cm':180,'body_classification':'experimental assisted',
 'finger_classification':'automatic mapping rejected for Lara, correction effort unmeasured','anatomy_passed':extended['passed'],'failed_gate_count':len(extended['failed']),
 'actual_corrections_applied':0,'minimal_correction_proven':False,'downstream_authorised':extended['downstream_authorised'],'downstream_assets_created':[],
 'protected_file_audit_passed':audit['passed'],'proven_for_lara':'Temporary semantic donor extraction and deterministic inverse mapping; not anatomically accepted automation',
 'likely_reusable':'Editor-only public posed-DNA bridge to independent joint data, subject to version and licence review','generalisation':'unproven'} )
dep=read(O/'dependency_evidence.json');dep['commandlet_exit_code']=1;dep['commandlet_exit_reason']='DDC installed graph has no writable nodes; memory fallback logged an engine error. Python dependency query and fresh donor reload completed; exit is not reported as clean.';save('dependency_evidence.json',dep)
assert audit['passed'] and audit['archive_byte_identical'];assert not extended['passed'];assert len(d:=read(O/'solved_donor_joints.json')['joints'])==342
print('FINAL GATE',len(extended['failed']),'failures; audit',len(before),'unchanged')
