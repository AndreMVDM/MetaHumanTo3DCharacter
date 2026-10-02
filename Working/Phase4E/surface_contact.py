"""Bounded post-retarget surface-contact IK; current lengths/pivots, actor/root unchanged."""
from model import *
m=Model();weights=m.dense(load(W/'selected_weights.json'))
def solve(pose,side,goal):
    hi=m.bi['thigh_'+side];ki=m.bi['calf_'+side];ai=m.bi['foot_'+side];a=pose[hi,:3,3].copy();b=pose[ki,:3,3].copy();c=pose[ai,:3,3].copy();l1=np.linalg.norm(b-a);l2=np.linalg.norm(c-b)
    axis=goal-a;d=np.linalg.norm(axis);axis/=d;d=np.clip(d,abs(l1-l2)+1e-4,l1+l2-1e-4);goal=a+d*axis
    pole=b-a-axis*np.dot(b-a,axis)
    if np.linalg.norm(pole)<1e-6:return False
    pole/=np.linalg.norm(pole);along=(l1*l1-l2*l2+d*d)/(2*d);height=math.sqrt(max(0,l1*l1-along*along));knee=a+axis*along+pole*height
    thighR=swing(b-a,knee-a);calfR=swing(c-b,goal-knee)
    pose[hi,:3,:3]=thighR@pose[hi,:3,:3];pose[ki,:3,:3]=calfR@pose[ki,:3,:3];pose[ki,:3,3]=knee
    delta=goal-c;pose[m.descendants('foot_'+side),:3,3]+=delta
    return True
def correct(pose,max_iterations=5):
    out=pose.copy();events=[]
    for _ in range(max_iterations):
        surface=m.deform(weights,out);changed=False
        for s in ['l','r']:
            mask=m.regions['left_sole' if s=='l' else 'right_sole'];z=float(surface[mask,2].min())
            if z>=-.01:continue
            foot=out[m.bi['foot_'+s],:3,3].copy();lift=min(6.,-z+.015)
            if solve(out,s,foot+[0,0,lift]):events.append({'side':s,'surface_z_before_cm':z,'goal_delta_z_cm':lift});changed=True
        if not changed:break
    return out,events
if __name__=='__main__':
    samples=[];events=[];summary=[]
    for s in m.samples:
        if s['role'] not in ['idle','walk','run']:continue
        pose=m.from_sample(s);out,edits=correct(pose);surface=m.deform(weights,out);length_error=max(abs(np.linalg.norm(out[m.bi['calf_'+side],:3,3]-out[m.bi['thigh_'+side],:3,3])-np.linalg.norm(pose[m.bi['calf_'+side],:3,3]-pose[m.bi['thigh_'+side],:3,3])) for side in ['l','r'])
        row={'role':s['role'],'time_s':s['time_s'],'fraction':s['fraction'],'component_matrices':out.tolist(),'sole_min_z_cm':{side:float(surface[m.regions['left_sole' if side=='l' else 'right_sole'],2].min()) for side in ['l','r']},'thigh_length_error_cm':float(length_error),'events':edits};samples.append(row)
    for role in ['idle','walk','run']:
        seq=[s for s in samples if s['role']==role];summary.append({'role':role,'max_penetration_cm':max(0,-min(z for s in seq for z in s['sole_min_z_cm'].values())),'max_thigh_length_error_cm':max(s['thigh_length_error_cm'] for s in seq),'corrected_samples':sum(bool(s['events']) for s in seq)})
    save('surface_contact_experiment.json',{'method':'Sole-aware authoring IK after native bake; two-bone leg solve toward penetration-derived ankle goal; preserves existing lengths and knee bend plane; no actor/root shift; five iterations maximum','summary':summary,'samples':samples,'limits':'Flat-floor collision correction, no speed planting/stride/world locomotion; contact labels unproven; clip-loop continuity must be measured after bake'});print(summary)
