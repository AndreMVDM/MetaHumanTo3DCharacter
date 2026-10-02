"""Final evidence integrity/acceptance self-review; read-only except its Phase4B record."""
import json,hashlib,re,ast
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B';checks=[]
def check(n,value):
    checks.append({'check':n,'passed':bool(value)});assert value,n
def read(n):return json.loads((O/n).read_text(),parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON '+x)))
for p in O.glob('*.json'):json.loads(p.read_text(),parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON '+x)))
check('all_documentation_json_strict_finite',True)
for p in W.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
check('retained_scripts_parse',True)
report=(O/'Phase4BSemanticJointFitting.md').read_text();numbers=[int(x) for x in re.findall(r'^## (\d+)\.',report,re.M)];check('required_23_report_sections',numbers==list(range(1,24)))
refs=re.findall(r'\]\(([^)]+)\)',report)
for ref in refs:
    if not ref.startswith('https://'):check('report_reference_exists_'+ref,(O/ref).exists())
for name in ['raw_geometry_sections','automatic_major_landmarks','fitted_skeleton_front','fitted_skeleton_side','hand_finger_evidence','foot_ankle_ball','ue_fit_front','ue_fit_side']:
    with Image.open(O/(name+'.png')) as im:im.verify()
check('all_required_applicable_images_readable',True)
fit=read('automatic_fit_v2.json');gate=read('anatomical_validation_v2.json');summary=read('experiment_result.json');control=read('manual_control_comparison_v2.json');audit=read('protected_file_audit.json');imp=read('ue_import_validation.json');corr=read('correction_model_validation.json')
sha=hashlib.sha256((O/'automatic_fit_v2.json').read_bytes()).hexdigest()
check('control_compared_current_immutable_fit',control['automatic_proposal_unchanged_sha256']==sha)
check('correction_patch_bound_current_fit',json.loads((W/'corrections.json').read_text())['input_fit_sha256']==sha)
check('gate_bound_current_fit',gate['proposal_sha256']==sha)
check('result_count_consistency',len(fit['joints'])==23 and summary['ambiguous_body_role_count']==sum(r['status']=='ambiguous' for r in fit['joints'])==17)
check('rejected_anatomy_no_downstream_claim',not gate['downstream_authorised'] and not summary['runtime_source_independence']['verified'] and summary['bake']['animations']==[])
check('protected_audit_pass',audit['passed'] and audit['protected_baseline_files']==980)
check('final_geometry_uv_readback_pass',imp['geometry_vertex_positions_pass'] and imp['uv_at_position_pass'] and imp['triangle_count_difference']==0)
check('replay_fixtures_pass',all(corr[k] for k in ['deterministic_replay_pass','patch_order_independence_pass','explicit_child_correction_preserved','fit_hash_binding_pass','dependency_anatomical_acceptance_invalidated']))
synthetic=read('anatomical_validation_corrected.json');check('synthetic_moved_spines_still_rejected',not synthetic['downstream_authorised'] and all('anatomical_role_resolved_spine_%02d'%i in synthetic['failed'] for i in [1,2,3]))
check('no_manual_anatomical_signoff_claim',summary['actual_user_corrections']==0 and not gate['manual_anatomical_review_roles'])
inventory=read('semantic_api_inventory.json');check('unique_installed_systems',len({s['name'] for s in inventory['systems']})==len(inventory['systems'])==16 and all(s['installed'] for s in inventory['systems']))
result={'passed':all(c['passed'] for c in checks),'checks':checks,'review_level':'Level 1 self-review plus one focused Level 2 independent source reviewer','independent_review':'Prior correction ordering/hash/revalidation issues repaired. Final reviewer confirmed code closures; root verified exact field dependency_anatomical_acceptance_invalidated=true in current evidence. Review is not anatomical certification.','actual_human_anatomical_review_count':0,'report_sha256':hashlib.sha256((O/'Phase4BSemanticJointFitting.md').read_bytes()).hexdigest()}
(O/'self_review.json').write_text(json.dumps(result,indent=2));print('SELF_REVIEW',result['passed'],len(checks))
manifest={}
for root in [W,O,P/'Content/MetaHumanTo3DCharacter/Phase4B']:
    for p in root.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence_manifest.json':manifest[str(p.relative_to(P))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(O/'evidence_manifest.json').write_text(json.dumps(manifest,indent=2));print('EVIDENCE_FILES',len(manifest))
