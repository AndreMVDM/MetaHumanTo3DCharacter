"""Read-only preservation/signature audit. Writes only new diagnosis artefacts."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
import apose_review_core as core
core.configure('John')
P=core.P;D=P/'Documentation/Phase4F/JohnBodySupportDiagnosis'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
baseline=core.read(D/'preservation_before.json')
changed=[p for p,h in baseline.items() if not Path(p).is_file() or sha(Path(p))!=h]
assert not changed,changed
s=core.read(core.W/'session.json');fit=core.read(core.O/'current_proposal.json');review=core.read(core.O/'human_review.json')
approvals={n:a['signature']==core.review_signature(s,n) for n,a in s['approvals'].items()}
assert all(approvals.values()) and len(approvals)==29
assert review['proposal_sha256']==sha(core.O/'current_proposal.json')
assert s['joints']==fit['joints'] and s['fingers']==fit['finger_chains']
for event in s['events']:
    assert event==core.read(core.W/'InteractionEvidence'/f"event_{event['id']:05}.json")
for group in ['roles','fingers']:
    for n,r in review[group].items():
        assert r['evidence_sha256']==sha(Path(r['evidence_artifact']))
        assert s['approvals'][n]['event_id']==r['event_id']
        if group=='fingers':assert r['chain_sha256']==core.digest(s['fingers'][n])
        else:
            joint=next(j for j in fit['joints'] if j['role']==n)
            assert r['position_cm']==joint['position_cm'] and r['resolved_ambiguity_flags']==joint['ambiguity_flags']
gate=core.read(core.O/'anatomical_validation.json')
assert sum(c['pass'] for c in gate['checks'])==176 and len(gate['checks'])==186 and not gate['downstream_authorised']
result={'files_verified_unchanged':len(baseline),'changed':changed,'approval_signatures':approvals,'events_verified':len(s['events']),
        'proposal_review_binding_current':True,'evidence_hashes_current':True,'score':'176/186','downstream_authorised':False,
        'anatomical_checks_passed':sum(c['pass'] for c in gate['checks'] if c['kind']=='anatomical'),
        'validator_run':False,'policy_implemented':False,'human_inputs_altered':False,'Jane_files_unchanged':sum('/Jane/' in p.replace('\\','/') for p in baseline)}
(D/'human_evidence_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
protected=core.read(P/'Documentation/Phase4F/apose_protected_before.json')['files']
allowed={'Documentation/Phase4F/'+n for n in ['HumanReviewInstructions.md','Phase4FQualityGeneralisationGate.md','phase_status.json','product_generalisation_matrix.json']}
historical=[];unexpected=[];missing=[]
for name,r in protected.items():
    path=P/name
    if not path.is_file():missing.append(name)
    elif sha(path)!=r['sha256']:(historical if name in allowed else unexpected).append(name)
assert not unexpected and not missing,(unexpected,missing)
report={'protected_baseline_files':len(protected),'unexpected_changed':unexpected,'missing':missing,
        'historically_authorised_shared_changes':historical,'current_turn_scope':'Only new Phase4F diagnosis scripts/artifacts authored; 385 current files also frozen.',
        'Bill_Jill_originals_and_Phase4D_preserved':True,'external_engine_reference_scope':'Not exhaustively hashed; no writes issued.'}
(D/'protected_preservation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'current_files_unchanged':len(baseline),'protected_files_checked':len(protected),'approval_signatures_current':len(approvals),
                  'events_current':len(s['events']),'unexpected_changes':unexpected,'gate':'176/186'},indent=2))
