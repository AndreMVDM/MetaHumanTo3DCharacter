"""Run retained Phase4C numeric gate plus Phase4D poles/axes/finger gates."""
import json, sys, runpy, math
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import review_core as core
core.configure('Jill')
P=core.P;W=core.W;O=core.O
def validate():
    old=sys.argv[:]
    try:
        sys.argv=['inherited_validate.py','--fit',str(O/'current_proposal.json'),'--review',str(O/'human_review.json')]
        runpy.run_path(str(W/'inherited_validate.py'),run_name='__main__')
    finally: sys.argv=old
    result=core.read(O/'inherited_anatomical_validation_corrected.json');fit=core.read(O/'current_proposal.json');review=core.read(O/'human_review.json');checks=result['checks'];v=np.load(W/'normalised_geometry.npz')['vertices']
    def check(name,passed,measured,threshold,kind='hard'):
        checks.append({'name':name,'pass':bool(passed),'measured':measured,'threshold':threshold,'kind':kind})
    for n,a in fit['recomputed_axes'].items():
        R=np.column_stack([a['aim_x'],a['y'],a['z']]);check('reference_axes_'+n,np.max(abs(R.T@R-np.eye(3)))<1e-6 and abs(np.linalg.det(R)-1)<1e-6,{'determinant':float(np.linalg.det(R)),'orthogonality_error':float(np.max(abs(R.T@R-np.eye(3))))},'proper right-handed local basis; finite orthonormal axes')
    for n,pole in fit['limb_poles'].items():
        check('pole_nondegenerate_'+n,pole['plane_normal'] is not None and pole['bend_distance_cm']>.05,pole,'bend > .05cm and valid plane; signed direction additionally requires human review')
        role=('lowerarm_' if n.startswith('arm') else 'calf_')+n[-1]
        check('pole_anatomical_direction_'+n,role in review['roles'],{'reviewed_role':role},'explicit elbow/knee anatomical review includes front/side bend direction','anatomical')
    for side in ['l','r']:
        keys=[d+'_'+side for d in core.DIGITS]; chains=fit['finger_chains'];present=[chains[k] for k in keys if k in chains]
        check('finger_complete_unique_identity_'+side,len(present)==5 and len({f['track_id'] for f in present})==5,[f['track_id'] for f in present],'five independently user-identified distinct tracks; naming is not acceptance','anatomical')
        allpaths=[]
        for key in keys:
            f=chains.get(key);approval=review['fingers'].get(key,{});approved=False
            if f and approval.get('chain_sha256')==core.digest(f) and approval.get('anatomical_valid') is True:
                evidence=Path(approval.get('evidence_artifact','')).resolve()
                if evidence.is_file() and evidence.is_relative_to(W.resolve()) and core.file_sha(evidence)==approval.get('evidence_sha256'):
                    event=core.read(evidence);approved=event.get('provenance')=='human_editor_action' and event.get('kind')=='review' and key in event['details']['roles'] and event['details']['judgement']=='accept'
            check('finger_review_'+key,approved,{'present':bool(f),'approved':approved},'SHA-bound explicit human digit identity, root/tip and generated-chain review','anatomical')
            if not f: continue
            pts=np.array(f['phalanges_cm']);path=np.array(f['path_cm']);allpaths.append((key,path));sign=1 if side=='l' else -1
            check('finger_side_'+key,np.all(sign*pts[:,0]>0),pts[:,0].tolist(),'all phalanges on correct side')
            distances=np.sqrt(((pts[:,None,:]-v[None,:,:])**2).sum(2).min(1));check('finger_surface_'+key,float(distances.max())<1.2,distances.tolist(),'nearest target vertex <1.2cm; coarse track support, independent review still required')
            lengths=np.linalg.norm(np.diff(pts,axis=0),axis=1);check('finger_segments_'+key,np.all(lengths>.05) and np.all(lengths<8),lengths.tolist(),'finite separated consecutive phalanges .05..8cm')
            # Sample actual continuous segments, not only endpoints, for collision screens.
        for i,(ka,a) in enumerate(allpaths):
            sa=np.array([core.path_sample(a.tolist(),u) for u in np.linspace(0,1,41)])
            for kb,b in allpaths[i+1:]:
                sb=np.array([core.path_sample(b.tolist(),u) for u in np.linspace(0,1,41)]);separation=float(np.sqrt(((sa[:,None,:]-sb[None,:,:])**2).sum(2)).min())
                check('finger_no_collision_'+ka+'_'+kb,separation>.25,separation,'sampled path separation >.25cm; discrete screen, not a volumetric proof')
    # Retain the two aggregate Phase4C finger gates as well as the more
    # explicit per-chain screens; absence of correspondence cannot pass.
    unique=all(sum(k.endswith('_'+side) for k in chains)==5 and len({f['track_id'] for f in chains.values() if f['side']==side})==5 for side in ['l','r'])
    collision_checks=[c for c in checks if c['name'].startswith('finger_no_collision_')]
    check('finger_target_tracks_not_collapsed',unique and len(collision_checks)==20 and all(c['pass'] for c in collision_checks),{'unique_complete':unique,'collision_screens':len(collision_checks)},'ten distinct independently identified target paths; every retained collision screen passes')
    finger_reviews=[c for c in checks if c['name'].startswith('finger_review_')]
    check('finger_chains_anatomically_resolved',len(finger_reviews)==10 and all(c['pass'] for c in finger_reviews),sum(c['pass'] for c in finger_reviews),'10/10 independently accepted chains','anatomical')
    failed=[r['name'] for r in checks if not r['pass']];result.update(passed=not failed,failed=failed,structural_geometric_passed=all(c['pass'] for c in checks if c['kind']=='hard'),automatic_anatomical_passed=not result['manual_anatomical_review_roles'] and all(c['pass'] for c in checks if c['kind']=='anatomical'),downstream_authorised=not failed,phase='Phase4F',baseline_numeric_thresholds_unchanged=True,review_change='Explicit review allowed at unchanged positions; all prior numeric checks retained',additional_limits='Pole sign judged by human front/side review; coarse envelope/finger vertex screens cannot certify exact internal anatomy or skin deformation')
    result['gate_policy_correction']={'check':'left_right_not_crossed','change':'Clavicle side is measured relative to its thoracic parent; strict sign thresholds and all other coordinates/thresholds retained','evidence':'Retained Phase4D parent-relative clavicle convention; current character values in left_right_not_crossed check','classification':'pivot/skeleton convention mismatch'}
    core.save(O/'anatomical_validation.json',result)
    path=O/'experiment_result.json'
    experiment=core.read(path) if path.exists() else {}
    # A gate refresh updates anatomy/provenance without discarding measured assets
    # or the downstream quality conclusion from a completed evaluation.
    experiment.update(anatomy_passed=not failed,failed_gate_count=len(failed),downstream_authorised=not failed,actual_interactions=core.read(O/'correction_metrics.json'))
    experiment.setdefault('downstream_assets_created',[])
    experiment.setdefault('body_classification','experimental assisted')
    experiment.setdefault('finger_classification','experimental assisted')
    experiment.setdefault('overall_mode_a','experimental assisted')
    experiment.setdefault('generalisation','unproven')
    if failed:experiment['downstream_status']='blocked_by_anatomy'
    elif not experiment['downstream_assets_created']:experiment['downstream_status']='anatomy_passed_next_stage_pending'
    core.save(path,experiment)
    print('Phase4D gate:',len(checks),'checks;',len(failed),'failed; downstream',not failed)
    return result
if __name__=='__main__':validate()
