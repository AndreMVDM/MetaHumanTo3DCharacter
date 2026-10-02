from fingers_contact_analysis import *
result={}
for name in ['direct_02_5','direct_08_4','geo256_02_5','geo256_06_4','geo128_08_4','geo128_02_8']:
    w=m.dense(load(W/(name+'_weights.json')));result[name]=finger_results(w);print(name,[(r['digit'],round(r['support_cm'],3)) for r in result[name]],flush=True)
save('finger_binding_controls.json',result)
# Bind alone is selected only when every digit support screen passes.
valid=[n for n,rs in result.items() if all(r['support_cm']<=1.2 for r in rs)]
if valid:
    name=min(valid,key=lambda n:max(r['support_cm'] for r in result[n]));raw=m.dense(load(W/(name+'_weights.json')));w=m.dense(load(W/'selected_weights.json'))
    for s in ['l','r']:
        hand=m.pos[m.bi['hand_'+s]];distance=np.linalg.norm(m.v-hand,axis=1);alpha=1-smoothstep(9,15,distance);w=(1-alpha[:,None])*w+alpha[:,None]*raw
    w=m.pack(w,max_influences=8);rows=finger_results(w)
    if all(r['support_cm']<=1.2 for r in rows):
        (W/'selected_weights.json').write_text(json.dumps(m.rows(w)));save('finger_candidate_decision.json',{'accepted':True,'selected':name,'results':rows,'method':'Skeleton-relative hand envelope blends UE binder; accepted semantic correspondence unchanged','natural_thumb_opposition':'unproven'})
    else:save('finger_candidate_decision.json',{'accepted':False,'selected':name,'results':rows,'reason':'Local blending reintroduced support regression'})
