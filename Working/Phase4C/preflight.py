"""Read-only prior evidence and immutable protected baseline for Phase4C."""
import json, hashlib, zipfile, datetime
from pathlib import Path
P=Path(__file__).resolve().parents[2]; W=P/'Working/Phase4C'; O=P/'Documentation/Phase4C'
O.mkdir(parents=True,exist_ok=True)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def save(n,x): (O/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
if not (O/'protected_before.json').exists():
    files={}
    for root in ['Characters','Config','Content','Reference','Documentation','Working']:
        for p in (P/root).rglob('*'):
            if p.is_file() and 'Phase4C' not in p.parts and not any(s in p.parts for s in ['Intermediate','Saved','Binaries','DerivedDataCache','__pycache__']):
                files[str(p.relative_to(P))]={'sha256':sha(p),'bytes':p.stat().st_size}
    files['MHTo3DCharacter.uproject']={'sha256':sha(P/'MHTo3DCharacter.uproject')}
    save('protected_before.json',{'scope':'All Characters, Config, Content, Reference, prior Documentation and authored Working; excludes execution/build caches','files':files})
reports=['RetargetingInvestigation/InvestigationReport.md','RetargetingInvestigation/SupplementalIKConfiguration.md','Phase2/Phase2RetargetingReport.md','Phase3/MetaHumanResizeConformInvestigation.md','Phase3B/Phase3BHeightNormalisationRetargeting.md','Phase4A/Phase4AAutoRigInvestigation.md','Phase4B/Phase4BSemanticJointFitting.md']
index=[]
for r in reports:
    p=P/'Documentation'/r; s=p.read_text(encoding='utf-8-sig')
    index.append({'path':r,'sha256':sha(p),'characters':len(s),'headings':[l for l in s.splitlines() if l.startswith('#')]})
ev={}
for n in ['semantic_api_inventory','python_api_probe','automatic_fit_v2','anatomical_validation_v2','manual_control_comparison_v2','experiment_result','protected_file_audit']:
    p=P/'Documentation/Phase4B'/f'{n}.json'; x=json.loads(p.read_text())
    ev[n]={'sha256':sha(p),'type':type(x).__name__,'keys':list(x) if isinstance(x,dict) else len(x)}
save('existing_evidence_index.json',{'reports':index,'phase4b':ev})
archive=P/'Characters/Lara_UnRigged_Textured.zip'; dest=W/'Inputs';dest.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
    entries=[]
    for e in z.infolist():
        if e.is_dir():continue
        p=(dest/e.filename).resolve(); assert p.is_relative_to(dest.resolve())
        p.parent.mkdir(parents=True,exist_ok=True); b=z.read(e);p.write_bytes(b)
        entries.append({'name':e.filename,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
save('input_inventory.json',{'archive_sha256':sha(archive),'entries':entries})
print('baseline',len(json.loads((O/'protected_before.json').read_text())['files']))
print('Phase4B outcome',json.loads((P/'Documentation/Phase4B/experiment_result.json').read_text()))
