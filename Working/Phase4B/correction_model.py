"""Explicit correction replay; demonstration fixtures never author UE assets."""
import copy,json,hashlib,math
import numpy as np
from pathlib import Path
def recompose(fit,patch,source_sha256=None):
    if not source_sha256 or patch.get('input_fit_sha256')!=source_sha256:raise ValueError('missing, stale or unverified input fit hash')
    result=copy.deepcopy(fit);j={r['role']:r for r in result['joints']};seen=set()
    explicit={c['role'] for c in patch['corrections']}
    order={r['role']:i for i,r in enumerate(fit['joints'])}
    for c in sorted(patch['corrections'],key=lambda c:order.get(c['role'],len(order))):
        role=c['role']
        if role not in j or role in seen:raise ValueError('unknown or duplicate role')
        seen.add(role);r=j[role]
        if 'position_cm' in c:p=np.array(c['position_cm'],dtype=float)
        else:
            idx=c['candidate_index']
            if not isinstance(idx,int) or isinstance(idx,bool) or idx<0 or idx>=len(r['competing_candidates']):raise ValueError('candidate index out of range')
            p=np.array(r['competing_candidates'][idx]['position_cm'])
        if p.shape!=(3,) or not np.isfinite(p).all():raise ValueError('finite XYZ required')
        if not c.get('provenance') or not c.get('reason'):raise ValueError('correction provenance and reason required')
        previous=np.array(r['position_cm']);r['position_cm']=p.tolist();r['manual_correction']=copy.deepcopy(c);r['status']='manually_corrected';r['correction_requires_anatomical_revalidation']=True
        if role=='pelvis':
            delta=p-previous
            for i in range(1,4):
                if f'spine_{i:02}' in explicit:continue
                child=j[f'spine_{i:02}'];child['position_cm']=(np.array(child['position_cm'])+delta*(1-i/4)).tolist();child['dependency_recomputation']={'from':role,'rule':'linear axial blend with upper anchor fixed'}
            for side in ['l','r']:
                if 'thigh_'+side in explicit:continue
                child=j['thigh_'+side];child['position_cm']=(np.array(child['position_cm'])+delta).tolist();child['dependency_recomputation']={'from':role,'rule':'retain pelvic hip offsets; rerun volume gates'}
        if role.startswith('upperarm_'):
            if 'clavicle_'+role[-1] in explicit:continue
            child=j['clavicle_'+role[-1]];child['position_cm']=(np.array(child['position_cm'])+(p-previous)*.48).tolist();child['dependency_recomputation']={'from':role,'rule':'retain fitted shoulder-girdle interpolation; revalidate'}
    # Propagated positions invalidate the previous automatic anatomical acceptance.
    for r in j.values():
        if r.get('dependency_recomputation'):
            r['status']='dependency_recomputed';r['correction_requires_anatomical_revalidation']=True;r['ambiguity_flags']=sorted(set(r['ambiguity_flags']+['dependency_moved_position_requires_anatomical_review']))
    # Recompute every local translation and segment orientation from the modified connected hierarchy.
    locals={};axes={}
    children={n:[] for n in j}
    for n,r in j.items():
        parent=r['parent_role'];p=np.array(r['position_cm']);locals[n]=(p-np.array(j[parent]['position_cm'])).tolist() if parent else p.tolist()
        if parent:
            if np.linalg.norm(p-np.array(j[parent]['position_cm']))<1e-6:raise ValueError('zero-length segment after correction')
            children[parent].append(n)
    for n,r in j.items():
        if not children[n]:axes[n]=copy.deepcopy(axes[r['parent_role']]);axes[n]['terminal']=True;axes[n].pop('primary_child',None);continue
        child=children[n][0];a=np.array(j[child]['position_cm'])-r['position_cm'];length=np.linalg.norm(a)
        if length<1e-6:raise ValueError('zero-length segment after correction')
        x=a/length;up=np.array([0.,0.,1.]);roll=np.cross(up,x)
        if np.linalg.norm(roll)<.05:roll=np.cross(np.array([0.,1.,0.]),x)
        y=roll/np.linalg.norm(roll);z=np.cross(x,y);axes[n]={'aim_x':x.tolist(),'y':y.tolist(),'z':z.tolist(),'primary_child':child}
    # These are real parent-frame local transforms, not world-space position differences.
    matrices={n:np.column_stack((a['aim_x'],a['y'],a['z'])) for n,a in axes.items()}
    rotations={}
    for n,r in j.items():
        parent=r['parent_role'];R=matrices[parent] if parent else np.eye(3)
        locals[n]=(R.T@np.array(locals[n])).tolist();rotations[n]=(R.T@matrices[n]).tolist()
    result['recomputed_local_translations_cm']=locals;result['recomputed_local_rotation_matrices']=rotations;result['recomputed_axes']=axes;result['correction_count']=len(patch['corrections']);result['downstream_authorised']=False
    return result
if __name__=='__main__':
    P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase4B';W=P/'Working/Phase4B';fit=json.loads((O/'automatic_fit_v2.json').read_text())
    pending=[r['role'] for r in fit['joints'] if r['status']=='ambiguous'];schema={'schema_version':1,'input_fit_sha256':hashlib.sha256((O/'automatic_fit_v2.json').read_bytes()).hexdigest(),'corrections':[],'pending_anatomical_review':pending,'actual_user_corrections':0}
    (W/'corrections.json').write_text(json.dumps(schema,indent=2))
    fitsha=schema['input_fit_sha256']
    pelvis=next(r['position_cm'] for r in fit['joints'] if r['role']=='pelvis');patch={'input_fit_sha256':fitsha,'corrections':[{'role':'pelvis','position_cm':[pelvis[0],pelvis[1]+1,pelvis[2]+2],'provenance':'synthetic_test_only','reason':'Verify dependency and deterministic replay; not actual anatomical correction'}]}
    a=recompose(fit,patch,fitsha);b=recompose(fit,patch,fitsha);assert a==b
    (W/'correction_replay_fixture.json').write_text(json.dumps(a,indent=2))
    rejected=[]
    for bad in [{'role':'unknown','position_cm':[0,0,0]},{'role':'pelvis','position_cm':[math.nan,0,1]},{'role':'lowerarm_l','candidate_index':-1},{'role':'hand_l','position_cm':next(r['position_cm'] for r in fit['joints'] if r['role']=='lowerarm_l')}]:
        try:recompose(fit,{'input_fit_sha256':fitsha,'corrections':[dict(bad,provenance='test',reason='negative test')]},fitsha)
        except ValueError as e:rejected.append(str(e))
    assert len(rejected)==4
    for badhash in [None,'stale']:
        try:recompose(fit,dict(patch,input_fit_sha256=badhash),fitsha)
        except ValueError as e:rejected.append(str(e))
    assert len(rejected)==6
    explicit_spine={'role':'spine_01','position_cm':[0,3,115],'provenance':'synthetic_test_only','reason':'Explicit location takes precedence over propagated pelvis dependency'}
    combined=dict(patch,corrections=patch['corrections']+[explicit_spine]);first=recompose(fit,combined,fitsha);last=recompose(fit,dict(combined,corrections=list(reversed(combined['corrections']))),fitsha)
    assert first==last and next(r['position_cm'] for r in first['joints'] if r['role']=='spine_01')==[0.,3.,115.]
    # Round-trip parent-frame transforms must reconstruct the amended world positions.
    reconstructed={};rotations={};max_error=0
    for r in a['joints']:
        n=r['role'];parent=r['parent_role'];R=rotations[parent] if parent else np.eye(3);origin=reconstructed[parent] if parent else np.zeros(3)
        reconstructed[n]=origin+R@a['recomputed_local_translations_cm'][n];rotations[n]=R@a['recomputed_local_rotation_matrices'][n];max_error=max(max_error,float(np.linalg.norm(reconstructed[n]-r['position_cm'])))
    assert max_error<1e-9
    result={'deterministic_replay_pass':a==b,'dependency_spine_01_delta_cm':(np.array(a['joints'][2]['position_cm'])-fit['joints'][2]['position_cm']).tolist(),'changed_dependents':[r['role'] for r in a['joints'] if r.get('dependency_recomputation')],'local_transform_axes_recomputed':len(a['recomputed_axes']),'negative_cases_rejected':rejected,'actual_user_corrections':0,'synthetic_fixture_used_for_binding':False,'pending_review_roles':pending}
    result['parent_frame_roundtrip_max_error_cm']=max_error
    result['patch_order_independence_pass']=first==last;result['explicit_child_correction_preserved']=True;result['fit_hash_binding_pass']=True
    result['dependency_anatomical_acceptance_invalidated']=all(r['status']=='dependency_recomputed' for r in a['joints'] if r.get('dependency_recomputation'));assert result['dependency_anatomical_acceptance_invalidated']
    (O/'correction_model_validation.json').write_text(json.dumps(result,indent=2));print('CORRECTION_MODEL',result)
