from model import *
m=Model();w=m.weights;choices={'baseline':w}
root=w.copy();root[:,m.bi['pelvis']]+=root[:,m.bi['root']];root[:,m.bi['root']]=0;choices['root_to_pelvis']=root
choices['smooth_global']=m.smoothing(w,4,.4)
for ps,ss in [(1,0),(0,1),(.6,.6),(1,1)]:
    choices[f'semantic_{ps}_{ss}']=m.semantic_refine(w,ps,ss)
choices['semantic_smooth']=m.smoothing(choices['semantic_1_1'],3,.3,mask=m.regions['front_pants']|m.regions['back_hips']|m.regions['shoulders'])
for p in W.glob('*_weights.json'):
    if p.name in ['selected_weights.json']:continue
    choices[p.stem.removesuffix('_weights')]=m.dense(load(p))
result={};poses={k:p for k,p in m.poses.items() if not k.startswith('finger_')}
for name,weights in choices.items():
    per={n:m.measure(weights,pose) for n,pose in poses.items()}
    score={r:float(np.mean([p[r]['edge_log_strain_rms'] for n,p in per.items() if n!='neutral'])) for r in ['front_pants','back_hips','shoulders','upper_torso']}
    result[name]={'scores':score,'poses':per,'reference_max_error_cm':float(np.max(np.linalg.norm(m.deform(weights,m.ref)-m.v,axis=1))),'weights_stats':{'max_influences':int((weights>0).sum(1).max()),'normalisation_error':float(abs(weights.sum(1)-1).max())}}
    print(name,{k:round(v,4) for k,v in score.items()},flush=True)
save('candidate_comparison.json',result)
for name in ['root_to_pelvis','semantic_1_1','semantic_smooth']:(W/(name+'_weights.json')).write_text(json.dumps(m.rows(choices[name])))
# A measured preliminary choice. Native/visual review may supersede it.
selected='semantic_1_1';(W/'selected_weights.json').write_text(json.dumps(m.rows(choices[selected])));save('candidate_selection.json',{'selected':selected,'status':'pending_visual_and_native_review','reason':'Root exclusion + semantic pelvis/shoulder envelopes; no bone/geometry change','bounded_candidates':list(choices)})
