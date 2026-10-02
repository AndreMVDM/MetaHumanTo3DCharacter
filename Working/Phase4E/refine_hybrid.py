from model import *
from render import compare
m=Model();base=m.semantic_refine(m.weights,1,0);v=m.v;p=m.pos;bi=m.bi
z=smoothstep(p[bi['spine_02'],2]-4,p[bi['spine_02'],2]+6,v[:,2])*(1-smoothstep(p[bi['neck_01'],2]-1,p[bi['neck_01'],2]+5,v[:,2]))
near=np.minimum(np.linalg.norm(v-p[bi['upperarm_l']],axis=1),np.linalg.norm(v-p[bi['upperarm_r']],axis=1))
blend=z*(1-smoothstep(24,38,near))
choices={'baseline':m.weights,'semantic_smooth':m.dense(load(W/'semantic_smooth_weights.json'))}
for n in ['direct_02_5','direct_08_4','geo256_02_5','geo256_06_4']:
    raw=m.dense(load(W/(n+'_weights.json')));raw=m.semantic_refine(raw,0,0)
    hybrid=m.pack((1-blend[:,None])*base+blend[:,None]*raw)
    choices['hybrid_'+n]=hybrid
results={}
for name,w in choices.items():
    per={n:m.measure(w,pose) for n,pose in m.poses.items() if not n.startswith('finger_')}
    results[name]={'poses':per,'score':{r:float(np.mean([p[r]['edge_log_strain_rms'] for n,p in per.items() if n!='neutral'])) for r in ['front_pants','back_hips','shoulders','upper_torso']}}
    print(name,results[name]['score'],flush=True)
save('hybrid_comparison.json',results)
compare(m,{k:choices[k] for k in ['baseline','hybrid_direct_02_5','hybrid_direct_08_4']},'shoulder_hybrid_control.png',['arms_horizontal','arms_overhead','reach_0.5'],'shoulders')
selected='hybrid_direct_08_4';w=choices[selected];(W/'selected_weights.json').write_text(json.dumps(m.rows(w)));save('candidate_selection.json',{'selected':selected,'status':'pending_native_review','method':'pelvis semantic/root refinement with soft skeleton-relative shoulder blend to UE direct-distance stiff bind','skeleton_changes':[],'geometry_changes':[]})
