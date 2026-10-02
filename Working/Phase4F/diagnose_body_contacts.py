"""Read-only endpoint/edge contact measurements for the body diagnosis."""
import json
import numpy as np
from diagnose_body_topology import D,W,O,policy,extract_segments,planar_faces

fit=json.loads((O/'current_proposal.json').read_text())
mesh,_=policy.load_source(W,O,fit)
data=json.loads((D/'measurements.json').read_text())
out={}
for role in ['thigh_l','thigh_r']:
    row=data['roles'][role]; z=row['pivot_cm'][2]
    graph,points,boundary,parts=mesh.sections(z)
    segments=row['segments']; rows=[]
    for part in parts:
        if 25 not in part['components']:continue
        for key in part['ends']:
            p=points[key]; nearest=[]
            for s in segments:
                if s['component']!=25:continue
                a=np.array(s['a_cm']); b=np.array(s['b_cm']); v=b-a
                if min(np.linalg.norm(p-a),np.linalg.norm(p-b))<1e-7:continue
                t=float(np.dot(p-a,v)/np.dot(v,v)); q=a+np.clip(t,0,1)*v
                nearest.append({'triangle':s['triangle_index'],'distance_cm':float(np.linalg.norm(p-q)),
                                'parameter':t,'nearest_cm':q.tolist(),'a_cm':a.tolist(),'b_cm':b.tolist()})
            rows.append({'key':str(key),'point_cm':p.tolist(),'nearest_nonincident_segments':sorted(nearest,key=lambda x:x['distance_cm'])[:8]})
    out[role]=rows
out['thigh_r_plane_sweep']=[]
p=np.array(data['roles']['thigh_r']['pivot_cm'])
for dz in [-2,-1,-.2,-.01,-.008,-.007,-.006,0,.006,.01,.2,1,2]:
    q=p+np.array([0,0,dz]);s=[a for a in extract_segments(mesh,q[2]) if a['component']==25]
    faces=planar_faces(s,q,True)
    out['thigh_r_plane_sweep'].append({'z_offset_cm':dz,'region_count':faces['containing_valid_regions'],
                                      'dangling_edges':faces['diagnostic_dangling_edges_removed']})
(D/'endpoint_contacts.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
