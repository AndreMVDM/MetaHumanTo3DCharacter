from surface_contact import *
source=load(O/'native_contact_frame_export.json');assert source['status']=='passed';rows=[]
for s in source['samples']:
    pose=m.from_sample(s);out,events=correct(pose)
    locals=[]
    for n in m.names:
        b=m.bi[n];parent=m.parents[n];locals.append(out[b] if parent=='None' else np.linalg.inv(out[m.bi[parent]])@out[b])
    rows.append({'role':s['role'],'frame':s['frame'],'local_matrices':np.array(locals).tolist(),'events':events})
(W/'contact_bake_keys.json').write_text(json.dumps({'clips':source['clips'],'bone_names':m.names,'frames':rows},allow_nan=False));print('Prepared native contact keys',len(rows))
