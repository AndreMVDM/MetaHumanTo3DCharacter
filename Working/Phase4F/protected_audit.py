import sys,json
sys.dont_write_bytecode=True
from preflight import P,W,O,protected
before=json.loads((O/'protected_before.json').read_text())['files'];after=protected()
changed=[p for p,v in before.items() if p in after and v['sha256']!=after[p]['sha256']]
missing=[p for p in before if p not in after];new=[p for p in after if p not in before]
result={'status':'passed' if not changed and not missing and not new else 'failed','protected_files':len(before),'changed':changed,'missing':missing,'unexpected_authored_outside_phase4f':new,
    'original_archives_preserved':all(not any(p in items for items in [changed,missing]) for p in ['Characters/Lara_UnRigged_Textured.zip','Characters/Bill_Textured_Unrigged.zip','Characters/Jill_Textured_Unrigged.zip']),
    'human_ledger_preserved':not any('Phase4D' in p for p in changed+missing),'external_engine_reference_scope':'Read-only execution inputs; no exhaustive external baseline',
    'git':'Workspace is not a Git repository; no staging, commit, push or configuration change performed'}
(O/'protected_file_audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
if result['status']!='passed':raise SystemExit(1)
