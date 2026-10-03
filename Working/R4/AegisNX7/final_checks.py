"""Independent acceptance checks over native R4 evidence and saved file hashes."""
import json,hashlib,collections,subprocess
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/R4/AegisNX7'
read=lambda n:json.loads((O/n).read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
M=read('animation_library_manifest.json');F=read('fresh_validation.json');N=read('native_library.json');I=read('native_verification.json');P=read('preservation_audit.json');S=read('installed_source_provenance.json');checks={}
checks['all_default_baked']=M['status']=='PASS' and M['totals']['default']==M['totals']['succeeded']==M['totals']['attempted'] and M['totals']['failed']==0
rows=[r for r in M['entries'] if r.get('bake_result')=='PASS'];checks['unique_destinations']=len({r['destination_path'] for r in rows})==len(rows)
checks['all_saved_reloaded']=F['status']=='PASS' and F['total']==len(rows) and {r['path'] for r in F['animations']}=={r['destination_path'] for r in rows}
checks['saved_animation_hashes_stable']=all(sha((R/'Content'/r['path'].split('.')[0].removeprefix('/Game/')).with_suffix('.uasset'))==r['sha256'] for r in F['animations'])
checks['installed_sources_and_staged_copies_unchanged']=all(sha(Path(r['installed_source']))==r['sha256'] and sha((R/'Content'/r['staged_package'].removeprefix('/Game/')).with_suffix('.uasset'))==r['sha256'] for r in S['copies'])
checks['root_policy_and_metadata_retained']=all(all(r['metadata_comparison'].values()) and r['root_flags']==r['destination_metadata']['root_flags'] for r in rows)
checks['source_bound_root_certificates']=all(r['validation']['status']=='PASS' and r['validation']['source_bound_root_deltas']==f['validation']['source_bound_root_deltas'] for r,f in zip(rows,F['animations']))
checks['representative_native_playback']=N['status']=='PASS' and len(N['phases'])==8 and all(r['status']=='PASS' for r in N['phases'])
checks['all_controls_and_jump_flow']=I['status']=='PASS' and len(I['phases'])==9 and all(r['status']=='PASS' for r in I['phases'])
j=I['phases'][-1]['air_observations'];checks['actual_jump_fall_land_and_return']=any(r['airborne'] and r['jump_start'] and r['vertical_velocity']>0 for r in j) and any(r['airborne'] and not r['jump_start'] and r['vertical_velocity']<0 for r in j) and any(r['landing'] for r in j) and not j[-1]['airborne'] and not j[-1]['landing']
checks['destination_runtime_closure']=F['runtime_dependency_closure']['certificate']['status']=='PASS' and not F['runtime_dependency_closure']['authoring_packages'] and not F['bridge_loaded']
append=read('runtime_log_append_audit.json');b=read('baseline.json');log=R/append['path'];prefix_bytes=append['baseline_prefix_bytes'];prefix_verified=prefix_bytes is not None and hashlib.sha256(log.read_bytes()[:prefix_bytes]).hexdigest()==b['protected'][append['path']]
checks['protected_authored_files_and_git_unchanged']=P['changed']==[append['path']] and not P['missing'] and P['git_preserved'] and prefix_verified
checks['ready_handoff']=I['ready_to_press_Play'] and I['PIE_stopped'] and I['editor_left_open'] and I['review_level_loaded'].split('.')[0]==read('review_build.json')['assets']['level']
command=subprocess.check_output(['powershell','-NoProfile','-Command',f"(Get-CimInstance Win32_Process -Filter 'ProcessId={I['pid']}').CommandLine"],text=True)
checks['review_editor_process_still_running']='Working/R4/AegisNX7/verify_and_handoff.py' in command.replace('\\','/')
result=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,totals=M['totals'],categories=dict(collections.Counter(r['category'] for r in rows)),reference_height_cm=F['height_cm'],jump_rise_cm=max(r['position'][2] for r in j)-min(r['position'][2] for r in j),preservation=dict(protected=P['protected_count'],authored_files_changed=0,runtime_log_append=append['path'],original_log_prefix_preserved=prefix_verified,git_preserved=P['git_preserved']),editor_pid=I['pid'],visual_quality='Technical playback acceptance only; Andre human review remains',evidence_hashes={n:sha(O/n) for n in ['animation_library_manifest.json','source_inventory.json','fresh_validation.json','native_library.json','native_verification.json','review_build.json','preservation_audit.json','runtime_log_append_audit.json']})
(O/'final_acceptance.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
