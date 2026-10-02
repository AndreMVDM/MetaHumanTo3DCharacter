"""Per-character donor proposals and target-only digit branches; no human judgements."""
import sys, json, hashlib, shutil, importlib.util
import numpy as np
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F';O=P/'Documentation/Phase4F'
sys.path.insert(0,str(P/'Working/Phase4B'))
from geometry_tools import sections
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def schema():
    rows=[('root',None),('pelvis','root'),('spine_01','pelvis'),('spine_02','spine_01'),('spine_03','spine_02'),('neck_01','spine_03'),('head','neck_01')]
    for s in ['l','r']:
        rows += [(n+'_'+s,p+'_'+s if p not in ['spine_03','pelvis'] else p) for n,p in [('clavicle','spine_03'),('upperarm','clavicle'),('lowerarm','upperarm'),('hand','lowerarm'),('thigh','pelvis'),('calf','thigh'),('foot','calf'),('ball','foot')]]
    return rows
def tracks(v,t,side):
    sign=1 if side=='l' else -1;H=np.ptp(v[:,2])
    pose=json.loads((O/character/'source_pose_validation.json').read_text())
    wrist=np.array(pose['arms'][side]['wrist_surface_narrowing_cm'])
    hand=v[(sign*v[:,0]>sign*wrist[0]-H*.045)&(v[:,2]<wrist[2]+H*.025)&(v[:,2]>H*.32)]
    active=[];finished=[];slice_evidence=[]
    for z in np.arange(hand[:,2].min()+.15,wrist[2]+1,.4):
        candidates=[]
        for c in sections(v,t,z):
            widths=np.array(c['max'])-c['min']
            if c['count']>=6 and max(widths[:2])<H*.026 and sign*c['centre'][0]>sign*wrist[0]-H*.045:
                candidates.append(c)
        slice_evidence.append({'z_cm':float(z),'contours':len(candidates)})
        next_active=[];used=set()
        for branch in active:
            p=np.array(branch[-1]['centre']);choices=[(float(np.linalg.norm(np.array(c['centre'])-p)),i,c) for i,c in enumerate(candidates) if i not in used]
            if choices and min(choices)[0]<H*.01222:
                dist,i,c=min(choices,key=lambda q:q[0]);used.add(i);branch.append(c);next_active.append(branch)
            else:finished.append(branch)
        next_active.extend([c] for i,c in enumerate(candidates) if i not in used);active=next_active
    finished.extend(active)
    branches=[b for b in finished if len(b)>=4 and np.linalg.norm(np.array(b[-1]['centre'])-b[0]['centre'])>H*.008]
    branches.sort(key=lambda b:(-len(b),b[0]['centre'][0],b[0]['centre'][1]))
    result=[]
    for i,b in enumerate(branches):
        pts=[c['centre'] for c in b]
        result.append({'candidate_id':f'digit_branch_{i+1}_{side}','sample_count':len(b),'extent_cm':float(np.linalg.norm(np.array(pts[-1])-pts[0])),
            'ordered_surface_section_centres_cm':pts,'order':'distal to proximal; reversed by correction core',
            'status':'unnamed_surface_branch_requires_identity_and_root_tip_review','accepted':False})
    return result,slice_evidence

core=(P/'Working/Phase4D/core.py').read_text()
core=core.replace("W=P/'Working/Phase4D'; O=P/'Documentation/Phase4D'","W=P/'Working/Phase4F'; O=P/'Documentation/Phase4F'")
core=core.replace("tracks=read(P/'Documentation/Phase4B/finger_branch_prototype.json')['sides']","tracks=read(O/'finger_tracks.json')['sides']")
core=core.replace("read(P/'Documentation/Phase4C/solved_donor_joints.json')","read(O/'solved_donor_joints.json')")
core=core.replace("proposal['phase']='Phase4D'","proposal['phase']='Phase4F'").replace('correction-panel anatomical acceptance','native review-utility anatomical acceptance')
core += "\n\ndef configure(character):\n    global W,O\n    if character not in ['John','Jane']: raise ValueError('unknown Phase4F character')\n    W=P/'Working/Phase4F'/character; O=P/'Documentation/Phase4F'/character\n"
(W/'apose_review_core.py').write_text(core,encoding='utf-8')
spec=importlib.util.spec_from_file_location('apose_review_core',W/'apose_review_core.py');c=importlib.util.module_from_spec(spec);sys.modules['apose_review_core']=c;spec.loader.exec_module(c)
for character in ['John','Jane']:
    cw=W/character;co=O/character;co.mkdir(exist_ok=True)
    donor=json.loads((O/character/'solved_donor_joints.json').read_text());j={r['name']:r for r in donor['joints']}
    src=np.load(cw/'normalised_geometry.npz');v=src['vertices'];t=src['triangles']
    ue=json.loads((cw/'ue_target_geometry.json').read_text());uv=np.array(ue['vertices_cm']);ut=np.array(ue['triangle_indices']).reshape(-1,3)
    delta=float(np.linalg.norm(uv-v,axis=1).max()) if uv.shape==v.shape else None
    assert delta is not None and delta<.001,('Coordinate export mismatch',character,delta)
    save(co/'source_ue_comparison.json',{'indexwise_vertex_max_cm':delta,'blender_triangles':len(t),'ue_triangles':len(ut),
        'triangles_equal':bool(np.array_equal(t,ut)),'limit':'UE import drops degenerate source faces and triangulates independently; original polygon/UV arrays untouched. Native final surface preservation must be verified against UE original import as well.'})
    rows=[]
    for role,parent in schema():
        name={'spine_01':'spine_02','spine_02':'spine_04','spine_03':'spine_05'}.get(role,role);q=j[name]
        automatic=role in ['root','spine_01','spine_02','spine_03']
        flag='internal_articulation_not_certified_by_clothed_surface'
        if role.startswith('hand'):flag='donor_wrist_and_target_palm_transition_require_correspondence_review'
        if role.startswith(('foot','ball')):flag='boot_surface_hides_ankle_or_metatarsal_articulation'
        if role.startswith(('clavicle','upperarm')):flag='girdle_pivot_and_shirt_transition_require_review'
        if role in ['neck_01','head']:flag='neck_head_pivot_and_hair_envelope_require_review'
        rows.append({'role':role,'parent_role':parent,'position_cm':q['world_cm'],'side':'left' if role.endswith('_l') else 'right' if role.endswith('_r') else 'centre',
            'source_joint_name':name,'source_joint_index':q['index'],'confidence_score':.85 if automatic else .65,
            'confidence_score_kind':'Retained provisional evidence screen, not probability or human anatomical judgement',
            'ambiguity_flags':[] if automatic else [flag],'status':'automatically_accepted' if automatic else 'ambiguous',
            'evidence_sources':['Character-local actual solved DNA; two public extraction APIs agree','Retained 4D hierarchy contraction and review policy'],
            'competing_candidates':[],'manual_correction':None})
    proposal={'character':character,'height_cm':180,'method':'Established MetaHuman donor initial proposal plus guided review; character-local solved positions',
        'joints':rows,'input_geometry_sha256':sha(cw/'normalised_geometry.npz'),'donor_sha256':sha(cw/'Donor'/f'{character}_Posed.dna'),
        'prior_character_coordinates_used':False,'downstream_authorised':False,'human_review_count':0}
    save(co/'automatic_starting_proposal.json',proposal);save(co/'solved_donor_joints.json',donor)
    assert (co/'coordinate_frame.json').is_file()
    branch={};evidence={}
    for side in ['l','r']:branch[side],evidence[side]=tracks(v,t,side)
    save(co/'finger_tracks.json',{'method':'Retained section-component track architecture, A-pose slices along Z from actual character-local hand extent to surface wrist proxy; geometric branches remain unnamed.',
        'sides':branch,'slice_evidence':evidence,'named_chains_accepted':0,'prior_character_tracks_used':False})
    c.configure(character)
    if not (cw/'session.json').exists():c.export(c.rebuild(c.fresh_state()))
    # Isolated copies retain all numeric thresholds and human-review provenance checks.
    inherited=(P/'Working/Phase4D/inherited_validate.py').read_text().replace("parents[2];W=P/'Working/Phase4D';O=P/'Documentation/Phase4D'",f"parents[3];W=P/'Working/Phase4F/{character}';O=P/'Documentation/Phase4F/{character}'")
    # A child-directory validator must still find the read-only geometry library in the project root.
    inherited=inherited.replace("Path(__file__).resolve().parents[2]/'Working/Phase4B'","Path(__file__).resolve().parents[3]/'Working/Phase4B'")
    (cw/'inherited_validate.py').write_text(inherited,encoding='utf-8')
    validate=(P/'Working/Phase4D/validate.py').read_text()
    validate=validate.replace("sys.path.insert(0,str(Path(__file__).resolve().parent))", "sys.path.insert(0,str(Path(__file__).resolve().parent.parent))")
    validate=validate.replace('import core',f"import apose_review_core as core\ncore.configure('{character}')")
    validate=validate.replace("phase='Phase4D'","phase='Phase4F'")
    validate=validate.replace("'evidence':'Parent X=0.6902815699577332; right clavicle relative X=-0.6232463121414185; left=0.7635632157325745; bilateral upper arms remain correctly separated'","'evidence':'Retained Phase4D parent-relative clavicle convention; current character values in left_right_not_crossed check'")
    (cw/'validate.py').write_text(validate,encoding='utf-8')
    print(character,'donor',[(r['role'],[round(x,2) for x in r['position_cm']]) for r in rows], 'branches',[(s,len(branch[s]),[round(t['extent_cm'],2) for t in branch[s]]) for s in branch],flush=True)
save(O/'APoseContinuation/budget_consumption.json',{'semantic_passes':{'John':1,'Jane':1,'Lara':0},'John_pass1':'Source-verified actual solve and two-API extraction','Jane_pass1':'Source-verified actual solve and two-API extraction','skin_candidates':{'Lara':0,'John':0,'Jane':0},'remaining_semantic_passes':{'John':2,'Jane':2}})
