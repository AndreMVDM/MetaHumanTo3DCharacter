import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase4B';before=json.loads((O/'protected_before.json').read_text());missing=[];changed=[]
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
for rel,meta in before['files'].items():
    p=P/rel
    if not p.exists():missing.append(rel)
    elif digest(p)!=meta['sha256']:changed.append(rel)
new=[]
for root in ['Characters','Content','Config','Reference','Documentation','Working/Phase4A']:
    for p in (P/root).rglob('*'):
        if p.is_file() and 'Phase4B' not in p.parts and not any(t in p.parts for t in ['DDC','Intermediate','Saved','Binaries','__pycache__']) and str(p.relative_to(P)) not in before['files']:new.append(str(p.relative_to(P)))
engine=[]
for s in json.loads((O/'semantic_api_inventory.json').read_text())['systems']:
    for r in s['source']:
        if digest(Path(r['path']))!=r['sha256']:engine.append(r['path'])
inputs=json.loads((O/'input_inventory.json').read_text());workcopy=[]
for r in inputs['entries']:
    p=P/'Working/Phase4B/Inputs'/r['name'];workcopy.append({'entry':r['name'],'bytes_equal':p.exists() and digest(p)==r['sha256']})
result={'protected_baseline_files':len(before['files']),'changed_files':changed,'missing_files':missing,'new_files_outside_phase4b_in_protected_scopes':new,'engine_inventory_source_hash_changes':sorted(set(engine)),'working_input_entries':workcopy,'original_lara_archive_sha256':digest(P/'Characters/Lara_UnRigged_Textured.zip'),'passed':not (missing or changed or new or engine) and all(r['bytes_equal'] for r in workcopy),'audit_scope':before['scope'],'audit_limit':'Engine source hash check covers inventoried files, not entire engine. Baseline excludes caches; Working/Phase2/3/3B not broadly hashed. No writes were authored there. Git status reports not a Git repository; no commit/push attempted.'}
(O/'protected_file_audit.json').write_text(json.dumps(result,indent=2));print('PROTECTED_AUDIT',result['passed'],len(before['files']),changed,missing,new,sorted(set(engine)))
