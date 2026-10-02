"""Reusable skeletal weight/stress analysis. No anatomy solving or prior writes."""
import json, sys, math, hashlib
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4E';O=P/'Documentation/Phase4E'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,d):(O/n).write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
def matrix(t):
    x,y,z,w=t['rotation_xyzw'];m=np.eye(4)
    m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])*np.array(t['scale'])[None,:]
    m[:3,3]=t['translation'];return m
def rotation(axis,angle):
    a=np.array(axis,dtype=float);a/=np.linalg.norm(a);x,y,z=a;K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    return np.eye(3)+math.sin(angle)*K+(1-math.cos(angle))*(K@K)
def swing(a,b):
    a=np.array(a,dtype=float);b=np.array(b,dtype=float);a/=np.linalg.norm(a);b/=np.linalg.norm(b)
    c=np.cross(a,b);n=np.linalg.norm(c)
    if n<1e-9:return np.eye(3)
    return rotation(c,math.atan2(n,np.dot(a,b)))
def smoothstep(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
class Model:
    def __init__(self):
        self.data=load(W/'baseline_skin.json');d=self.data
        self.v=np.array(d['geometry']['vertices']);self.h=np.c_[self.v,np.ones(len(self.v))];self.tri=np.array(d['geometry']['triangles']);self.names=list(d['reference']['bones']);self.bi={n:i for i,n in enumerate(self.names)};self.parents=d['parents']
        self.ref=np.array([matrix(d['reference']['bones'][n]['component']) for n in self.names]);self.inv=np.linalg.inv(self.ref);self.pos=self.ref[:,:3,3]
        self.weights=self.dense(d['weights']);self.restarea=np.linalg.norm(np.cross(self.v[self.tri[:,1]]-self.v[self.tri[:,0]],self.v[self.tri[:,2]]-self.v[self.tri[:,0]]),axis=1)
        self.edges=np.unique(np.sort(np.concatenate([self.tri[:,[0,1]],self.tri[:,[1,2]],self.tri[:,[2,0]]]),axis=1),axis=0)
        self.edgelen=np.linalg.norm(self.v[self.edges[:,1]]-self.v[self.edges[:,0]],axis=1)
        self.adj=[[] for _ in self.v]
        for a,b in self.edges:self.adj[a].append(b);self.adj[b].append(a)
        # Connectivity with positional seam weld for analysis only. Actual topology is unchanged.
        parent=np.arange(len(self.v))
        def find(x):
            while x!=parent[x]:parent[x]=parent[parent[x]];x=parent[x]
            return x
        def union(a,b):parent[find(a)]=find(b)
        for a,b in self.edges:union(a,b)
        seen={}
        for i,p in enumerate(self.v):
            key=tuple(np.round(p,5))
            if key in seen:union(i,seen[key])
            else:seen[key]=i
        self.components=np.array([find(i) for i in range(len(self.v))]);self.regions=self.region_masks()
        self.samples=load(P/'Documentation/Phase4D/runtime_samples.json')['samples']
        self.fingers=load(P/'Documentation/Phase4D/finger_pose_samples.json')
        if isinstance(self.fingers,dict):self.fingers=self.fingers['samples']
        self.poses=self.pose_suite()
    def dense(self,rows):
        w=np.zeros((len(self.v),len(self.names)))
        for i,row in enumerate(rows):
            for b,x in row:w[i,b]+=x
        return w
    def pack(self,w,max_influences=5):
        w=np.maximum(w,0);ix=np.argsort(-w,axis=1)[:,:max_influences];out=np.zeros_like(w);np.put_along_axis(out,ix,np.take_along_axis(w,ix,axis=1),axis=1)
        out/=out.sum(axis=1)[:,None];return out
    def rows(self,w):return [[[int(b),float(row[b])] for b in np.argsort(-row) if row[b]>1e-7] for row in w]
    def descendants(self,n):
        result=[n];todo=[n]
        while todo:
            p=todo.pop();children=[k for k,v in self.parents.items() if v==p];result+=children;todo+=children
        return [self.bi[k] for k in result]
    def rotate_branch(self,pose,n,R):
        ids=self.descendants(n);p=pose[self.bi[n],:3,3].copy();M=np.eye(4);M[:3,:3]=R;M[:3,3]=p-R@p
        pose[ids]=M@pose[ids]
    def from_sample(self,s):return np.array([matrix(s['bones'][n]['component']) for n in self.names])
    def pose_suite(self):
        poses={'neutral':self.ref.copy()}
        for name,angle in [('arms_45',-45),('arms_horizontal',0),('arms_overhead',80)]:
            pose=self.ref.copy()
            for side,sign in [('l',1),('r',-1)]:
                n='upperarm_'+side;i=self.bi[n];j=self.bi['lowerarm_'+side]
                target=[sign*math.cos(math.radians(angle)),0,math.sin(math.radians(angle))]
                self.rotate_branch(pose,n,swing(pose[j,:3,3]-pose[i,:3,3],target))
            poses[name]=pose
        pose=poses['arms_horizontal'].copy()
        for side in ['l','r']:self.rotate_branch(pose,'lowerarm_'+side,rotation(pose[self.bi['lowerarm_'+side],:3,2],math.pi/2))
        poses['elbows_bent']=pose
        pose=self.ref.copy()
        for side,sign in [('l',1),('r',-1)]:self.rotate_branch(pose,'thigh_'+side,rotation([0,1,0],-sign*math.radians(25)))
        poses['wide_stance']=pose
        pose=self.ref.copy();pose[self.descendants('pelvis'),:3,3]+=[0,0,-25]
        for side in ['l','r']:
            self.rotate_branch(pose,'thigh_'+side,rotation([1,0,0],math.radians(-50)))
            self.rotate_branch(pose,'calf_'+side,rotation([1,0,0],math.radians(90)))
        poses['knee_bend']=pose
        for role in ['idle','walk','run','reach']:
            seq=[s for s in self.samples if s['role']==role]
            for fraction in [0,.25,.5,.75]:
                s=min(seq,key=lambda s:abs(s['fraction']-fraction));poses[f'{role}_{fraction}']=self.from_sample(s)
        for i,s in enumerate(self.fingers):
            if i%2==1:poses[f'finger_{i}']=self.from_sample(s)
        return poses
    def deform(self,w,pose):
        out=np.zeros_like(self.v);ms=pose@self.inv
        for b in range(len(self.names)):
            ix=np.flatnonzero(w[:,b]>0)
            if len(ix):out[ix]+=(self.h[ix]@ms[b].T)[:,:3]*w[ix,b,None]
        return out
    def region_masks(self):
        v=self.v;p=self.pos[self.bi['pelvis']];span=np.linalg.norm(self.pos[self.bi['thigh_l']]-self.pos[self.bi['thigh_r']]);h=p[2];x=v[:,0]-p[0]
        torso=(v[:,2]>h-span*.9)&(v[:,2]<h+span*.65)&(abs(x)<span*.8)
        return {'front_pants':torso&(v[:,1]>p[1]+span*.08),'back_hips':torso&(v[:,1]<p[1]-span*.08),'waistband':torso&(v[:,2]>h+span*.1),
                'shoulders':(v[:,2]>self.pos[self.bi['spine_03'],2]-span*.65)&(v[:,2]<self.pos[self.bi['neck_01'],2])&(abs(x)>span*.45)&(abs(x)<span*1.4),
                'upper_torso':(v[:,2]>self.pos[self.bi['spine_02'],2])&(v[:,2]<self.pos[self.bi['neck_01'],2])&(abs(x)<span*.8),
                'left_sole':(v[:,0]>span*.4)&(v[:,2]<2),'right_sole':(v[:,0]<-span*.4)&(v[:,2]<2)}
    def measure(self,w,pose):
        out=self.deform(w,pose);t=out[self.tri];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1);rat=area/np.maximum(self.restarea,1e-8)
        er=np.linalg.norm(out[self.edges[:,1]]-out[self.edges[:,0]],axis=1)/np.maximum(self.edgelen,1e-8)
        result={}
        for n,mask in self.regions.items():
            ti=np.all(mask[self.tri],axis=1)&(self.restarea>1e-6);ei=np.all(mask[self.edges],axis=1)&(self.edgelen>1e-5)
            r=rat[ti];e=er[ei]
            result[n]={'vertices':int(mask.sum()),'triangles':int(ti.sum()),'area_p01_median_p99':np.quantile(r,[.01,.5,.99]).tolist() if len(r) else [],'area_below_0_5':int((r<.5).sum()),'area_below_0_1':int((r<.1).sum()),'area_above_2':int((r>2).sum()),'edge_p01_median_p99':np.quantile(e,[.01,.5,.99]).tolist() if len(e) else [],'edge_log_strain_rms':float(np.sqrt(np.mean(np.log(np.clip(e,1e-5,1e5))**2))) if len(e) else 0,'min_z_cm':float(out[mask,2].min()) if mask.any() else None}
        result['global']={'collapsed':int(((rat<.1)&(self.restarea>1e-6)).sum()),'stretched':int(((rat>5)&(self.restarea>1e-6)).sum()),'finite':bool(np.isfinite(out).all())}
        return result
    def smoothing(self,w,iterations=3,alpha=.3,mask=None):
        out=w.copy();a,b=self.edges.T;deg=np.bincount(np.r_[a,b],minlength=len(w));ids=np.arange(len(w)) if mask is None else np.flatnonzero(mask)
        for _ in range(iterations):
            sums=np.zeros_like(out);np.add.at(sums,a,out[b]);np.add.at(sums,b,out[a]);avg=sums/np.maximum(deg,1)[:,None];out[ids]=(1-alpha)*out[ids]+alpha*avg[ids]
        return self.pack(out)
    def semantic_refine(self,w,pelvis_strength=1,shoulder_strength=1):
        """Root excluded; side gating; articulated pelvis/arm envelopes from accepted pivots."""
        out=w.copy();idx=self.bi;v=self.v;p=self.pos[idx['pelvis']];span=np.linalg.norm(self.pos[idx['thigh_l']]-self.pos[idx['thigh_r']]);x=v[:,0]-p[0]
        out[:,idx['pelvis']]+=out[:,idx['root']];out[:,idx['root']]=0
        # Soft side exclusion; never crosses an entire limb at a midline seam.
        left=smoothstep(-span*.12,span*.12,x)
        for side,gate in [('l',left),('r',1-left)]:
            for prefix in ['thigh','calf','foot','ball','upperarm','lowerarm','hand']:
                b=idx[prefix+'_'+side];lost=out[:,b]*(1-gate);out[:,b]*=gate;out[:,idx['pelvis' if prefix in ['thigh','calf','foot','ball'] else 'spine_03']]+=lost
        # Pelvis garment envelope: high waist + central crotch, fade into each thigh below hip.
        h=np.mean([self.pos[idx['thigh_'+s],2] for s in ['l','r']]);height=smoothstep(h-span*.6,h+span*.2,v[:,2]);centre=1-smoothstep(span*.25,span*.65,abs(x))
        proximity=1-smoothstep(span*.8,span*1.05,np.linalg.norm(v[:,:2]-p[:2],axis=1))
        region=(1-smoothstep(p[2]+span*.35,p[2]+span*.9,v[:,2]))*proximity
        stable=np.maximum(height,centre*smoothstep(h-span*.9,h-span*.2,v[:,2]))*region*pelvis_strength
        for n in ['thigh_l','thigh_r','calf_l','calf_r']:
            b=idx[n];lost=out[:,b]*stable;out[:,b]-=lost;out[:,idx['pelvis']]+=lost
        # Shoulder: distinguish torso panel from arm sleeve by shoulder lateral station.
        for side,sign in [('l',1),('r',-1)]:
            s=self.pos[idx['upperarm_'+side]];el=self.pos[idx['lowerarm_'+side]];length=np.linalg.norm(el-s)
            lateral=sign*(v[:,0]-s[0]);arm=smoothstep(-length*.12,length*.18,lateral)
            near=1-smoothstep(length*.45,length*.9,np.linalg.norm(v-s,axis=1))
            above=smoothstep(s[2]-length*.4,s[2]-length*.1,v[:,2])
            amount=(1-arm)*near*above*shoulder_strength
            for n in ['upperarm_'+side,'lowerarm_'+side,'hand_'+side]:
                b=idx[n];lost=out[:,b]*amount;out[:,b]-=lost;out[:,idx['clavicle_'+side]]+=lost*.35;out[:,idx['spine_03']]+=lost*.65
        return self.pack(out)
