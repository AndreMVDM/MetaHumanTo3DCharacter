import json,math,numpy as np,sys,hashlib,argparse
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'Working/Phase4B'))
from geometry_tools import sections,nearest_distances
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4C';O=P/'Documentation/Phase4C'
review={};manual_review_used=[]
if '--fit' in sys.argv:
    parser=argparse.ArgumentParser();parser.add_argument('--fit',required=True);parser.add_argument('--review');args=parser.parse_args();fitpath=Path(args.fit).resolve();assert fitpath.is_relative_to(W.resolve()) or fitpath.is_relative_to(O.resolve());suffix='_corrected'
    if args.review:
        reviewpath=Path(args.review).resolve();assert reviewpath.is_relative_to(W.resolve()) or reviewpath.is_relative_to(O.resolve());review=json.loads(reviewpath.read_text())
else:
    suffix=sys.argv[1] if len(sys.argv)>1 else '';assert suffix in ['', '_v2'];fitpath=O/('automatic_fit'+suffix+'.json')
fit=json.loads(fitpath.read_text());fitsha=hashlib.sha256(fitpath.read_bytes()).hexdigest();d=np.load(W/'normalised_geometry.npz');v=d['vertices'];t=d['triangles'];j={r['role']:r for r in fit['joints']};p={n:np.array(r['position_cm']) for n,r in j.items()};checks=[]
def reviewed_correction(n):
    r=j[n];approval=review.get('roles',{}).get(n,{})
    if r['status'] not in ['manually_corrected','dependency_recomputed'] or review.get('proposal_sha256')!=fitsha or review.get('provenance_kind')!='human_anatomical_review':return False
    if approval.get('anatomical_valid') is not True or not approval.get('method') or sorted(approval.get('resolved_ambiguity_flags',[]))!=sorted(r['ambiguity_flags']):return False
    xyz=np.array(approval.get('position_cm',[]))
    if xyz.shape!=(3,) or not np.isfinite(xyz).all() or np.linalg.norm(xyz-p[n])>1e-6:return False
    artifact=Path(approval.get('evidence_artifact','')).resolve()
    if not artifact.is_file() or not (artifact.is_relative_to(W.resolve()) or artifact.is_relative_to(O.resolve())):return False
    if approval.get('evidence_sha256')!=hashlib.sha256(artifact.read_bytes()).hexdigest():return False
    manual_review_used.append(n);return True
def check(name,passed,value,threshold,kind='hard'):
    checks.append({'name':name,'pass':bool(passed),'measured':value,'threshold':threshold,'kind':kind})
reachable={'root'}
for _ in j:
    reachable.update(n for n,r in j.items() if r['parent_role'] in reachable)
check('single_connected_hierarchy',len(j)==len(fit['joints']) and len(reachable)==len(j) and all(r['parent_role'] in j for r in fit['joints'] if r['parent_role']) and sum(not r['parent_role'] for r in fit['joints'])==1,{'joints':len(j),'reachable':len(reachable)},'one grounded root; unique roles; every role reachable; no cycle')
check('finite_nonzero_segments',all(np.isfinite(x).all() for x in p.values()) and all(np.linalg.norm(p[n]-p[r['parent_role']])>.001 for n,r in j.items() if r['parent_role']),{n:float(np.linalg.norm(p[n]-p[r['parent_role']])) for n,r in j.items() if r['parent_role']},'finite XYZ and all parent segments >.001cm')
check('root_grounded_distinct_pelvis',np.linalg.norm(p['root'])<.01 and np.linalg.norm(p['pelvis'])>50,np.linalg.norm(p['pelvis']).item(),'root=(0,0,0), pelvis >50cm away')
check('height',abs(float(np.ptp(v[:,2]))-180)<.01,float(np.ptp(v[:,2])),'180 +/- .01cm')
sym=[]
for n in p:
    if n.endswith('_l'):
        counterpart=n[:-1]+'r';a=p[n].copy();a[0]*=-1;sym.append({'role':n,'difference_cm':float(np.linalg.norm(a-p[counterpart]))})
check('left_right_not_crossed',all(x[0]>0 for n,x in p.items() if n.endswith('_l')) and all(x[0]<0 for n,x in p.items() if n.endswith('_r')), {n:float(x[0]) for n,x in p.items() if n.endswith(('_l','_r'))},'positive left, negative right')
check('bilateral_body_consistency',max(r['difference_cm'] for r in sym)<6,sym,'maximum mirrored role difference <6cm; prototype tolerance')
for side in ['l','r']:
    foot=p['foot_'+side];ball=p['ball_'+side]
    check('ball_forward_'+side,ball[1]-foot[1]>1,float(ball[1]-foot[1]),'>1cm along inferred forward')
    check('knee_monotonic_'+side,p['thigh_'+side][2]>p['calf_'+side][2]>foot[2],[float(p[n+'_'+side][2]) for n in ['thigh','calf','foot']],'descending hip/knee/ankle height')
    check('elbow_between_shoulder_wrist_'+side,p['upperarm_'+side][2]>p['lowerarm_'+side][2]>p['hand_'+side][2],[float(p[n+'_'+side][2]) for n in ['upperarm','lowerarm','hand']],'descending shoulder/elbow/wrist height')
# Cross-section envelope is a conservative geometric screen, not proof of internal medical articulation.
for n,point in p.items():
    if n=='root':continue
    cs=sections(v,t,float(point[2]));containing=[]
    for c in cs:
        lo=np.array(c['min']);hi=np.array(c['max'])
        if np.all(point[:2]>=lo[:2]-.8) and np.all(point[:2]<=hi[:2]+.8):containing.append(c)
    check('surface_envelope_'+n,bool(containing),{'position_cm':point.tolist(),'enclosing_contour_count':len(containing)},'inside at least one actual section bounding envelope +/- .8cm; does not certify concave volume')
    auto=j[n]['status']=='automatically_accepted' and not j[n]['ambiguity_flags'] and j[n]['confidence_score']>=.80
    check('anatomical_role_resolved_'+n,auto or reviewed_correction(n),j[n]['ambiguity_flags'],'automatic score >=.80 with no flags OR corrected position with SHA-bound explicit human anatomical review/evidence; all geometry gates still required','anatomical')
check('neck_exits_torso',p['neck_01'][2]>p['spine_03'][2] and p['head'][2]>p['neck_01'][2],[float(p[n][2]) for n in ['spine_03','neck_01','head']],'spine < neck < head')
frame=json.loads((O/'coordinate_frame.json').read_text());R=np.array(frame['rotation_columns_world']);check('frame_orthonormal',np.max(abs(R.T@R-np.eye(3)))<1e-6 and abs(np.linalg.det(R)+1)<1e-6,{'orthogonality_error':float(np.max(abs(R.T@R-np.eye(3)))),'determinant':float(np.linalg.det(R))},'orthonormal determinant -1; explicit left/forward/up LH canonical frame')
check('paired_sole_up_evidence',frame['ground_plane_points']>=40,frame['ground_plane_points'],'>=40 near-ground supporting vertices; geometric up evidence, no medical upright certification')
for side,sign in [('l',1),('r',-1)]:
    sole=v[(sign*v[:,0]>10)&(v[:,2]<8)];shank=v[(sign*v[:,0]>8)&(v[:,2]>25)&(v[:,2]<36)];anchor=float(np.median(shank[:,1]));rear,front=np.quantile(sole[:,1],[.01,.99]);evidence={'forward_extent_cm':float(front-anchor),'rear_extent_cm':float(anchor-rear)}
    check('geometry_shoe_facing_'+side,evidence['forward_extent_cm']>evidence['rear_extent_cm'],evidence,'paired shoe anterior extension greater than heel extension from lower shank')
failed=[r['name'] for r in checks if not r['pass']];result={'checks':checks,'passed':not failed,'failed':failed,'structural_geometric_passed':all(r['pass'] for r in checks if r['kind']=='hard'),'automatic_anatomical_passed':not manual_review_used and all(r['pass'] for r in checks if r['kind']=='anatomical'),'manual_anatomical_review_roles':manual_review_used,'proposal_sha256':fitsha,'downstream_authorised':not failed,'numeric_screen_limit':'Section bounding envelopes are conservative; no claim of exact internal anatomical ground truth. Unresolved anatomical roles block downstream even when geometric screens pass.','skin':{'status':'not_run_if_rejected'},'retarget_bake':{'status':'not_run_if_rejected'}}
(O/('anatomical_validation'+suffix+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print('GATES',suffix,result['structural_geometric_passed'],result['automatic_anatomical_passed'],failed)

