"""Frozen metric definitions on native pose samples; diagnostics never tuned acceptance caps."""
import json,gzip,math,sys,os
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged'
d=json.loads((O/'native_reload.json').read_text());offline=json.load(gzip.open(O/'baked_pose_samples.json.gz','rt'));data=json.load(gzip.open(O/'native_live_samples.json.gz','rt'))+[x for x in offline if x['variant']=='SourceControl'];names=list(d['bones']);ix={n:i for i,n in enumerate(names)}
V=np.array(d['native_geometry']['vertices_cm']);F=np.array(d['native_geometry']['triangles']);W=np.zeros((len(V),len(names)))
for i,ws in enumerate(d['native_geometry']['weights']):
    for n,w in ws:W[i,ix[n]]=w
def mat(tr):
    t,q,s=map(np.asarray,tr);x,y,z,w=q/np.linalg.norm(q);a=np.eye(4)
    a[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])*s
    a[:3,3]=t;return a
ref=np.array([mat([d['bones'][n]['component'][k] for k in ['translation','rotation_xyzw','scale']]) for n in names]);inv=np.linalg.inv(ref)
owners=[np.flatnonzero(W[:,j]>0) for j in range(len(names))]
def posed(bs):
    ms=np.array([mat(b[1]) for b in bs])@inv;out=np.zeros_like(V)
    for j,ids in enumerate(owners):out[ids]+=W[ids,j,None]*(V[ids]@ms[j,:3,:3].T+ms[j,:3,3])
    return out
refbs=[[[d['bones'][n]['local'][k] for k in ['translation','rotation_xyzw','scale']],[d['bones'][n]['component'][k] for k in ['translation','rotation_xyzw','scale']]] for n in names]
epsilon=max(1e-6,32*2**-23*max(1,float(np.abs(V).max())));area_eps=epsilon**2
e1=V[F[:,1]]-V[F[:,0]];e2=V[F[:,2]]-V[F[:,0]];length=np.linalg.norm(e1,axis=1);area=np.linalg.norm(np.cross(e1,e2),axis=1)/2;good=(area>area_eps)&(length>epsilon);ids=np.flatnonzero(good);fg=F[good];ag=area[good];l=length[good];u=e1[good]/l[:,None];c=np.einsum('ij,ij->i',e2[good],u);h=np.linalg.norm(e2[good]-c[:,None]*u,axis=1)
def wq(x):
    order=np.argsort(x);cum=np.cumsum(ag[order]);return [float(x[order[min(len(order)-1,np.searchsorted(cum,p*cum[-1]))]]) for p in [.5,.95,.99]]
patches={}
normal=np.cross(e1,e2)
for side in ['l','r']:
    owned=(W[:,ix['foot_'+side]]+W[:,ix['ball_'+side]])>.5
    ft=np.flatnonzero(np.all(owned[F],axis=1)&(normal[:,2]<0));ball=d['bones']['ball_'+side]['component']['translation'][1]
    patches[side]={k:ft[(V[F[ft]].mean(axis=1)[:,1]<ball)==(k=='heel')].tolist() for k in ['heel','toe']}
result=dict(method='Double CPU skinning of unchanged native imported weights, driven by actual LIVE UE component-space bone samples; offline AnimPose and stale commandlet component deformation explicitly not authoritative',length_epsilon_cm=epsilon,area_epsilon_cm2=area_eps,rest_nondegenerate_triangles=len(ids),rest_excluded_triangles=int((~good).sum()),reference_lbs_max_error_cm=float(np.linalg.norm(posed(refbs)-V,axis=1).max()),foot_patch_definition='Existing common source-native majority foot+ball skin ownership, downward triangles, original ball anterior split; no pose-based patch selection',foot_patch_triangle_ids=patches,clips=[])
for row in data:
    if row['variant']=='SourceControl':continue
    frames=[];maxstretch=-1;worst=None;collapse=set();finite=True;worstpos=None
    for tm,bs in row['pose_data']['frames']:
        p=posed(bs);finite &= bool(np.isfinite(p).all());a=p[fg[:,1]]-p[fg[:,0]];b=p[fg[:,2]]-p[fg[:,0]]
        f1=a/l[:,None];f2=(b-(c/l)[:,None]*a)/h[:,None];g11=np.einsum('ij,ij->i',f1,f1);g22=np.einsum('ij,ij->i',f2,f2);g12=np.einsum('ij,ij->i',f1,f2);disc=np.sqrt((g11-g22)**2+4*g12*g12);sm=np.sqrt(np.maximum(0,(g11+g22-disc)/2));sx=np.sqrt(np.maximum(0,(g11+g22+disc)/2));ar=np.linalg.norm(np.cross(a,b),axis=1)/2;ratio=ar/ag
        coll=ids[ar<=area_eps];collapse.update(map(int,coll));j=int(np.argmax(sx))
        if sx[j]>maxstretch:maxstretch=float(sx[j]);worst=dict(time_s=tm,triangle_id=int(ids[j]),sigma_max=maxstretch,sigma_min=float(sm[j]),area_ratio=float(ratio[j]));worstpos=p.copy()
        feet={}
        for side,ps in patches.items():
            feet[side]={}
            for k,ts in ps.items():
                ts=np.array(ts);z=p[F[ts],2];a0=area[ts];feet[side][k]=dict(min_height_cm=float(z.min()),max_height_cm=float(z.max()),near_ground_area_fraction=float(np.sum(a0*(np.abs(z)<=.5).mean(axis=1))/a0.sum()))
        frames.append(dict(time_s=tm,finite=bool(np.isfinite(p).all()),collapse_count=len(coll),sigma_min_area_weighted_p50_p95_p99=wq(sm),sigma_max_area_weighted_p50_p95_p99=wq(sx),area_ratio_area_weighted_p50_p95_p99=wq(ratio),maximum_sigma_max=float(sx.max()),minimum_sigma_min=float(sm.min()),bounds=[p.min(axis=0).tolist(),p.max(axis=0).tolist()],feet=feet))
    clip=dict(task_id=row['task_id'],variant=row['variant'],sample_count=len(frames),finite=finite,numerical_collapse_triangle_ids=sorted(collapse),worst_stretch=worst,frames=frames)
    result['clips'].append(clip);np.savez_compressed(O/(row['task_id']+'_'+row['variant']+'_worst_geometry.npz'),vertices_cm=worstpos,triangles=F,time_s=worst['time_s'])
    print(row['task_id'],row['variant'],'collapse',len(collapse),'stretch',round(maxstretch,3),flush=True)
    (O/'deformation_metrics.json').write_text(json.dumps(result))
# Strict P11 independent local tracks, compare each target bone with OWN imported reference.
src=next(x for x in data if x['variant']=='SourceControl' and x['task_id']=='P11')['pose_data'];dst=next(x for x in data if x['variant']=='Final' and x['task_id']=='P11')['pose_data'];bound=32*2**-23*180/math.pi
def angle(a,b):
    a=np.array(a)/np.linalg.norm(a);b=np.array(b)/np.linalg.norm(b);return float(2*math.acos(min(1,abs(float(a@b))))*180/math.pi)
violations=[];per_digit={};srcbase={n:src['frames'][0][1][i][0] for i,n in enumerate(src['bones'])}
for side in ['l','r']:
 for digit in ['thumb','index','middle','ring','pinky']:
    ns=[f'{digit}_{i:02}_{side}' for i in range(1,4)];unmax=0;commandmax=0;bad=[]
    for tm,db in dst['frames']:
        stm,sb=min(src['frames'],key=lambda x:abs(x[0]-tm));assert abs(tm-stm)<1e-6
        commanded=max(angle(sb[src['bones'].index(n)][0][1],srcbase[n][1]) for n in ns)>bound
        target=max(angle(db[ix[n]][0][1],d['bones'][n]['local']['rotation_xyzw']) for n in ns)
        if commanded:commandmax=max(commandmax,target)
        else:
            unmax=max(unmax,target)
            if target>bound:bad.append(tm)
    key=digit+'_'+side;per_digit[key]=dict(max_uncommanded_reference_rotation_error_deg=unmax,max_commanded_reference_rotation_delta_deg=commandmax,violating_uncommanded_sample_count=len(bad),first_violation_s=bad[0] if bad else None)
    if bad:violations.append(key)
result['finger_identity']=dict(arithmetic_rotation_bound_deg=bound,pass_=not violations,uncommanded_reference_failures=violations,per_digit=per_digit,source_control_reference='Existing corrected canonical source P11 time zero is independently certified true Manny reference; commanded cue determined from its native local excursion',support='Deformed owned root/path/tip containment and continuous triangle collision are not implemented by this prototype metric harness; do not claim acceptance from chain names or finite distances')
srcroot=next(x for x in offline if x['variant']=='SourceControl' and x['task_id']=='P14')['pose_data'];dstroot=next(x for x in offline if x['variant']=='Final' and x['task_id']=='P14')['pose_data'];delta=lambda x:np.array(x['frames'][-1][1][0][1][0])-np.array(x['frames'][0][1][0][1][0]);sd=delta(srcroot);dd=delta(dstroot);scale=json.loads((O/'native_retarget_setup.json').read_text())['reference_stature_ratio'];result['root_motion']=dict(method='Authored native AnimSequence root track diagnostic, separate from root-extracted live component; no world-contact acceptance inferred',source_delta_cm=sd.tolist(),destination_delta_cm=dd.tolist(),required_reference_stature_ratio=scale,expected_destination_delta_cm=(sd*scale).tolist(),residual_cm=float(np.linalg.norm(dd-sd*scale)),measured_translation_ratio=float(np.linalg.norm(dd)/np.linalg.norm(sd)),root_reference_scale=d['bones']['root']['local']['scale'],offline_animpose_root_scale=dstroot['frames'][0][1][0][0][2],policy_correction_applied=False)
(O/'deformation_metrics.json').write_text(json.dumps(result));print('FINGER_IDENTITY',violations);print('ROOT',result['root_motion'])
