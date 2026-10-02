from model import *
m=Model();w=m.dense(load(W/'saved_Refined_weights.json'));baseline=m.weights
stress={}
for label,weights in [('baseline',baseline),('refined',w)]:stress[label]={n:m.measure(weights,p) for n,p in m.poses.items()}
save('final_stress_comparison.json',stress)
summary={}
for label,weights in [('baseline',baseline),('refined',w)]:
    rows=[{'role':s['role'],'time_s':s['time_s'],'fraction':s['fraction'],'metrics':m.measure(weights,m.from_sample(s))} for s in m.samples]
    summary[label]={role:{region:{'mean_edge_log_strain_rms':float(np.mean([r['metrics'][region]['edge_log_strain_rms'] for r in rows if r['role']==role])),'max_area_below_0_5':max(r['metrics'][region]['area_below_0_5'] for r in rows if r['role']==role),'max_area_above_2':max(r['metrics'][region]['area_above_2'] for r in rows if r['role']==role)} for region in ['front_pants','back_hips','shoulders','upper_torso']} for role in ['idle','walk','run','reach']}
    save('final_'+label+'_244_pose_metrics.json',rows)
save('final_deformation_summary.json',summary)
fields={}
for region,mask in m.regions.items():
    fields[region]={label:{m.names[b]:float(weight[mask,b].mean()) for b in range(len(m.names)) if weight[mask,b].mean()>1e-5} for label,weight in [('baseline',baseline),('refined',w)]}
save('before_after_weights.json',fields)
contact=load(O/'surface_contact_native_bake.json');assert contact['status']=='passed';rows=[]
for s in contact['samples']:
    pose=m.from_sample(s);out=m.deform(w,pose);rows.append({'role':s['role'],'time_s':s['time_s'],'min_z_cm':{side:float(out[m.regions['left_sole' if side=='l' else 'right_sole'],2].min()) for side in ['l','r']},'root_position_cm':pose[m.bi['root'],:3,3].tolist(),'max_unit_scale_error':max(abs(x-1) for b in s['bones'].values() for x in b['component']['scale'])})
cs=[]
for role in ['idle','walk','run']:
    seq=[s for s in rows if s['role']==role];cs.append({'role':role,'poses':len(seq),'max_penetration_cm':max(0,-min(z for s in seq for z in s['min_z_cm'].values())),'sole_range':{side:[min(s['min_z_cm'][side] for s in seq),max(s['min_z_cm'][side] for s in seq)] for side in ['l','r']},'root_max_displacement_cm':max(np.linalg.norm(s['root_position_cm']) for s in seq),'max_scale_error':max(s['max_unit_scale_error'] for s in seq)})
save('surface_contact_dense_validation.json',{'status':'measured','method':'Fresh UE native baked animation at every key and half-key (120 Hz), saved candidate weights','summary':cs,'samples':rows,'actor_offset_cm':[0,0,0]});print('Dense contact',cs)
# Export individual diagnostic static-pose animation keys for native visual review.
poses=[]
for name,pose in m.poses.items():
    if name not in ['neutral','arms_45','arms_horizontal','arms_overhead','elbows_bent','wide_stance','knee_bend']:continue
    locals=[]
    for n in m.names:
        i=m.bi[n];parent=m.parents[n];locals.append(pose[i] if parent=='None' else np.linalg.inv(pose[m.bi[parent]])@pose[i])
    poses.append({'name':name,'local_matrices':np.array(locals).tolist()})
(W/'stress_native_keys.json').write_text(json.dumps({'bone_names':m.names,'poses':poses}));print('Final measurements complete')
