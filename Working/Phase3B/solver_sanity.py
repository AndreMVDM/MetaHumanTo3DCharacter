"""Phase3B project gates. Static stature is distinct from an animated envelope."""
import math

def validate_reference(height, measured_height, bones, goals=(), component_scale=(1,1,1), actor_scale=(1,1,1)):
    issues=[]
    if not math.isfinite(height) or height<=0:return ['invalid_requested_height']
    if not math.isfinite(measured_height) or abs(measured_height-height)>0.1:issues.append('output_height_mismatch')
    for name,b in bones.items():
        for space in ['local','component']:
            tr=b[space]
            if not all(math.isfinite(x) for vals in tr.values() for x in vals):issues.append('non_finite_reference:'+name)
            if any(abs(x-1)>0.001 for x in tr['scale']):issues.append('suspicious_reference_scale:'+name)
        if math.dist(b['component']['translation'],(0,0,0))>3*height:issues.append('reference_bone_envelope:'+name)
    for goal in goals:
        if not all(math.isfinite(x) for x in goal) or math.dist(goal,(0,0,0))>3*height:issues.append('goal_envelope')
    if any(abs(x-1)>0.001 for x in component_scale+actor_scale):issues.append('external_scale')
    return sorted(set(issues))

def validate_pose(height,bones,pelvis,root,reference,root_motion=False):
    issues=[]
    if not all(math.isfinite(x) for b in bones.values() for tr in b.values() for vals in tr.values() for x in vals):return ['non_finite_pose']
    rp=bones[root]['component']['translation'];pp=bones[pelvis]['component']['translation']
    refp=reference[pelvis]['component']['translation'];refr=reference[root]['component']['translation']
    trajectory=[rp[i]-refr[i] for i in range(3)] if root_motion else [0,0,0]
    if root==pelvis:trajectory[2]=0 # A pelvis root cannot also define the ground's vertical motion.
    displacement=math.dist([pp[i]-trajectory[i] for i in range(3)],refp)
    if displacement>height:issues.append('pelvis_displacement')
    if not 0.2*height<=pp[2]-trajectory[2]<=1.5*height:issues.append('pelvis_height')
    if max(math.dist(b['component']['translation'],rp) for b in bones.values())>3*height:issues.append('bone_envelope')
    if any(abs(x-1)>0.001 for b in bones.values() for tr in b.values() for x in tr['scale']):issues.append('non_unit_bone_scale')
    return issues

if __name__=='__main__':
    import copy,json
    tr={'translation':[0,0,0],'rotation_xyzw':[0,0,0,1],'scale':[1,1,1]}
    ref={'root':{'local':copy.deepcopy(tr),'component':copy.deepcopy(tr)},'pelvis':{'local':copy.deepcopy(tr),'component':copy.deepcopy(tr)}}
    ref['pelvis']['component']['translation']=[0,0,90]
    checks=[]
    def test(name,issues,expected):
        assert expected in issues,(name,issues);checks.append({'case':name,'detected':expected})
    bad=copy.deepcopy(ref);bad['pelvis']['component']['translation']=[0,0,5000]
    test('50 metre pelvis',validate_pose(180,bad,'pelvis','root',ref),'pelvis_displacement')
    bad=copy.deepcopy(ref);bad['root']['local']['scale']=[100,100,100]
    test('root scale 100',validate_reference(180,180,bad),'suspicious_reference_scale:root')
    bad=copy.deepcopy(ref);bad['pelvis']['component']['translation'][0]=float('nan')
    test('NaN transform',validate_pose(180,bad,'pelvis','root',ref),'non_finite_pose')
    test('far IK goal',validate_reference(180,180,ref,[[5000,0,0]]),'goal_envelope')
    test('wrong stature',validate_reference(180,100,ref),'output_height_mismatch')
    moving=copy.deepcopy(ref)
    for b in moving.values():b['component']['translation'][0]+=1000
    assert not validate_pose(180,moving,'pelvis','root',ref,True)
    checks.append({'case':'coherent 10m root motion','detected':'accepted after trajectory subtraction'})
    from pathlib import Path
    (Path(__file__).resolve().parents[2]/'Documentation/Phase3B/gate_self_tests.json').write_text(json.dumps(checks,indent=2))
    print('GATE_TESTS_PASS',len(checks))
