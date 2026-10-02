"""Phase4F-local source support. No review commands or source/proposal writes.

Garment semantics come from character-local provenance, never component constants.
Source sections use topological edge keys, not rounded section-point adjacency.
"""
import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

POLICY_PATH = Path(__file__).resolve().parents[2]/'Documentation/Phase4F/anatomy_geometry_policy_v2.json'
POLICY = json.loads(POLICY_PATH.read_text(encoding='utf-8'))
EPS = POLICY['numerical_epsilon_cm']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def segment_distances(point, a, b):
    d=b-a
    u=np.clip(((point-a)*d).sum(-1)/np.maximum((d*d).sum(-1),EPS**2),0,1)
    return np.linalg.norm(a+u[...,None]*d-point,axis=-1)


def polygon_contains(poly, point, allowance=0.):
    a=poly[:,:2]; b=np.roll(a,-1,axis=0); p=np.asarray(point)[:2]
    distance=float(segment_distances(p,a,b).min())
    active=(a[:,1]>p[1])!=(b[:,1]>p[1])
    x=a[:,0]+(p[1]-a[:,1])*(b[:,0]-a[:,0])/np.where(abs(b[:,1]-a[:,1])>EPS,b[:,1]-a[:,1],1.)
    inside=bool(np.count_nonzero(active & (x>p[0]))%2)
    return inside or distance<=allowance+EPS, distance


def invalid_polygon(poly):
    """Reject zero area, non-adjacent crossings/touches and overlapping edges."""
    a=poly[:,:2]; b=np.roll(a,-1,axis=0)
    if len(a)<3 or abs(np.sum(a[:,0]*b[:,1]-b[:,0]*a[:,1]))<=EPS: return True
    def cross(x,y): return x[...,0]*y[...,1]-x[...,1]*y[...,0]
    ab=b-a; c=a[None,:,:]; d=b[None,:,:]; aa=a[:,None,:]; bb=b[:,None,:]
    o1=cross(ab[:,None,:],c-aa);o2=cross(ab[:,None,:],d-aa)
    o3=cross((d-c),aa-c);o4=cross((d-c),bb-c)
    bounding=np.all(np.maximum(np.minimum(aa,bb),np.minimum(c,d))<=np.minimum(np.maximum(aa,bb),np.maximum(c,d))+EPS,axis=2)
    crosses=(o1*o2<=EPS**2)&(o3*o4<=EPS**2)&bounding
    n=len(a); i,j=np.indices((n,n)); adjacent=(i==j)|((i-j)%n==1)|((j-i)%n==1)
    return bool(np.any(crosses & ~adjacent))


def nearest_triangle(point, triangles):
    a,b,c=triangles[:,0],triangles[:,1],triangles[:,2]; ab=b-a;ac=c-a
    normal=np.cross(ab,ac); n2=(normal*normal).sum(1)
    projected=point-normal*(np.einsum('ij,ij->i',point-a,normal)/np.maximum(n2,EPS**2))[:,None]
    ap=projected-a;d00=(ab*ab).sum(1);d01=(ab*ac).sum(1);d11=(ac*ac).sum(1)
    d20=(ap*ab).sum(1);d21=(ap*ac).sum(1);denom=d00*d11-d01*d01
    u=(d11*d20-d01*d21)/np.maximum(denom,EPS**2);w=(d00*d21-d01*d20)/np.maximum(denom,EPS**2)
    inside=(n2>EPS**2)&(denom>EPS**2)&(u>=0)&(w>=0)&(u+w<=1)
    candidates=[projected]
    for start,end in [(a,b),(b,c),(c,a)]:
        edge=end-start;q=np.clip(((point-start)*edge).sum(1)/np.maximum((edge*edge).sum(1),EPS**2),0,1)
        candidates.append(start+q[:,None]*edge)
    points=np.stack(candidates);dist2=((points-point)**2).sum(2);dist2[0,~inside]=np.inf
    k,i=np.unravel_index(int(dist2.argmin()),dist2.shape)
    return {'distance_cm':float(np.sqrt(dist2[k,i])),'triangle_index':int(i),'point_cm':points[k,i].tolist()}


class SourceSupport:
    def __init__(self, vertices, faces, components, provenance=None, garment_groups=None):
        self.v=np.asarray(vertices);self.f=np.asarray(faces);self.components=np.asarray(components)
        self.tri=self.v[self.f];self.lo=self.tri[:,:,2].min(1);self.hi=self.tri[:,:,2].max(1)
        self.provenance=provenance or {};self.garments=garment_groups or {};self.cache={}
        _,self.weld=np.unique(np.round(self.v/POLICY['coordinate_weld_cm']).astype(np.int64),axis=0,return_inverse=True)
        edges=np.concatenate([self.weld[self.f[:,[0,1]]],self.weld[self.f[:,[1,2]]],self.weld[self.f[:,[2,0]]]])
        self.edge_counts=Counter(tuple(sorted(pair)) for pair in edges)

    def sections(self,z):
        key=float(z)
        if key in self.cache:return self.cache[key]
        graph=defaultdict(set);points={};sources=defaultdict(set);boundary=set();coplanar=Counter();records=[]
        def add(a,b,pa,pb,tid):
            if a==b or np.linalg.norm(pa-pb)<=EPS:return
            graph[a].add(b);graph[b].add(a);points[a]=pa;points[b]=pb
            sources[a].add(tid);sources[b].add(tid)
        for tid in np.where((self.lo<=z+EPS)&(self.hi>=z-EPS))[0]:
            tri=self.tri[tid];delta=tri[:,2]-z;delta[abs(delta)<=EPS]=0.;ids=self.weld[self.f[tid]]
            hits={}
            if np.all(delta==0):
                for i,j in [(0,1),(1,2),(2,0)]:
                    a,b=('v',int(ids[i])),('v',int(ids[j]));edge=tuple(sorted((a,b)))
                    pa,pb=(tri[i],tri[j]) if a<=b else (tri[j],tri[i])
                    coplanar[edge]+=1;records.append((edge,pa,pb,int(tid)))
                    if self.edge_counts[tuple(sorted((int(ids[i]),int(ids[j]))))]==1:boundary.update([a,b])
                continue
            for i in range(3):
                if delta[i]==0:hits[('v',int(ids[i]))]=tri[i]
            for i,j in [(0,1),(1,2),(2,0)]:
                pair=tuple(sorted((int(ids[i]),int(ids[j]))))
                if delta[i]*delta[j]<0:
                    k=('e',*pair);hits[k]=tri[i]+(tri[j]-tri[i])*(-delta[i]/(delta[j]-delta[i]))
                    if self.edge_counts[pair]==1:boundary.add(k)
                if self.edge_counts[pair]==1:
                    if delta[i]==0:boundary.add(('v',int(ids[i])))
                    if delta[j]==0:boundary.add(('v',int(ids[j])))
            if len(hits)==2:
                (a,pa),(b,pb)=hits.items();add(a,b,pa,pb,int(tid))
        for edge,a,b,tid in records:
            if coplanar[edge]==1:add(*edge,a,b,tid)
        parts=[];seen=set()
        for k in graph:
            if k in seen:continue
            stack=[k];ks=[]
            while stack:
                n=stack.pop()
                if n in seen:continue
                seen.add(n);ks.append(n);stack.extend(graph[n]-seen)
            tids=set().union(*(sources[n] for n in ks));ends=[n for n in ks if len(graph[n])==1]
            degrees=[len(graph[n]) for n in ks]
            parts.append({'keys':ks,'triangles':tids,'components':set(int(self.components[self.f[t,0]]) for t in tids),
                          'ends':ends,'valid':all(d<=2 for d in degrees) and (len(ends)==2 or all(d==2 for d in degrees))})
        result=(graph,points,boundary,parts);self.cache[key]=result;return result

    def loops(self,z,reconstruct=False):
        original,points,boundary,parts=self.sections(z);graph={k:set(ns) for k,ns in original.items()}
        bridges=[];errors=[]
        if reconstruct:
            ends=[(i,k) for i,p in enumerate(parts) if p['valid'] and len(p['ends'])==2 for k in p['ends'] if k in boundary]
            groups=[];tokens=[]
            for part in parts:
                groups.append(set(self.garments[c] for c in part['components'] if c in self.garments))
                tokens.append(set(self.provenance.get(c) for c in part['components']))
            candidates=defaultdict(list)
            for i,(pi,a) in enumerate(ends):
                for j,(pj,b) in enumerate(ends[:i]):
                    if np.linalg.norm(points[a]-points[b])>POLICY['maximum_reconstructed_seam_gap_cm']+EPS:continue
                    compatible=len(tokens[pi])==len(tokens[pj])==1 and None not in tokens[pi] and tokens[pi]==tokens[pj]
                    compatible &= len(groups[pi])<=1 and len(groups[pj])<=1 and bool(groups[pi] or groups[pj])
                    compatible &= not (groups[pi] and groups[pj] and groups[pi]!=groups[pj])
                    if compatible:candidates[i].append(j);candidates[j].append(i)
            matches={i:js[0] for i,js in candidates.items() if len(js)==1 and len(candidates[js[0]])==1}
            # Satellites need both terminals matched directly to one known garment.
            allowed=set()
            for pi,part in enumerate(parts):
                terminal_ids=[i for i,(pj,_) in enumerate(ends) if pj==pi]
                if not part['valid'] or len(terminal_ids)!=2 or not all(i in matches for i in terminal_ids):continue
                if groups[pi]:allowed.add(pi);continue
                targets=[groups[ends[matches[i]][0]] for i in terminal_ids]
                if all(len(g)==1 for g in targets) and targets[0]==targets[1]:allowed.add(pi)
            for i,j in matches.items():
                if i>=j:continue
                pi,a=ends[i];pj,b=ends[j]
                if pi not in allowed or pj not in allowed:continue
                graph[a].add(b);graph[b].add(a)
                bridges.append({'a_cm':points[a].tolist(),'b_cm':points[b].tolist(),'gap_cm':float(np.linalg.norm(points[a]-points[b])),
                                'garment_group':next(iter(groups[pi] or groups[pj]))})
            errors=[{'part':i,'reason':'branched_section' if not p['valid'] else 'unclosed_or_ambiguous_section'} for i,p in enumerate(parts) if not p['valid'] or any(len(graph[k])!=2 for k in p['keys'])]
        loops=[];seen=set()
        for first in graph:
            if first in seen:continue
            stack=[first];ks=[]
            while stack:
                k=stack.pop()
                if k in seen:continue
                seen.add(k);ks.append(k);stack.extend(graph[k]-seen)
            if not all(len(graph[k])==2 for k in ks):continue
            order=[first];previous=None;current=first
            while True:
                nxt=next(k for k in graph[current] if k!=previous)
                if nxt==first:break
                order.append(nxt);previous,current=current,nxt
            poly=np.array([points[k] for k in order])
            if invalid_polygon(poly):errors.append({'reason':'invalid_polygon'});continue
            source_parts=[p for p in parts if any(k in p['keys'] for k in ks)]
            loops.append({'polygon':poly,'components':set().union(*(p['components'] for p in source_parts)),
                          'reconstructed':any(b['a_cm'] in poly.tolist() and b['b_cm'] in poly.tolist() for b in bridges)})
        return loops,bridges,errors

    def body(self,point):
        loops,bridges,errors=self.loops(float(point[2]),reconstruct=True)
        contained=[]
        for loop in loops:
            inside,distance=polygon_contains(loop['polygon'],point,POLICY['placement_allowance_cm'])
            if inside:contained.append({'boundary_distance_cm':distance,'source_components':sorted(loop['components']),'reconstructed':loop['reconstructed']})
        return bool(contained),{'position_cm':np.asarray(point).tolist(),'containing_polygons':contained,'seam_bridges':bridges,'unsupported_fragments':errors}

    def segment_crosses(self,a,b,component_ids):
        tri=self.tri[np.isin(self.components[self.f[:,0]],list(component_ids))]
        direction=b-a; edge1=tri[:,1]-tri[:,0];edge2=tri[:,2]-tri[:,0];h=np.cross(direction,edge2);det=(edge1*h).sum(1)
        valid=abs(det)>EPS;inv=np.zeros_like(det);inv[valid]=1/det[valid];s=a-tri[:,0]
        u=(s*h).sum(1)*inv;q=np.cross(s,edge1);v=(q*direction).sum(1)*inv;t=(q*edge2).sum(1)*inv
        return bool(np.any(valid&(u>=-EPS)&(v>=-EPS)&(u+v<=1+EPS)&(t>EPS)&(t<1-EPS)))

    def finger(self,chain,source_path,expected_path):
        path=np.asarray(chain['path_cm']);centres=np.asarray(chain['phalanges_cm']);source_path=np.asarray(source_path)
        out={'failures':[],'phalanges':[],'support_samples':0,'continuous_segments':0}
        if path.shape!=np.asarray(expected_path).shape or not np.allclose(path,expected_path,rtol=0,atol=EPS):out['failures'].append('path_not_bound_to_track_and_endpoints')
        if not np.allclose(path[0],chain['root_cm'],rtol=0,atol=EPS) or not np.allclose(path[-1],chain['tip_cm'],rtol=0,atol=EPS):out['failures'].append('endpoint_path_mismatch')
        if not np.all(np.diff(source_path[:,2])<-EPS):out['failures'].append('source_track_not_monotonic')
        def supported(p):
            if p[2]<source_path[-1,2]-EPS or p[2]>source_path[0,2]+EPS:return False,set(),'outside_named_track_height'
            reference=np.array([np.interp(p[2],source_path[::-1,2],source_path[::-1,k]) for k in [0,1,2]])
            loops,_,_=self.loops(float(p[2]),reconstruct=False)
            associated=[l for l in loops if polygon_contains(l['polygon'],reference)[0]]
            if len(associated)!=1:return False,set(),'open_or_ambiguous_named_track_section'
            loop=associated[0]
            return polygon_contains(loop['polygon'],p)[0],loop['components'],'outside_named_finger_polygon'
        for i,p in enumerate(centres):
            ok,components,reason=supported(p);nearest=nearest_triangle(p,self.tri)
            vd=float(np.linalg.norm(self.v-p,axis=1).min())
            out['phalanges'].append({'index':i+1,'supported':ok,'nearest_vertex_cm':vd,'nearest_triangle':nearest,'source_components':sorted(components)})
            if not ok:out['failures'].append(f'phalange_{i+1}:{reason}')
        for kind,polyline in [('path',path),('phalange_segment',centres)]:
            for i,(a,b) in enumerate(zip(polyline,polyline[1:])):
                length=np.linalg.norm(b-a);count=max(1,int(np.ceil(length/POLICY['finger_support_sample_spacing_cm'])))
                components=set();valid=True
                for p in np.linspace(a,b,count+1):
                    ok,c,reason=supported(p);out['support_samples']+=1;components.update(c)
                    if not ok:valid=False;out['failures'].append(f'{kind}_{i}:{reason}');break
                out['continuous_segments']+=1
                if valid and self.segment_crosses(a,b,components):out['failures'].append(f'{kind}_{i}:source_surface_crossing')
        return not out['failures'],out


def load_source(work,docs,fit):
    work=Path(work);docs=Path(docs)
    if sha(work/'normalised_geometry.npz')!=fit['input_geometry_sha256']:raise ValueError('proposal source geometry binding mismatch')
    normal=np.load(work/'normalised_geometry.npz');source=np.load(work/'source_geometry.npz')
    if not np.array_equal(normal['triangles'],source['triangles']):raise ValueError('source topology provenance mismatch')
    summary=json.loads((docs/'geometry_summary.json').read_text());objects=summary['objects'];provenance={}
    for component in np.unique(normal['weld_component']):
        tids=np.where(normal['weld_component'][normal['triangles'][:,0]]==component)[0];object_ids=set(int(i) for i in source['object_triangle_ids'][tids]);tokens=[]
        for oid in object_ids:
            obj=objects[oid];materials=obj['polygon_material_counts']
            if len(materials)!=1:continue  # absent per-triangle material provenance is insufficient
            material=int(next(iter(materials)));tokens.append((obj['name'],obj['materials'][material]))
        if len(tokens)==1 and len(object_ids)==1:provenance[int(component)]=tokens[0]
    classification=json.loads((docs/'clothing_classification.json').read_text())
    garments={int(component):role for role,component in classification['diagnostic_component_labels'].items()}
    return SourceSupport(normal['vertices'],normal['triangles'],normal['weld_component'],provenance,garments),{
        'normalised_geometry_sha256':sha(work/'normalised_geometry.npz'),'source_geometry_sha256':sha(work/'source_geometry.npz'),
        'geometry_summary_sha256':sha(docs/'geometry_summary.json'),'garment_classification_sha256':sha(docs/'clothing_classification.json'),
        'garment_anchors':{str(k):v for k,v in garments.items()},'provenance_tokens':{str(k):list(v) for k,v in provenance.items()}}


def apply_policy(checks,fit,work,docs,core):
    migration=[]
    try:mesh,provenance=load_source(work,docs,fit)
    except (ValueError,KeyError,TypeError,IndexError,OSError) as error:
        for check in checks:
            if not check['name'].startswith(('surface_envelope_','finger_surface_')):continue
            migration.append({'name':check['name'],'legacy':copy.deepcopy(check),'corrected_pass':False})
            check.update({'pass':False,'measured':{'failures':['source_provenance_invalid'],'detail':str(error)},
                          'threshold':'valid source geometry binding and provenance required','policy_version':POLICY['version']})
        return {'version':POLICY['version'],'policy_sha256':sha(POLICY_PATH),'legacy_results':migration,
                'source_provenance_error':str(error),'baseline_numeric_thresholds_unchanged':False}
    joints={j['role']:j for j in fit['joints']};track_error=None;track_sha=None
    try:
        tracks=json.loads((Path(docs)/'finger_tracks.json').read_text())['sides']
        if not isinstance(tracks,dict):raise ValueError('invalid source track collection')
        track_sha=sha(Path(docs)/'finger_tracks.json')
    except (ValueError,KeyError,OSError) as error:
        tracks={};track_error=str(error)
    for check in checks:
        if check['name'].startswith('surface_envelope_'):
            role=check['name'][len('surface_envelope_'):];passed,measured=mesh.body(np.array(joints[role]['position_cm']))
            threshold='valid ordered source polygon +/-0.8cm; bounded reciprocal garment seams per policy v2'
        elif check['name'].startswith('finger_surface_'):
            name=check['name'][len('finger_surface_'):];chain=fit['finger_chains'][name]
            matches=[t for t in tracks.get(chain['side'],[]) if t['candidate_id']==chain['track_id']]
            if len(matches)!=1:passed=False;measured={'failures':['missing_or_ambiguous_source_track']}
            else:
                track=matches[0];passed,measured=mesh.finger(chain,core.track_points(track),core.finger_path(track,chain['root_cm'],chain['tip_cm']))
            threshold='closed independent named-finger source containment, path/segment support and no continuous surface crossing per policy v2'
        else:continue
        migration.append({'name':check['name'],'legacy':copy.deepcopy(check),'corrected_pass':passed})
        check['pass']=bool(passed);check['measured']=measured;check['threshold']=threshold
        check['policy_version']=POLICY['version']
    return {'version':POLICY['version'],'policy_sha256':sha(POLICY_PATH),'baseline_numeric_thresholds_unchanged':False,
            'placement_allowance_unchanged_cm':POLICY['placement_allowance_cm'],'source_provenance':provenance,
            'legacy_results':migration,'source_tracks_sha256':track_sha,'source_tracks_error':track_error}


def finger_approval_current(core,chain,approval,key,work):
    """Retained exact Phase4F approval requirements, extracted for regression use."""
    if not chain or approval.get('chain_sha256')!=core.digest(chain) or approval.get('anatomical_valid') is not True:return False
    evidence=Path(approval.get('evidence_artifact','')).resolve()
    if not evidence.is_file() or not evidence.is_relative_to(Path(work).resolve()) or core.file_sha(evidence)!=approval.get('evidence_sha256'):return False
    event=core.read(evidence)
    return event.get('provenance')=='human_editor_action' and event.get('kind')=='review' and key in event['details']['roles'] and event['details']['judgement']=='accept'


def path_separation(core,a,b):
    """Retained 41-sample collision screen and numerical convention, unchanged."""
    sa=np.array([core.path_sample(a.tolist(),u) for u in np.linspace(0,1,41)])
    sb=np.array([core.path_sample(b.tolist(),u) for u in np.linspace(0,1,41)])
    return float(np.sqrt(((sa[:,None,:]-sb[None,:,:])**2).sum(2)).min())
