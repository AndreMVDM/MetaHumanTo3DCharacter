"""Regression fixtures operate on copies; never export or append human events."""
import ast,copy,sys
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));import core
tests=[]
def test(name,condition):
 tests.append({'name':name,'passed':bool(condition)});assert condition,name
s=core.read(core.W/'HumanTrialFinalisation/InputSnapshot/session_from_editor.json');r=core.rebuild(copy.deepcopy(s))
for key in ['fingers','approvals','events','joints','generated_joint_schema']:
 test('exact accepted editor replay: '+key,r[key]==s[key])
def max_delta(a,b):
 if isinstance(a,dict):
  assert a.keys()==b.keys();return max((max_delta(a[k],b[k]) for k in a),default=0)
 if isinstance(a,list):
  assert len(a)==len(b);return max((max_delta(x,y) for x,y in zip(a,b)),default=0)
 if isinstance(a,(float,int)):return abs(a-b)
 assert a==b;return 0
transform_delta=max_delta(r['local_transforms'],s['local_transforms'])
test('derived local transforms replay within 1e-10',transform_delta<=1e-10)
for field in ['root_cm','tip_cm']:
 changed=copy.deepcopy(s);changed['fingers']['thumb_l'][field][1]+=.01;changed=core.rebuild(changed)
 test(field+' real change invalidates thumb approval','thumb_l' not in changed['approvals'])
changed=copy.deepcopy(s);changed['fingers']['thumb_l']['track_id']='digit_branch_1_l';changed=core.rebuild(changed)
test('changed track invalidates thumb approval','thumb_l' not in changed['approvals'])
changed=copy.deepcopy(s);changed['body_overrides']['neck_01'][2]+=.01;changed=core.rebuild(changed)
test('changed neck invalidates body approval','neck_01' not in changed['approvals'])
# Execute precisely the installed validator's side expression without its exports.
tree=ast.parse((core.W/'inherited_validate.py').read_text());nodes=[]
for n in tree.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='side_values' for t in n.targets):nodes.append(n)
 if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and n.value.args and isinstance(n.value.args[0],ast.Constant) and n.value.args[0].value=='left_right_not_crossed':nodes.append(n)
assert len(nodes)==2
code=compile(ast.Module(body=nodes,type_ignores=[]),'actual_side_check','exec');j={x['role']:x for x in s['joints']};p={n:np.array(x['position_cm']) for n,x in j.items()}
def side_check(points):
 results=[];exec(code,{'j':j,'p':points,'check':lambda *args:results.append(args)});return results[0][1]
test('actual human proposal passes parent-relative clavicle check',side_check(p))
bad=copy.deepcopy(p);bad['clavicle_r'][0]=bad[j['clavicle_r']['parent_role']][0]+.1
test('wrong-side clavicle still rejected',not side_check(bad))
bad=copy.deepcopy(p);bad['hand_r'][0]=abs(bad['hand_r'][0])
test('crossed wrist still rejected',not side_check(bad))
core.save(core.O/'finalisation_regression.json',{'passed':all(x['passed'] for x in tests),'tests':tests,'maximum_local_transform_replay_delta':transform_delta,'fixture_provenance':'Synthetic copies of recovered real editor state; no recorded human commands or approval exports'})
print('Finalisation regression:',len(tests),'passed')
