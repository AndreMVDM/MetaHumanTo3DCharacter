"""Append-only Phase4F continuation baseline and fresh archive inspection."""
import sys
sys.dont_write_bytecode = True
import json, hashlib, zipfile, importlib.util
from pathlib import Path
from datetime import datetime, timezone
P = Path(__file__).resolve().parents[2]
W = P/'Working/Phase4F'; O = P/'Documentation/Phase4F'
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
baseline=O/'apose_protected_before.json'
if not baseline.exists():
    files={}
    for root in ['Characters','Config','Content','Reference','Documentation','Working']:
        for p in (P/root).rglob('*'):
            if not p.is_file() or any(s in p.parts for s in ['Intermediate','Saved','DerivedDataCache','DDC','Shaders','__pycache__']): continue
            files[p.relative_to(P).as_posix()]={'sha256':sha(p),'bytes':p.stat().st_size}
    files['MHTo3DCharacter.uproject']={'sha256':sha(P/'MHTo3DCharacter.uproject')}
    save(baseline,{'captured_utc':datetime.now(timezone.utc).isoformat(),'files':files,
        'scope':'Prior phases plus ALL current Phase4F authored evidence, original five test ZIPs and Phase4D human ledger. Shared report/status changes explicitly audited against historical snapshots.'})
    for name in ['Phase4FQualityGeneralisationGate.md','HumanReviewInstructions.md','phase_status.json','product_generalisation_matrix.json','budget_consumption.json','evaluation_policy.json']:
        (O/'APoseContinuation/Before').mkdir(parents=True,exist_ok=True)
        (O/'APoseContinuation/Before'/name).write_bytes((O/name).read_bytes())
spec=importlib.util.spec_from_file_location('readonly_fbx',P/'Documentation/Phase3/Evidence/collect_evidence.py')
parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
for character in ['John','Jane']:
    cw=W/character;co=O/character;cw.mkdir(exist_ok=True);co.mkdir(exist_ok=True)
    src=P/'Characters'/f'{character}_Textured_Unrigged.zip'
    row={'character':character,'archive':str(src.relative_to(P)),'sha256':sha(src),'bytes':src.stat().st_size,'entries':[],'fbx':[]}
    dest=cw/'Input'
    with zipfile.ZipFile(src) as z:
        for e in z.infolist():
            if e.is_dir():continue
            target=(dest/e.filename).resolve()
            if not target.is_relative_to(dest.resolve()):raise ValueError('ZIP path escape')
            data=z.read(e);target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():assert target.read_bytes()==data
            else:target.write_bytes(data)
            row['entries'].append({'name':e.filename,'bytes':e.file_size,'compressed_bytes':e.compress_size,'crc32':e.CRC,'sha256':hashlib.sha256(data).hexdigest()})
            if target.suffix.lower()=='.fbx':row['fbx'].append(parser.fbx(target))
    save(co/'input_inventory.json',row)
    print(character,row['sha256'],[(f['object_counts'],f['geometries']) for f in row['fbx']])
policy=json.loads((O/'evaluation_policy.json').read_text())
policy.update(continuation_subjects=['John','Jane'],supported_v1_input='Clean unrigged humanoid in neutral A-pose',
    pose_normalisation_deferred=True,primary_subjects_superseded=['Bill','Jill'])
policy['height_profiles_cm'].update(John=180,Jane=180)
save(O/'APoseContinuation/evaluation_policy.json',policy)
print('BASELINE',len(json.loads(baseline.read_text())['files']))
