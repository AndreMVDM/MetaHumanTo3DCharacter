"""Proportional acceptance review of final Phase4C evidence; fail if internally inconsistent."""
import json,re,hashlib,ast
from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4C';O=P/'Documentation/Phase4C'
def read(n):return json.loads((O/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(n,ok,evidence):checks.append({'check':n,'passed':bool(ok),'evidence':evidence})
fit=read('automatic_fit_v2.json');mapping=read('donor_to_lara_mapping.json');gate=read('anatomical_validation.json');f=read('finger_validation.json');a=read('protected_file_audit.json');tr=read('transform_mapping.json');d=read('donor_extraction.json')
check('actual_combined_solve',read('solve_result_combined.json')['solve_success'] and read('solve_result_combined.json')['stage']=='complete','real Boolean result and completion marker')
check('public_extract_name_position_correspondence',d['extraction_success'] and d['joint_count']==342 and d['python_native_joint_max_cm']==0,'Both public APIs; 342 names/parents and identical positions')
check('saved_donor_reload',read('dependency_evidence.json')['saved_donor_fresh_process_reload'],'Separate commandlet; DDC exit limitation disclosed')
check('mapping_sha_matches_independent_proposal',mapping['proposal_sha256']==sha(O/'automatic_fit_v2.json'),'Donor proposal saved before control evaluation')
check('no_missing_body_substitution',len(fit['joints'])==23 and all(r['direct_solved_joint'] for r in fit['joints']),'Every canonical body point has direct donor provenance')
check('numeric_roundtrip',tr['round_trip_max_cm']<1e-9 and tr['donor_round_trip_max_cm']<1e-9 and tr['ue_target_indexwise_vertex_max_difference_cm']<1e-4,'Mesh/joint inverse and actual target readback')
check('ue_triangulation_limit_disclosed',not tr['ue_target_triangle_indices_identical'] and bool(tr.get('ue_triangle_connectivity_limit')),'Temporary UE triangulation differs; original polygon preservation separately verified')
base=(P/'Working/Phase4B/validate_fit.py').read_text();actual=(W/'validate_fit.py').read_text(encoding='utf-8-sig')
expected=base.replace("W=P/'Working/Phase4B';O=P/'Documentation/Phase4B'","W=P/'Working/Phase4C';O=P/'Documentation/Phase4C'").replace('from geometry_tools import sections,nearest_distances',"sys.dont_write_bytecode=True\nsys.path.insert(0,str(Path(__file__).resolve().parents[2]/'Working/Phase4B'))\nfrom geometry_tools import sections,nearest_distances")
check('inherited_gate_algorithm_unchanged',actual.strip()==expected.strip(),'Only output/input namespace and read-only helper import adapted')
check('body_gate_rejected_with_19_review_roles',not gate['passed'] and len([r for r in fit['joints'] if r['status']=='ambiguous'])==19 and len(gate['failed'])==22,'20 inherited failures plus two finger extension failures')
check('finger_semantics_and_collapse',f['exposed_phalange_joints']==30 and [r['distinct_assigned_branches'] for r in f['checks']]==[1,2] and f['named_chains_accepted_for_lara']==0,'All five target tracks considered; no forced finger acceptance')
cor=read('correction_measurements.json');check('real_corrections_not_fabricated',cor['actual_corrections_applied']==0 and not cor['minimal_correction_proven'],'Empty hash-bound patch; effort explicitly unmeasured')
for n in ['skinning_results.json','ik_retarget_configuration.json','animation_bake_results.json','source_independent_playback.json']:
    x=read(n);check(n,not x['authorised'] and not x['created_assets'],'Stopped at rejected anatomy')
assets=read('dependency_evidence.json')['phase4c_assets'];check('no_downstream_assets',len(assets)==2 and all('MHC_LaraDonor_combined' in n or 'SM_Lara180' in n for n in assets),assets)
check('protected_authored_files',a['passed'] and a['archive_byte_identical'] and a['protected_file_count']==2392,'Fresh hashes against immutable preflight baseline')
check('source_polygon_uv_preservation',read('source_preservation.json')['passed'],'Independent final Blender source reload')
report=(O/'Phase4CMetaHumanSemanticDonor.md').read_text();headings=re.findall(r'^## (\d+)\.',report,re.M);check('24_requested_sections',headings==[str(i) for i in range(1,25)],headings)
broken=[]
for link in re.findall(r'\]\(([^)]+)\)',report):
    if link.startswith('https://'):continue
    target=(O/link).resolve()
    if target.name in ['self_review.json','execution_manifest.json']:continue
    if not target.exists():broken.append(link)
check('local_report_links_resolve',not broken,broken)
views=['original_Lara_surface','temporary_donor_overlay','donor_semantic_skeleton','mapped_donor_front','mapped_donor_side','front_comparison','side_comparison','pelvis_hip_closeup','shoulder_elbow_closeup','knee_closeup','ankle_ball_foot_closeup','hand_finger_closeup','hand_finger_right_closeup','Phase4B_vs_Phase4C_overlay']
check('14_visuals_decode',all(Image.open(O/(n+'.png')).size==(1250,1050) for n in views),'Contact sheet plus selected full-size views inspected')
for p in W.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
check('python_sources_parse',True,'All Phase4C top-level Python scripts parsed; Engine Python scripts also executed where required')
result={'passed':all(r['passed'] for r in checks),'workflow':'Level 1 single agent self-review; no independent reviewer claimed','checks':checks,'visual_inspection':'14-view contact sheet and full-size donor side/hand views inspected; labels and both hands made readable','anatomical_quality':'rejected; this review verifies faithful evidence and safe stopping, not acceptable anatomy'}
(O/'self_review.json').write_text(json.dumps(result,indent=2));assert result['passed'],[r for r in checks if not r['passed']]
manifest={'date':'2026-10-01','engine':'5.8.3-58210709','temporary_namespace':'/Game/MetaHumanTo3DCharacter/Phase4C',
 'configuration_changes':[],'execution_phases':[{'phase':'preflight/fresh ZIP/source frame','scripts':['preflight.py','prepare_geometry.py','normalise.py'],'logs':['source_verification.log']},
 {'phase':'plugin probe','scripts':['ue_probe.py'],'logs':['probe.log','probe_memory.log']},
 {'phase':'body-only diagnostic (historical configuration recorded; script later adapted to combined)','scripts':['ue_solve.py'],'logs':['solve.log'],'evidence':['solve_result_bodyonly_fullsurface.json','donor_joints_bodyonly_fullsurface.json']},
 {'phase':'combined solve','scripts':['ue_solve.py'],'logs':['solve_combined.log','solve_combined_stdout.log'],'evidence':['solve_result_combined.json','solve_configuration_combined.json']},
 {'phase':'public native helper build','scripts':['run_native_actions.py'],'logs':['native_build_stdout.log','native_actions_stdout.log'],'limit':'UBT UBA executor failed; compiled/linker actions and module execution verified'},
 {'phase':'posed public extraction','scripts':['ue_extract.py'],'logs':['extract_combined.log'],'evidence':['donor_extraction.json','solved_donor_joints.json']},
 {'phase':'fresh reload and authoring dependency edges','scripts':['ue_dependencies.py'],'logs':['dependencies.log','dependencies_stdout.log'],'limit':'exit code 1 due DDC error; query succeeded'},
 {'phase':'mapping/evaluation/gate/correction/render/audit/report','scripts':['analyse.py','validate_fit.py','render_evidence.py','verify_source.py','finalise.py','write_report.py','self_review.py']}],
 'commandlet_load_flags':['-EnablePlugins=MetaHumanCharacter','-DDC-ForceMemoryCache','-unattended','-nullrhi'],
 'extraction_additional_flags':['-Plugin=<absolute Phase4CTools.uplugin>','-EnablePlugins=MetaHumanCharacter,Phase4CTools'],
 'rerun_limit':'Solve script deliberately rejects an existing donor asset and refuses overwrite. Use a fresh namespace for a new solve; do not rerun against this retained evidence without adaptation.',
 'document_sha256':sha(O/'Phase4CMetaHumanSemanticDonor.md'),'evidence_files':[{ 'path':str(p.relative_to(P)), 'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(O.glob('*')) if p.is_file() and p.name!='execution_manifest.json'],
 'script_hashes':{p.name:sha(p) for p in sorted(W.glob('*.py'))},'native_helper_source':[{ 'path':str(p.relative_to(P)), 'sha256':sha(p)} for p in (W/'NativeHost/Plugins/Phase4CTools/Source').rglob('*') if p.is_file()]}
(O/'execution_manifest.json').write_text(json.dumps(manifest,indent=2));print('SELF_REVIEW',len(checks),'checks passed')
