"""Standard-library correction engine, shared by UE and offline validation.

No Phase4A coordinates are imported. UI events are explicit, immutable records;
preview movement is not a human anatomical approval.
"""
import copy, hashlib, json, math, time, uuid
from pathlib import Path
P=Path(__file__).resolve().parents[2]; W=P/'Working/Phase4F'; O=P/'Documentation/Phase4F'
DIGITS=('thumb','index','middle','ring','pinky')
LABELS={'pelvis':'Pelvis centre','upperarm_l':'Left shoulder pivot','upperarm_r':'Right shoulder pivot','lowerarm_l':'Left elbow','lowerarm_r':'Right elbow','hand_l':'Left wrist','hand_r':'Right wrist','calf_l':'Left knee','calf_r':'Right knee','foot_l':'Left ankle','foot_r':'Right ankle','ball_l':'Left ball / toe','ball_r':'Right ball / toe','neck_01':'Neck base','head':'Head pivot','thigh_l':'Left hip (optional)','thigh_r':'Right hip (optional)','clavicle_l':'Left clavicle root (advanced)','clavicle_r':'Right clavicle root (advanced)'}
GROUPS={'Pelvis / hips / lower spine':['pelvis','thigh_l','thigh_r','spine_01','spine_02','spine_03'], 'Left shoulder / clavicle':['upperarm_l','clavicle_l'], 'Right shoulder / clavicle':['upperarm_r','clavicle_r'], 'Neck / head':['neck_01','head']}
def add(a,b): return [x+y for x,y in zip(a,b)]
def sub(a,b): return [x-y for x,y in zip(a,b)]
def mul(a,s): return [x*s for x in a]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a): return math.sqrt(dot(a,a))
def unit(a):
    n=norm(a)
    if n<1e-8: raise ValueError('zero-length segment')
    return mul(a,1/n)
def xyz(a):
    if len(a)!=3 or any(isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) for x in a): raise ValueError('finite XYZ required')
    if norm(a)>540: raise ValueError('point outside 3x stature')
    return list(map(float,a))
def canonical(data): return json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(data): return hashlib.sha256(canonical(data)).hexdigest()
def file_sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p,data):
    p.parent.mkdir(parents=True,exist_ok=True); tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        tmp.write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')
        # Tk reads the heartbeat frequently. Windows can briefly deny atomic
        # replacement while that read handle is open; retain atomic publication.
        for attempt in range(6):
            try:tmp.replace(p);return
            except PermissionError:
                if attempt==5:raise
                time.sleep(.01)
    finally:
        if tmp.exists():tmp.unlink()
def signature(r): return digest({'position_cm':r['position_cm'],'ambiguity_flags':r['ambiguity_flags']})
def track_points(track):
    # 4B target tracks are ascending in Z, from distal end towards palm.
    return list(reversed(track['ordered_surface_section_centres_cm']))
def path_sample(points,fraction):
    lengths=[norm(sub(b,a)) for a,b in zip(points,points[1:])]; total=sum(lengths)
    if total<.001: raise ValueError('collapsed digit track')
    distance=max(0,min(1,fraction))*total
    for a,b,length in zip(points,points[1:],lengths):
        if distance<=length: return add(a,mul(sub(b,a),distance/length))
        distance-=length
    return points[-1]
def finger_path(track,root,tip):
    points=track_points(track); root=xyz(root); tip=xyz(tip)
    # Preserve geometric curvature; blend endpoint deltas along arc length.
    lengths=[0.]
    for a,b in zip(points,points[1:]): lengths.append(lengths[-1]+norm(sub(b,a)))
    if lengths[-1]<.001: raise ValueError('collapsed track')
    dr=sub(root,points[0]);dt=sub(tip,points[-1])
    return [add(p,add(mul(dr,1-d/lengths[-1]),mul(dt,d/lengths[-1]))) for p,d in zip(points,lengths)]
def axes(joints):
    rows={r['role']:r for r in joints}; children={n:[] for n in rows}; result={}
    for n,r in rows.items():
        if r['parent_role']: children[r['parent_role']].append(n)
    # Child selection is explicitly axial for pelvis/spine, rather than arbitrary branching.
    preference={'root':'pelvis','pelvis':'spine_01','spine_01':'spine_02','spine_02':'spine_03','spine_03':'neck_01','neck_01':'head'}
    for n,r in rows.items():
        if children[n]:
            child=preference.get(n,children[n][0]); x=unit(sub(rows[child]['position_cm'],r['position_cm'])); y=cross([0,0,1],x)
            if norm(y)<.05: y=cross([0,1,0],x)
            y=unit(y);z=cross(x,y);result[n]={'aim_x':x,'y':y,'z':z,'primary_child':child}
        else:
            result[n]=copy.deepcopy(result[r['parent_role']]);result[n].pop('primary_child',None)
        if r['parent_role'] and norm(sub(r['position_cm'],rows[r['parent_role']]['position_cm']))<.001: raise ValueError('zero-length parent segment')
    return result
def local_transforms(joints,world_axes):
    rows={r['role']:r for r in joints};result={}
    columns=lambda a:[a['aim_x'],a['y'],a['z']]
    for n,r in rows.items():
        parent=r['parent_role'];parentcols=columns(world_axes[parent]) if parent else [[1,0,0],[0,1,0],[0,0,1]]
        delta=sub(r['position_cm'],rows[parent]['position_cm']) if parent else r['position_cm']
        localcols=[[dot(a,b) for a in parentcols] for b in columns(world_axes[n])]
        result[n]={'translation_cm':[dot(a,delta) for a in parentcols],'rotation_matrix_columns':localcols,'scale':[1,1,1]}
    return result
def fresh_state():
    baseline=read(O/'automatic_starting_proposal.json'); tracks=read(O/'finger_tracks.json')['sides']
    return {'schema_version':1,'baseline_sha256':file_sha(O/'automatic_starting_proposal.json'),'session_id':str(uuid.uuid4()),'joints':copy.deepcopy(baseline['joints']),'body_overrides':{},'tracks':tracks,'fingers':{},'approvals':{},'events':[],'trial_started_at':None,'trial_finished_at':None,'downstream_authorised':False}
def rebuild(state):
    reviewed_fingers={n:copy.deepcopy(state['fingers'][n]) for n,a in state['approvals'].items() if n in state['fingers'] and a['signature']==review_signature(state,n)}
    base=read(O/'automatic_starting_proposal.json'); rows={r['role']:copy.deepcopy(r) for r in base['joints']}; orig={n:r['position_cm'][:] for n,r in rows.items()}; overrides=state['body_overrides']
    for n,p in overrides.items():
        if n not in rows or n=='root': raise ValueError('unknown or grounded role override')
        rows[n]['position_cm']=xyz(p);rows[n]['status']='manually_corrected'
    dependencies={}
    if 'pelvis' in overrides:
        delta=sub(overrides['pelvis'],orig['pelvis'])
        for i in range(1,4): dependencies[f'spine_{i:02}']=('pelvis',mul(delta,1-i/4),'lower-spine blend, upper anchor retained')
        for side in ['l','r']: dependencies['thigh_'+side]=('pelvis',delta,'retain independent donor hip offset')
    for side in ['l','r']:
        n='upperarm_'+side
        if n in overrides:
            dependencies['clavicle_'+side]=(n,mul(sub(overrides[n],orig[n]),.48),'retain 4B shoulder-girdle propagation factor; pivot convention still reviewed')
    for n,(source,delta,rule) in dependencies.items():
        if n in overrides: continue
        rows[n]['position_cm']=add(orig[n],delta);rows[n]['status']='dependency_recomputed';rows[n]['dependency_recomputation']={'from':source,'rule':rule}
        if norm(delta)>.000001: rows[n]['ambiguity_flags']=sorted(set(rows[n]['ambiguity_flags']+['dependency_moved_position_requires_anatomical_review']))
    state['joints']=list(rows.values());state['axes']=axes(state['joints']);state['poles']={}
    for side in ['l','r']:
        for kind,names in [('arm',['upperarm','lowerarm','hand']),('leg',['thigh','calf','foot'])]:
            a,b,c=[rows[n+'_'+side]['position_cm'] for n in names]; ac=sub(c,a); fraction=dot(sub(b,a),ac)/dot(ac,ac); bend=sub(b,add(a,mul(ac,fraction)))
            state['poles'][kind+'_'+side]={'bend_vector_cm':bend,'bend_distance_cm':norm(bend),'plane_normal':unit(cross(sub(b,a),sub(c,b))) if norm(cross(sub(b,a),sub(c,b)))>.00001 else None}
    for key,f in state['fingers'].items():
        points=finger_path(next(t for t in state['tracks'][f['side']] if t['candidate_id']==f['track_id']),f['root_cm'],f['tip_cm']);f['path_cm']=points
        donor=read(O/'solved_donor_joints.json'); donorrows={r['name']:r for r in donor['joints']}; donorpoints=[donorrows[f"{f['digit']}_0{i}_{f['side']}"]['world_cm'] for i in [1,2,3]]
        lengths=[norm(sub(b,a)) for a,b in zip(donorpoints,donorpoints[1:])]; end=lengths[-1]*.65;total=sum(lengths)+end
        fractions=[0,lengths[0]/total,sum(lengths)/total];f['phalanges_cm']=[path_sample(points,u) for u in fractions];f['donor_length_fractions']=fractions
        f['ambiguity_flags']=['track_identity_and_root_tip_require_human_review','section_track_may_be_partial','phalange_interpolation_requires_review']
        recorded=reviewed_fingers.get(key)
        # CPython/UE summation differs by a few ULPs. Retain the exact accepted
        # derived coordinates only when every input and all other fields match.
        # Real endpoint/track changes still invalidate the exact review signature.
        if recorded and all(recorded[k]==f[k] for k in f if k!='phalanges_cm') and len(recorded['phalanges_cm'])==len(f['phalanges_cm']) and max(norm(sub(a,b)) for a,b in zip(recorded['phalanges_cm'],f['phalanges_cm']))<=1e-10:
            f['phalanges_cm']=copy.deepcopy(recorded['phalanges_cm'])
    # Revalidation is bound to final positions: dependent changes invalidate earlier approvals.
    state['approvals']={n:a for n,a in state['approvals'].items() if a['signature']==review_signature(state,n)}
    expanded=copy.deepcopy(state['joints'])
    for key,f in state['fingers'].items():
        for i,p in enumerate(f['phalanges_cm']):expanded.append({'role':f"{f['digit']}_0{i+1}_{f['side']}",'parent_role':'hand_'+f['side'] if i==0 else f"{f['digit']}_0{i}_{f['side']}",'position_cm':p})
    state['generated_joint_schema']=expanded;state['generated_axes']=axes(expanded);state['local_transforms']=local_transforms(expanded,state['generated_axes'])
    state['downstream_authorised']=False
    return state
def review_signature(state,n):
    if n in state['fingers']: return digest(state['fingers'][n])
    return signature(next(r for r in state['joints'] if r['role']==n))
def append_event(state,kind,details,provenance='human_editor_action'):
    event={'id':len(state['events'])+1,'utc_epoch':time.time(),'kind':kind,'provenance':provenance,'details':details}
    state['events'].append(event);return event
def command(state,cmd,provenance='human_editor_action'):
    if state['baseline_sha256']!=file_sha(O/'automatic_starting_proposal.json'): raise ValueError('stale baseline')
    s=copy.deepcopy(state); action=cmd['action']; detail=copy.deepcopy(cmd)
    if s['trial_finished_at'] is not None and action in ['move','assign','review','finish']:
        raise ValueError('Trial is finished. Start / resume it before further corrections or reviews.')
    if action=='start':
        if s['trial_started_at'] is not None and s['trial_finished_at'] is None: raise ValueError('trial already started')
        if s['trial_started_at'] is None: s['trial_started_at']=time.time()
        s['trial_finished_at']=None
    elif action=='move':
        if s['trial_started_at'] is None: raise ValueError('Start trial before recording placements')
        moves=cmd['positions'];detail['moves']=[]
        for n,p in moves.items():
            p=xyz(p)
            if n in s['fingers'] or n.endswith((':root',':tip')):
                key,endpoint=n.rsplit(':',1);f=s['fingers'][key]; old=f[endpoint+'_cm'];f[endpoint+'_cm']=p
            else:
                old=next(r['position_cm'] for r in s['joints'] if r['role']==n);s['body_overrides'][n]=p
            detail['moves'].append({'landmark':n,'from_cm':old,'to_cm':p,'distance_cm':norm(sub(p,old))})
        rebuild(s)
    elif action=='assign':
        if s['trial_started_at'] is None: raise ValueError('Start trial before identifying digits')
        side=cmd['side'];digit=cmd['digit'];tid=cmd['track_id']
        if side not in ['l','r'] or digit not in DIGITS: raise ValueError('invalid side/digit')
        if any(f['track_id']==tid and k!=digit+'_'+side for k,f in s['fingers'].items()): raise ValueError('track already assigned; each digit must have a distinct track')
        track=next(t for t in s['tracks'][side] if t['candidate_id']==tid);pts=track_points(track)
        s['fingers'][digit+'_'+side]={'side':side,'digit':digit,'track_id':tid,'root_cm':pts[0],'tip_cm':pts[-1]}; rebuild(s)
    elif action=='review':
        if s['trial_started_at'] is None: raise ValueError('Start trial before anatomical review')
        if cmd.get('judgement') not in ['accept','unresolved']: raise ValueError('explicit judgement required')
        if not cmd.get('category'): raise ValueError('disagreement classification required')
        detail['reviewed_positions']={}
        for n in cmd['roles']:
            sig=review_signature(s,n)
            detail['reviewed_positions'][n]=copy.deepcopy(s['fingers'][n] if n in s['fingers'] else next(r['position_cm'] for r in s['joints'] if r['role']==n))
            if cmd['judgement']=='accept': s['approvals'][n]={'signature':sig,'category':cmd['category'],'event_id':len(s['events'])+1,'provenance':provenance}
            else: s['approvals'].pop(n,None)
    elif action=='finish':
        if s['trial_started_at'] is None: raise ValueError('trial has not started')
        s['trial_finished_at']=time.time()
    else: raise ValueError('unknown correction command')
    append_event(s,action,detail,provenance);return s
def metrics(s):
    events=[e for e in s['events'] if e['provenance']=='human_editor_action']; moves=[m for e in events if e['kind']=='move' for m in e['details']['moves'] if m['distance_cm']>1e-6]; reviewed={n for e in events if e['kind']=='review' for n in e['details']['roles']}; moved={m['landmark'] for m in moves}
    # A chain is moved when either endpoint moved; avoid counting its later
    # acceptance as an unchanged review merely because keys differ.
    moved_review_roles=moved | {n.split(':')[0] for n in moved if ':' in n}
    base={'navigation_commands':sum(e['kind'] in ['select','view','overlay','preview_track'] for e in events),'automatically_accepted_roles':[r['role'] for r in s['joints'] if r['status']=='automatically_accepted'],'currently_accepted_human_roles':sorted(n for n,a in s['approvals'].items() if a['provenance']=='human_editor_action'),'reviewed_without_movement':[n for n in sorted(reviewed) if n not in moved_review_roles and n in s['approvals'] and s['approvals'][n]['provenance']=='human_editor_action']}
    return {'trial_status':'awaiting_human_review' if s['trial_started_at'] is None else ('finished' if s['trial_finished_at'] else 'in_progress'),'recorded_user_commands':len(events),'placement_commands':sum(e['kind']=='move' for e in events),'digit_identification_commands':sum(e['kind']=='assign' for e in events),'review_commands':sum(e['kind']=='review' for e in events),'landmarks_reviewed':len(reviewed),**base,'landmarks_actually_moved':len(moved),'body_landmarks_moved':sorted(n for n in moved if ':' not in n),'finger_landmarks_moved':sorted(n for n in moved if ':' in n),'total_moved_distance_cm':sum(m['distance_cm'] for m in moves),'maximum_individual_move_cm':max([m['distance_cm'] for m in moves],default=0),'grouped_correction_commands':sum(e['kind']=='move' and len(e['details']['moves'])>1 for e in events),'unresolved_body_roles':[r['role'] for r in s['joints'] if r['status']!='automatically_accepted' and r['role'] not in s['approvals']],'unresolved_finger_chains':[d+'_'+side for side in ['l','r'] for d in DIGITS if d+'_'+side not in s['approvals']],'elapsed_trial_seconds':s['trial_finished_at']-s['trial_started_at'] if s['trial_finished_at'] else None,'raw_mouse_clicks_or_drag_gestures':None,'metric_definition':'Explicit panel commands and recorded placements; navigation clicks and unrecorded exploratory drags are not measured. Zero performed is not zero required; time is measured only Start to Finish and includes pauses.'}
def export(s):
    proposal=read(O/'automatic_starting_proposal.json');proposal['joints']=copy.deepcopy(s['joints']);proposal['phase']='Phase4F';proposal['baseline_sha256']=s['baseline_sha256'];proposal['recomputed_axes']=s['generated_axes'];proposal['generated_joint_schema']=s['generated_joint_schema'];proposal['recomputed_local_transforms']=s['local_transforms'];proposal['limb_poles']=s['poles'];proposal['finger_chains']=s['fingers'];proposal['downstream_authorised']=False
    save(W/'session.json',s);save(O/'current_proposal.json',proposal)
    artifacts={}
    for event in s['events']:
        path=W/'InteractionEvidence'/f"event_{event['id']:05}.json"
        if path.exists() and read(path)!=event: raise ValueError('immutable event changed')
        if not path.exists(): save(path,event)
        artifacts[event['id']]=path
    review={'proposal_sha256':file_sha(O/'current_proposal.json'),'provenance_kind':'human_anatomical_review','roles':{},'fingers':{}}
    for n,a in s['approvals'].items():
        if a['provenance']!='human_editor_action' or a['signature']!=review_signature(s,n): continue
        path=artifacts[a['event_id']]; evidence={'anatomical_valid':True,'method':'Explicit native review-utility anatomical acceptance after front/side inspection','evidence_artifact':str(path),'evidence_sha256':file_sha(path),'event_id':a['event_id'],'category':a['category']}
        if n in s['fingers']: review['fingers'][n]=dict(evidence,chain_sha256=digest(s['fingers'][n]))
        else:
            r=next(r for r in s['joints'] if r['role']==n);review['roles'][n]=dict(evidence,position_cm=r['position_cm'],resolved_ambiguity_flags=r['ambiguity_flags'])
    save(O/'human_review.json',review);save(O/'correction_metrics.json',metrics(s));save(O/'actual_correction_list.json',{'events':s['events'],'human_approval_not_fabricated':True})
    return proposal


def configure(character):
    global W,O
    if character not in ['Bill','Jill']: raise ValueError('unknown Phase4F character')
    W=P/'Working/Phase4F'/character; O=P/'Documentation/Phase4F'/character
