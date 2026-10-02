"""Source-owned oriented planar certificates. No geometry or review writes.

This deliberately has no 3D acceptance fallback. An open oriented source boundary
cannot be turned into a volume by sampling other slices or rays.
"""
import math
from collections import defaultdict
import numpy as np
import geometry_support_policy as v2

EPS=1e-8

def cross(a,b):return float(a[0]*b[1]-a[1]*b[0])

def source_sheets(mesh):
    """Original oriented manifold triangle patches; never rewrites source faces."""
    if hasattr(mesh,'region_sheet_ids'):return mesh.region_sheet_ids
    parent=list(range(len(mesh.f)));edges=defaultdict(list)
    def find(k):
        while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
        return k
    for tid,face in enumerate(mesh.f):
        for a,b in zip(face,np.roll(face,-1)):
            edges[tuple(sorted([int(a),int(b)]))].append((tid,1 if a<b else -1))
    for pairs in edges.values():
        if len(pairs)!=2:continue
        (a,sa),(b,sb)=pairs
        if sa==sb or mesh.components[mesh.f[a,0]]!=mesh.components[mesh.f[b,0]]:continue
        parent[find(b)]=find(a)
    mesh.region_sheet_ids=[find(k) for k in range(len(mesh.f))]
    return mesh.region_sheet_ids

def source_segments(mesh,z,orientation):
    records=[];sheets=source_sheets(mesh)
    for tid in np.where((mesh.lo<=z+EPS)&(mesh.hi>=z-EPS))[0]:
        tri=mesh.tri[tid];delta=tri[:,2]-z;delta[abs(delta)<=EPS]=0
        normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);outward=normal*orientation
        hits={};ids=mesh.weld[mesh.f[tid]]
        for i in range(3):
            if delta[i]==0:hits[('v',int(ids[i]))]=tri[i]
        for i,j in [(0,1),(1,2),(2,0)]:
            if delta[i]*delta[j]<0:
                key=('e',*sorted([int(ids[i]),int(ids[j])]))
                hits[key]=tri[i]+(tri[j]-tri[i])*(-delta[i]/(delta[j]-delta[i]))
        # Horizontal coplanar triangles do not invent volume. Vertical side
        # sections supply their outer edge on an exact end plane.
        if len(hits)!=2 or np.linalg.norm(outward[:2])<=EPS:continue
        (ka,a),(kb,b)=hits.items()
        if np.linalg.norm(b-a)<=EPS:continue
        if cross((b-a)[:2],outward[:2])>0:ka,kb,a,b=kb,ka,b,a
        component=int(mesh.components[mesh.f[tid,0]])
        records.append({'a':a[:2].copy(),'b':b[:2].copy(),'keys':[ka,kb],
                        'triangle_id':int(tid),'raw_vertex_ids':mesh.f[tid].tolist(),
                        'component':component,'sheet_id':int(sheets[tid]),'owner':component,'normal':normal.tolist(),
                        'provenance':mesh.provenance.get(component),'garment':mesh.garments.get(component),
                        'synthetic':False})
    return records

def seam_records(mesh,z,records,budget):
    graph,points,boundary,parts=mesh.sections(z)
    ends=[(i,k) for i,p in enumerate(parts) for k in p['ends'] if k in boundary]
    groups=[{mesh.garments[c] for c in p['components'] if c in mesh.garments} for p in parts]
    tokens=[{mesh.provenance.get(c) for c in p['components']} for p in parts]
    candidates=defaultdict(list)
    for i,(pi,a) in enumerate(ends):
        for j,(pj,b) in enumerate(ends[:i]):
            if np.linalg.norm(points[a]-points[b])>budget+EPS:continue
            compatible=len(tokens[pi])==len(tokens[pj])==1 and None not in tokens[pi] and tokens[pi]==tokens[pj]
            compatible &= len(groups[pi])<=1 and len(groups[pj])<=1 and bool(groups[pi] or groups[pj])
            compatible &= not(groups[pi] and groups[pj] and groups[pi]!=groups[pj])
            if compatible:candidates[i].append(j);candidates[j].append(i)
    match={i:js[0] for i,js in candidates.items() if len(js)==1 and len(candidates[js[0]])==1}
    allowed=set()
    for pi,part in enumerate(parts):
        ids=[i for i,(pj,_) in enumerate(ends) if pj==pi]
        if len(groups[pi])==1:allowed.add(pi);continue
        if not ids or not all(i in match for i in ids):continue
        targets=[groups[ends[match[i]][0]] for i in ids]
        if all(len(g)==1 for g in targets) and all(g==targets[0] for g in targets):allowed.add(pi)
    incident=defaultdict(list)
    for r in records:
        incident[r['keys'][0]].append((1,r));incident[r['keys'][1]].append((-1,r))
    bridges=[];rejected=[]
    for i,j in match.items():
        if i>=j:continue
        pi,a=ends[i];pj,b=ends[j]
        if pi not in allowed or pj not in allowed:continue
        ia=incident[a];ib=incident[b]
        sa={s for s,_ in ia};sb={s for s,_ in ib}
        if len(sa)!=1 or len(sb)!=1 or sa==sb:
            rejected.append({'reason':'ambiguous_or_inconsistent_seam_direction','keys':[str(a),str(b)]});continue
        # A seam must continue arriving source into departing source.
        if next(iter(sa))==1:a,b=b,a;ia,ib=ib,ia
        cs=set(parts[pi]['components'])|set(parts[pj]['components'])
        bridges.append({'a':points[a][:2].copy(),'b':points[b][:2].copy(),'keys':[a,b],
                        'triangle_id':None,'endpoint_triangle_ids':sorted({r['triangle_id'] for _,r in ia+ib}),
                        'component':None,'sheet_id':None,'components':sorted(cs),'owner':None,'normal':None,
                        'provenance':next(iter(tokens[pi])),'garment':next(iter(groups[pi] or groups[pj])),
                        'synthetic':True,'gap_cm':float(np.linalg.norm(points[a]-points[b]))})
    # Only independently eligible seam links create common ownership scopes.
    parent={int(c):int(c) for c in np.unique(mesh.components)}
    def find(c):
        while parent[c]!=c:c=parent[c]
        return c
    for b in bridges:
        cs=b['components'];root=find(cs[0])
        for c in cs:parent[find(c)]=root
    for r in records:r['owner']=find(r['component'])
    for b in bridges:b['owner']=find(b['components'][0])
    return bridges,rejected

def arrangement(records):
    """Split proper crossings, T contacts and all collinear overlap endpoints.

    Ownership scopes are supplied separately. Numerical equality is EPS, not the
    placement/seam allowance. Multiplicity and source records survive splitting.
    """
    splits=[[0.,1.] for _ in records];contacts=0
    for i,r in enumerate(records):
        a=r['a'];u=r['b']-a;lu=np.linalg.norm(u)
        for j in range(i):
            s=records[j];b=s['a'];v=s['b']-b;lv=np.linalg.norm(v);den=cross(u,v)
            if abs(den)>EPS*lu*lv:
                t=cross(b-a,v)/den;q=cross(b-a,u)/den
                if -EPS/lu<=t<=1+EPS/lu and -EPS/lv<=q<=1+EPS/lv:
                    splits[i].append(float(np.clip(t,0,1)));splits[j].append(float(np.clip(q,0,1)));contacts+=1
            elif abs(cross(b-a,u))<=EPS*lu:
                for p in [s['a'],s['b']]:
                    t=float((p-a)@u/(u@u))
                    if -EPS/lu<=t<=1+EPS/lu:splits[i].append(float(np.clip(t,0,1)))
                for p in [r['a'],r['b']]:
                    q=float((p-b)@v/(v@v))
                    if -EPS/lv<=q<=1+EPS/lv:splits[j].append(float(np.clip(q,0,1)))
    points=[];buckets=defaultdict(list)
    def node(p):
        key=tuple(np.floor(p/EPS).astype(np.int64))
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                for k in buckets[(key[0]+dx,key[1]+dy)]:
                    if np.linalg.norm(points[k]-p)<=EPS:return k
        k=len(points);points.append(p);buckets[key].append(k);return k
    edges=defaultdict(list)
    for i,(r,ts) in enumerate(zip(records,splits)):
        ts=sorted(set(ts))
        for t,q in zip(ts,ts[1:]):
            a=r['a']+(r['b']-r['a'])*t;b=r['a']+(r['b']-r['a'])*q
            if np.linalg.norm(b-a)<=EPS:continue
            x,y=node(a),node(b)
            if x==y:continue
            key=tuple(sorted([x,y]));edges[key].append({'record':i,'direction':1 if key==(x,y) else -1,'range':[t,q]})
    return np.array(points),edges,contacts

def strongly_connected(vertices,adj):
    # Iterative Kosaraju avoids source-size recursion limits.
    seen=set();order=[]
    for root in vertices:
        if root in seen:continue
        stack=[(root,False)]
        while stack:
            k,finished=stack.pop()
            if finished:order.append(k);continue
            if k in seen:continue
            seen.add(k);stack.append((k,True));stack.extend((n,False) for n in adj[k] if n not in seen)
    reverse=defaultdict(set)
    for a,ns in adj.items():
        for b in ns:reverse[b].add(a)
    labels={};label=0
    for root in reversed(order):
        if root in labels:continue
        stack=[root]
        while stack:
            k=stack.pop()
            if k in labels:continue
            labels[k]=label;stack.extend(reverse[k]-labels.keys())
        label+=1
    return labels

def closed_cycles(points,edges,records):
    directed={};adj=defaultdict(set);ambiguous=[]
    for key,origins in edges.items():
        signs={o['direction'] for o in origins}
        if len(signs)!=1:ambiguous.append(key);continue
        a,b=key if next(iter(signs))==1 else key[::-1]
        directed[key]=(a,b);adj[a].add(b)
    labels=strongly_connected(set(k for e in directed.values() for k in e),adj)
    # A tail cannot participate in any directed cycle. Do not discard it from
    # evidence, and never supply its missing edge from another slice.
    closed={k:e for k,e in directed.items() if labels[e[0]]==labels[e[1]]}
    graph=defaultdict(set)
    for a,b in closed.values():graph[a].add(b);graph[b].add(a)
    neighbours={k:sorted(ns,key=lambda n:math.atan2(*(points[n]-points[k])[::-1])) for k,ns in graph.items()}
    used=set();cycles=[];rejected=[]
    for a in graph:
        for b in graph[a]:
            if (a,b) in used:continue
            start=(a,b);edge=start;order=[]
            while edge not in used:
                used.add(edge);x,y=edge;order.append(x);ns=neighbours[y]
                edge=(y,ns[(ns.index(x)-1)%len(ns)])
                if edge==start:break
            if edge!=start:continue
            # Decompose touching weak boundaries; preserve cycle orientation.
            path=[]
            for k in order+[order[0]]:
                if k not in path:path.append(k);continue
                at=path.index(k);part=path[at:];path=path[:at+1]
                if len(part)<3:continue
                pairs=list(zip(part,part[1:]+part[:1]));poly=points[part]
                area=sum(cross(x,y) for x,y in zip(poly,np.roll(poly,-1,axis=0)))/2
                if abs(area)<=EPS:continue
                orientation=[closed[tuple(sorted(e))]==e for e in pairs]
                if not all(orientation):
                    if any(orientation):rejected.append({'reason':'ambiguous_branch_or_inconsistent_boundary_orientation','area_cm2':area})
                    continue
                poly3=np.column_stack([poly,np.zeros(len(poly))])
                if v2.invalid_polygon(poly3):rejected.append({'reason':'invalid_cycle'});continue
                source=sorted({o['record'] for e in pairs for o in edges[tuple(sorted(e))]})
                cycles.append({'polygon':poly3,'area_cm2':area,'records':source,'edge_nodes':pairs})
    # Directed boundaries appear only once; opposite half-edge walk is discarded.
    return cycles,{'ambiguous_coincident_edges':[list(k) for k in ambiguous],
                   'unused_noncycle_edges':len(directed)-len(closed),'rejected_boundaries':rejected}

def original_owned_cycles(records):
    """Retain independently closed oriented source loops as separate layers.

    Intersections with another fold do not erase an already supported loop.
    These are not v2 pass-throughs: provenance, orientation, exact continuity,
    simplicity and explicit holes still apply.
    """
    graph=defaultdict(set);edges=defaultdict(list);points={};invalid=set()
    for i,r in enumerate(records):
        a,b=r['keys'];key=tuple(sorted([a,b]));edges[key].append((i,a,b))
        graph[a].add(b);graph[b].add(a)
        for k,p in [(a,r['a']),(b,r['b'])]:
            if k in points and np.linalg.norm(points[k]-p)>EPS:invalid.add(k)
            points[k]=p
    seen=set();cycles=[]
    for root in graph:
        if root in seen:continue
        pending=[root];part=[]
        while pending:
            k=pending.pop()
            if k in seen:continue
            seen.add(k);part.append(k);pending.extend(graph[k]-seen)
        if any(len(graph[k])!=2 or k in invalid for k in part):continue
        order=[root];previous=None;current=root
        while True:
            nxt=next(n for n in graph[current] if n!=previous)
            if nxt==root:break
            order.append(nxt);previous,current=current,nxt
        pairs=list(zip(order,order[1:]+order[:1]));directions=[];ids=[]
        for a,b in pairs:
            signs={1 if (x,y)==(a,b) else -1 for _,x,y in edges[tuple(sorted([a,b]))]}
            if len(signs)!=1:break
            directions.append(next(iter(signs)));ids.extend(i for i,_,_ in edges[tuple(sorted([a,b]))])
        if len(directions)!=len(pairs) or len(set(directions))!=1:
            poly=np.column_stack([np.array([points[k] for k in order]),np.zeros(len(order))])
            if not v2.invalid_polygon(poly):
                cycles.append({'polygon':poly,'records':sorted({i for a,b in pairs for i,_,_ in edges[tuple(sorted([a,b]))]}),
                               'uncertain_orientation':True})
            continue
        if directions[0]<0:order=order[::-1]
        poly=np.column_stack([np.array([points[k] for k in order]),np.zeros(len(order))])
        if v2.invalid_polygon(poly):continue
        area=sum(cross(a,b) for a,b in zip(poly,np.roll(poly,-1,axis=0)))/2
        cycles.append({'polygon':poly,'area_cm2':area,'records':sorted(set(ids)),
                       'certificate':'original_owned_oriented_loop'})
    return cycles

def unique_cycles(cycles):
    """Deduplicate equivalent certificates without losing any source origins."""
    result={}
    for c in cycles:
        poly=[p[:2].copy() for p in c['polygon']];changed=True
        while changed and len(poly)>3:
            changed=False
            for i,p in enumerate(poly):
                a=poly[i-1];b=poly[(i+1)%len(poly)];v=b-a
                if np.linalg.norm(v)>EPS and abs(cross(p-a,v))<=EPS*np.linalg.norm(v) and (p-a)@(p-b)<=EPS**2:
                    poly.pop(i);changed=True;break
        keys=[tuple(np.round(p/EPS).astype(np.int64)) for p in poly]
        first=min(range(len(keys)),key=lambda i:keys[i]);key=tuple(keys[first:]+keys[:first])
        if key in result:result[key]['records']=sorted(set(result[key]['records'])|set(c['records']))
        else:result[key]=c
    return list(result.values())

def evaluate(mesh,point,orientation,policy,binding=None):
    if orientation not in [-1.,1.]:
        return False,{'failures':['missing_or_invalid_source_orientation'],'three_dimensional_fallback':False}
    p=np.asarray(point);records=source_segments(mesh,float(p[2]),orientation)
    bridges,seam_errors=seam_records(mesh,float(p[2]),records,policy['maximum_reconstructed_seam_gap_cm'])
    records+=bridges;owners=sorted({r['owner'] for r in records});regions=[];diagnostics=[];owned_cycles=[];uncertain_cycles=[]
    for owner in owners:
        source=[r for r in records if r['owner']==owner]
        points,edges,contacts=arrangement(source);cycles,detail=closed_cycles(points,edges,source)
        original=original_owned_cycles(source)
        uncertain_cycles.extend((owner,c,source) for c in original if c.get('uncertain_orientation'))
        cycles=unique_cycles(cycles+[c for c in original if not c.get('uncertain_orientation')])
        positive=[c for c in cycles if c['area_cm2']>0];negative=[c for c in cycles if c['area_cm2']<0]
        owned_cycles.extend((owner,c,source) for c in cycles)
        hole_parents={}
        for i,h in enumerate(negative):
            containers=[c for c in positive if all(v2.polygon_contains(c['polygon'],q)[0] for q in h['polygon'])]
            if containers:hole_parents[i]=min(containers,key=lambda c:c['area_cm2'])
        for c in positive:
            local_holes=[h for i,h in enumerate(negative) if hole_parents.get(i) is c]
            holes=[h for h in local_holes if v2.polygon_contains(h['polygon'],p)[0]]
            inside,distance=v2.polygon_contains(c['polygon'],p,policy['placement_allowance_cm'])
            if not inside or holes:continue
            # An inward loop crossing this positive boundary leaves interior
            # ownership unresolved. A certified island wholly inside a cavity
            # is different: its own positive boundary supplies filled support.
            crossing_void=[h for h in negative if v2.polygon_contains(h['polygon'],p)[0]
                           and not all(v2.polygon_contains(h['polygon'],q)[0] for q in c['polygon'])
                           and not all(v2.polygon_contains(c['polygon'],q)[0] for q in h['polygon'])]
            if crossing_void:continue
            # The exterior placement allowance cannot bridge a cavity, including
            # the void around a filled island nested within that cavity.
            if not v2.polygon_contains(c['polygon'],p)[0] and any(v2.polygon_contains(h['polygon'],p)[0] for h in negative):continue
            origins=[source[i] for i in c['records']]
            if any(r['provenance'] is None for r in origins):continue
            components={r['component'] for r in origins if r['component'] is not None}
            groups={r['garment'] for r in origins if r['garment'] is not None}
            if binding is None:continue
            anchored=bool(groups) and groups.issubset(set(binding.get('garment_groups',[])))
            associated=components.issubset(set(binding.get('source_components',[]))) and not groups
            if not anchored and not associated:continue
            regions.append({'boundary_distance_cm':distance,'source_components':sorted({r['component'] for r in origins if r['component'] is not None}),
                            'source_triangle_ids':sorted({r['triangle_id'] for r in origins if r['triangle_id'] is not None}),
                            'source_sheet_ids':sorted({r['sheet_id'] for r in origins if r['sheet_id'] is not None}),
                            'owner':owner,'garment_groups':sorted({r['garment'] for r in origins if r['garment'] is not None}),
                            'provenance_tokens':sorted({r['provenance'] for r in origins}),
                            'boundary_xy_cm':c['polygon'][:,:2].tolist(),'area_cm2':c['area_cm2'],
                            'hole_boundaries_xy_cm':[h['polygon'][:,:2].tolist() for h in local_holes],
                            'reconstructed':any(r['synthetic'] for r in origins)})
        diagnostics.append({'owner_components':sorted({r['component'] for r in source if r['component'] is not None}),
                            'arrangement_contacts':contacts,'closed_oriented_cycles':len(cycles),
                            'positive_cycles':len(positive),'negative_cycles':len(negative),**detail})
    # A separately connected inward shell may represent a true cavity. Common
    # provenance is never used to close a boundary, but uncertainty about a
    # nested cavity must veto a proposed outer support certificate.
    cavity_veto=[];kept=[]
    for region in regions:
        veto=False;outer=np.column_stack([np.array(region['boundary_xy_cm']),np.zeros(len(region['boundary_xy_cm']))])
        for owner,c,source in owned_cycles:
            if owner==region['owner'] or c['area_cm2']>=0:continue
            if not v2.polygon_contains(c['polygon'],p)[0]:continue
            origins=[source[i] for i in c['records']]
            tokens={r['provenance'] for r in origins};groups={r['garment'] for r in origins if r['garment'] is not None}
            if tokens.intersection(region['provenance_tokens']) and (not groups or not region['garment_groups'] or groups.intersection(region['garment_groups'])):
                veto=True;cavity_veto.append({'region_owner':region['owner'],'nested_owner':owner,'reason':'nested_inward_shell_cavity_or_ambiguous_ownership'})
        if not veto:kept.append(region)
    regions=kept
    kept=[]
    for region in regions:
        outer=np.column_stack([np.array(region['boundary_xy_cm']),np.zeros(len(region['boundary_xy_cm']))]);veto=False
        for owner,c,source in uncertain_cycles:
            if not v2.polygon_contains(c['polygon'],p)[0]:continue
            # An independently filled inner layer need not rely on an uncertain
            # larger outer shell. An uncertain nested/crossing shell can be a
            # cavity and must not silently disappear from interior semantics.
            if all(v2.polygon_contains(c['polygon'],q)[0] for q in outer):continue
            tokens={source[i]['provenance'] for i in c['records']}
            if owner==region['owner'] or tokens.intersection(region['provenance_tokens']):
                veto=True;cavity_veto.append({'region_owner':region['owner'],'uncertain_owner':owner,'reason':'nested_or_crossing_shell_orientation_uncertain'})
        if not veto:kept.append(region)
    regions=kept
    def serial(r):
        return {k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in r.items()}
    return bool(regions),{'position_cm':p.tolist(),'containing_regions':regions,
                          'seam_bridges':[serial(b) for b in bridges],'seam_rejections':seam_errors,
                          'source_section_records':[serial(r) for r in records],
                          'ownership_arrangements':diagnostics,'cavity_veto':cavity_veto,'failures':[] if regions else ['no_owned_closed_oriented_region'],
                          'orientation_handedness':orientation,'role_owner_binding':binding,'three_dimensional_fallback':False}
