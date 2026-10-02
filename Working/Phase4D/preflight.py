"""Phase4D immutable inputs and protected authored-file baseline."""
import hashlib, json, shutil, zipfile
from pathlib import Path
P = Path(__file__).resolve().parents[2]
W = P/'Working/Phase4D'; O = P/'Documentation/Phase4D'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def save(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8'); tmp.replace(path)
def protected():
    result={}
    for root in ['Characters','Config','Content','Reference','Documentation','Working']:
        for p in (P/root).rglob('*'):
            if p.is_file() and 'Phase4D' not in p.parts and not any(x in p.parts for x in ['Intermediate','Saved','Binaries','DerivedDataCache','__pycache__']):
                result[str(p.relative_to(P))]={'sha256':sha(p),'bytes':p.stat().st_size}
    result['MHTo3DCharacter.uproject']={'sha256':sha(P/'MHTo3DCharacter.uproject')}
    return result
if __name__=='__main__':
    W.mkdir(parents=True,exist_ok=True); O.mkdir(parents=True,exist_ok=True)
    if not (O/'protected_before.json').exists(): save(O/'protected_before.json',{'files':protected(),'excluded':'Normal editor/build/cache outputs; external engine installation not comprehensively hashed'})
    reports=['RetargetingInvestigation/InvestigationReport.md','RetargetingInvestigation/SupplementalIKConfiguration.md','Phase2/Phase2RetargetingReport.md','Phase3/MetaHumanResizeConformInvestigation.md','Phase3B/Phase3BHeightNormalisationRetargeting.md','Phase4A/Phase4AAutoRigInvestigation.md','Phase4B/Phase4BSemanticJointFitting.md','Phase4C/Phase4CMetaHumanSemanticDonor.md']
    index=[]
    for r in reports:
        p=P/'Documentation'/r; text=p.read_text(encoding='utf-8-sig')
        index.append({'path':r,'sha256':sha(p),'characters':len(text),'headings':[s for s in text.splitlines() if s.startswith('#')]})
    evidence={}
    for phase in ['Phase4B','Phase4C']:
        for p in (P/'Documentation'/phase).glob('*.json'):
            data=json.loads(p.read_text(encoding='utf-8-sig'))
            evidence[str(p.relative_to(P))]={'sha256':sha(p),'keys':list(data) if isinstance(data,dict) else len(data)}
    save(O/'existing_evidence_index.json',{'reports':index,'machine_evidence':evidence})
    for n in ['automatic_fit_v2.json','coordinate_frame.json','transform_mapping.json']:
        dst=O/('automatic_starting_proposal.json' if n=='automatic_fit_v2.json' else n)
        if not dst.exists(): shutil.copyfile(P/'Documentation/Phase4C'/n,dst)
    assert sha(O/'automatic_starting_proposal.json')==sha(P/'Documentation/Phase4C/automatic_fit_v2.json')
    for n in ['normalised_geometry.npz','source_geometry.npz']:
        if not (W/n).exists(): shutil.copyfile(P/'Working/Phase4C'/n,W/n)
    entries=[]
    archive=P/'Characters/Lara_UnRigged_Textured.zip'
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            if entry.is_dir(): continue
            target=(W/'Inputs'/entry.filename).resolve(); assert target.is_relative_to((W/'Inputs').resolve())
            target.parent.mkdir(parents=True,exist_ok=True); data=z.read(entry); target.write_bytes(data)
            entries.append({'name':entry.filename,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
    save(O/'source_preservation.json',{'archive_sha256':sha(archive),'archive_matches_phase4c':sha(archive)=='45fa309b7b9114ff71618feac8d0951dd55596d091d4f03e2434b6cc1384f959','entries':entries,'normalised_geometry_matches_phase4c':sha(W/'normalised_geometry.npz')==sha(P/'Working/Phase4C/normalised_geometry.npz'),'source_geometry_matches_phase4c':sha(W/'source_geometry.npz')==sha(P/'Working/Phase4C/source_geometry.npz'),'original_polygon_uv_material_arrays':'Reused byte-identical Phase4C source arrays; original FBX/texture entries freshly extracted unchanged; no source geometry authoring'})
    print('Protected files',len(json.loads((O/'protected_before.json').read_text())['files']))
