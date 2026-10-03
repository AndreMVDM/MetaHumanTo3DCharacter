"""Bounded transform conversion controls, independent of subject/policy validator."""
import sys,json,math
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True;R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'Working/Phase4F'));from rigged_unit_canonicalisation import plan
O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/UnitCorrection';O.mkdir(exist_ok=True)
def matrix(t):
    x,y,z,w=t['rotation_xyzw'];m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])*t['scale'];m[:3,3]=t['translation'];return m
def global_mats(b,ts):
    out={}
    def get(n):
        if n not in out:out[n]=(get(b[n]['parent']) if b[n]['parent'] else np.eye(4))@matrix(ts[n])
        return out[n]
    for n in b:get(n)
    return out
tests=[]
for s in [1,.01,100,2.54]:
    b={'carrier':dict(parent=None,local=dict(translation=[8,-3,2],rotation_xyzw=[0,0,math.sin(.3),math.cos(.3)],scale=[s]*3)),'hip':dict(parent='carrier',local=dict(translation=[.3,-.8,1],rotation_xyzw=[math.sin(.2),0,0,math.cos(.2)],scale=[1]*3)),'end':dict(parent='hip',local=dict(translation=[.1,.2,.7],rotation_xyzw=[0,math.sin(.1),0,math.cos(.1)],scale=[1]*3))}
    p=plan(b);old=global_mats(b,{n:x['local'] for n,x in b.items()});new=global_mats(b,p['transforms']);error=max(np.linalg.norm(old[n][:3,3]-new[n][:3,3]) for n in b);rotation_error=max(np.linalg.norm(old[n][:3,:3]/s-new[n][:3,:3]) for n in b);assert error<1e-12 and rotation_error<1e-12;tests.append(dict(name='arbitrary_names_rotated_translated_root_factor_'+str(s),pass_=True,position_error=error,scale_removed_basis_error=rotation_error))
for label,scales in [('nonuniform',[100,101,100]),('negative',[-1]*3),('zero',[0]*3),('nonfinite',[float('nan')]*3)]:
    b['carrier']['local']['scale']=scales
    try:plan(b);raise AssertionError('unsafe scale accepted')
    except ValueError:tests.append(dict(name='reject_'+label,pass_=True))
b['carrier']['local']['scale']=[100]*3;b['carrier']['parent']='end'
try:plan(b);raise AssertionError('cycle accepted')
except ValueError:tests.append(dict(name='reject_cycle',pass_=True))
(O/'unit_plan_regressions.json').write_text(json.dumps(dict(status='passed',count=len(tests),tests=tests),indent=2));print('UNIT_PLAN_TESTS',len(tests))
