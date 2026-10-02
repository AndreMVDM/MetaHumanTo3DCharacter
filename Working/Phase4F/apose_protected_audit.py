import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase4F';A=O/'APoseContinuation'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
before=json.loads((O/'apose_protected_before.json').read_text())['files']
allowed={'Documentation/Phase4F/'+n for n in ['Phase4FQualityGeneralisationGate.md','HumanReviewInstructions.md','phase_status.json','product_generalisation_matrix.json']}
changed=[];missing=[];intentional=[]
for name,r in before.items():
    p=P/name
    if not p.is_file():missing.append(name)
    elif sha(p)!=r['sha256']:
        (intentional if name in allowed else changed).append(name)
prefixes={n:(O/n).read_bytes().startswith((A/'Before'/n).read_bytes()) for n in ['Phase4FQualityGeneralisationGate.md','HumanReviewInstructions.md']}
new=[]
for root in ['Characters','Config','Content','Reference','Documentation','Working']:
    for p in (P/root).rglob('*'):
        if not p.is_file() or any(s in p.parts for s in ['Intermediate','Saved','DerivedDataCache','DDC','Shaders','APoseDDC','APoseShaders','__pycache__']):continue
        rel=p.relative_to(P).as_posix()
        if rel not in before and 'Phase4F' not in p.parts:new.append(rel)
protected_controls=[n for n in before if ('Phase4F/Bill/' in n or 'Phase4F/Jill/' in n)]
archives={ch:sha(P/'Characters'/filename) for ch,filename in [('John','John_Textured_Unrigged.zip'),('Jane','Jane_Textured_Unrigged.zip'),('Bill','Bill_Textured_Unrigged.zip'),('Jill','Jill_Textured_Unrigged.zip'),('Lara','Lara_UnRigged_Textured.zip')]}
result={'status':'passed' if not changed and not missing and not new and all(prefixes.values()) else 'failed',
    'protected_files':len(before),'unexpected_changed':changed,'missing':missing,'unexpected_authored_outside_phase4f':new,
    'authorised_shared_updates':intentional,'historical_report_prefixes_byte_identical':prefixes,
    'bill_jill_control_files_protected':len(protected_controls),'bill_jill_control_files_unchanged':not any(n in changed+missing for n in protected_controls),
    'five_original_zip_sha256':archives,'phase4d_human_ledger_unchanged':not any('Phase4D' in n for n in changed+missing),
    'external_scope':'Engine source/external reference projects used read-only; no exhaustive external-tree baseline.',
    'git_state':'Workspace has no .git; no staging, commit, push or branch/config changes.'}
(A/'protected_file_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
if result['status']!='passed':raise SystemExit(1)
