from model import *
from PIL import Image,ImageDraw,ImageFont
m=Model();selected=m.dense(load(W/'selected_weights.json'));fit=load(P/'Documentation/Phase4D/current_proposal.json');chains=fit['finger_chains'];digits=list(chains)
dist=np.stack([np.linalg.norm(m.v[:,None,:]-np.array(chains[k]['path_cm'])[None,:,:],axis=2).min(1) for k in digits],axis=1);nearest=dist.argmin(1);groups={k:np.flatnonzero((nearest==i)&(dist[:,i]<.9)) for i,k in enumerate(digits)}
def finger_results(w):
    rows=[]
    for s in m.fingers:
        active=s['active_digit']
        if not active:continue
        pose=m.from_sample(s);out=m.deform(w,pose);ix=groups[active];d,side=active.split('_');ids=[m.bi[f'{d}_0{i}_{side}'] for i in [1,2,3]];points=pose[ids,:3,3]
        support=float(np.linalg.norm(points[:,None,:]-out[ix][None,:,:],axis=2).min(1).max())
        rows.append({'digit':active,'support_cm':support,'own_chain_mean':float(w[ix][:,ids].sum(1).mean()),'vertices':len(ix),'support_under_1_2':support<=1.2})
    return rows
def segment_distance(points,a,b):
    ab=b-a;t=np.clip(((points-a)@ab)/(ab@ab),0,1);return np.linalg.norm(points-(a+t[:,None]*ab),axis=1),t
proposed=selected.copy()
for k in digits:
    digit,side=k.split('_');ids=[m.bi[f'{digit}_0{i}_{side}'] for i in [1,2,3]];ix=groups[k];points=np.vstack([m.pos[ids],chains[k]['tip_cm']]);raw=[]
    for a,b in zip(points,points[1:]):raw.append(segment_distance(m.v[ix],a,b)[0])
    ds=np.stack(raw,axis=1);dw=1/np.maximum(ds,.2)**4;dw/=dw.sum(1)[:,None]
    # Human-accepted chain supplies identity, not a new geometric correspondence solve.
    along=segment_distance(m.v[ix],points[0],points[-1])[1];hand=1-smoothstep(.02,.28,along)
    target=np.zeros((len(ix),len(m.names)));target[:,ids]=dw*(1-hand[:,None]);target[:,m.bi['hand_'+side]]=hand
    strength=.8*(1-smoothstep(.65,.9,dist[ix,digits.index(k)]));proposed[ix]=(1-strength[:,None])*selected[ix]+strength[:,None]*target
proposed=m.pack(proposed);finger_compare={'baseline':finger_results(m.weights),'body_refined':finger_results(selected),'track_segment_refined':finger_results(proposed)}
save('finger_weight_experiment.json',{'method':'Accepted-track segment inverse-distance weighting, hand-root fade, bounded 0.8 blend; no bone movement','results':finger_compare,'natural_thumb_opposition':'Not established by independent local-Z fixture; a separate two-axis opposition fixture is required','semantic_identity_unchanged':True,'chain_positions_unchanged':True})
print('Finger support',[(n,[(r['digit'],round(r['support_cm'],3)) for r in rs]) for n,rs in finger_compare.items()])
# Retain only if all originally passing support screens remain passing and failed ring improves.
old={r['digit']:r for r in finger_compare['body_refined']};new={r['digit']:r for r in finger_compare['track_segment_refined']};accept=all(new[k]['support_cm']<=1.2 for k in old if old[k]['support_cm']<=1.2) and new['ring_r']['support_cm']<old['ring_r']['support_cm']
if accept:
    (W/'selected_weights.json').write_text(json.dumps(m.rows(proposed)));selected=proposed
save('finger_candidate_decision.json',{'accepted':accept,'reason':'Requires no previously passing support-screen regression plus right-ring improvement','limitations':'Sparse support is not natural flexion/volume/collision acceptance'})
contact=load(O/'contact_ue_experiment.json');measured={}
for label,samples,w in [('Phase4D',m.samples,m.weights),('weights_only',m.samples,selected),('UE_FloorConstraint',contact.get('samples',[]),selected)]:
    summaries=[]
    for role in ['idle','walk','run']:
        seq=[s for s in samples if s['role']==role];rows=[]
        for s in seq:
            out=m.deform(w,m.from_sample(s));rows.append({'time_s':s['time_s'],'left_min_z':float(out[m.regions['left_sole'],2].min()),'right_min_z':float(out[m.regions['right_sole'],2].min())})
        if rows:summaries.append({'role':role,'max_penetration_cm':max(0,-min(min(r['left_min_z'],r['right_min_z']) for r in rows)),'left_range':[min(r['left_min_z'] for r in rows),max(r['left_min_z'] for r in rows)],'right_range':[min(r['right_min_z'] for r in rows),max(r['right_min_z'] for r in rows)],'samples':rows})
    measured[label]=summaries
save('contact_comparison.json',{'method':'Actual saved weights + original/UE FloorConstraint baked poses; same original sole masks; actor origin remains zero','results':measured,'limits':'Floor constraint is a penetration/contact authoring experiment; no world locomotion, terrain adaptation or planted speed curves'});print('Contact',[(k,[(r['role'],round(r['max_penetration_cm'],4)) for r in rs]) for k,rs in measured.items()])
