"""Synthetic rejection controls for the runtime-only ownership correction."""
import json
from pathlib import Path
from runtime_appearance_closure import certify, VERSION

cases = []
def test(name, edges, classes, roots, expected):
    result = certify(['/Game/Destination/Mesh'], set(edges), edges, roots, classes)
    passed = (result['status'] == expected)
    cases.append(dict(name=name, expected=expected, actual=result['status'], passed=passed, certificate=result))
    assert passed, name

base = {'/Game/Destination/Mesh':['/Game/Input/Mat'], '/Game/Input/Mat':['/Engine/Parent'], '/Engine/Parent':['/Game/Input/Tex'], '/Game/Input/Tex':[]}
types = {'/Game/Input/Mat':['MaterialInstanceConstant'], '/Game/Input/Tex':['Texture2D'], '/Engine/Parent':['Material']}
test('bound_material_and_texture_through_engine_parent', base, types, ['/Game/Input/Mat'], 'PASS')
test('unbound_material_rejected', base, types, [], 'FAIL')
test('missing_asset_type_rejected', base, {'/Game/Input/Mat':['MaterialInstanceConstant'],'/Engine/Parent':['Material']}, ['/Game/Input/Mat'], 'FAIL')
test('unclassified_material_root_rejected', base, types, ['/Game/Unknown'], 'FAIL')
for cls in ['SkeletalMesh','Skeleton','AnimSequence','IKRigDefinition','IKRetargeter','Blueprint','Unknown']:
    e = {**base, '/Engine/Parent':['/Game/Input/Tex','/Game/Other/Asset'], '/Game/Other/Asset':[]}
    test('appearance_must_not_hide_'+cls, e, {**types,'/Game/Other/Asset':[cls]}, ['/Game/Input/Mat'], 'FAIL')
test('same_namespace_unbound_texture_rejected', {**base,'/Game/Destination/Unbound':[]}, {**types,'/Game/Destination/Unbound':['Texture2D']}, ['/Game/Input/Mat'], 'FAIL')
test('mixed_package_ownership_rejected', base, {**types,'/Game/Input/Tex':['Texture2D','AnimSequence']}, ['/Game/Input/Mat'], 'FAIL')
test('missing_graph_node_rejected', {'/Game/Destination/Mesh':['/Game/Input/Mat'],'/Game/Input/Mat':['/Game/Input/Missing']}, types, ['/Game/Input/Mat'], 'FAIL')
test('engine_only_body_material', {'/Game/Destination/Mesh':['/Engine/Mat'],'/Engine/Mat':[]}, {'/Engine/Mat':['Material']}, ['/Engine/Mat'], 'PASS')
test('no_material_destination', {'/Game/Destination/Mesh':[]}, {}, [], 'PASS')
test('plugin_foreign_mesh_rejected', {**base,'/Engine/Parent':['/Game/Input/Tex','/Plugin/Donor'],'/Plugin/Donor':[]}, {**types,'/Plugin/Donor':['SkeletalMesh']}, ['/Game/Input/Mat'], 'FAIL')
test('unclassified_plugin_material_parent_rejected', base, {k:v for k,v in types.items() if k!='/Engine/Parent'}, ['/Game/Input/Mat'], 'FAIL')
test('ue_transient_container_is_not_persisted_content', {**base,'/Engine/Parent':['/Game/Input/Tex','/Engine/Transient'],'/Engine/Transient':[]}, types, ['/Game/Input/Mat'], 'PASS')
test('transient_must_not_hide_foreign_mesh', {**base,'/Engine/Parent':['/Game/Input/Tex','/Engine/Transient'],'/Engine/Transient':['/Game/Donor'],'/Game/Donor':[]}, {**types,'/Game/Donor':['SkeletalMesh']}, ['/Game/Input/Mat'], 'FAIL')
o = Path(__file__).resolve().parents[5]/'Documentation/Phase4F/Benchmark/Runs/02_AegisNX7/R3/runtime_appearance_regression.json'
o.write_text(json.dumps(dict(version=VERSION,status='PASS',passed=len(cases),total=len(cases),cases=cases),indent=2)+'\n')
print('Appearance regression:',len(cases),'PASS')
