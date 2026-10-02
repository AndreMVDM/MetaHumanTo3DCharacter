"""Read-only source-scoped 3D proof research; never supplies an acceptance gate."""
import hashlib,heapq,json,sys
from collections import defaultdict,deque
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
import geometry_support_policy as v2
import body_region_support as body
from diagnose_john_geometry import ray_hits
P=Path(__file__).resolve().parents[2];D=P/'Documentation/Phase4F/JohnLocalRegionPolicy';W=P/'Working/Phase4F/John';O=P/'Documentation/Phase4F/John'
fit=json.loads((O/'current_proposal.json').read_text());mesh,_=v2.load_source(W,O,fit)
p=np.array(next(j['position_cm'] for j in fit['joints'] if j['role']=='thigh_r'))
# Ownership is from the existing named garment classification, never an ID.
components=[c for c,g in mesh.garments.items() if g=='trouser_region']
assert len(components)==1
component=components[0];tids=np.where(mesh.components[mesh.f[:,0]]==component)[0]
f=mesh.f[tids];edges=defaultdict(list)
for local,face in enumerate(f):
    for a,b in zip(face,np.roll(face,-1)):edges[tuple(sorted([int(a),int(b)]))].append((local,1 if a<b else -1))
active=set(range(len(f)));queue=deque(edges);by_face=defaultdict(list)
for key,origins in edges.items():
    for t,_ in origins:by_face[t].append(key)
iterations=0
while queue:
    key=queue.popleft();origins=[(t,s) for t,s in edges[key] if t in active]
    # A source-only oriented closed 2-chain cannot use a sole remaining face
    # or any faces with no possible opposite incidence on that edge.
    if not origins or len({s for _,s in origins})>1:continue
    for t,_ in origins:
        active.remove(t);iterations+=1;queue.extend(by_face[t])

source=[r for r in body.source_segments(mesh,float(p[2]),-1.) if r['component']==component]
a=np.array([r['a'] for r in source]);b=np.array([r['b'] for r in source]);v=b-a
endpoints=np.vstack([a,b]);local=endpoints[(endpoints[:,0]<-14)&(endpoints[:,0]>-16)&(endpoints[:,1]>4.5)&(endpoints[:,1]<6.)]
nodes=[p[:2],np.array([-25.,20.])]
# Offsets only construct a collision-free research path. They are not support
# allowances, repairs, seams or acceptance thresholds.
for q in local:
    for radius in [.0001,.001,.01]:
        for angle in np.linspace(0,2*np.pi,8,endpoint=False):nodes.append(q+radius*np.array([np.cos(angle),np.sin(angle)]))
nodes=np.unique(np.array(nodes),axis=0)
start=int(np.argmin(np.linalg.norm(nodes-p[:2],axis=1)));target=int(np.argmin(np.linalg.norm(nodes-[-25.,20.],axis=1)))
def clear(x,y):
    u=y-x;den=u[0]*v[:,1]-u[1]*v[:,0];delta=a-x;valid=abs(den)>1e-14
    t=np.divide(delta[:,0]*v[:,1]-delta[:,1]*v[:,0],den,out=np.zeros_like(den),where=valid)
    q=np.divide(delta[:,0]*u[1]-delta[:,1]*u[0],den,out=np.zeros_like(den),where=valid)
    if np.any(valid&(t>=-1e-8/np.linalg.norm(u))&(t<=1+1e-8/np.linalg.norm(u))&(q>=-1e-8/np.linalg.norm(v,axis=1))&(q<=1+1e-8/np.linalg.norm(v,axis=1))):return False
    if np.any(v2.segment_distances(x,a,b)<1e-8) or np.any(v2.segment_distances(y,a,b)<1e-8):return False
    if np.any(v2.segment_distances(a,x,y)<1e-8) or np.any(v2.segment_distances(b,x,y)<1e-8):return False
    # Reject collinear contact rather than treating it as a clear path.
    col=~valid&(abs(delta[:,0]*u[1]-delta[:,1]*u[0])<1e-12)
    if np.any(col):
        t0=(delta@u)/(u@u);t1=((b-x)@u)/(u@u)
        if np.any(col&(np.maximum(t0,t1)>=0)&(np.minimum(t0,t1)<=1)):return False
    return True
cost={start:0.};parent={};pending=[(0.,start)];visited=set()
while pending:
    _,i=heapq.heappop(pending)
    if i in visited:continue
    visited.add(i)
    if i==target:break
    for j in range(len(nodes)):
        if j in visited or j==i:continue
        distance=cost[i]+float(np.linalg.norm(nodes[j]-nodes[i]))
        if distance>=cost.get(j,float('inf')) or not clear(nodes[i],nodes[j]):continue
        cost[j]=distance;parent[j]=i
        heapq.heappush(pending,(distance+float(np.linalg.norm(nodes[j]-nodes[target])),j))
path=[]
if target in visited:
    k=target
    while k!=start:path.append(nodes[k]);k=parent[k]
    path.append(nodes[start]);path=np.array(path[::-1])
checks=[]
if len(path):
    path3=np.column_stack([path,np.full(len(path),p[2])])
    tri=mesh.tri[tids]
    for x,y in zip(path3,path3[1:]):
        length=np.linalg.norm(y-x);hits=[h for h in ray_hits(x,(y-x)/length,tri) if h['distance_cm']<=length]
        assert not hits,hits
        clearance=min(float(v2.segment_distances(x[:2],a,b).min()),float(v2.segment_distances(y[:2],a,b).min()),
                      float(v2.segment_distances(a,x[:2],y[:2]).min()),float(v2.segment_distances(b,x[:2],y[:2]).min()))
        assert clearance>1e-8
        checks.append({'length_cm':float(length),'source_triangle_intersections':len(hits),'minimum_plane_source_clearance_cm':clearance})
    # The target is outside all garment XY extents. Continue towards -X
    # forever at this Y, which is above every section trace.
    assert path[-1,1]>max(a[:,1].max(),b[:,1].max())
else:path3=np.empty((0,3))
result={'mode':'research only; no acceptance rule','proposal_sha256':v2.sha(O/'current_proposal.json'),
        'normalised_geometry_sha256':v2.sha(W/'normalised_geometry.npz'),'pivot_cm':p.tolist(),
        'scoped_component':int(component),'scope_authority':'existing trouser_region classification',
        'whole_triangle_closed_chain_necessary_condition':{'input_faces':len(f),'forced_zero_faces':iterations,'remaining_faces':len(active),
           'remaining_original_triangle_ids':tids[sorted(active)].tolist(),
           'limitation':'Necessary condition only; does not exhaust arrangements that split intersecting source triangles.'},
        'escape_path':{'found':bool(len(path3)),'path_cm':path3.tolist(),'segment_readbacks':checks,
           'terminal_unbounded_direction':[-1,0,0] if len(path3) else None,
           'interpretation':'A complete collision-free polygonal escape path contradicts a bounded cell in this component-scoped source surface complement. It is a rejection witness, not a finite-ray acceptance test.'},
        'proposed_3d_acceptance_implemented':False}
(D/'right_thigh_3d_research.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
if len(path3):
    from PIL import Image,ImageDraw,ImageFont
    canvas=Image.new('RGB',(1500,820),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    draw.text((20,15),'Right thigh: source-only exterior escape witness (research, not an acceptance rule)',fill='#142c40',font=font)
    draw.text((20,48),'Blue = actual trouser section; green = exhaustive collision-free path; red = unchanged accepted pivot.',fill='#142c40',font=font)
    pivot_xy=p[:2];turn=path3[1,:2]
    views=[((20,95,750,740),np.array([-27.,-18.]),np.array([22.,22.])),((790,95,1470,740),turn-.006,turn+.006)]
    for box,low,high in views:
        x0,y0,x1,y1=box;scale=min((x1-x0)/(high[0]-low[0]),(y1-y0)/(high[1]-low[1]));centre=(low+high)/2
        def project(q):return ((x0+x1)/2+(q[0]-centre[0])*scale,(y0+y1)/2-(q[1]-centre[1])*scale)
        # Clip the source/path lines at the viewport; clipping is presentation.
        def line(x,y,colour,width):
            u=y-x;t0=0.;t1=1.
            for k in [0,1]:
                if abs(u[k])<1e-15:
                    if x[k]<low[k] or x[k]>high[k]:return
                else:
                    ta=(low[k]-x[k])/u[k];tb=(high[k]-x[k])/u[k];t0=max(t0,min(ta,tb));t1=min(t1,max(ta,tb))
            if t0<=t1:draw.line([project(x+t0*u),project(x+t1*u)],fill=colour,width=width)
        draw.rectangle(box,outline='#bdbdbd')
        for x,y in zip(a,b):line(x,y,'#256bad',2)
        for x,y in zip(path3[:,:2],path3[1:,:2]):line(x,y,'#178a4d',3)
        x,y=project(pivot_xy)
        if x0<x<x1 and y0<y<y1:draw.line([(x-7,y),(x+7,y)],fill='#d22a40',width=3);draw.line([(x,y-7),(x,y+7)],fill='#d22a40',width=3)
    draw.text((20,775),'The route stays at the accepted Z. No geometry, pivot, seam or review evidence was changed.',fill='#142c40',font=font)
    canvas.save(D/'right_thigh_escape.png')
print(json.dumps({'faces':len(f),'forced_zero':iterations,'remaining':len(active),'escape_path_found':bool(len(path3)),'escape_segments':len(checks)},indent=2))
