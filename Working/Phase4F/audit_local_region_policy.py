"""Read-only final audit; writes only this correction's evidence directory."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
import apose_review_core as core
import geometry_support_policy_v3 as policy
core.configure('John');P=core.P;D=P/'Documentation/Phase4F/JohnLocalRegionPolicy'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
before=core.read(D/'preservation_before.json')
allowed={str(core.W/'validate.py'),*(str(core.O/n) for n in ['anatomical_validation.json','geometry_policy_migration.json','experiment_result.json'])}
changed=[p for p,h in before.items() if not Path(p).is_file() or sha(p)!=h]
runtime_status=str(P/'Working/Phase4F/ReviewPanel/runtime/status.json')
derived_changes=[p for p in changed if p==runtime_status]
unexpected=[p for p in changed if p not in allowed and p!=runtime_status];assert not unexpected,unexpected
s=core.read(core.W/'session.json');fit=core.read(core.O/'current_proposal.json');review=core.read(core.O/'human_review.json')
if derived_changes:
    # Bridge.publish writes a derived heartbeat/snapshot, never persisted review evidence.
    # Do not restore it or infer that only the heartbeat changed without an old snapshot.
    status=core.read(Path(runtime_status))
    assert status['character']=='John' and status['session_id']==s['session_id']
    assert status['revision']==core.digest(s) and status['fingers']==s['fingers']
    assert status['metrics']==core.metrics(s) and not status['pending']
    publisher=P/'Working/Phase4F/ReviewPanel/bridge.py'
    assert str(publisher) in before and sha(publisher)==before[str(publisher)]
approvals={n:a['signature']==core.review_signature(s,n) for n,a in s['approvals'].items()}
assert all(approvals.values()) and len(approvals)==29
assert review['proposal_sha256']==sha(core.O/'current_proposal.json')
assert s['joints']==fit['joints'] and s['fingers']==fit['finger_chains']
for e in s['events']:assert e==core.read(core.W/'InteractionEvidence'/f"event_{e['id']:05}.json")
for group in ['roles','fingers']:
    for n,r in review[group].items():
        assert r['evidence_sha256']==sha(r['evidence_artifact']) and r['event_id']==s['approvals'][n]['event_id']
        if group=='fingers':assert r['chain_sha256']==core.digest(s['fingers'][n])
        else:
            j=next(j for j in fit['joints'] if j['role']==n)
            assert r['position_cm']==j['position_cm'] and r['resolved_ambiguity_flags']==j['ambiguity_flags']
gate=core.read(core.O/'anatomical_validation.json');old=core.read(D/'before_anatomical_validation.json')
assert gate['validator_policy_version']==policy.POLICY['version']
assert len(gate['checks'])==186 and sum(c['pass'] for c in gate['checks'])==185
assert gate['failed']==['surface_envelope_thigh_r'] and not gate['downstream_authorised']
old_checks={c['name']:c for c in old['checks']};checks={c['name']:c for c in gate['checks']}
unchanged=[n for n in checks if not n.startswith('surface_envelope_')]
assert all(checks[n]==old_checks[n] for n in unchanged)
migration=core.read(core.O/'geometry_policy_migration.json');old_migration=core.read(D/'before_geometry_policy_migration.json')
assert migration['legacy_results']==old_migration['legacy_results']
assert all(c==old_checks[c['name']] for c in migration['body_v2_results'])
metrics=core.read(core.O/'correction_metrics.json')
assert metrics['trial_status']=='finished' and metrics['placement_commands']==0 and metrics['landmarks_actually_moved']==0
protected=core.read(P/'Documentation/Phase4F/apose_protected_before.json')['files']
historical={'Documentation/Phase4F/'+n for n in ['HumanReviewInstructions.md','Phase4FQualityGeneralisationGate.md','phase_status.json','product_generalisation_matrix.json']}
protected_changed=[];missing=[];historical_changes=[]
for name,r in protected.items():
    p=P/name
    if not p.is_file():missing.append(name)
    elif sha(p)!=r['sha256']:(historical_changes if name in historical else protected_changed).append(name)
assert not protected_changed and not missing,(protected_changed,missing)
regression=core.read(D/'regression_results.json');assert regression['successful']
result={'policy_version':policy.POLICY['version'],'finger_policy_version':migration['finger_policy_version'],'score':'185/186',
        'failed':gate['failed'],'downstream_authorised':False,'anatomical_checks_passed':sum(c['pass'] for c in gate['checks'] if c['kind']=='anatomical'),
        'finger_support_passed':sum(c['pass'] for c in gate['checks'] if c['name'].startswith('finger_surface_')),
        'collision_checks_passed':sum(c['pass'] for c in gate['checks'] if c['name'].startswith('finger_no_collision_')),
        'nine_former_failures_passed':[n for n in old['failed'] if checks[n]['pass']],
        'non_body_checks_identical':len(unchanged),'legacy_results_exactly_preserved':len(migration['legacy_results']),
        'v2_body_results_exactly_preserved':len(migration['body_v2_results']),
        'proposal_sha256':sha(core.O/'current_proposal.json'),'review_sha256':sha(core.O/'human_review.json'),
        'approval_signatures_current':approvals,'immutable_events_verified':len(s['events']),
        'baseline_files_checked':len(before),'input_files_unchanged':len(before)-len(changed),
        'authorised_existing_changes':[p for p in changed if p in allowed],'unexpected_changes':unexpected,
        'live_derived_runtime_changes':derived_changes,
        'runtime_snapshot_matches_persisted_session':bool(derived_changes),
        'runtime_status_publisher':'Working/Phase4F/ReviewPanel/bridge.py:Bridge.publish',
        'Jane_files_unchanged':sum('/Jane/' in p.replace('\\','/') for p in before),
        'protected_files_checked':len(protected),'protected_unexpected_changed':protected_changed,'protected_missing':missing,
        'historical_shared_changes':historical_changes,'regression_tests_passed':regression['tests_run'],
        'new_source_ownership_evidence':str(core.O/'body_region_ownership.json'),'source_geometry_changed':False,'human_inputs_changed':False,
        'right_thigh_3d_acceptance_implemented':False,'downstream_work_performed':False,'git_directory_present':(P/'.git').is_dir()}
(D/'validation_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['score','failed','regression_tests_passed','non_body_checks_identical','input_files_unchanged','Jane_files_unchanged','protected_files_checked','unexpected_changes']},indent=2))
