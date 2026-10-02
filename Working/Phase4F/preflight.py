"""Capture protection and policy before any Phase4F optimisation or asset work."""
import sys
sys.dont_write_bytecode = True
import hashlib, json, zipfile, importlib.util
from datetime import datetime, timezone
from pathlib import Path
P = Path(__file__).resolve().parents[2]
W = P/'Working/Phase4F'
O = P/'Documentation/Phase4F'
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, allow_nan=False), encoding='utf-8')
def protected():
    result = {}
    for root in ['Characters','Config','Content','Reference','Documentation','Working']:
        for p in (P/root).rglob('*'):
            if not p.is_file() or 'Phase4F' in p.parts: continue
            if any(s in p.parts for s in ['Intermediate','Saved','DerivedDataCache','DDC','__pycache__']): continue
            result[p.relative_to(P).as_posix()] = {'sha256':sha(p),'bytes':p.stat().st_size}
    result['MHTo3DCharacter.uproject'] = {'sha256':sha(P/'MHTo3DCharacter.uproject')}
    return result
if __name__ == '__main__':
    W.mkdir(parents=True, exist_ok=True); O.mkdir(parents=True, exist_ok=True)
    baseline = O/'protected_before.json'
    if not baseline.exists():
        save(baseline, {'captured_utc':datetime.now(timezone.utc).isoformat(), 'files':protected(),
            'excluded':'Phase4F; normal execution/build/cache directories. Prior binaries and human events included.',
            'external_scope':'Engine and external reference projects are read-only, not exhaustively hashed.'})
    policy = O/'evaluation_policy.json'
    if not policy.exists():
        save(policy, {'frozen_utc':datetime.now(timezone.utc).isoformat(), 'semantic_pass_limit_per_new_character':3,
            'skin_variants_per_region_including_baseline':4, 'regions':['shoulders','pelvis_pants','fingers_thumb','feet_contact'],
            'full_manual_weight_painting_allowed':False, 'prior_character_coordinates_allowed':False,
            'final_vertex_id_masks_allowed':False, 'human_approval_required_for_ambiguous_anatomy':True,
            'anatomy_gate':'Retain Phase4D numerical and explicit position-bound human-review requirements; adapt paths only.',
            'height_profiles_cm':{'Lara':180,'Bill':180,'Jill':180},
            'height_rationale':'Controlled common 180 cm physical profile; preserve individual dimensionless proportions. Not a claim about generated intended stature.',
            'stress_suite':['neutral','arms45','horizontal','overhead','elbows_bent','wide_stance','strong_knee_bend','idle','walk','run','reach_JumpingJacks','independent_fingers','thumb_opposition_flex'],
            'measurement':'Per-frame area ratios <0.5/<0.1/>2, edge log RMS strain and worst cases; finite LBS, local volume/thickness diagnostics where feasible, native visual review; same region definitions relative to anatomy.',
            'contact':'Sole-aware authoring-only two-bone IK, max5 iterations, max0.033333*height shift/iteration, 60Hz bake/120Hz key-half-key evaluation; unchanged root policy.',
            'rejection':'Reject geometry/UV/reference changes, unresolved anatomy, worst-case gross collapse or cross-region regressions. Means never override worst-case review.',
            'product_gate':'User GO/HOLD/NO-GO criteria; incomplete human review = pending gate and no Phase5 authorisation, not inferred architecture failure.',
            'budget_consumption':{'Bill':{'semantic':0,'skin':0},'Jill':{'semantic':0,'skin':0},'Lara':{'semantic':0,'skin':0}}})
    sources = ['Phase4D/Phase4DGuidedLandmarkCorrection.md','Phase4E/Phase4ECharacterQualityRefinement.md',
        'Phase3B/Phase3BHeightNormalisationRetargeting.md','Phase4A/Phase4AAutoRigInvestigation.md',
        'Phase4B/Phase4BSemanticJointFitting.md','Phase4C/Phase4CMetaHumanSemanticDonor.md',
        'Phase4D/anatomical_validation.json','Phase4D/current_proposal.json','Phase4D/correction_metrics.json',
        'Phase4D/human_ledger_preservation.json','Phase4D/skeleton_construction.json','Phase4D/skinning_results.json',
        'Phase4E/final_deformation_summary.json','Phase4E/final_finger_validation.json',
        'Phase4E/surface_contact_dense_validation.json','Phase4E/final_dependency_closure.json']
    save(O/'prior_evidence_index.json',[{'path':'Documentation/'+s,'sha256':sha(P/'Documentation'/s)} for s in sources])
    spec = importlib.util.spec_from_file_location('readonly_fbx',P/'Documentation/Phase3/Evidence/collect_evidence.py')
    parser = importlib.util.module_from_spec(spec); spec.loader.exec_module(parser)
    inventory=[]
    for character, filename in [('Lara','Lara_UnRigged_Textured.zip'),('Bill','Bill_Textured_Unrigged.zip'),('Jill','Jill_Textured_Unrigged.zip')]:
        src = P/'Characters'/filename; dest = W/'Inputs'/character
        row={'character':character,'archive':'Characters/'+filename,'sha256':sha(src),'bytes':src.stat().st_size,'entries':[],'fbx':[]}
        with zipfile.ZipFile(src) as z:
            for e in z.infolist():
                if e.is_dir(): continue
                target=(dest/e.filename).resolve()
                if not target.is_relative_to(dest.resolve()): raise ValueError('ZIP path escapes destination')
                target.parent.mkdir(parents=True,exist_ok=True); data=z.read(e); target.write_bytes(data)
                row['entries'].append({'name':e.filename,'bytes':e.file_size,'compressed_bytes':e.compress_size,'crc32':e.CRC,'sha256':hashlib.sha256(data).hexdigest()})
                if target.suffix.lower()=='.fbx': row['fbx'].append(parser.fbx(target))
        save(O/f'{character.lower()}_fbx_summary.json',row['fbx'])
        inventory.append(row)
    save(O/'input_inventory.json',inventory)
    print('Protected files',len(json.loads(baseline.read_text())['files']))
    for row in inventory:
        print(row['character'], row['sha256'], [(f['object_counts'],[(g['name'],g['control_points'],g['polygon_count']) for g in f['geometries']]) for f in row['fbx']])
