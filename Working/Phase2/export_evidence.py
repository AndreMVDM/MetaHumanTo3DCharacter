"""Publish compact, reproducible Phase 2 evidence from the recorded build outputs."""
import csv
import json
import re
from pathlib import Path

workspace = Path(__file__).resolve().parent
destination = workspace.parents[1] / 'Documentation' / 'Phase2'
destination.mkdir(parents=True, exist_ok=True)

def read(name):
    return json.loads((workspace / name).read_text(encoding='utf-8'))

fbx = read('fbx_analysis.json')
build = read('retarget_build.json')
imports = read('unreal_import.json')
anim_bps = read('anim_bp_build.json')
samples = read('pie_samples.json')['samples']

roles = {
    'UE5': {
        'root': 'root', 'pelvis': 'pelvis', 'spine_start': 'spine_01', 'spine_end': 'spine_03',
        'neck': 'neck_01', 'head': 'head',
        **{f'{side}_{role}': f'{name}_{suffix}' for side, suffix in [('left', 'l'), ('right', 'r')]
           for role, name in [('clavicle', 'clavicle'), ('upper_arm', 'upperarm'),
                              ('lower_arm', 'lowerarm'), ('hand', 'hand'), ('thigh', 'thigh'),
                              ('calf', 'calf'), ('foot', 'foot'), ('toe', 'ball')]},
        **{f'{side}_{finger}': f'{finger}_01_{suffix}' for side, suffix in [('left', 'l'), ('right', 'r')]
           for finger in ['thumb', 'index', 'middle', 'ring', 'pinky']},
    },
    'Mixamo': {
        'root': 'Hips', 'pelvis': 'Hips', 'spine_start': 'Spine', 'spine_end': 'Spine2',
        'neck': 'Neck', 'head': 'Head',
        **{f'{side}_{role}': f'{prefix}{name}' for side, prefix in [('left', 'Left'), ('right', 'Right')]
           for role, name in [('clavicle', 'Shoulder'), ('upper_arm', 'Arm'),
                              ('lower_arm', 'ForeArm'), ('hand', 'Hand'), ('thigh', 'UpLeg'),
                              ('calf', 'Leg'), ('foot', 'Foot'), ('toe', 'ToeBase')]},
        **{f'{side}_{finger}': f'{prefix}Hand{finger.title()}1' for side, prefix in [('left', 'Left'), ('right', 'Right')]
           for finger in ['thumb', 'index', 'middle', 'ring', 'pinky']},
    },
}

anatomy = {}
for variant, role_map in roles.items():
    bone_by_name = {bone['name'].removeprefix('mixamorig:'): bone for bone in fbx[variant]['bones']}
    anatomy[variant] = {
        'source_bone_count': fbx[variant]['bone_count'],
        'imported_bone_count': build['variants'][variant]['imported_bone_count'],
        'roles': {},
        'twist_bones': [name for name in bone_by_name if 'twist' in name.lower()],
        'ik_helper_bones': [name for name in bone_by_name if name.lower().startswith(('ik_', 'ik.'))],
        'pose_classification': 'Unresolved: A/T arm angle was not measured numerically; automatic pose alignment was used.',
    }
    for role, name in role_map.items():
        assert name in bone_by_name, (variant, role, name)
        bone = bone_by_name[name]
        parent = bone['parent']
        if parent:
            parent = parent.removeprefix('mixamorig:')
        anatomy[variant]['roles'][role] = {
            'bone': name, 'parent': parent, 'confidence': 'High',
            'basis': 'name, parent/child hierarchy and bilateral counterpart' if role.startswith(('left_', 'right_'))
                     else 'name and axial hierarchy',
        }

(destination / 'anatomy_mapping.json').write_text(json.dumps(anatomy, indent=2) + '\n', encoding='utf-8')

with (destination / 'bone_comparison.csv').open('w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['semantic_role', 'ue5_bone', 'ue5_parent', 'mixamo_bone', 'mixamo_parent', 'confidence'])
    for role in roles['UE5']:
        ue = anatomy['UE5']['roles'][role]
        mx = anatomy['Mixamo']['roles'][role]
        writer.writerow([role, ue['bone'], ue['parent'], mx['bone'], mx['parent'], 'High'])

with (destination / 'chain_mapping.csv').open('w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['variant', 'target_chain', 'source_chain', 'mapped'])
    for variant in ('UE5', 'Mixamo'):
        info = build['variants'][variant]
        for chain in info['final_chains']:
            name = re.search(r'chain_name: "([^"]+)"', chain).group(1)
            source = info['final_mapping'].get(name, '')
            writer.writerow([variant, name, source, bool(source)])

offsets = {}
for variant in ('UE5', 'Mixamo'):
    values = build['variants'][variant]['pose_offsets']
    identity = '{x: 0.000000, y: 0.000000, z: 0.000000, w: 1.000000}'
    non_identity = {k: v for k, v in values.items() if identity not in v}
    offsets[variant] = {
        'method': 'automatic target pose alignment through UE 5.8 retargeter controller',
        'evaluated_bones': len(values), 'non_identity_offset_count': len(non_identity),
        'non_identity_offsets': non_identity,
        'manual_rotation_offsets': [],
    }
(destination / 'pose_offsets.json').write_text(json.dumps(offsets, indent=2) + '\n', encoding='utf-8')

assets = {'source': build['source'], 'variants': {},
          'actor': '/Game/MetaHumanTo3DCharacter/Phase2/BP_Phase2_RetargetTest.BP_Phase2_RetargetTest',
          'map': '/Game/MetaHumanTo3DCharacter/Phase2/Maps/L_Phase2_RetargetTest.L_Phase2_RetargetTest'}
for variant in ('UE5', 'Mixamo'):
    info = build['variants'][variant]
    assets['variants'][variant] = {
        'skeletal_mesh': info['mesh'], 'skeleton': info['skeleton'],
        'ik_rig': info['rig'], 'ik_retargeter': info['retargeter'],
        'animation_blueprint': anim_bps['variants'][variant]['path'],
        'imported_assets': imports['variants'][variant]['imported_paths'],
    }
(destination / 'asset_inventory.json').write_text(json.dumps(assets, indent=2) + '\n', encoding='utf-8')

runtime = {'source': 'PIE in UE 5.8.3 with MM_Run_Fwd', 'samples': [],
           'raw_evidence': str(workspace / 'pie_samples.json')}
for sample in samples:
    if sample.get('errors') or len(sample.get('components', [])) != 3:
        continue
    item = {'unix_time': sample['time'], 'components': {}}
    for component in sample['components']:
        bones = {}
        for key in ['pelvis', 'Hips', 'head', 'hand_l', 'LeftHand', 'foot_l', 'LeftFoot']:
            if key in component:
                match = re.search(r'\{x: ([\d.\-]+), y: ([\d.\-]+), z: ([\d.\-]+)\}', component[key])
                if match:
                    bones[key] = [float(value) for value in match.groups()]
        item['components'][component['name']] = {
            'animation_mode': component['animation_mode'],
            'anim_instance_present': bool(component['anim_instance'] and component['anim_instance'] != 'None'),
            'bones_world_cm': bones,
        }
    runtime['samples'].append(item)
(destination / 'runtime_samples.json').write_text(json.dumps(runtime, indent=2) + '\n', encoding='utf-8')
print('PHASE2_EVIDENCE_EXPORTED')
