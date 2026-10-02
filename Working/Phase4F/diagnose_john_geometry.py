"""Read-only geometric diagnostics; never commands/exports review or reruns gates."""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parents[2]
W = P / 'Working/Phase4F/John'
O = P / 'Documentation/Phase4F/John'
D = P / 'Documentation/Phase4F/JohnGeometryDiagnosis'
sys.path.insert(0, str(P / 'Working/Phase4B'))
from geometry_tools import sections


def surface_nearest(query, triangles):
    """Exact plane projection if barycentrically inside, otherwise edge projection."""
    a, b, c = triangles[:, 0], triangles[:, 1], triangles[:, 2]
    ab, ac = b-a, c-a
    normal = np.cross(ab, ac)
    n2 = (normal*normal).sum(1)
    plane = query - normal * (np.einsum('ij,ij->i', query-a, normal) / np.maximum(n2, 1e-30))[:, None]
    ap = plane-a
    d00 = (ab*ab).sum(1); d01 = (ab*ac).sum(1); d11 = (ac*ac).sum(1)
    d20 = (ap*ab).sum(1); d21 = (ap*ac).sum(1)
    denominator = d00*d11-d01*d01
    u = (d11*d20-d01*d21)/np.maximum(denominator, 1e-30)
    v = (d00*d21-d01*d20)/np.maximum(denominator, 1e-30)
    interior = (n2 > 1e-24) & (denominator > 1e-24) & (u >= -1e-12) & (v >= -1e-12) & (u+v <= 1+1e-12)
    candidates = [plane]
    for start, end in [(a,b),(b,c),(c,a)]:
        edge = end-start
        fraction = np.clip(((query-start)*edge).sum(1)/np.maximum((edge*edge).sum(1), 1e-30), 0, 1)
        candidates.append(start+fraction[:, None]*edge)
    points = np.stack(candidates)
    distances2 = ((points-query)**2).sum(2)
    distances2[0, ~interior] = np.inf
    flat = int(distances2.argmin()); candidate, tri = np.unravel_index(flat, distances2.shape)
    return dict(distance_cm=float(np.sqrt(distances2[candidate, tri])), triangle_index=int(tri),
                point_cm=points[candidate,tri].tolist(), region='face' if candidate==0 else 'edge/vertex')


def ray_hits(query, direction, triangles):
    a=triangles[:,0];e1=triangles[:,1]-a;e2=triangles[:,2]-a
    h=np.cross(np.broadcast_to(direction,e2.shape),e2);det=(e1*h).sum(1)
    valid=abs(det)>1e-12;inv=np.zeros_like(det);inv[valid]=1/det[valid]
    s=query-a;u=inv*(s*h).sum(1);q=np.cross(s,e1);v=inv*(q*direction).sum(1);distance=inv*(e2*q).sum(1)
    ids=np.where(valid&(u>=-1e-10)&(v>=-1e-10)&(u+v<=1+1e-10)&(distance>1e-7))[0]
    ids=ids[np.argsort(distance[ids])];result=[]
    for i in ids:
        if result and abs(distance[i]-result[-1]['distance_cm'])<1e-6:continue
        result.append(dict(distance_cm=float(distance[i]),triangle_index=int(i),point_cm=(query+distance[i]*direction).tolist()))
    return result


def raw_sections(vertices, faces, z, grid=.005):
    tv=vertices[faces];delta=tv[:,:,2]-z;ids=np.where((delta.min(1)<0)&(delta.max(1)>0))[0]
    graph=defaultdict(set);points={};key_triangles=defaultdict(set);segments=[]
    for tri_id in ids:
        tri=tv[tri_id];d=delta[tri_id];hits=[]
        for i,j in [(0,1),(1,2),(2,0)]:
            if d[i]*d[j]<0:hits.append(tri[i]+(tri[j]-tri[i])*(-d[i]/(d[j]-d[i])))
        if len(hits)!=2:continue
        keys=[tuple(np.round(p/grid).astype(int)) for p in hits]
        for key,point in zip(keys,hits):points[key]=point;key_triangles[key].add(int(tri_id))
        graph[keys[0]].add(keys[1]);graph[keys[1]].add(keys[0]);segments.append((int(tri_id),*hits))
    components=[];seen=set()
    for key in graph:
        if key in seen:continue
        stack=[key];keys=[]
        while stack:
            k=stack.pop()
            if k in seen:continue
            seen.add(k);keys.append(k);stack.extend(graph[k]-seen)
        ps=np.array([points[k] for k in keys]);lo=ps.min(0);hi=ps.max(0)
        components.append(dict(points_cm=ps.tolist(),min=lo.tolist(),max=hi.tolist(),count=len(ps),
                               retained=bool(len(ps)>=5 and np.linalg.norm(hi-lo)>=.15),
                               degree_counts=dict(Counter(len(graph[k]) for k in keys)),
                               endpoints_cm=[points[k].tolist() for k in keys if len(graph[k])==1],
                               triangle_indices=sorted(set().union(*(key_triangles[k] for k in keys)))))
    return components,segments


def polyline_nearest(query, points):
    starts=points[:-1];edge=np.diff(points,axis=0)
    f=np.clip(((query-starts)*edge).sum(1)/np.maximum((edge*edge).sum(1),1e-30),0,1)
    candidates=starts+f[:,None]*edge;distance=np.linalg.norm(candidates-query,axis=1);i=int(distance.argmin())
    return dict(distance_cm=float(distance[i]),segment_index=i,fraction=float(f[i]),point_cm=candidates[i].tolist())


def self_checks():
    tri=np.array([[[0.,0,0],[2.,0,0],[0.,2,0]]])
    for p,want in [([.5,.5,3],3),([1,1,0],0),([3,0,0],1),([-1,-1,0],np.sqrt(2))]:
        assert abs(surface_nearest(np.array(p),tri)['distance_cm']-want)<1e-10
    assert abs(surface_nearest(np.array([0,0,2]),np.zeros((1,3,3)))['distance_cm']-2)<1e-10
    assert len(ray_hits(np.array([.5,.5,3]),np.array([0,0,-1.]),tri))==1


def main():
    self_checks();D.mkdir(exist_ok=True)
    paths=set()
    for folder in [W,P/'Working/Phase4F/Jane',O,P/'Documentation/Phase4F/Jane']:
        paths.update(p for p in folder.rglob('*') if p.is_file())
    paths.update((P/'Working/Phase4F').glob('*.py'))
    paths.update([P/'Working/Phase4B/geometry_tools.py',P/'Documentation/Phase4F/evaluation_policy.json'])
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (D/'preservation_before.json').write_text(json.dumps(before,indent=2))
    data=np.load(W/'normalised_geometry.npz');vertices=data['vertices'];faces=data['triangles'];labels=data['weld_component'];triangles=vertices[faces]
    fit=json.loads((O/'current_proposal.json').read_text());joints={j['role']:j for j in fit['joints']}
    result=dict(surface_method='Exact closest point on source triangles, independently cross-checked below; no source or reviewer positions changed',
                distance_self_checks='passed',body={},fingers={})
    for name in ['spine_03','clavicle_l','clavicle_r']:
        p=np.array(joints[name]['position_cm']);raw,segments=raw_sections(vertices,faces,p[2]);retained=sections(vertices,faces,p[2])
        for c in raw:
            c['source_components']=sorted(set(int(labels[faces[i,0]]) for i in c['triangle_indices']))
            c['contains_xy_with_original_margin']=bool(np.all(p[:2]>=np.array(c['min'])[:2]-.8)&np.all(p[:2]<=np.array(c['max'])[:2]+.8))
        by_shell={}
        for shell in sorted(set(int(labels[faces[i,0]]) for i,*_ in segments)):
            points=np.array([q for i,*qs in segments if labels[faces[i,0]]==shell for q in qs]);lo=points.min(0);hi=points.max(0)
            by_shell[str(shell)]=dict(min=lo.tolist(),max=hi.tolist(),contains_xy_with_original_margin=bool(np.all(p[:2]>=lo[:2]-.8)&np.all(p[:2]<=hi[:2]+.8)))
        nearest=surface_nearest(p,triangles);nearest['source_component']=int(labels[faces[nearest['triangle_index'],0]])
        rays={}
        for axis in [0,1,2]:
            for sign in [-1,1]:
                direction=np.eye(3)[axis]*sign;hits=ray_hits(p,direction,triangles)
                for hit in hits:hit['source_component']=int(labels[faces[hit['triangle_index'],0]])
                rays[f'{axis}:{sign}']=hits
        sensitivity=[]
        for dz in [-1,-.2,-.01,0,.01,.2,1]:
            for grid in [.00001,.001,.005,.01]:
                parts,_=raw_sections(vertices,faces,p[2]+dz,grid)
                contains=sum(c['retained'] and np.all(p[:2]>=np.array(c['min'])[:2]-.8) and np.all(p[:2]<=np.array(c['max'])[:2]+.8) for c in parts)
                sensitivity.append(dict(z_offset_cm=dz,quantisation_cm=grid,containing_count=int(contains),component_count=len(parts)))
        result['body'][name]=dict(pivot_cm=p.tolist(),retained_section_count=len(retained),raw_component_count=len(raw),
                                 raw_components=raw,section_bounds_per_source_component=by_shell,nearest_triangle=nearest,rays=rays,sensitivity=sensitivity)
    for name,f in fit['finger_chains'].items():
        track=next(t for t in json.loads((O/'finger_tracks.json').read_text())['sides'][f['side']] if t['candidate_id']==f['track_id'])
        accepted_path=np.array(f['path_cm']);original_path=np.array(list(reversed(track['ordered_surface_section_centres_cm'])))
        phalanges=[]
        for index,position in enumerate(f['phalanges_cm'],1):
            p=np.array(position);distances=np.linalg.norm(vertices-p,axis=1);nearest_vertex=int(distances.argmin());triangle=surface_nearest(p,triangles)
            triangle['source_component']=int(labels[faces[triangle['triangle_index'],0]])
            cs=sections(vertices,faces,p[2]);same=[c for c in cs if np.all(p[:2]>=np.array(c['min'])[:2]) and np.all(p[:2]<=np.array(c['max'])[:2])]
            rays={}
            for axis in [0,1,2]:
                for sign in [-1,1]:
                    hits=ray_hits(p,np.eye(3)[axis]*sign,triangles)
                    rays[f'{axis}:{sign}']={'count':len(hits),'nearest':hits[0] if hits else None}
            phalanges.append(dict(phalange=index,role=f"{name[:-2]}_0{index}_{f['side']}",position_cm=p.tolist(),
                                  nearest_vertex_index=nearest_vertex,nearest_vertex_cm=vertices[nearest_vertex].tolist(),
                                  nearest_vertex_distance_cm=float(distances[nearest_vertex]),nearest_vertex_component=int(labels[nearest_vertex]),
                                  nearest_triangle=triangle,on_accepted_path=polyline_nearest(p,accepted_path),
                                  on_original_track=polyline_nearest(p,original_path),
                                  containing_sections=[{k:c[k] for k in ['min','max','centre','count','closed']} for c in same],rays=rays))
        # Subdivide triangle vertices analytically for a density counterfactual: same surface.
        edges_mid=np.concatenate([(triangles[:,0]+triangles[:,1])/2,(triangles[:,1]+triangles[:,2])/2,(triangles[:,2]+triangles[:,0])/2])
        density_points=np.vstack([vertices,edges_mid,triangles.mean(axis=1)])
        for row in phalanges:
            row['same_surface_added_vertex_distance_cm']=float(np.linalg.norm(density_points-np.array(row['position_cm']),axis=1).min())
        result['fingers'][name]=dict(track_id=f['track_id'],sample_count=track['sample_count'],root_cm=f['root_cm'],tip_cm=f['tip_cm'],
                                   root_equals_original_track=bool(np.array_equal(np.array(f['root_cm']),original_path[0])),
                                   tip_equals_original_track=bool(np.array_equal(np.array(f['tip_cm']),original_path[-1])),
                                   path_equals_original_track=bool(np.array_equal(accepted_path,original_path)),
                                   path_length_cm=float(np.linalg.norm(np.diff(accepted_path,axis=0),axis=1).sum()),
                                   donor_length_fractions=f['donor_length_fractions'],phalanges=phalanges,
                                   max_vertex_phalange=max(phalanges,key=lambda p:p['nearest_vertex_distance_cm'])['phalange'])
    changed=[p for p,sha in before.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=sha]
    assert not changed,changed
    result['preservation']=dict(files_checked=len(before),changed=changed)
    (D/'measurements.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'body':{k:dict(sections=v['retained_section_count'],raw=v['raw_component_count'],nearest_surface=v['nearest_triangle']['distance_cm'],shells_containing=[n for n,s in v['section_bounds_per_source_component'].items() if s['contains_xy_with_original_margin']]) for k,v in result['body'].items()},
                      'fingers':{k:dict(max_phalange=f['max_vertex_phalange'],vertex=[round(p['nearest_vertex_distance_cm'],5) for p in f['phalanges']],triangle=[round(p['nearest_triangle']['distance_cm'],5) for p in f['phalanges']],closed=[any(c['closed'] for c in p['containing_sections']) for p in f['phalanges']]) for k,f in result['fingers'].items()},'preservation':result['preservation']},indent=2))


if __name__=='__main__':main()
