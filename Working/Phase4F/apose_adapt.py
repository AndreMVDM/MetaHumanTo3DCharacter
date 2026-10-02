"""Create isolated adaptations; original Bill/Jill scripts remain byte-identical."""
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F'
def adapt(source,dest,replacements):
    text=(W/source).read_text(encoding='utf-8')
    for old,new in replacements:
        assert old in text,(source,old)
        text=text.replace(old,new)
    (W/dest).write_text(text,encoding='utf-8')
adapt('inspect_geometry.py','apose_inspect_geometry.py',[
    ("['Lara','Bill','Jill']","['John','Jane']"),
    ("W/'Inputs'/character","W/character/'Input'"),
    ("O/f'{character.lower()}_geometry_summary.json'","O/character/'geometry_summary.json'")])
adapt('prepare_sources.py','apose_prepare_sources.py',[
    ("(['Bill'] if '--bill-only' in sys.argv else ['Lara','Bill','Jill'])","['John','Jane']"),
    ("O/f'{character.lower()}_coordinate_frame.json'","O/character/'coordinate_frame.json'"),
    ("O/f'{character.lower()}_source_{name}.png'","O/character/f'source_{name}.png'"),
    ("if character=='Bill': facing=-1","if character in ['John','Jane']: facing=-1"),
    ("Bill: initial toe heuristic rejected by textured face/buckle images; -Y verified. Others: source textured front agrees with heuristic. No joint anatomical approval.","A-pose continuation: -Y facing must be verified from source front/back renders BEFORE fitting. No anatomical approval.")])
adapt('ue_proposals.py','apose_ue_proposals.py',[
    ("['Bill','Jill']","['John','Jane']"),
    ("save('automatic_proposal_execution.json',results)","save('APoseContinuation/automatic_proposal_execution.json',results)"),
    ("character.lower()+'_solved_donor_joints.json'","character+'/solved_donor_joints.json'")])
adapt('prepare_review.py','apose_prepare_review.py',[
    ("['Bill','Jill']","['John','Jane']"),
    ("review_core","apose_review_core"),
    ("O/(character.lower()+'_solved_donor_joints.json')","O/character/'solved_donor_joints.json'"),
    ("shutil.copyfile(O/(character.lower()+'_coordinate_frame.json'),co/'coordinate_frame.json')","assert (co/'coordinate_frame.json').is_file()"),
    ("save(O/'budget_consumption.json'","save(O/'APoseContinuation/budget_consumption.json'"),
    ("'Bill':2,'Jill':1,'Lara':0","'John':1,'Jane':1,'Lara':0"),
    ("'Bill_pass1':'Frame-rejected aborted donor solve; retained failed import and execution log; no anatomy accepted',\n    'Bill_pass2':'Frame-verified actual solve and two-API extraction','Jill_pass1':'Actual solve and two-API extraction'","'John_pass1':'Source-verified actual solve and two-API extraction','Jane_pass1':'Source-verified actual solve and two-API extraction'"),
    ("'Lara':0,'Bill':0,'Jill':0","'Lara':0,'John':0,'Jane':0"),
    ("'Bill':1,'Jill':2","'John':2,'Jane':2")])
# A-pose finger sections run up Z from actual hand lower extent, retaining
# neighbouring section connectivity and independent, unnamed branches.
p=W/'apose_prepare_review.py';text=p.read_text()
start=text.index('def tracks(');end=text.index('\ncore=',start)
text=text[:start]+'''def tracks(v,t,side):
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
''' +text[end:]
text=text.replace('slices along outward T-pose arm axis X rather than A-pose Z','A-pose slices along Z from actual character-local hand extent to surface wrist proxy')
p.write_text(text,encoding='utf-8')
adapt('ue_review.py','apose_ue_review.py',[
    ("['Bill','Jill']","['John','Jane']"),
    ("import review_core as core","import apose_review_core as core"),
    ("/ReviewMaterials/","/APoseReviewMaterials/"),
    ("B+'/ReviewMaterials'","B+'/APoseReviewMaterials'"),
    ("review_agent_request.json","apose_review_agent_request.json"),
    ("review_agent_response.json","apose_review_agent_response.json")])
adapt('render_review_evidence.py','apose_render_review_evidence.py',[
    ("['Bill','Jill']","['John','Jane']"),
    ("O/(character.lower()+'_geometry_summary.json')","O/character/'geometry_summary.json'"),
    ("O/(character.lower()+'_coordinate_frame.json')","O/character/'coordinate_frame.json'")])
adapt('ue_verify_reviews.py','apose_ue_verify_reviews.py',[
    ("['Bill','Jill']","['John','Jane']"),
    ("O/'native_review_fresh_readback.json'","O/'APoseContinuation/native_review_fresh_readback.json'")])
