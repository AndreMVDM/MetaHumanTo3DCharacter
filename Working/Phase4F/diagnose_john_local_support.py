"""Read-only follow-up: local topology, section winding, ray parity and plots."""
import json
import hashlib
from collections import Counter, defaultdict
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from diagnose_john_geometry import P, W, O, D, raw_sections, ray_hits, surface_nearest


def edge_distance(p, edges):
    a = edges[:, 0]; d = edges[:, 1]-a
    u = np.clip(((p-a)*d).sum(1)/np.maximum((d*d).sum(1), 1e-30), 0, 1)
    return float(np.linalg.norm(a+u[:, None]*d-p, axis=1).min())


def section_polygon(segments, query, grid=.00001):
    graph = defaultdict(set); points = {}
    for _, a, b in segments:
        ka, kb = [tuple(np.round(q/grid).astype(int)) for q in [a,b]]
        points[ka]=a; points[kb]=b; graph[ka].add(kb); graph[kb].add(ka)
    seen=set(); rows=[]
    for key in graph:
        if key in seen: continue
        stack=[key]; component=[]
        while stack:
            k=stack.pop()
            if k in seen: continue
            seen.add(k); component.append(k); stack.extend(graph[k]-seen)
        if not all(len(graph[k])==2 for k in component): continue
        loop=[key]; previous=None; current=key
        while True:
            next_key=next(k for k in graph[current] if k!=previous)
            if next_key==key: break
            loop.append(next_key); previous,current=current,next_key
            assert len(loop)<=len(component)
        ps=np.array([points[k] for k in loop]); a=ps[:,:2]; b=np.roll(a,-1,axis=0); q=query[:2]
        crossing=(a[:,1]>q[1])!=(b[:,1]>q[1])
        at_x=a[:,0]+(q[1]-a[:,1])*(b[:,0]-a[:,0])/np.where(abs(b[:,1]-a[:,1])>1e-20,b[:,1]-a[:,1],1)
        inside=bool(np.count_nonzero(crossing & (at_x>q[0]))%2)
        if inside:
            edges=np.stack([ps,np.roll(ps,-1,axis=0)],axis=1)
            rows.append(dict(count=len(ps),inside_polygon=inside,boundary_clearance_cm=edge_distance(query,edges),
                             min_cm=ps.min(0).tolist(),max_cm=ps.max(0).tolist()))
    return rows


def diagnostic_seam_closure(parts, segments, query):
    """Counterfactual closure of nearby garment boundary endpoints only, no mesh edit.

    Components 34 and 1 are the observed shirt and separate sleeve pieces for this
    diagnostic. This is NOT an implementation of a generic validation policy.
    """
    garment_parts=[c for c in parts if set(c['source_components']) <= {1,34}]
    endpoints=[(index,np.array(p),c['source_components']) for index,c in enumerate(garment_parts) for p in c['endpoints_cm']]
    possible=[]
    for i,(ci,a,_) in enumerate(endpoints):
        for j,(cj,b,_) in enumerate(endpoints[:i]):
            if ci==cj: continue
            distance=float(np.linalg.norm(a-b))
            if distance<=.8: possible.append((distance,i,j))
    used=set(); bridges=[]; augmented=list(segments)
    for distance,i,j in sorted(possible):
        if i in used or j in used: continue
        used.update([i,j]); a=endpoints[i][1]; b=endpoints[j][1]
        bridges.append({'gap_cm':distance,'endpoints_cm':[a.tolist(),b.tolist()],
                        'source_components':[endpoints[i][2],endpoints[j][2]]})
        augmented.append((-1,a,b))
    return {'diagnostic_only':True,'bridges':bridges,'enclosing_polygons':section_polygon(augmented,query)}


def main():
    baseline=json.loads((D/'preservation_before.json').read_text())
    data=np.load(W/'normalised_geometry.npz'); v=data['vertices']; f=data['triangles']; labels=data['weld_component']; tris=v[f]
    measured=json.loads((D/'measurements.json').read_text())
    proposal=json.loads((O/'current_proposal.json').read_text())
    donor={r['name']:np.array(r['world_cm']) for r in json.loads((O/'solved_donor_joints.json').read_text())['joints']}
    _,weld=np.unique(np.round(v/.00001).astype(np.int64),axis=0,return_inverse=True)
    pairs=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]])
    keys=np.sort(weld[pairs],axis=1)
    _,first,counts=np.unique(keys,axis=0,return_index=True,return_counts=True)
    boundary=v[pairs[first[counts==1]]]
    result={'weld_tolerance_cm':.00001,'source_boundary_edge_count':len(boundary),'body':{},'fingers':{}}
    body_panels=[]; finger_panels=[]
    for name,row in measured['body'].items():
        p=np.array(row['pivot_cm']); parts,segs=raw_sections(v,f,p[2],grid=.00001)
        endpoints=[]
        for part in parts:
            part['source_components']=sorted(set(int(labels[f[i,0]]) for i in part['triangle_indices']))
            for q in part['endpoints_cm']:
                endpoints.append(dict(point_cm=q,source_components=sorted(set(int(labels[f[i,0]]) for i in part['triangle_indices'])),
                                      nearest_source_boundary_edge_cm=edge_distance(np.array(q),boundary)))
        component_data={}
        for shell in row['section_bounds_per_source_component']:
            mask=labels==int(shell); indices=np.where(labels[f[:,0]]==int(shell))[0]
            component_data[shell]={'bounds_cm':[v[mask].min(0).tolist(),v[mask].max(0).tolist()], 'vertices':int(mask.sum()),'triangles':len(indices)}
        result['body'][name]={'source_component_bounds':component_data,'section_endpoints':endpoints,
                              'endpoints_on_source_boundary_count':sum(q['nearest_source_boundary_edge_cm']<1e-7 for q in endpoints),
                              'endpoint_count':len(endpoints),
                              'nearby_garment_seam_counterfactual':diagnostic_seam_closure(parts,segs,p)}
        body_panels.append((name,p,segs))
    directions=[np.array(q,dtype=float)/np.linalg.norm(q) for q in [[1,.173,.319],[-.231,1,.117],[.127,-.241,1],[-1,-.173,-.319],[.231,-1,-.117],[-.127,.241,-1]]]
    for name,row in measured['fingers'].items():
        component=36 if name.endswith('_l') else 0
        ids=np.where(labels[f[:,0]]==component)[0]; localtris=tris[ids]
        phalanges=[]
        for item in row['phalanges']:
            p=np.array(item['position_cm']); _,segs=raw_sections(v,f,p[2],grid=.00001)
            local_segs=[s for s in segs if labels[f[s[0],0]]==component]
            loops=section_polygon(local_segs,p)
            parity=[len(ray_hits(p,d,localtris)) for d in directions]
            closest=surface_nearest(p,localtris)
            phalanges.append({'phalange':item['phalange'],'enclosing_exact_section_polygons':loops,
                              'local_hand_oblique_ray_counts':parity,'all_six_odd':all(n%2 for n in parity),
                              'nearest_local_triangle_distance_cm':closest['distance_cm']})
            if item['phalange']==1: finger_panels.append((name,p,local_segs))
        path=np.array(proposal['finger_chains'][name]['path_cm'])
        digit,side=name.rsplit('_',1)
        donor_points=np.array([donor[f'{digit}_0{i}_{side}'] for i in [1,2,3]])
        lengths=np.linalg.norm(np.diff(donor_points,axis=0),axis=1)
        total=lengths.sum()+.65*lengths[-1]
        fractions=np.array([0.,lengths[0]/total,lengths.sum()/total])
        segment_lengths=np.linalg.norm(np.diff(path,axis=0),axis=1)
        cumulative=np.r_[0.,np.cumsum(segment_lengths)]
        generated=[]
        for fraction in fractions:
            distance=fraction*cumulative[-1]; index=min(int(np.searchsorted(cumulative,distance,side='right')-1),len(path)-2)
            u=(distance-cumulative[index])/segment_lengths[index]
            generated.append(path[index]*(1-u)+path[index+1]*u)
        # An explicitly synthetic outside point demonstrates why unsigned proximity
        # cannot certify an interior joint. It is never saved in the proposal.
        root=path[0]; closest=surface_nearest(root,localtris); contact=np.array(closest['point_cm'])
        outward=(contact-root)/np.linalg.norm(contact-root); outside=contact+.2*outward
        outside_counts=[len(ray_hits(outside,d,localtris)) for d in directions]
        control={'synthetic_outside_point_cm':outside.tolist(),'local_oblique_ray_counts':outside_counts,
                 'all_six_even':all(n%2==0 for n in outside_counts),
                 'nearest_vertex_distance_cm':float(np.linalg.norm(v-outside,axis=1).min()),
                 'nearest_local_triangle_distance_cm':surface_nearest(outside,localtris)['distance_cm']}
        # Original track samples plus three interior samples of each segment.
        dense=np.vstack([path,*[path[:-1]*(1-u)+path[1:]*u for u in [.25,.5,.75]]])
        dense_parity=[all(len(ray_hits(p,d,localtris))%2 for d in directions) for p in dense]
        result['fingers'][name]={'phalanges':phalanges,'dense_path_samples':len(dense),'dense_path_all_six_odd_count':sum(dense_parity),
                                 'root_surface_distance_cm':surface_nearest(path[0],localtris)['distance_cm'],
                                 'tip_surface_distance_cm':surface_nearest(path[-1],localtris)['distance_cm'],
                                 'root_z_cm':float(path[0,2]),'tip_z_cm':float(path[-1,2]),
                                 'recomputed_donor_fraction_max_error':float(np.max(abs(fractions-np.array(proposal['finger_chains'][name]['donor_length_fractions'])))),
                                 'recomputed_generated_position_max_error_cm':float(np.max(np.linalg.norm(np.array(generated)-np.array(proposal['finger_chains'][name]['phalanges_cm']),axis=1))),
                                 'negative_control':control}
    # Numeric section plots: actual triangle-plane segments, no reconstructed surface.
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19); small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    panels=body_panels+finger_panels; width=1200; height=250*len(panels)+90
    canvas=Image.new('RGB',(width,height),'white'); draw=ImageDraw.Draw(canvas)
    draw.text((20,15),'John: source XY sections and accepted pivots / generated roots (cm)',fill='#172c40',font=font)
    draw.text((20,43),'Blue = actual section segments; red = centre. Fingers: orange circle = existing 1.2 cm criterion.',fill='#374c60',font=small)
    for index,(name,p,segs) in enumerate(panels):
        top=80+index*250; xy=np.array([q[:2] for _,a,b in segs for q in [a,b]])
        if index>=3:
            # Focus on the root's local digit region; neighbouring fingers remain visible.
            lo=p[:2]-np.array([4.,4.]); hi=p[:2]+np.array([4.,4.])
        else: lo=xy.min(0)-2; hi=xy.max(0)+2
        scale=min(880/(hi[0]-lo[0]),200/(hi[1]-lo[1])); origin=np.array([290.,top+225.])
        def point(q):
            loc=(np.array(q[:2])-lo)*scale; return tuple(origin+loc*np.array([1.,-1.]))
        draw.text((20,top+12),name,fill='#172c40',font=font)
        draw.text((20,top+42),f'Z = {p[2]:.3f} cm',fill='#374c60',font=small)
        draw.text((20,top+68),f'X = {p[0]:.3f}, Y = {p[1]:.3f}',fill='#374c60',font=small)
        for _,a,b in segs:
            if np.all(a[:2]>=lo)&np.all(a[:2]<=hi)&np.all(b[:2]>=lo)&np.all(b[:2]<=hi): draw.line([point(a),point(b)],fill='#256ba6',width=2)
        x,y=point(p)
        if index>=3:
            r=1.2*scale; draw.ellipse((x-r,y-r,x+r,y+r),outline='#c67c15',width=2)
        draw.line([(x-6,y),(x+6,y)],fill='#b92336',width=3);draw.line([(x,y-6),(x,y+6)],fill='#b92336',width=3)
        draw.line([(10,top+245),(width-10,top+245)],fill='#dddddd')
    canvas.save(D/'source_sections.png')
    changed=[path for path,sha in baseline.items() if hashlib.sha256(__import__('pathlib').Path(path).read_bytes()).hexdigest()!=sha]
    assert not changed,changed
    result['preservation']={'protected_files_checked':len(baseline),'changed':changed}
    (D/'local_support.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'body':{k:[r['endpoints_on_source_boundary_count'],r['endpoint_count']] for k,r in result['body'].items()},
                      'fingers':{k:{'section_polygon_inside':[bool(p['enclosing_exact_section_polygons']) for p in r['phalanges']],
                                    'local_oblique_ray_inside':[p['all_six_odd'] for p in r['phalanges']],
                                    'path_inside':[r['dense_path_all_six_odd_count'],r['dense_path_samples']]} for k,r in result['fingers'].items()},
                      'preservation':result['preservation']},indent=2))


if __name__=='__main__':main()
