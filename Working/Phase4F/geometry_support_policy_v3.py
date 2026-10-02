"""Versioned body-region adapter; v2 finger/support safeguards are unchanged."""
import copy,json
from pathlib import Path
import numpy as np
import geometry_support_policy as v2
import body_region_support as body

POLICY_PATH=Path(__file__).resolve().parents[2]/'Documentation/Phase4F/anatomy_geometry_policy_v3.json'
POLICY=json.loads(POLICY_PATH.read_text(encoding='utf-8'))
finger_approval_current=v2.finger_approval_current
path_separation=v2.path_separation

def role_binding(mesh,role,joints,previous,ownership=None):
    """Binding is association, never a substitute for closed geometric support.

    Preserve existing source associations for unclassified skin. New garment
    regions require the existing named principal garment classification. New
    footwear associations require explicit source-bound footwear classification,
    plus both reviewed same-side landmarks projecting onto source triangles.
    """
    families={'pelvis':['trouser_region'],'spine_01':['trouser_region','shirt_region'],
              'spine_02':['shirt_region'],'spine_03':['shirt_region']}
    stem=role.rsplit('_',1)[0]
    groups=families.get(role,{'clavicle':['shirt_region'],'upperarm':['shirt_region'],
                            'thigh':['trouser_region'],'calf':['trouser_region']}.get(stem,[]))
    allowed=set();evidence=[]
    if not groups:
        for r in previous.get('measured',{}).get('containing_polygons',[]):
            allowed.update(r['source_components'])
        if allowed:evidence.append('unchanged v2 independently closed source-loop association; v3 orientation and holes still required')
    if stem in ['foot','ball']:
        allowed=set();side=role[-1];sign=1 if side=='l' else -1
        a=np.asarray(joints['foot_'+side]['position_cm']);b=np.asarray(joints['ball_'+side]['position_cm'])
        classified={c for entry in ownership or [] if entry['family']=='footwear' and entry['side']==side for c in entry['components']}
        for component in classified:
            vertices=mesh.v[mesh.components==component]
            if not np.all(sign*vertices[:,0]>body.EPS):continue
            if vertices[:,2].max()<min(a[2],b[2])-body.EPS or vertices[:,2].min()>max(a[2],b[2])+body.EPS:continue
            tids=np.where(mesh.components[mesh.f[:,0]]==component)[0];tri=mesh.tri[tids]
            def projected_source_hit(p):
                xy=tri[:,:,:2];v=xy[:,1]-xy[:,0];w=xy[:,2]-xy[:,0];delta=p[:2]-xy[:,0]
                det=v[:,0]*w[:,1]-v[:,1]*w[:,0];valid=abs(det)>body.EPS**2
                u=np.divide(delta[:,0]*w[:,1]-delta[:,1]*w[:,0],det,out=np.zeros_like(det),where=valid)
                t=np.divide(v[:,0]*delta[:,1]-v[:,1]*delta[:,0],det,out=np.zeros_like(det),where=valid)
                return bool(np.any(valid&(u>=0)&(t>=0)&(u+t<=1)))
            if projected_source_hit(a) and projected_source_hit(b):allowed.add(int(component))
        evidence=['source-bound explicit footwear classification; same-side component and actual triangle footprint at both accepted foot/ball landmarks; association only, not volumetric proof']
    return {'role':role,'garment_groups':groups,'source_components':sorted(allowed),'association_evidence':evidence}

def apply_policy(checks,fit,work,docs,core):
    # Evaluate and retain exact v2 outcomes before replacing only body support.
    legacy=v2.apply_policy(checks,fit,work,docs,core)
    previous=[copy.deepcopy(c) for c in checks if c['name'].startswith('surface_envelope_')]
    try:
        mesh,provenance=v2.load_source(work,docs,fit)
        frame=json.loads((Path(docs)/'coordinate_frame.json').read_text())
        matrix=np.asarray(frame['rotation_columns_world'],dtype=float)
        determinant=float(np.linalg.det(matrix))
        if matrix.shape!=(3,3) or not np.isfinite(matrix).all() or abs(abs(determinant)-1)>body.EPS:raise ValueError('invalid source frame orientation')
        if abs(determinant-frame['handedness_determinant'])>body.EPS:raise ValueError('source frame determinant mismatch')
        raw=np.load(Path(work)/'source_geometry.npz')['vertices']
        transformed=(raw@matrix-np.asarray(frame['origin_body_coordinates_cm']))*frame['factor']
        if transformed.shape!=mesh.v.shape or not np.allclose(transformed,mesh.v,rtol=0,atol=body.EPS):raise ValueError('source orientation frame does not reproduce bound geometry')
        provenance['coordinate_frame_sha256']=v2.sha(Path(docs)/'coordinate_frame.json')
        provenance['source_orientation_determinant']=determinant
        ownership_path=Path(docs)/'body_region_ownership.json';ownership=[]
        if ownership_path.is_file():
            document=json.loads(ownership_path.read_text())
            if document['schema_version']!=1:raise ValueError('unsupported source ownership schema')
            if document['normalised_geometry_sha256']!=v2.sha(Path(work)/'normalised_geometry.npz') or document['source_geometry_sha256']!=v2.sha(Path(work)/'source_geometry.npz'):raise ValueError('source ownership geometry binding mismatch')
            artifact=Path(document['evidence_artifact']).resolve()
            root=Path(__file__).resolve().parents[2]/'Documentation/Phase4F'
            if not artifact.is_relative_to(root.resolve()) or v2.sha(artifact)!=document['evidence_sha256']:raise ValueError('source ownership classification evidence mismatch')
            ownership=document['regions']
            seen_components=set()
            for entry in ownership:
                if entry['family']!='footwear' or entry['side'] not in ['l','r']:raise ValueError('unsupported source ownership semantics')
                for c in entry['components']:
                    if isinstance(c,bool) or not isinstance(c,int) or c in seen_components:raise ValueError('ambiguous source ownership component')
                    seen_components.add(c)
                    if c not in mesh.provenance or list(mesh.provenance[c])!=entry['source_provenance_token']:raise ValueError('source ownership provenance mismatch')
            provenance['body_region_ownership_sha256']=v2.sha(ownership_path)
            provenance['ownership_evidence_sha256']=document['evidence_sha256']
        orientation=float(np.sign(determinant))
        joints={j['role']:j for j in fit['joints']}
        old_by_name={c['name']:c for c in previous}
        for c in checks:
            if not c['name'].startswith('surface_envelope_'):continue
            role=c['name'].removeprefix('surface_envelope_')
            binding=role_binding(mesh,role,joints,old_by_name[c['name']],ownership)
            passed,measured=body.evaluate(mesh,joints[role]['position_cm'],orientation,POLICY,binding)
            c.update({'pass':passed,'measured':measured,'threshold':'owned closed oriented source region with explicit holes; existing +/-0.8cm allowance and reciprocal seam budget; no 3D fallback',
                      'policy_version':POLICY['version']})
        source_error=None
    except (ValueError,KeyError,TypeError,IndexError,OSError,np.linalg.LinAlgError) as error:
        source_error=str(error);provenance=legacy.get('source_provenance')
        for c in checks:
            if c['name'].startswith('surface_envelope_'):
                c.update({'pass':False,'measured':{'failures':['source_or_orientation_provenance_invalid'],'detail':source_error},
                          'threshold':'valid source and orientation provenance required','policy_version':POLICY['version']})
    return {'version':POLICY['version'],'policy_sha256':v2.sha(POLICY_PATH),'body_v2_results':previous,
            'v2_migration':legacy,'legacy_results':legacy['legacy_results'],'source_provenance':provenance,
            'source_error':source_error,'finger_policy_version':v2.POLICY['version'],
            'placement_allowance_unchanged_cm':POLICY['placement_allowance_cm'],'baseline_numeric_thresholds_unchanged':False}
