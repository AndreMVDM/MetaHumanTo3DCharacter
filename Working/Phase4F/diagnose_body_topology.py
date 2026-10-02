"""Body-only diagnostic experiments; never edits/invokes validator or review.

Planar faces and winding are measurements of candidate representations, not gates.
"""
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.dont_write_bytecode=True
import geometry_support_policy as policy
from diagnose_john_geometry import ray_hits, surface_nearest, raw_sections
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F/John';O=P/'Documentation/Phase4F/John';D=P/'Documentation/Phase4F/JohnBodySupportDiagnosis'


def winding(p,tri):
    a,b,c=[tri[:,i]-p for i in range(3)];la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lc=np.linalg.norm(c,axis=1)
    numerator=np.einsum('ij,ij->i',a,np.cross(b,c))
    denominator=la*lb*lc+np.einsum('ij,ij->i',a,b)*lc+np.einsum('ij,ij->i',b,c)*la+np.einsum('ij,ij->i',c,a)*lb
    return float((2*np.arctan2(numerator,denominator)).sum()/(4*np.pi))


def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]


def crossings(segments):
    if not segments:return []
    a=np.array([s['a_cm'][:2] for s in segments],dtype=float);b=np.array([s['b_cm'][:2] for s in segments],dtype=float);d=b-a
    rows=[]
    for i in range(len(a)):
        denominator=cross(d[i],d[i+1:]);delta=a[i+1:]-a[i]
        valid=abs(denominator)>1e-10
        t=np.divide(cross(delta,d[i+1:]),denominator,out=np.zeros_like(denominator),where=valid)
        u=np.divide(cross(delta,d[i]),denominator,out=np.zeros_like(denominator),where=valid)
        for local in np.where(valid&(t>1e-7)&(t<1-1e-7)&(u>1e-7)&(u<1-1e-7))[0]:
            j=i+1+int(local);q=a[i]+t[local]*d[i]
            rows.append({'segment_indices':[i,j],'xy_cm':q.tolist(),'triangle_indices':[segments[i]['triangle_index'],segments[j]['triangle_index']],
                         'source_components':[segments[i]['component'],segments[j]['component']],
                         'parameters':[float(t[local]),float(u[local])]})
    return rows


def planar_faces(segments,p,region_mode=False):
    """Split actual crossings, then walk half-edge faces. No arbitrary gap closure."""
    splits=[[0.,1.] for _ in segments]
    hits=crossings(segments)
    for row in hits:
        for i,u in zip(row['segment_indices'],row['parameters']):splits[i].append(u)
    # Exact endpoint-on-edge and collinear overlap contacts also belong in an
    # arrangement. This is numerical equality, never a gap-bridging allowance.
    endpoint_contacts=0
    for i,s in enumerate(segments):
        a=np.array(s['a_cm'][:2]);b=np.array(s['b_cm'][:2]);v=b-a;vv=float(v@v)
        for j,t in enumerate(segments):
            if i==j:continue
            for q in [np.array(t['a_cm'][:2]),np.array(t['b_cm'][:2])]:
                u=float((q-a)@v/vv)
                if 1e-9<u<1-1e-9 and np.linalg.norm(a+u*v-q)<1e-9:
                    splits[i].append(u);endpoint_contacts+=1
    graph=defaultdict(set);points={}
    for segment,parameters in zip(segments,splits):
        a=np.array(segment['a_cm'][:2]);b=np.array(segment['b_cm'][:2]);ps=sorted(set(parameters))
        for u,v in zip(ps,ps[1:]):
            pa=a+(b-a)*u;pb=a+(b-a)*v
            ka=tuple(np.round(pa/1e-7).astype(int));kb=tuple(np.round(pb/1e-7).astype(int))
            if ka==kb:continue
            points[ka]=pa;points[kb]=pb;graph[ka].add(kb);graph[kb].add(ka)
    dangling_edges=0
    if region_mode:
        # Dangling source edges cannot enclose a planar face. Keep them in the
        # original evidence; remove them only from this diagnostic face traversal.
        pending=[k for k in graph if len(graph[k])<2]
        while pending:
            k=pending.pop()
            for n in list(graph[k]):
                graph[n].remove(k);dangling_edges+=1
                if len(graph[n])==1:pending.append(n)
            graph[k].clear()
        graph={k:ns for k,ns in graph.items() if ns}
    neighbours={k:sorted(ns,key=lambda n:math.atan2(*(points[n]-points[k])[::-1])) for k,ns in graph.items()}
    used=set();faces=[]
    for a in graph:
        for b in graph[a]:
            if (a,b) in used:continue
            start=(a,b);edge=start;order=[]
            while edge not in used:
                used.add(edge);x,y=edge;order.append(x)
                ns=neighbours[y];index=ns.index(x);edge=(y,ns[(index-1)%len(ns)])
                if edge==start:break
            if edge!=start:continue
            poly=np.array([points[k] for k in order]);nextp=np.roll(poly,-1,axis=0);area=float(np.sum(cross(poly,nextp))/2)
            if area<=1e-9:continue
            poly3=np.column_stack([poly,np.full(len(poly),p[2])]);inside,distance=policy.polygon_contains(poly3,p)
            cycles=[];path=[]
            for k in order+[order[0]]:
                if k in path:
                    at=path.index(k);cycle=path[at:];path=path[:at+1]
                    if len(cycle)<3:continue
                    cp=np.array([points[n] for n in cycle]);ca=float(np.sum(cross(cp,np.roll(cp,-1,axis=0)))/2)
                    cp3=np.column_stack([cp,np.full(len(cp),p[2])]);ci,cd=policy.polygon_contains(cp3,p)
                    cycles.append({'area_cm2':ca,'contains_pivot':ci,'simple':not policy.invalid_polygon(cp3),'polygon_cm':cp3.tolist(),'boundary_distance_cm':cd})
                else:path.append(k)
            region_inside=any(c['area_cm2']>0 and c['contains_pivot'] for c in cycles) and not any(c['area_cm2']<0 and c['contains_pivot'] for c in cycles)
            faces.append({'area_cm2':area,'contains_pivot':inside,'boundary_distance_cm':distance,
                          'simple':not policy.invalid_polygon(poly3),'polygon_cm':poly3.tolist(),'boundary_cycles':cycles,
                          'region_inside':region_inside,'valid_boundary_cycles':bool(cycles) and all(c['simple'] for c in cycles)})
    return {'bounded_faces':faces,'containing_simple_faces':sum(f['simple'] and f['contains_pivot'] for f in faces),
            'containing_valid_regions':sum(f['valid_boundary_cycles'] and f['region_inside'] for f in faces),'diagnostic_dangling_edges_removed':dangling_edges,
            'source_crossing_count':len(hits),'exact_endpoint_on_edge_contacts':endpoint_contacts}


def extract_segments(mesh,z):
    result=[]
    for tid in np.where((mesh.lo<z)&(mesh.hi>z))[0]:
        tri=mesh.tri[tid];delta=tri[:,2]-z;points=[]
        for i,j in [(0,1),(1,2),(2,0)]:
            if delta[i]*delta[j]<0:points.append(tri[i]+(tri[j]-tri[i])*(-delta[i]/(delta[j]-delta[i])))
        if len(points)==2 and np.linalg.norm(points[0]-points[1])>1e-10:
            result.append({'triangle_index':int(tid),'component':int(mesh.components[mesh.f[tid,0]]),'a_cm':points[0].tolist(),'b_cm':points[1].tolist()})
    return result


def extra_bounded_bridges(mesh,z,allow_partial_anchored_part=False):
    """Diagnostic candidate: allow branch junctions, retain other v2 budgets/provenance.

    Does not decide valid support. Planar faces examine whether it makes a region.
    """
    graph,points,boundary,parts=mesh.sections(z)
    ends=[(i,k) for i,part in enumerate(parts) for k in part['ends'] if k in boundary]
    groups=[set(mesh.garments[c] for c in p['components'] if c in mesh.garments) for p in parts]
    tokens=[set(mesh.provenance.get(c) for c in p['components']) for p in parts]
    candidates=defaultdict(list)
    for i,(pi,a) in enumerate(ends):
        for j,(pj,b) in enumerate(ends[:i]):
            if np.linalg.norm(points[a]-points[b])>.8:continue
            compatible=len(tokens[pi])==len(tokens[pj])==1 and None not in tokens[pi] and tokens[pi]==tokens[pj]
            compatible &= len(groups[pi])<=1 and len(groups[pj])<=1 and bool(groups[pi] or groups[pj])
            compatible &= not(groups[pi] and groups[pj] and groups[pi]!=groups[pj])
            if compatible:candidates[i].append(j);candidates[j].append(i)
    match={i:js[0] for i,js in candidates.items() if len(js)==1 and len(candidates[js[0]])==1}
    allowed=set()
    for pi,part in enumerate(parts):
        ids=[i for i,(pj,_) in enumerate(ends) if pj==pi]
        if allow_partial_anchored_part and groups[pi]:allowed.add(pi);continue
        if not ids or not all(i in match for i in ids):continue
        if groups[pi]:allowed.add(pi);continue
        target=[groups[ends[match[i]][0]] for i in ids]
        if all(len(g)==1 for g in target) and all(g==target[0] for g in target):allowed.add(pi)
    return [{'a_cm':points[ends[i][1]].tolist(),'b_cm':points[ends[j][1]].tolist(),'gap_cm':float(np.linalg.norm(points[ends[i][1]]-points[ends[j][1]])),
             'component':None,'triangle_index':None} for i,j in match.items() if i<j and ends[i][0] in allowed and ends[j][0] in allowed]


def branch_details(mesh,z,raw_components):
    graph,points,boundary,parts=mesh.sections(z);rows=[]
    weldfaces=mesh.weld[mesh.f]
    for key in graph:
        if len(graph[key])<=2:continue
        if key[0]!='e':continue
        a,b=key[1:];incident=np.where(np.any(weldfaces==a,axis=1)&np.any(weldfaces==b,axis=1))[0]
        va=np.where(mesh.weld==a)[0];vb=np.where(mesh.weld==b)[0]
        raw_pairs=Counter()
        for tid in incident:
            face=mesh.f[tid];pa=next(int(k) for k in face if mesh.weld[k]==a);pb=next(int(k) for k in face if mesh.weld[k]==b)
            raw_pairs[tuple(sorted((pa,pb)))]+=1
        normals=np.cross(mesh.tri[incident,1]-mesh.tri[incident,0],mesh.tri[incident,2]-mesh.tri[incident,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-30)
        rows.append({'graph_degree':len(graph[key]),'position_cm':points[key].tolist(),'canonical_source_edge_cm':[mesh.v[va[0]].tolist(),mesh.v[vb[0]].tolist()],
                     'position_welded_edge_incident_faces':len(incident),'raw_edge_incident_face_counts':{str(k):v for k,v in raw_pairs.items()},
                     'triangle_indices':incident.tolist(),'source_components':sorted(set(int(mesh.components[mesh.f[t,0]]) for t in incident)),
                     'raw_components':sorted(set(int(raw_components[mesh.f[t,0]]) for t in incident)),
                     'face_normals':normals.tolist(),'face_normal_dot_products':(normals@normals.T).tolist(),
                     'section_neighbour_points_cm':[points[k].tolist() for k in graph[key]]})
    return rows


def paint_plot(name,row,colours):
    p=np.array(row['pivot_cm']);segments=row['segments'];allxy=np.array([s[k][:2] for s in segments for k in ['a_cm','b_cm']])
    canvas=Image.new('RGB',(1600,900),'white');draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
    draw.text((20,15),f'John / {name}: actual horizontal source section at Z={p[2]:.5f} cm',fill='#142c40',font=font)
    draw.text((20,46),'Red cross = accepted pivot; orange = branch; magenta = real surface crossing; dashed green = existing v2 seam link.',fill='#314858',font=small)
    lo=allxy.min(0)-2;hi=allxy.max(0)+2;zoom=np.array([13.,13.]) if p[2]>100 else np.array([12.,12.])
    panels=[(20,100,740,690,lo,hi,'Whole section: X right, Y up (cm)'),(810,100,760,690,p[:2]-zoom,p[:2]+zoom,'Pivot neighbourhood')]
    for x,y,width,height,low,high,label in panels:
        scale=min((width-30)/(high[0]-low[0]),(height-45)/(high[1]-low[1]));offset=np.array([x+15,y+height-15])
        def xy(q):return tuple(offset+(np.array(q[:2])-low)*scale*np.array([1.,-1.]))
        draw.rectangle((x,y,x+width,y+height),outline='#cccccc');draw.text((x+5,y+5),label,fill='#142c40',font=small)
        def visible(q):return np.all(np.array(q[:2])>=low)&np.all(np.array(q[:2])<=high)
        for s in segments:
            if visible(s['a_cm']) and visible(s['b_cm']):draw.line([xy(s['a_cm']),xy(s['b_cm'])],fill=colours[s['component']],width=2)
        for s in row['v2_bridges']:
            if visible(s['a_cm']) and visible(s['b_cm']):
                a=np.array(s['a_cm']);b=np.array(s['b_cm'])
                for u in np.arange(0,1,.2):draw.line([xy(a+(b-a)*u),xy(a+(b-a)*min(u+.1,1))],fill='#228858',width=2)
        for b in row['branch_nodes']:
            if visible(b['position_cm']):
                xx,yy=xy(b['position_cm']);draw.ellipse((xx-5,yy-5,xx+5,yy+5),outline='#e97810',width=3)
        for c in row['crossings']:
            if visible(c['xy_cm']):
                xx,yy=xy(c['xy_cm']);draw.ellipse((xx-4,yy-4,xx+4,yy+4),outline='#bf249a',width=2)
        xx,yy=xy(p);draw.line([(xx-9,yy),(xx+9,yy)],fill='#dc2434',width=3);draw.line([(xx,yy-9),(xx,yy+9)],fill='#dc2434',width=3)
    legend='Components: '+', '.join(str(c) for c in row['section_components'])+'; complete triangle IDs and coordinates in measurements.json'
    draw.text((20,815),legend,fill='#314858',font=small)
    for i,c in enumerate(row['section_components']):
        draw.rectangle((20+i*160,848,45+i*160,868),fill=colours[c]);draw.text((50+i*160,844),f'Component {c}',fill='#142c40',font=small)
    canvas.save(D/f'{name}_section.png')


def main():
    frozen=json.loads((D/'preservation_before.json').read_text());data=np.load(W/'normalised_geometry.npz');source=np.load(W/'source_geometry.npz')
    fit=json.loads((O/'current_proposal.json').read_text());gate=json.loads((O/'anatomical_validation.json').read_text())
    mesh,provenance=policy.load_source(W,O,fit);rawmesh=policy.SourceSupport(mesh.v,mesh.f,mesh.components,mesh.provenance,mesh.garments)
    rawmesh.weld=np.arange(len(mesh.v));rawmesh.edge_counts=Counter(tuple(sorted(pair)) for pair in np.concatenate([mesh.f[:,[0,1]],mesh.f[:,[1,2]],mesh.f[:,[2,0]]]))
    uv=np.load(D/'triangle_uv_readback.npz')['triangle_uv'];summary=json.loads((O/'geometry_summary.json').read_text());texture=np.array(Image.open(summary['images'][0]['source_path']).convert('RGB'))
    uvcentre=uv.mean(1);pixels=np.column_stack([np.clip(uvcentre[:,0]*texture.shape[1],0,texture.shape[1]-1),np.clip((1-uvcentre[:,1])*texture.shape[0],0,texture.shape[0]-1)]).astype(int)
    tri_colours=texture[pixels[:,1],pixels[:,0]];normal=np.cross(mesh.tri[:,1]-mesh.tri[:,0],mesh.tri[:,2]-mesh.tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-30)
    directions=[np.array([math.cos(a),math.sin(a),0.]) for a in np.linspace(0,2*np.pi,16,endpoint=False)]
    directions += [d/np.linalg.norm(d) for d in np.array([[1,.173,.319],[-.231,1,.117],[.127,-.241,1],[-1,-.173,-.319],[.231,-1,-.117],[-.127,.241,-1]])]
    results={'method':'Read-only topology and representation experiments. No pass/fail policy change.','source_provenance':provenance,'roles':{},'components':{}}
    labels=mesh.components;tri_labels=labels[mesh.f[:,0]]
    for c in np.unique(labels):
        mask=labels==c;ts=np.where(tri_labels==c)[0];component_edges=[]
        for tid in ts:
            face=mesh.weld[mesh.f[tid]];component_edges.extend(tuple(sorted((int(face[i]),int(face[j])))) for i,j in [(0,1),(1,2),(2,0)])
        ec=Counter(component_edges)
        results['components'][str(c)]={'vertices':int(mask.sum()),'triangles':len(ts),'bounds_cm':[mesh.v[mask].min(0).tolist(),mesh.v[mask].max(0).tolist()],
                                      'boundary_edges':sum(v==1 for v in ec.values()),'nonmanifold_edges':sum(v>2 for v in ec.values()),
                                      'raw_component_labels':sorted(set(int(k) for k in source['raw_component'][mask])),
                                      'median_texture_rgb':np.median(tri_colours[ts],axis=0).tolist()}
    palette=['#256bad','#bf7624','#398b57','#9053a0','#c34457','#4f8598','#939220','#252f40']
    component_colours={int(c):palette[i%len(palette)] for i,c in enumerate(np.unique(labels))}
    for name in [n.removeprefix('surface_envelope_') for n in gate['failed']]:
        p=np.array(next(j['position_cm'] for j in fit['joints'] if j['role']==name));z=float(p[2]);segments=extract_segments(mesh,z)
        actual_cross=crossings(segments)
        for c in actual_cross:
            a,b=c['triangle_indices'];c['normal_dot']=float(normal[a]@normal[b]);c['source_triangle_xyz_cm']=[mesh.tri[a].tolist(),mesh.tri[b].tolist()]
            c['source_texture_rgb']=[tri_colours[a].tolist(),tri_colours[b].tolist()]
        _,v2bridges,v2errors=mesh.loops(z,True);branches=branch_details(mesh,z,source['raw_component'])
        possible=extra_bounded_bridges(mesh,z)
        local_possible=extra_bounded_bridges(mesh,z,allow_partial_anchored_part=True)
        section_graph,section_points,section_boundary,section_parts=mesh.sections(z)
        part_evidence=[]
        for part in section_parts:
            ends=[{'key':str(k),'point_cm':section_points[k].tolist(),'source_boundary':k in section_boundary} for k in part['ends']]
            part_evidence.append({'components':sorted(part['components']),'valid':part['valid'],'closed':part['valid'] and not ends,'ends':ends,
                                  'two_end_gap_cm':float(np.linalg.norm(section_points[part['ends'][0]]-section_points[part['ends'][1]])) if len(ends)==2 else None})
        def bridge_segments(bridges):return [{'triangle_index':None,'component':None,'a_cm':b['a_cm'],'b_cm':b['b_cm']} for b in bridges]
        section_cs=sorted(set(s['component'] for s in segments));wcomponent={str(c):winding(p,mesh.tri[tri_labels==c]) for c in np.unique(labels)}
        sensitivity=[]
        for dz in [-.2,-.01,0.,.01,.2]:
            graph,_,_,parts=mesh.sections(z+dz);rawgraph,_,_,_=rawmesh.sections(z+dz)
            s=extract_segments(mesh,z+dz)
            sensitivity.append({'z_offset_cm':dz,'branch_nodes':sum(len(v)>2 for v in graph.values()),'unwelded_branch_nodes':sum(len(v)>2 for v in rawgraph.values()),
                                'crossings':len(crossings(s)),'raw_on_plane_vertices':int(np.count_nonzero(abs(mesh.v[:,2]-(z+dz))<1e-8))})
        rays=[]
        # Scopes are reported individually, never combined into an authorised volume.
        for direction in directions:
            hits=ray_hits(p,direction,mesh.tri)
            for hit in hits:
                tid=hit['triangle_index'];hit['component']=int(tri_labels[tid]);hit['normal_dot_direction']=float(normal[tid]@direction)
            rays.append({'direction':direction.tolist(),'hits':hits})
        local_rays={str(c):[len(ray_hits(p,d,mesh.tri[tri_labels==c])) for d in directions] for c in section_cs}
        near=surface_nearest(p,mesh.tri);near['component']=int(tri_labels[near['triangle_index']])
        controls=[]
        for delta in [[0,0,.2],[0,0,-.2],[.2,0,0],[-.2,0,0],[0,.2,0],[0,-.2,0],[0,30,0],[0,-30,0],[40,0,0],[-40,0,0]]:
            q=p+np.array(delta);controls.append({'delta_cm':delta,'global_winding':winding(q,mesh.tri),
                                               'component_winding':{str(c):winding(q,mesh.tri[tri_labels==c]) for c in section_cs}})
        row={'pivot_cm':p.tolist(),'section_components':section_cs,'section_parts':part_evidence,'segments':segments,'crossings':actual_cross,'branch_nodes':branches,
             'v2_bridges':v2bridges,'v2_errors':v2errors,'diagnostic_branch_aware_bounded_bridges':possible,
             'diagnostic_locally_matched_bounded_bridges':local_possible,
             'raw_graph_planar_faces':planar_faces(segments,p),'v2_bridge_planar_faces':planar_faces(segments+bridge_segments(v2bridges),p),
             'branch_aware_bridge_planar_faces':planar_faces(segments+bridge_segments(possible),p),
             'raw_source_region_arrangement':planar_faces(segments,p,region_mode=True),
             'v2_bridge_region_arrangement':planar_faces(segments+bridge_segments(v2bridges),p,region_mode=True),
             'branch_aware_region_arrangement':planar_faces(segments+bridge_segments(possible),p,region_mode=True),
             'locally_matched_region_arrangement':planar_faces(segments+bridge_segments(local_possible),p,region_mode=True),
             'sensitivity':sensitivity,'nearest_triangle':near,'global_winding':winding(p,mesh.tri),'component_winding':wcomponent,
             'rays':rays,'individual_component_ray_counts':local_rays,'winding_controls':controls}
        results['roles'][name]=row;paint_plot(name,row,component_colours)
        print(name, 'components',section_cs,'branches',len(branches),'crossings',len(actual_cross),'regions',[row[k]['containing_valid_regions'] for k in ['raw_source_region_arrangement','v2_bridge_region_arrangement','branch_aware_region_arrangement']], 'winding',round(row['global_winding'],6),flush=True)
    np.savez(D/'triangle_texture_rgb.npz',triangle_rgb=tri_colours)
    changed=[name for name,sha in frozen.items() if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=sha]
    assert not changed,changed
    results['preservation']={'files_verified':len(frozen),'changed':changed,'validator_run':False,'policy_changed':False}
    (D/'measurements.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('PRESERVED',len(frozen))


if __name__=='__main__':main()
