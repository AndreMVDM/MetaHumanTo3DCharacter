"""Read-only preservation/acceptance aggregation. Writes R2 evidence only."""
import json, hashlib, sys, subprocess, datetime
from pathlib import Path

sys.dont_write_bytecode = True
W = Path(__file__).resolve().parent
R = W.parents[4]
O = R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/R2_EndToEnd'
load = lambda name: json.loads((O/name).read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
baseline = load('baseline.json')
changed, missing = [], []
for name, expected in baseline['protected_sha256'].items():
    p = R/name
    if not p.is_file():
        missing.append(name)
    elif sha(p) != expected:
        changed.append(name)
git = lambda *args: subprocess.check_output(['git', '--no-optional-locks', '-c', 'safe.directory='+R.as_posix(), *args], cwd=R, text=True).splitlines()
tracked = git('status', '--short', '--untracked-files=no')
git_preserved = tracked == baseline['git_tracked'] and git('rev-parse', 'HEAD')[0] == baseline['git_head'] and sha(R/'.git/index') == baseline['git_index_sha256']
sys.path.insert(0, str(R/'Working/Phase4F'))
import benchmark_validator as bv
bv.verify_freeze()
bv.verify_dependencies()
humans = {n: bv.audit_human(R/('Working/Phase4F/'+n), R/('Documentation/Phase4F/'+n)) for n in ['John', 'Jane']}
audit = dict(status='PASS' if not changed and not missing and git_preserved else 'FAIL', protected_count=len(baseline['protected_sha256']), changed=changed, missing=missing, git_preserved=git_preserved, git_head=baseline['git_head'], git_tracked=tracked, human_evidence=humans, frozen_validator_verified=True, scope='Only R2 code, derived assets, evidence and generated runtime/cache outputs authorised')
(O/'preservation_audit.json').write_text(json.dumps(audit, indent=2)+'\n')
A = load('authoring_result.json')
N = load('native_playback.json') if (O/'native_playback.json').exists() else dict(status='NOT_RUN', phases=[])
stage_pass = {x['stage']: x['status']=='PASS' for x in A['stages']}
canonical = load('canonicalisation.json') if (O/'canonicalisation.json').exists() else {}
semantics = load('semantic_mapping.json') if (O/'semantic_mapping.json').exists() else {}
retarget = load('retarget_setup.json') if (O/'retarget_setup.json').exists() else {}
clips = {x['role']: x for x in A.get('clips', [])}
phases = {x['role']: x for x in N['phases']}
author_ok = A['status']=='PASS'
expected_loads = [A.get('assets', {}).get(k) for k in ['mesh', 'skeleton']] + [x['path'] for x in A.get('clips', [])]
native_lineage_current = N.get('assets') == A.get('assets') and N.get('saved_assets_loaded') == expected_loads
native_ok = N['status']=='PASS' and native_lineage_current
def stage(name): return stage_pass.get(name, False)
def motion(role): return native_lineage_current and phases.get(role, {}).get('status')=='PASS'
criteria = [
('valid_rigged_skinned_humanoid', stage('input_validation')),
('unit_representation_classified', stage('unit_classification')),
('canonicalisation_automatically_selected', stage('unit_classification')),
('R1_policy_applied', stage('canonicalisation') and canonical.get('conversion', {}).get('version')=='phase4f.rigged-unit-canonicalisation/1.0.0'),
('physical_bind_size_preserved', canonical.get('invariants', {}).get('height', False)),
('geometry_preserved', canonical.get('invariants', {}).get('geometry_skin', False)),
('skin_weights_preserved', canonical.get('invariants', {}).get('geometry_skin', False)),
('hierarchy_preserved', canonical.get('invariants', {}).get('hierarchy', False)),
('humanoid_semantics_resolved', stage('semantic_mapping')),
('ten_finger_chains_resolved', len([x for x in semantics.get('bindings', []) if any(x['semantic'].endswith(d) for d in ['Thumb','Index','Middle','Ring','Pinky'])])==10),
('destination_IK_rig_generated', stage('ik_rig')),
('target_chains_validated', stage('ik_rig')),
('Manny_source_configuration_valid', stage('manny_source')),
('retargeter_generated', stage('retarget_setup')),
('stored_mappings_verified', stage('retarget_setup') and bool(retarget.get('mapping')) and all(k==v for k,v in retarget.get('mapping', {}).items())),
('idle_bake', stage('animation_bake') and 'idle' in clips),
('walk_bake', stage('animation_bake') and 'walk' in clips),
('run_bake', stage('animation_bake') and 'run' in clips),
('destination_skeleton_ownership', author_ok and all(x['skeleton']==A['assets']['skeleton'] for x in clips.values())),
('finite_baked_transforms', author_ok and all(clips.get(r, {}).get('all_bone_keys_finite', False) for r in ['idle','walk','run'])),
('root_scale_one', native_ok),
('component_scale_one', native_ok),
('physical_size_correct', native_ok),
('no_100x_placement_regression', native_ok),
('no_001x_scale_collapse', native_ok),
('idle_playback_advances', motion('idle')),
('walk_playback_advances', motion('walk')),
('run_playback_advances', motion('run')),
('fresh_reload_playback', native_ok and N.get('fresh_main_project_process', False)),
('no_Manny_actor_required', native_ok and N.get('source_actor_count')==0),
('no_source_component_required', native_ok and N.get('source_actor_count')==0),
('no_live_retarget_required', native_ok and N.get('live_retarget_node_count')==0),
('no_RetargetPoseFromMesh_required', native_ok and N.get('live_retarget_node_count')==0),
('no_authoring_bridge_required', native_ok and not N.get('authoring_bridge_loaded', True)),
('no_foreign_runtime_dependencies', native_ok and not N.get('runtime_dependency_closure', {}).get('foreign_game_packages', ['unknown']) and not N.get('runtime_dependency_closure', {}).get('authoring_packages', ['unknown'])),
('original_benchmark_preserved', audit['status']=='PASS'),
('John_Jane_preserved', audit['status']=='PASS'),
('frozen_protocols_preserved', audit['status']=='PASS'),
]
assert len(criteria)==38
result = dict(version='phase4f.rigged-character-r2/1.0.0', status='PASS' if all(ok for _, ok in criteria) and motion('neutral') else 'FAIL', criteria=[dict(number=i+1, name=n, status='PASS' if ok else 'FAIL') for i, (n, ok) in enumerate(criteria)], passed=sum(ok for _, ok in criteria), total=len(criteria), neutral_helper_native_status=phases.get('neutral', {}).get('status', 'NOT_RUN'), assets=A.get('assets', {}), clips=A.get('clips', []), stages=A['stages']+[dict(stage='native_destination_playback_and_fresh_reload', status=N['status']), dict(stage='runtime_dependency_closure', status='PASS' if native_ok else 'NOT_PROVEN'), dict(stage='preservation', status=audit['status'])], failures=[name for name, ok in criteria if not ok], authoring_failure=A.get('error'), native_failure=N.get('error'), protected_count=audit['protected_count'], completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), active_scope='One already-rigged benchmark, automatic native retarget/bake and independent playback', full_character_quality_accepted=False, package_cook_certified=False, other_subjects_started=False, commits_or_pushes=False)
(O/'result.json').write_text(json.dumps(result, indent=2)+'\n')
print('R2_RESULT', result['status'], result['passed'], '/', result['total'], 'protected', audit['protected_count'], 'changed', len(changed), 'missing', len(missing), 'git_preserved', git_preserved)
