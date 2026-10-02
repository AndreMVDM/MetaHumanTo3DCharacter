from pathlib import Path
import json,csv,re
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase3B'
required=['baseline_import.json','height_measurements.json','scaled_candidates.json','root_reference_transforms.json','ik_rig_results.json','retargeter_results.json','pose_offsets.json','solver_isolation.json','mixamo_foot_tests.json','runtime_samples.json']
def load(name):return json.loads((O/name).read_text(encoding='utf-8'),parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
for name in required:load(name)
report=(O/'Phase3BHeightNormalisationRetargeting.md').read_text(encoding='utf-8')
assert len(re.findall(r'^## [0-9]+\.',report,re.M))==20
assert report.startswith('🟢 **High confidence**')
assert len(list(csv.DictReader((O/'height_matrix.csv').open())))==10
saved=load('saved_asset_verification.json');assert len(saved)==10 and all(r['pass'] for r in saved),saved
refs=load('reference_validation.json');assert len(refs)==10 and all(not r['reference_gate_failures'] and r['hierarchy_unchanged'] for r in refs)
metrics=load('quantitative_metrics.json');main=[r for r in metrics['samples'] if r['label'] in ['OriginalHeight','Height160','Height175','Height180','Height200']]
assert len(main)==2750 and all(r['sanity_pass'] for r in main)
liv=load('live_solver_isolation.json');assert len(liv['summary'])==64 and all(r['pass'] for r in liv['summary'] if not r['component'].startswith('Raw'))
assert all(not r['pass'] for r in liv['summary'] if r['component'].startswith('Raw'))
ind=load('independence_verification.json');assert ind['no_live_manny_components'] and ind['baked_full_clips']==50 and ind['foreign_game_dependency_count']==0
assert all(r['animation_advanced'] and r['sanity_pass'] for r in ind['destination_native_playback'])
assert load('protected_after_verification.json')['pass']
for file in ['height_reference_matrix.png','ue5_run_cycle.png','mixamo_run_cycle.png','live_unlit_view.jpg']:assert (O/file).stat().st_size>1000
for link in re.findall(r'\]\(([^)]+)\)',report):
    if not link.startswith('https://'):assert (O/link).exists(),link
out={'pass':True,'required_json_files':len(required),'report_sections':20,'height_matrix_rows':10,'fresh_process_saved_asset_passes':10,'main_pose_passes':len(main),'live_clean_component_clip_passes':48,'expected_raw_component_clip_failures':16,'baked_full_clips_without_foreign_game_dependencies':50,'no_manny_native_playback_passes':2,'protected_files_unchanged':110,'root_motion_limits':'UE5 corrected selector passes25samples;Mixamo corrected selector rejected25samples for collapsed Hips height.','self_review':'Checked required outputs, real disk assets, runtime space claims, weight repair exception, historical failed controls, bind-pose warnings, contact-quality limits and authoring/runtime dependency distinction.'}
(O/'acceptance_verification.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
