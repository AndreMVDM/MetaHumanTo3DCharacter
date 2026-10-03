"""Final focused integration verification and version provenance."""
import json,hashlib,ast,math
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=R/'Working/PlayableCharacter/LocomotionV1';O=R/'Documentation/PlayableCharacter/LocomotionV1';load=lambda n:json.loads((O/n).read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();G=load('generation.json');F=load('fresh_validation.json');P=load('preservation_audit.json');B=load('baseline.json');checks=[]
def check(n,x):checks.append(dict(name=n,status='PASS' if x else 'FAIL'))
check('fresh generation through generic entry',G['status']=='PASS' and G['landing_rule_installed_during_generation'] and G['post_generation_manual_edits']==0)
registry=json.loads((W.parent/'default_template.json').read_text());check('default registry pins executed generic implementation',registry['implementation_sha256']==G['generator_sha256']==sha(W/'generator.py') and registry['default_version']==G['version']);check('default entry exists', (W.parent/registry['entry_point']).is_file());route=load('DefaultRouteCheck/generation.json');check('default entry invokes generator and rejects overwrites',route['version']==G['version'] and route['status']=='FAIL' and 'output namespace must be empty; no overwrite' in route['error'])
check('fresh native bindings/closure and three rejection controls',F['status']=='PASS' and len(F['negative_controls'])==3 and all(c['status']=='PASS' for c in F['checks']))
subjects={}
for name in ['Fresh','Female','Aegis']:
 d=load(name+'_after_native.json');check(name+' fourteen native regressions',d['status']=='PASS' and len(d['cases'])==14);check(name+' main-project source-free runtime',not d['authoring_bridge_loaded'])
 measurements=[]
 for c in d['cases']:
  for e in c['touchdowns']:
   measurements.append(dict(case=c['name'],touchdown_speed_cm_s=e['touchdown_horizontal_speed'],first_grounded_state=e['first_grounded_state'],time_to_locomotion_s=e['delay_s'],distance_to_locomotion_cm=e['distance_cm']))
   if c['name']!='stationary_jump':check(name+' immediate moving touchdown '+c['name'],e['delay_s']==0 and e['distance_cm']==0 and e['first_grounded_state'] in ['Walk','Run'])
 # Sequence-player time and bone excursion after the retained blend confirm
 # resumed animation playback, beyond simply asserting bool selection.
 run=next(c for c in d['cases'] if c['name']=='run_jump_hold');td=run['touchdowns'][0]['touchdown']['t'];rows=[x for x in run['observations'] if td+.2<x['t']<td+.55];advance=max(x['player_times']['8'] for x in rows)-min(x['player_times']['8'] for x in rows);pose=max(math.dist(x['joints'][b],rows[0]['joints'][b]) for x in rows for b in x['joints']);check(name+' resumed native run is not frozen',len(rows)>2 and advance>.1 and pose>1)
 subjects[name]=dict(status=d['status'],map=d['map'],case_count=len(d['cases']),measurements=measurements,run_sequence_advance_s=advance,run_pose_excursion_cm=pose,CMC=d['CMC'],stature_cm=d['stature_cm'],runtime_root_motion_mode=d['runtime_root_motion_mode'])
 check(name+' stationary land retained',next(c for c in d['cases'] if c['name']=='stationary_jump')['touchdowns'][0]['first_grounded_state']=='Land')
check('native fresh run verifies final generated namespace',subjects['Fresh']['map']==G['assets']['level'])
libraries={}
for subject,folder in [('Female','FinalAcceptance/FemaleBodyRigged'),('Aegis','R4/AegisNX7')]:
 M=json.loads((R/'Documentation'/folder/'animation_library_manifest.json').read_text());rows=[]
 for e in M['entries']:
  if e.get('bake_result')!='PASS':continue
  path=(R/'Content'/e['destination_path'].split('.')[0].removeprefix('/Game/')).with_suffix('.uasset');rel=path.relative_to(R).as_posix();rows.append(dict(path=rel,sha256=sha(path),unchanged=sha(path)==B['protected'][rel]['sha256']))
 libraries[subject]=rows;check(subject+' 89 library assets unchanged',len(rows)==89 and all(r['unchanged'] for r in rows))
check('all accepted prior files and Git preserved',P['status']=='PASS' and P['git_preserved'] and not P['changed'] and not P['missing'])
source_files=[W/'generator.py',W/'generate.py',W/'native_regression.py',W.parent/'generate.py',W.parent/'default_template.json'];hashes={p.relative_to(R).as_posix():sha(p) for p in source_files};literals=[x.value for x in ast.walk(ast.parse((W/'generator.py').read_text())) if isinstance(x,ast.Constant) and isinstance(x.value,str)];check('generic generator contains no subject/source asset constants',not any(any(t in x for t in ['Female','Aegis','/John/','/Jane/','/Game/Characters/Mannequins','SK_Destination']) for x in literals))
D=dict(status='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL',version=G['version'],default_entry='Working/PlayableCharacter/generate.py',implementation='Working/PlayableCharacter/LocomotionV1/generator.py',registry='Working/PlayableCharacter/default_template.json',source_hashes=hashes,generation=G,regression=subjects,libraries=libraries,checks=checks,protected_count=P['protected_count'],preservation=P['status'],git_preserved=P['git_preserved'],animation_rebakes=0,timing_note='Zero moving delay/distance denotes first observed touchdown branch selection. Existing 0.1 s pose blend is retained; no zero blend-duration claim.',old_review_note='Read-only regression uses the accepted corrected review copies. Archived pre-fix originals remain unchanged and retain historical behaviour.',wizard_contract='Future playable output uses the default profile-driven generator. Historical per-subject builders are retained for reproduction and are not the future wizard API.')
(O/'integration_result.json').write_text(json.dumps(D,indent=2)+'\n');(O/'template_provenance.json').write_text(json.dumps(dict(version=G['version'],source_hashes=hashes,generator_sha256=G['generator_sha256'],profile_sha256=G['profile_sha256'],generated_assets=G['assets']),indent=2)+'\n');print('INTEGRATION',D['status'],len(checks),'checks')
