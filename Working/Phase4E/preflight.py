"""Read-only prior-phase inventory, captured before UE authoring."""
import hashlib, json, shutil, sys
from pathlib import Path
sys.dont_write_bytecode = True
P = Path(__file__).resolve().parents[2]
W = P/'Working/Phase4E'; O = P/'Documentation/Phase4E'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def inventory():
    files={}
    for name in ['Characters','Config','Content','Reference','Documentation','Working']:
        for p in (P/name).rglob('*'):
            if not p.is_file() or 'Phase4E' in p.parts: continue
            if any(s in p.parts for s in ['Intermediate','Saved','DerivedDataCache','DDC','__pycache__']): continue
            files[p.relative_to(P).as_posix()]={'sha256':sha(p),'bytes':p.stat().st_size}
    files['MHTo3DCharacter.uproject']={'sha256':sha(P/'MHTo3DCharacter.uproject')}
    return files
if __name__=='__main__':
    W.mkdir(parents=True,exist_ok=True);O.mkdir(parents=True,exist_ok=True)
    dst=O/'protected_before.json'
    if not dst.exists(): dst.write_text(json.dumps({'files':inventory(),'excluded':'execution/build/cache directories only; prior phase binaries/runtime included'},indent=2))
    sources=['Phase4DGuidedLandmarkCorrection.md','current_proposal.json','anatomical_validation.json','skeleton_construction.json','skinning_results.json','animation_bake_results.json','deformation_contact_results.json','finger_animation_validation.json','source_independent_playback.json','final_dependency_closure.json','protected_file_audit.json','runtime_samples.json','finger_pose_samples.json','human_ledger_preservation.json']
    evidence=[]
    for n in sources:
        p=P/'Documentation/Phase4D'/n
        evidence.append({'path':p.relative_to(P).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
    (O/'phase4d_evidence_index.json').write_text(json.dumps(evidence,indent=2))
    for n in ['accepted_skin.json','normalised_geometry.npz']:
        dst=W/('baseline_recorded_skin.json' if n=='accepted_skin.json' else n)
        if not dst.exists(): shutil.copyfile(P/'Working/Phase4D'/n,dst)
    print('Protected files:',len(json.loads((O/'protected_before.json').read_text())['files']))
