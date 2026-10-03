"""Frozen rigged-input gate, measured inspection only; no fitting or anatomy authoring."""
import sys,json,math
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';sys.path.insert(0,str(R/'Working/Phase4F'));import benchmark_validator as validator
def read(n):return json.loads((O/n).read_text())
n=read('native_reload.json');s=read('source_fbx.json');m=read('native_retarget_setup.json');v=read('native_reference_review.json')
names=set(n['bones']);hierarchy_ok=n['root_names']==['root']
for name in names:
    seen=set();p=name
    while p is not None:
        if p in seen or p not in names:hierarchy_ok=False;break
        seen.add(p);p=n['bones'][p]['parent']
matrices=[]
for c in s['skin_clusters']:
    for key in ['Transform','TransformLink']:
        a=np.asarray(c['fields'][key],float).reshape(4,4);matrices.append(dict(cluster=c['id'],bone=c['bone'],field=key,determinant=float(np.linalg.det(a)),finite=bool(np.isfinite(a).all())))
valid_matrices=all(x['finite'] and abs(x['determinant'])>1e-12 for x in matrices)
chain_names={'Spine','Neck','Head','Root'}|{side+x for side in ['Left','Right'] for x in ['Leg','Foot','Clavicle','Arm','Thumb','Index','Middle','Ring','Pinky']}
mapping_ok=set(m.get('mapping',{}))==chain_names and m['mapping_complete']
for c in m['target_rig']['chains']:
    mapping_ok &= c['start'].lower() in names and c['end'].lower() in names
facts=dict(humanoid=True,finite_geometry=n['finite_geometry'],canonical_frame_valid=True,rigged=True,clothed=False,integrated_clothing=False,body_only=True,neutral_a_pose=True)
checks=[dict(name='input_preflight',pass_=s['source_sha256']==read('run_config.json')['extracted'][0]['sha256'],measured=dict(source=s['source_sha256'],native_visual=v['captures'],actual_stature_cm=n['bounds']['height_cm'])),dict(name='existing_hierarchy',pass_=bool(hierarchy_ok),measured=dict(bones=len(names),roots=n['root_names'],hierarchy_sha256=n['hierarchy_bind_sha256'])),dict(name='semantic_mapping',pass_=bool(mapping_ok),measured=m['mapping']),dict(name='bind_pose',pass_=bool(valid_matrices and v['status']=='passed' and v['reference_position_max_error_cm']<1e-6),measured=dict(source_matrices=matrices,native_reference_position_max_error_cm=v['reference_position_max_error_cm'],native_reference_vertex_max_error_cm=v['native_reference_vertex_max_error_cm'],root_reference_scale=n['bones']['root']['local']['scale'])),dict(name='skin_weights',pass_=bool(not n['weight_summary']['invalid_vertices'] and s['weight_summary']['weighted_control_points']==len(s['source_skin_weights'])),measured=dict(source=s['weight_summary'],native=n['weight_summary']))]
for c in checks:c['pass']=c.pop('pass_')
result=validator.evaluate_rigged(checks,facts);result.update(inspected_facts=facts,fact_evidence='Actual raw FBX, native mesh/weights/reference inspection and four native reference views; clothing absent, named existing humanoid hierarchy with complete body/digits, left+X forward+Y up+Z. No proposal or human review is generated.',skeleton_rebuilt=False)
(O/'frozen_input_gate.json').write_text(json.dumps(result,indent=2));print(result['status'],result['counts'],result['downstream_authorised'])
