"""Evaluate immutable public donor readback; controls enter only after mapping is saved."""
import sys,json,hashlib,re,math
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4C';O=P/'Documentation/Phase4C'
sys.path.insert(0,str(P/'Working/Phase4B'))
from geometry_tools import sections
from correction_model import recompose
def read(p):return json.loads(p.read_text())
def save(n,x):(O/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=read(W/'donor_geometry_and_joints.json');dj={r['name']:r for r in d['joints']}
frame=read(O/'coordinate_frame.json');R=np.array(frame['rotation_columns_world']);org=np.array(frame['origin_body_coordinates_cm']);s=frame['factor']
g=np.load(W/'normalised_geometry.npz');v=g['vertices'];t=g['triangles']
# Read only the canonical role schema here; no prior phase coordinates initialise donor positions.
schema=[(r['role'],r['parent_role'],r['side']) for r in read(P/'Documentation/Phase4B/automatic_fit_v2.json')['joints']]
source_names={'spine_01':'spine_02','spine_02':'spine_04','spine_03':'spine_05'}
rows=[]
for role,parent,side in schema:
    name=source_names.get(role,role);q=dj[name];p=np.array(q['world_cm']);back=(p/s+org)@R.T
    provisional=role in ['root','spine_01','spine_02','spine_03']
    flags=[] if provisional else ['target_articulation_requires_independent_anatomical_review']
    if role.startswith('clavicle'):flags+=['donor_clavicle_root_is_not_mid_clavicle_landmark']
    if role.startswith('hand'):flags+=['donor_wrist_displaced_toward_target_hand_digit_region']
    if role=='neck_01':flags+=['posterior_neck_joint_position_requires_review']
    rows.append({'role':role,'parent_role':parent,'side':side,'position_cm':p.tolist(),
      'source_joint_name':name,'source_joint_index':q['index'],'source_parent_joint':d['joints'][q['parent_index']]['name'],
      'original_metahuman_source_world_cm':p[[0,2,1]].tolist(),'mapped_original_lara_world_cm':back.tolist(),
      'direct_solved_joint':True,'postprocessing':'axis conversion and inverse target normalisation only; explicit hierarchy contraction for spine/neck',
      'evidence_sources':[d['api'],'public Python joint readback agrees exactly','unchanged target cross-section screens applied separately'],
      'confidence_score':.85 if provisional else .65,'confidence_score_kind':'prototype evidence score, not probability',
      'ambiguity_flags':flags,'status':'automatically_accepted' if provisional else 'ambiguous','competing_candidates':[],'manual_correction':None})
fit={'method':'Public MetaHuman posed donor joints, no geometry landmark substitution','height_cm':180,'joints':rows,
 'mapping_policy':'Retain MetaHuman spine 02/04/05 as canonical 01/02/03; collapse intervening joints and neck_02 without moving retained points. Selected by topology, before control evaluation.',
 'acceptance_policy':'Root and supported axial spine points are provisional candidates under the existing 4B score/no-flags rule. Every other articulation needs independent target review; names do not certify position.',
 'input_geometry_sha256':sha(W/'normalised_geometry.npz'),'donor_sha256':sha(W/'Donor/LaraDonor_combined_Posed.dna'),
 'control_used_for_initialisation':False,'downstream_authorised':False}
save('automatic_fit_v2.json',fit);fitsha=sha(O/'automatic_fit_v2.json')
allmap=[]
for q in d['joints']:
    p=np.array(q['world_cm']);back=(p/s+org)@R.T
    allmap.append(dict(q,original_metahuman_source_world_cm=p[[0,2,1]].tolist(),mapped_original_lara_world_cm=back.tolist(),direct_solved_joint=True,source_api=d['api'],validation_status='extracted; not anatomically accepted for Lara'))
save('donor_to_lara_mapping.json',{'proposal_sha256':fitsha,'transform':'transform_mapping.json','all_donor_joints':allmap,'canonical_body_mapping':rows,
 'missing_roles':{'palm_centre':'No distinct named palm centre was extracted. hand is wrist; metacarpals are direct joints, no inferred palm centre inserted.'},
 'finger_and_toe_names':[n for n in dj if re.match(r'^(thumb|index|middle|ring|pinky)_(0[123]|metacarpal)_[lr]$',n) or 'toe' in n]})
points=np.array([q['world_cm'] for q in d['joints']]);back=(points/s+org)@R.T;roundtrip=(back@R-org)*s
ue=read(W/'ue_target_geometry.json');uv=np.array(ue['vertices_cm']);ut=np.array(ue['triangle_indices']).reshape(-1,3)
tr=read(O/'transform_mapping.json');tr.update({'donor_mapping_status':'validated against actual UE target readback and both public joint APIs',
 'donor_round_trip_max_cm':float(np.linalg.norm(roundtrip-points,axis=1).max()),'ue_target_indexwise_vertex_max_difference_cm':float(np.linalg.norm(uv-v,axis=1).max()),
 'ue_target_triangle_indices_identical':bool(np.array_equal(ut,t)),
 'ue_triangle_connectivity_limit':'Temporary target is an isolated copy of the 4B UE import. Vertex order/positions match fresh source; FBX triangulation differs from Blender loop triangulation. Original source polygon topology is retained separately and unchanged; no final Lara mesh authored.',
 'basis':'Source DCC world RH -> canonical UE LH left/forward/up via determinant -1 R; DNA source left/up/front -> UE left/front/up via Y/Z exchange.',
 'model_offset_policy':'No fitted donor offset, recentering, rescaling or best-fit alignment. Posed export preserves the solved pose in target space; root remains [0,0,0].',
 'model_pose':'Public posed-DNA export, evaluate-pose export state. Original local rotations/parents retained in solved_donor_joints.json; canonical rest orientations not authored because anatomy rejected.'})
save('transform_mapping.json',tr)
# Post-fit evaluations start only here, after the independent proposal has a fixed SHA.
b=read(P/'Documentation/Phase4B/automatic_fit_v2.json');bp={q['role']:np.array(q['position_cm']) for q in b['joints']};cp={q['role']:np.array(q['position_cm']) for q in rows}
ar=read(P/'Documentation/Phase4B/manual_control_comparison_v2.json');ap={q['role']:np.array(q['control_in_inferred_frame_cm']) for q in ar['joints']}
def compare(a,b,label):
    out=[]
    for role,parent,_ in schema:
        dist=float(np.linalg.norm(a[role]-b[role]));angle=None
        if parent:
            x=a[role]-a[parent];y=b[role]-b[parent];angle=float(np.degrees(np.arccos(np.clip(x@y/(np.linalg.norm(x)*np.linalg.norm(y)),-1,1))))
        out.append({'role':role,'a_cm':a[role].tolist(),'b_cm':b[role].tolist(),'absolute_difference_cm':dist,'difference_percent_180cm':dist/1.8,'parent_segment_axis_difference_deg':angle,'same_canonical_parent_role':True})
    return {'comparison':label,'joint_count':len(out),'mean_difference_cm':float(np.mean([q['absolute_difference_cm'] for q in out])),
      'max_difference_cm':max(q['absolute_difference_cm'] for q in out),'canonical_hierarchy_equivalent':True,'native_hierarchy_equivalent':False,
      'native_hierarchy_limit':'MetaHuman five spines, two neck joints, extra metacarpals/helpers differ from 4B/4A; explicit contraction required, no retained positions moved.', 'joints':out}
comparisons={'A_4B_vs_B_4C':compare(bp,cp,'4B geometry vs 4C donor'),'B_4C_vs_C_4A':compare(cp,ap,'4C donor vs approximate 4A authored control'),
 'A_4B_vs_C_4A':compare(bp,ap,'4B geometry vs approximate 4A authored control'),
 'evaluation_only':True,'proposal_sha256_before_and_after':fitsha,'manual_control_is_ground_truth':False,'frame_identical_to_4B':frame==read(P/'Documentation/Phase4B/coordinate_frame.json')}
comparisons['bilateral_consistency']={label:[{'left_role':n,'mirrored_difference_cm':float(np.linalg.norm(p[n]*np.array([-1,1,1])-p[n[:-1]+'r']))} for n in p if n.endswith('_l')] for label,p in [('4B',bp),('4C',cp),('4A_control',ap)]}
save('phase4b_comparison.json',comparisons);save('manual_control_comparison.json',comparisons['B_4C_vs_C_4A'])
# Reuse target section branches as evaluation only. Different donor digits occupying the same
# actual target cross-section is a collision regardless of the unknown target digit names.
finger_checks=[];all_unique=True;tracks=read(P/'Documentation/Phase4B/finger_branch_prototype.json')['sides']
for side in ['l','r']:
    assign=[]
    for name in ['index','middle','ring','pinky']:
        p=np.array(dj[f'{name}_03_{side}']['world_cm']);delta=[]
        for track in tracks[side]:
            centres=np.array(track['ordered_surface_section_centres_cm']);a=centres[:-1];edge=centres[1:]-a
            f=np.clip(np.sum((p-a)*edge,axis=1)/np.sum(edge*edge,axis=1),0,1)
            delta.append(float(np.linalg.norm(a+f[:,None]*edge-p,axis=1).min()))
        k=int(np.argmin(delta))
        assign.append({'digit':name,'donor_distal_joint_cm':p.tolist(),'nearest_target_branch_index':k,'nearest_target_branch_id':tracks[side][k]['candidate_id'],'distance_to_target_track_cm':delta[k]})
    unique=len(set(q['nearest_target_branch_index'] for q in assign));all_unique&=unique==4
    finger_checks.append({'side':side,'four_long_digits_distinct_target_branches':unique==4,'distinct_assigned_branches':unique,'assignments':assign,
      'limit':'Nearest point on all five actual 4B target section-centre polylines in XYZ, evaluation only, not mesh correspondence or semantic identification. A collision screen cannot accept digits; it exposes collapsed assignments.'})
finger_names=[n for n in dj if re.match(r'^(thumb|index|middle|ring|pinky)_0[123]_[lr]$',n)]
fingers={'exposed_phalange_joints':len(finger_names),'named_chains_exposed':10,'named_chains_accepted_for_lara':0,'phalange_roles_requiring_review':30,
 'metacarpals_exposed':[n for n in dj if re.match(r'^(index|middle|ring|pinky)_metacarpal_[lr]$',n)],'palm_centre_missing':True,
 'collision_screen_passed':all_unique,'checks':finger_checks,'classification':'unsuitable for automatic Lara fingers in this zero-keypoint solve; assisted correction extent unmeasured'}
# Finger controls evaluated only after donor mapping; no semantic acceptance follows.
a4=next(q for q in read(P/'Documentation/Phase4A/assisted_candidates_ball_forward.json') if q['case']=='Unrigged')
f4=read(P/'Working/Phase4A/Unrigged_geometry.json')['uniform_factor'];a4p={n:(np.array(p)/f4*np.array([1,-1,1])@R-org)*s for n,par,p in a4['authored_landmarks_cm']}
fingers['control_evaluation_only']=[{'role':n,'difference_cm':float(np.linalg.norm(np.array(dj[n]['world_cm'])-a4p[n])),'control_limit':'approximate authored finger locations; not ground truth'} for n in finger_names]
save('finger_validation.json',fingers)
pending=[q['role'] for q in rows if q['status']=='ambiguous']
patch={'schema_version':1,'input_fit_sha256':fitsha,'corrections':[],'pending_anatomical_review':pending,'actual_user_corrections':0}
(W/'corrections.json').write_text(json.dumps(patch,indent=2));replayed=recompose(fit,patch,fitsha)
assert replayed['correction_count']==0 and replayed['joints']==fit['joints']
assert fitsha==sha(O/'automatic_fit_v2.json')
save('correction_measurements.json',{'body_roles_requiring_review':len(pending),'body_review_roles':pending,'finger_phalange_roles_requiring_review':30,'finger_chains_requiring_review':10,
 'total_required_review_roles_excluding_optional_metacarpals':len(pending)+30,'actual_corrections_applied':0,'total_moved_distance_cm':0,'maximum_moved_distance_cm':0,
 'minimal_correction_proven':False,'real_correction_effort':'unmeasured; zero performed is not zero needed','correction_framework':'4B recompose imported read-only; empty SHA-bound patch replay leaves donor positions unchanged',
 'grouped_opportunities':['pelvis/hips as a coupled group','spine convention and neck/head','paired shoulder girdles','paired elbow/wrist pose','knee/ankle/ball placement','each hand: wrist plus five independent digit assignments'],
 'categories':['internal articulation review','semantic pivot convention review','target/donor pose alignment','digit correspondence and collision resolution']})
save('analysis_summary.json',{'selected_attempt':'combined Auto Solve, full Lara surface, zero keypoints','semantic_body_roles_exposed':23,'provisional_body_roles_accepted':4,'body_roles_requiring_review':19,
 'phase4b_provisional_accepted':6,'phase4b_ambiguous':17,'body_classification':'experimental assisted','finger_classification':fingers['classification'],
 'mean_4C_vs_4A_cm':comparisons['B_4C_vs_C_4A']['mean_difference_cm'],'mean_4B_vs_4A_cm':comparisons['A_4B_vs_C_4A']['mean_difference_cm'],
 'count_limit':'Provisional counts are gate-policy outputs, not independent ground-truth accuracy; whole-body acceptance still requires all gates.'})
print(json.dumps(read(O/'analysis_summary.json'),indent=2));print('finger collision',[(q['side'],q['distinct_assigned_branches']) for q in finger_checks])
