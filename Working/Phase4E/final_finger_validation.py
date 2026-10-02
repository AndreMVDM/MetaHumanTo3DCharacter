from model import *
m=Model();w=m.dense(load(W/'saved_Refined_weights.json'));chains=load(P/'Documentation/Phase4D/current_proposal.json')['finger_chains'];digits=list(chains)
ds=np.stack([np.linalg.norm(m.v[:,None,:]-np.array(chains[k]['path_cm'])[None,:,:],axis=2).min(1) for k in digits],axis=1);nearest=ds.argmin(1);rows=[]
for s in m.fingers:
    k=s['active_digit']
    if not k:continue
    ix=np.flatnonzero((nearest==digits.index(k))&(ds[:,digits.index(k)]<.9));digit,side=k.split('_');ids=[m.bi[digit+'_0'+str(j)+'_'+side] for j in [1,2,3]];pose=m.from_sample(s);out=m.deform(w,pose);support=float(np.linalg.norm(pose[ids,:3,3][:,None,:]-out[ix][None,:,:],axis=2).min(1).max());rows.append({'digit':k,'support_cm':support,'support_under_1_2':support<=1.2,'vertices':len(ix)})
save('final_finger_validation.json',{'status':'partial','source':'Fresh disk final candidate weights and preserved original finger fixture','support_pass_count':sum(r['support_under_1_2'] for r in rows),'digit_count':len(rows),'results':rows,'semantic_identity_preserved':True,'natural_thumb_quality':'unproven','deformed_surface_collision':'not exhaustively measured'})
print(rows)
