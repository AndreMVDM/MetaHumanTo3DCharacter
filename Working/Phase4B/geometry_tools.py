import numpy as np
from collections import defaultdict
def nearest_indices(query,points):
    # Deterministic blocked exact nearest-vertex distance, no external model/library.
    out=[]
    for start in range(0,len(query),32):
        q=query[start:start+32];d=((q[:,None,:]-points[None,:,:])**2).sum(2);out.extend(d.argmin(1))
    return np.array(out)
def nearest_distances(query,points):
    ids=nearest_indices(query,points);return np.linalg.norm(query-points[ids],axis=1)
def sections(v,t,z,axis=2):
    tv=v[t];zz=tv[:,:,axis]-z;mask=(zz.min(1)<0)&(zz.max(1)>0);a=tv[mask];dd=zz[mask]
    graph=defaultdict(set);points={}
    for tri,d in zip(a,dd):
        pts=[]
        for i,j in [(0,1),(1,2),(2,0)]:
            if d[i]*d[j]<0:pts.append(tri[i]+(tri[j]-tri[i])*(-d[i]/(d[j]-d[i])))
        if len(pts)!=2:continue
        keys=[tuple(np.round(p/0.005).astype(int)) for p in pts]
        for k,p in zip(keys,pts):points[k]=p
        graph[keys[0]].add(keys[1]);graph[keys[1]].add(keys[0])
    contours=[];seen=set()
    for key in graph:
        if key in seen:continue
        todo=[key];keys=[]
        while todo:
            k=todo.pop()
            if k in seen:continue
            seen.add(k);keys.append(k);todo.extend(graph[k]-seen)
        ps=np.array([points[k] for k in keys]);lo=ps.min(0);hi=ps.max(0)
        if len(ps)<5 or np.linalg.norm(hi-lo)<.15:continue
        contours.append({'centre':((lo+hi)/2).tolist(),'min':lo.tolist(),'max':hi.tolist(),'count':len(ps),'closed':all(len(graph[k])==2 for k in keys),'points':ps.tolist()})
    return sorted(contours,key=lambda q:q['centre'][0])
def body_frame(v):
    eigen,axes=np.linalg.eigh(np.cov(v.T));up=axes[:,-1]
    proj=v@up;ends=[]
    for sign in [-1,1]:
        d=sign*proj;lo=d.min();ids=d<lo+.4;ends.append((int(ids.sum()),sign))
    up*=max(ends)[1] # the broad, planar pair of sole patches rather than crown
    lateral=axes[:,1];lateral-=up*(lateral@up);lateral/=np.linalg.norm(lateral)
    anterior=np.cross(up,lateral)
    # Compare reflection about candidates around the up axis. A fixed index subsample is reproducible.
    # Fit the plane on the paired lower legs/shoes; asymmetric holsters/hair must not bias body left/right.
    pv=v@up;symmetric_region=v[pv<pv.min()+.35*np.ptp(pv)]
    centre=symmetric_region.mean(0);sample=symmetric_region[::max(1,len(symmetric_region)//900)];candidates=[]
    for angle in np.linspace(-.10,.10,9):
        x=lateral*np.cos(angle)+anterior*np.sin(angle);offset=(np.min(symmetric_region@x)+np.max(symmetric_region@x))/2
        reflected=sample-2*(sample@x-offset)[:,None]*x
        ds=nearest_distances(reflected,symmetric_region);candidates.append((float(np.mean(ds)),angle,x,offset))
    error,angle,x,offset=min(candidates,key=lambda q:q[0])
    # Refine the reflection plane from matched pair directions. This is not an FBX-axis assertion.
    for _ in range(3):
        mirrored=sample-2*(sample@x-offset)[:,None]*x;partners=symmetric_region[nearest_indices(mirrored,symmetric_region)]
        delta=sample-partners;delta=delta[np.linalg.norm(delta,axis=1)>8]
        _,ev=np.linalg.eigh(delta.T@delta);refined=ev[:,-1]
        if refined@x<0:refined=-refined
        x=refined;offset=float(np.median(((sample+partners)/2)@x))
    up-=x*(up@x);up/=np.linalg.norm(up);y=np.cross(up,x)
    # Lower-envelope support plane: maximise paired-sole near-plane support over small pitch candidates.
    low=v[(v@up)<(v@up).min()+.10*np.ptp(v@up)];ground_candidates=[]
    for pitch in np.linspace(-.09,.09,181):
        n=up*np.cos(pitch)+y*np.sin(pitch);p=low@n;support=int((p<p.min()+.28).sum())
        ground_candidates.append((support,-abs(pitch),pitch,n))
    support,_,pitch,up=max(ground_candidates,key=lambda q:q[:2]);y=np.cross(up,x)
    zz=v@up;foot=v[zz<zz.min()+.14*np.ptp(zz)]
    # Shoe toe extends further from ankle centre than heel. Compare horizontal shoe extrema to shank centre.
    shank=v[(zz>zz.min()+.14*np.ptp(zz))&(zz<zz.min()+.22*np.ptp(zz))]
    anchor=np.median(shank@y);extrema=np.quantile(foot@y,[.01,.99]);direction=1 if extrema[1]-anchor>anchor-extrema[0] else -1
    plane_normal=x.copy();y*=direction;x=np.cross(up,y);offset*=float(np.sign(x@plane_normal));rot=np.stack([x,y,up],axis=1)
    raw=v@rot;origin=np.array([(raw[:,0].min()+raw[:,0].max())/2,np.median(shank@y),raw[:,2].min()]);raw-=origin
    factor=180/np.ptp(raw[:,2]);normalised=raw*factor
    mirrored=sample-2*(sample@x-offset)[:,None]*x;ds=nearest_distances(mirrored,symmetric_region)
    return normalised,{'rotation_columns_world':rot.tolist(),'origin_body_coordinates_cm':origin.tolist(),'source_height_cm':float(np.ptp(raw[:,2])),'target_height_cm':180,'factor':float(factor),'up_world':up.tolist(),'left_world':x.tolist(),'forward_world':y.tolist(),'ground_endpoint_support':ends,'ground_plane_points':support,'ground_pitch_refinement_rad':pitch,'symmetry_search_mean_cm':error,'symmetry_refined_mean_p95_cm':[float(ds.mean()),float(np.quantile(ds,.95))],'symmetry_angle_candidates':[{'angle_rad':a,'mean_cm':e} for e,a,_,_ in candidates],'shoe_forward_extents_cm':(extrema-anchor).tolist(),'facing_rule':'larger paired shoe extension from lower-shank centre; checked both feet separately downstream','left_rule':'up cross forward in source RH space = anatomical left; canonical left/forward/up frame is LH for UE','probability':False}
