"""Evidence acceptance audit; no asset mutation and no production quality certification."""
import json,math,re,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase4A';checks=[]
def load(n):return json.loads((O/n).read_text())
def check(name,value,evidence):checks.append({'check':name,'passed':bool(value),'evidence':evidence});assert value,name
required=['zip_inventory.json','geometry_comparison.json','autorig_api_inventory.json','autoskin_api_inventory.json','skeleton_analysis.json','skin_weight_analysis.json','material_uv_validation.json','ik_rig_results.json','retargeter_results.json','runtime_samples.json','foot_comparison.json','bake_dependencies.json','Phase4AAutoRigInvestigation.md']
check('All requested deliverables exist',all((O/n).is_file() for n in required),required)
check('All Phase4A JSON parses',all(json.loads(p.read_text()) is not None for p in O.glob('*.json')),str(O))
report=(O/'Phase4AAutoRigInvestigation.md').read_text(encoding='utf-8');sections=re.findall(r'^## (\d+)\. ',report,re.M)
check('Twenty requested numbered report sections',sections==list(map(str,range(1,21))),'Phase4AAutoRigInvestigation.md')
check('Report distinguishes diagnosis and acceptance','production-quality automatic humanoid rig is not established' in report and 'assisted control' in report and 'clean-project migration and a packaged/cooked executable were not tested' in report,'Report sections 1, 10, 17, 19')
auto=load('medial_trials.json');check('Four executed automatic skeleton trials',len(auto)==4 and all(r['generated'] and not r.get('error') for r in auto),'medial_trials.json')
sk=load('skeleton_analysis.json');check('All four automatic candidates rejected on structural evidence',len([r for r in sk if r['type']=='automatic_medial' and not r['accepted_humanoid']])==4,'skeleton_analysis.json')
check('Original and corrected assisted bakes valid',all(len(load(n))==2 and all(not r.get('error') and r['auto_characterisation'] and len(r['clips'])==8 and all(c['finite'] for c in r['clips'].values()) for r in load(n)) for n in ['animation_results.json','animation_results_ball_forward.json']),'animation_results*.json')
check('800 UE baked pose samples',all(len(load(n)['samples'])==400 for n in ['runtime_samples.json','runtime_samples_ball_forward.json']),'runtime_samples*.json')
for suffix in ['', '_ball_forward']:
    live=load('independence_live'+suffix+'.json');check('Actual native playback with Manny removed'+suffix,len(live['samples'])==100 and live['manny_destroyed'] and not live['errors'] and not any(s['manny_components_remaining'] for s in live['samples']) and {s['role'] for s in live['samples']}=={'idle','walk','run','reach'},'independence_live'+suffix+'.json')
    for case in ['Unrigged','MixamoRecovered']:
        comp=[c for s in live['samples'] for c in s['components'] if c['name']==case]
        check('Native instance and unit component scale '+case+suffix,len(comp)==100 and all('AnimSingleNodeInstance' in c['anim_instance_class'] and c['world_transform']['scale']==[1,1,1] for c in comp),'Live native component records')
        check('Native poses change '+case+suffix,len({json.dumps(c['bones']['hand_l']['component']) for c in comp})>1,'Live native component bone records')
    disk=load('disk_reload_validation'+suffix+'.json');check('Disk geometry, UV and material persistence'+suffix,len(disk)==2 and all(not r.get('error') and r['geometry_equal_to_bound_dynamic_mesh'] and r['uv_equal_to_bound_dynamic_mesh'] and all(m['material'] for m in r['materials']) and not r['weight_stats']['invalid_or_unweighted_vertices'] for r in disk),'disk_reload_validation'+suffix+'.json')
    dep=load('bake_dependencies'+suffix+'.json');check('No foreign Game/helper dependency'+suffix,len(dep)==2 and all(not r['foreign_game_packages'] and not r['native_plugin_dependencies'] for r in dep),'bake_dependencies'+suffix+'.json')
height=load('height_ordering_results.json');check('Physical 175cm, unit scales and coordinated reference dimensions',len(height)==4 and all(not r.get('error') and abs(r['snapshot']['bounds']['height_cm']-175)<1e-5 and r['max_bone_translation_scale_error_cm']<1e-8 and r['uv_identical'] and r['triangles_identical'] and not r['weight_stats']['invalid_or_unweighted_vertices'] and all(abs(s-1)<1e-5 for b in r['snapshot']['bones'].values() for s in b['local']['scale']) for r in height),'height_ordering_results.json')
check('Coordinated scaling preserves all weights',all(r['weights_identical'] and r['weight_max_absolute_delta']==0 for r in height if r['route']=='BindThenScale'),'height_ordering_results.json')
check('Four final-height IK rigs',len(load('height_ik_results.json'))==4 and all(not r.get('error') and len(r['snapshot']['solvers'])==1 for r in load('height_ik_results.json')),'height_ik_results.json')
check('Full weighted coverage',all(r['zero_weight_vertices']==0 and r['max_positive_influences']<=5 for r in load('skin_weight_analysis.json')['statistics']),'skin_weight_analysis.json')
check('Source texture and UV preservation',load('material_uv_validation.json')['accepted_preservation'] and load('material_uv_validation.json')['source_jpeg_unchanged'] and load('uv_import_validation.json')['uv_import_comparison']['source_values_within_1e_6'],'material_uv_validation.json')
check('New authored asset boundary',all(n in load('protected_before.json') or n.startswith('Content/MetaHumanTo3DCharacter/Phase4A/') for n in [p.relative_to(P).as_posix() for p in (P/'Content').rglob('*.uasset')] if n.replace('/','\\') not in load('protected_before.json')),'Current Content assets against protected baseline')
check('Protected files unchanged',load('protected_validation.json')['all_unchanged'] and load('protected_validation.json')['baseline_files']==505,'protected_validation.json')
check('Final output remains diagnostic',not load('phase4a_result.json')['production_rig_accepted'] and not load('phase4a_result.json')['automatic_humanoid_rig_accepted'],'phase4a_result.json')
result={'workflow':'Level 1 single agent plus self-review','all_checks_passed':all(r['passed'] for r in checks),'checks':checks,'report_sha256':hashlib.sha256(report.encode()).hexdigest(),'quality_verdict':'Investigation complete; automatic humanoid and production skin quality not accepted','limits':['No independent second reviewer','No clean-project migration or cooked executable','No anatomical ground truth','No dedicated finger animation acceptance','No contact-aware world-speed test','175cm animation bake not validated']}
(O/'acceptance_self_review.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('SELF_REVIEW',len(checks),'checks passed')
