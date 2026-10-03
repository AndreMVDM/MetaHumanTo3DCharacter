"""R2 automatic authoring: input -> unchanged R1 conversion -> UE semantics -> IK -> bake.

Run only in the isolated R2 authoring host. Configuration supplies asset paths;
no subject bone names or positional compensation are supplied.
"""
import unreal, json, sys, math, hashlib, traceback
from pathlib import Path

sys.dont_write_bytecode = True
W = Path(__file__).resolve().parent
R = W.parents[4]
O = R / 'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/R2_EndToEnd'
C = json.loads((W / 'config.json').read_text())
B = C['output_namespace']
sys.path.insert(0, str(R / 'Working/Phase4F'))
from rigged_unit_canonicalisation import plan, derive, VERSION
sys.path.insert(0, str(R / 'Working/Phase3B'))
from common import rig_snapshot, ret_snapshot

REQUIRED = ['Root', 'Spine', 'Neck', 'Head'] + [side + role for side in ['Left', 'Right'] for role in ['Clavicle', 'Arm', 'Leg', 'Foot', 'Thumb', 'Index', 'Middle', 'Ring', 'Pinky']]
state = dict(version=C['version'], status='RUNNING', stages=[], assets={}, clips=[])


def write(name, value):
    (O / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def passed(stage, data):
    write(stage + '.json', dict(status='PASS', **data))
    state['stages'].append(dict(stage=stage, status='PASS'))
    write('authoring_result.json', state)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def v(x):
    return [float(x.x), float(x.y), float(x.z)]


def tr(x):
    return dict(translation=v(x.translation), rotation_xyzw=[x.rotation.x, x.rotation.y, x.rotation.z, x.rotation.w], scale=v(x.scale3d))


def inspect(mesh):
    require(isinstance(mesh, unreal.SkeletalMesh), 'not_skeletal_mesh')
    sk = mesh.skeleton
    require(sk is not None, 'missing_skeleton')
    ref = sk.get_reference_pose()
    component = unreal.new_object(unreal.SkeletalMeshComponent)
    component.set_skeletal_mesh_asset(mesh)
    # A shared Skeleton may contain compatibility/virtual bones absent from this mesh.
    # Validate the actual mesh hierarchy, not phantom roots from absent Skeleton bones.
    bones = {str(n): dict(parent=None if str(component.get_parent_bone(n)) == 'None' else str(component.get_parent_bone(n)), local=tr(ref.get_bone_pose(n, unreal.AnimPoseSpaces.LOCAL)), component=tr(ref.get_bone_pose(n, unreal.AnimPoseSpaces.WORLD))) for n in ref.get_bone_names() if component.get_bone_index(n) >= 0}
    require(bool(bones), 'invalid_hierarchy: empty')
    require(len({n.casefold() for n in bones}) == len(bones), 'invalid_hierarchy: duplicate bone')
    roots = [n for n, b in bones.items() if b['parent'] is None]
    require(len(roots) == 1, 'invalid_hierarchy: root count')
    for name, bone in bones.items():
        seen = set()
        p = name
        while p is not None:
            require(p in bones and p not in seen, 'invalid_hierarchy: parent or cycle')
            seen.add(p)
            p = bones[p]['parent']
        require(roots[0] in seen, 'invalid_hierarchy: disconnected')
        for space in ['local', 'component']:
            require(all(math.isfinite(x) for a in bone[space].values() for x in a), 'invalid_reference_transform')
            require(all(x != 0 for x in bone[space]['scale']), 'invalid_reference_transform: singular scale')
            require(sum(x*x for x in bone[space]['rotation_xyzw']) > 0, 'invalid_reference_transform: invalid rotation')
    dm = unreal.DynamicMesh()
    unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh, dm, unreal.GeometryScriptCopyMeshFromAssetOptions(), unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL, lod_index=0))
    Q, BW = unreal.GeometryScript_MeshQueries, unreal.GeometryScript_BoneWeights
    _, info = BW.get_all_bones_info(dm)
    names = {b.index: str(b.name) for b in info}
    vertices, weights, triangles, invalid = [], [], [], []
    for i in range(Q.get_num_vertex_i_ds(dm)):
        point, ok = Q.get_vertex_position(dm, i)
        require(ok, 'invalid_geometry: vertex index')
        vertices.append(v(point))
        _, ws, ok = BW.get_vertex_bone_weights(dm, i)
        raw = [(w.bone_index, float(w.weight)) for w in ws]
        good = ok and bool(raw) and all(j in names and names[j] in bones and math.isfinite(w) and w >= 0 for j, w in raw)
        pairs = [[names[j], w] for j, w in raw if j in names and w > 0]
        good = good and bool(pairs) and abs(sum(w for _, w in pairs) - 1) <= .001
        if not good:
            invalid.append(i)
        weights.append(pairs)
    for i in range(Q.get_num_triangle_i_ds(dm)):
        indices, ok = Q.get_triangle_indices(dm, i)
        require(ok, 'invalid_geometry: triangle index')
        triangles.append([indices.x, indices.y, indices.z])
    require(vertices and triangles, 'unskinned_mesh: no renderable source geometry')
    require(not invalid, 'invalid_weights: ' + str(len(invalid)) + ' vertices')
    require(all(math.isfinite(x) for p in vertices for x in p), 'invalid_geometry: nonfinite')
    return dict(mesh=mesh.get_path_name(), skeleton=sk.get_path_name(), bone_count=len(bones), bones=bones, root=roots[0], vertex_count=len(vertices), triangle_count=len(triangles), invalid_weight_vertices=invalid, max_weight_sum_error=max(abs(sum(w for _, w in x)-1) for x in weights), geometry_skin_sha256=hashlib.sha256(json.dumps([vertices, triangles, weights], sort_keys=True).encode()).hexdigest(), height_cm=2*mesh.get_bounds().box_extent.z)


def bone_name(bones, name):
    matches = [n for n in bones if n.casefold() == str(name).casefold()]
    require(len(matches) == 1, 'invalid_chain_bone: ' + str(name))
    return matches[0]


def chain_path(bones, start, end):
    start, end = bone_name(bones, start), bone_name(bones, end)
    result = [end]
    while result[-1] != start:
        p = bones[result[-1]]['parent']
        require(p is not None and p not in result, 'invalid_chain_ancestry: ' + start + ' -> ' + end)
        result.append(p)
    return list(reversed(result))


def analyse(mesh, bones):
    # Transient auto-characterisation is also the input's sufficient-anatomy screen.
    ik = unreal.new_object(unreal.IKRigDefinition)
    ctl = unreal.IKRigController.get_controller(ik)
    require(ctl.set_skeletal_mesh(mesh), 'insufficient_humanoid_anatomy: preview mesh')
    require(ctl.apply_auto_generated_retarget_definition(), 'insufficient_humanoid_anatomy: UE template')
    rows = {str(x.chain_name): dict(start=str(ctl.get_retarget_chain_start_bone(x.chain_name)), end=str(ctl.get_retarget_chain_end_bone(x.chain_name))) for x in ctl.get_retarget_chains()}
    root = next(n for n, b in bones.items() if b['parent'] is None)
    rows.setdefault('Root', dict(start=root, end=root))
    require(all(n in rows for n in REQUIRED), 'insufficient_humanoid_anatomy: missing ' + str([n for n in REQUIRED if n not in rows]))
    records = [dict(semantic=n, chain=n, bones=chain_path(bones, **rows[n]), resolved_by='UE automatic humanoid retarget definition; ancestry validated', required=True, confidence='UE template match, structural validation; template alternatives not exposed', ambiguous=False, passed=True) for n in REQUIRED]
    pelvis = bone_name(bones, ctl.get_retarget_root())
    records.append(dict(semantic='PelvisRetargetRoot', bone=pelvis, resolved_by='UE automatic retarget root', required=True, confidence='UE template match; existing reference bone', ambiguous=False, passed=True))
    return dict(bindings=records, chain_count=len(REQUIRED), semantic_binding_count=len(records), pelvis=pelvis, root=root, chains=rows)


stage = 'input_validation'
try:
    require(VERSION == C['canonicalisation_version'], 'unexpected_canonicalisation_policy')
    require(B.startswith('/Game/') and '/R2_EndToEnd' in B, 'invalid_output_namespace')
    require(not unreal.EditorAssetLibrary.list_assets(B, True, False), 'refuse_to_overwrite_R2_outputs: choose a new isolated namespace')
    original_mesh = unreal.load_asset(C['input_mesh'])
    original = inspect(original_mesh)
    original_analysis = analyse(original_mesh, original['bones'])
    passed(stage, dict(input=original, sufficient_humanoid_anatomy=True, automatic_analysis=original_analysis))

    stage = 'unit_classification'
    try:
        unit = plan(original['bones'])
    except ValueError as e:
        passed_data = dict(classification='unsupported_scale_representation', reason=str(e))
        write(stage + '.json', dict(status='FAIL', **passed_data))
        raise ValueError('unsupported_scale_representation: ' + str(e))
    classification = 'canonicalisation_required' if unit['needs_canonicalisation'] else 'already_canonical'
    passed(stage, dict(classification=classification, detected_factor=unit['factor'], detector_version=VERSION, root=unit['root']))

    stage = 'canonicalisation'
    mesh, conversion = derive(unreal, original_mesh, B+'/Character', 'SK_Destination', 'SKEL_Destination', original['bones'])
    destination = inspect(mesh)
    names_equal = set(original['bones']) == set(destination['bones'])
    require(names_equal, 'canonicalisation_bone_names_changed')
    hierarchy = all(b['parent'] == original['bones'][n]['parent'] for n, b in destination['bones'].items())
    error = max(math.dist(b['component']['translation'], original['bones'][n]['component']['translation']) for n, b in destination['bones'].items())
    invariants = dict(bone_names=names_equal, hierarchy=hierarchy, geometry_skin=original['geometry_skin_sha256'] == destination['geometry_skin_sha256'], height=abs(destination['height_cm']-original['height_cm']) < C['bind_position_tolerance_cm'], component_bind_positions=error < C['bind_position_tolerance_cm'], canonical_root_scale=max(abs(x-1) for x in destination['bones'][destination['root']]['local']['scale']) < 1e-6)
    require(all(invariants.values()), 'canonicalisation_invariant_failure')
    state['assets'].update(mesh=mesh.get_path_name(), skeleton=mesh.skeleton.get_path_name())
    passed(stage, dict(route='generated_canonical_derived_asset' if unit['needs_canonicalisation'] else 'original_canonical_asset', conversion=conversion, destination=destination, invariants=invariants, bind_position_max_error_cm=error))

    stage = 'semantic_mapping'
    semantics = analyse(mesh, destination['bones'])
    passed(stage, semantics)
    T = unreal.AssetToolsHelpers.get_asset_tools()
    stage = 'manny_source_probe'
    source_mesh = unreal.load_asset(C['manny_mesh'])
    source_description = inspect(source_mesh)
    source_semantics = analyse(source_mesh, source_description['bones'])

    stage = 'ik_rig'
    ik = T.create_asset('IK_Destination', B+'/Retarget', unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    ic = unreal.IKRigController.get_controller(ik)
    require(ic.set_skeletal_mesh(mesh) and ic.apply_auto_generated_retarget_definition() and ic.apply_auto_fbik(), 'target_auto_characterisation_or_fbik_failed')
    ic.set_retarget_root(semantics['pelvis'])
    ic.set_root_motion_bone(semantics['root'])
    if 'Root' not in [str(x.chain_name) for x in ic.get_retarget_chains()]:
        ic.add_retarget_chain('Root', semantics['root'], semantics['root'], '')
    # Match the proven source leg/ball convention using discovered Foot chain bones.
    for side in ['Left', 'Right']:
        foot = bone_name(destination['bones'], semantics['chains'][side+'Foot']['start'])
        ic.set_retarget_chain_end_bone(side+'Leg', foot)
        require(ic.set_goal_bone(ic.get_retarget_chain_goal(side+'Leg'), foot), 'invalid_leg_goal')
    target_snapshot = rig_snapshot(ik)
    for row in target_snapshot['chains']:
        chain_path(destination['bones'], row['start'], row['end'])
    for goal in ic.get_all_goals():
        bone_name(destination['bones'], goal.get_editor_property('bone_name'))
        for prop in ['initial_transform', 'current_transform']:
            require(all(math.isfinite(x) for a in tr(goal.get_editor_property(prop)).values() for x in a), 'nonfinite_goal')
    require(all(n in [x['name'] for x in target_snapshot['chains']] for n in REQUIRED), 'missing_target_chain')
    require(unreal.EditorAssetLibrary.save_loaded_asset(ik, False), 'target_rig_save_failed')
    state['assets']['target_rig'] = ik.get_path_name()
    passed(stage, dict(configuration=target_snapshot, root_motion_policy='In-place; identified root motion bone, Root chain; root motion op disabled'))

    stage = 'manny_source'
    epic_rig = unreal.load_asset(C['manny_rig'])
    source_ctl = unreal.IKRigController.get_controller(epic_rig)
    missing = [n for n in REQUIRED if n not in [str(x.chain_name) for x in source_ctl.get_retarget_chains()]]
    source_rig = epic_rig
    if missing:
        source_rig = T.duplicate_asset('IK_MannySource', B+'/Retarget', epic_rig)
        sc = unreal.IKRigController.get_controller(source_rig)
        for name in missing:
            desc = source_semantics['chains'][name]
            sc.add_retarget_chain(name, desc['start'], desc['end'], '')
        require(unreal.EditorAssetLibrary.save_loaded_asset(source_rig, False), 'source_copy_save_failed')
    source_snapshot = rig_snapshot(source_rig)
    for row in source_snapshot['chains']:
        chain_path(source_description['bones'], row['start'], row['end'])
    state['assets']['source_rig'] = source_rig.get_path_name()
    passed(stage, dict(original=C['manny_rig'], copied=bool(missing), added_chains=missing, reason='Required target foot chains absent from original source rig; endpoints discovered by UE source auto-characterisation', configuration=source_snapshot))

    stage = 'retarget_setup'
    rt = T.create_asset('RTG_MannyToDestination', B+'/Retarget', unreal.IKRetargeter, unreal.IKRetargetFactory())
    rc = unreal.IKRetargeterController.get_controller(rt)
    for side, rig, preview in [(unreal.RetargetSourceOrTarget.SOURCE, source_rig, source_mesh), (unreal.RetargetSourceOrTarget.TARGET, ik, mesh)]:
        rc.set_ik_rig(side, rig)
        rc.set_preview_mesh(side, preview)
    rc.remove_all_ops()
    rc.add_default_ops()
    rc.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    for i in range(rc.get_num_retarget_ops()):
        if str(rc.get_op_name(i)) in ['Root Motion', 'Speed Plant IK Goals', 'Stride Warp IK Goals']:
            rc.set_retarget_op_enabled(i, False)
    target_side = unreal.RetargetSourceOrTarget.TARGET
    rc.reset_retarget_pose(rc.get_current_retarget_pose_name(target_side), [], target_side)
    rc.auto_align_all_bones(target_side)
    mapping = {n: str(rc.get_source_chain(n)) for n in REQUIRED}
    require(all(k == val for k, val in mapping.items()), 'required_chain_mapping_failed')
    settings = ret_snapshot(rt, list(destination['bones']))
    require(all(math.isfinite(x) for q in settings['pose_offsets'].values() for x in q), 'nonfinite_retarget_pose')
    require(unreal.RiggedUnitBridgeLibrary.validate_retarget_initialisation(source_mesh, mesh, rt), 'native_retarget_processor_initialisation_failed')
    require(unreal.EditorAssetLibrary.save_loaded_asset(rt, False), 'retargeter_save_failed')
    # Inspect the saved asset through its actual controller, not the auto-map return value.
    saved = unreal.load_asset(rt.get_path_name())
    saved_ctl = unreal.IKRetargeterController.get_controller(saved)
    require(all(str(saved_ctl.get_source_chain(n)) == n for n in REQUIRED), 'saved_mapping_invalid')
    state['assets']['retargeter'] = rt.get_path_name()
    passed(stage, dict(mapping=mapping, semantic_binding_count=len(mapping)+1, source_rig=source_rig.get_path_name(), target_rig=ik.get_path_name(), processor_initialised=True, configuration=settings, alignment='UE automatic chain alignment; no actor offset, stature multiplier or unit compensation', source_root=source_snapshot['retarget_root'], target_root=target_snapshot['retarget_root']))

    stage = 'animation_bake'
    inputs = unreal.IKRetargetBatchOperationInputs()
    inputs.set_editor_properties(dict(assets_to_retarget=[unreal.EditorAssetLibrary.find_asset_data(p) for p in C['motions'].values()], source_mesh=source_mesh, target_mesh=mesh, ik_retarget_asset=rt, target_path=B+'/Animations', include_referenced_assets=False, overwrite_existing_files=False))
    baked = unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)
    require(len(baked) == len(C['motions']), 'animation_bake_count_failed')
    by_name = {x.get_asset().get_name(): x.get_asset() for x in baked}
    for role, path in C['motions'].items():
        anim = by_name[path.rsplit('/', 1)[-1]]
        source = unreal.load_asset(path)
        require(anim.get_editor_property('skeleton') == mesh.skeleton and abs(anim.get_play_length()-source.get_play_length()) < 1e-5, 'baked_skeleton_or_duration_invalid')
        require(unreal.RiggedUnitBridgeLibrary.validate_baked_tracks(anim, semantics['root'], destination['height_cm']*2), 'nonfinite_or_explosive_baked_keys')
        require(unreal.EditorAssetLibrary.save_loaded_asset(anim, False), 'animation_save_failed')
        model = anim.get_editor_property('data_model_interface')
        rate = model.get_frame_rate()
        state['clips'].append(dict(role=role, path=anim.get_path_name(), source=path, duration_s=anim.get_play_length(), frame_rate=[rate.numerator, rate.denominator], keys=model.get_number_of_keys(), skeleton=mesh.skeleton.get_path_name(), all_bone_keys_finite=True, root_keys_unit_scale=True, root_flags={k: str(anim.get_editor_property(k)) for k in ['enable_root_motion', 'force_root_lock', 'root_motion_root_lock']}))
    factory = unreal.AnimSequenceFactory()
    factory.set_editor_property('target_skeleton', mesh.skeleton)
    neutral = T.create_asset('Reference_Native', B+'/Animations', unreal.AnimSequence, factory)
    ctl = neutral.get_editor_property('controller')
    ctl.open_bracket('Destination reference helper', False)
    ctl.set_frame_rate(unreal.FrameRate(60, 1), False)
    ctl.set_number_of_frames(unreal.FrameNumber(60), False)
    ref = mesh.skeleton.get_reference_pose()
    for n in ref.get_bone_names():
        t = ref.get_bone_pose(n, unreal.AnimPoseSpaces.LOCAL)
        ctl.add_bone_track(n, False)
        require(ctl.set_bone_track_keys(n, [t.translation]*61, [t.rotation]*61, [t.scale3d]*61, False), 'reference_helper_track_failed')
    ctl.close_bracket(False)
    neutral.set_preview_skeletal_mesh(mesh)
    require(unreal.RiggedUnitBridgeLibrary.validate_baked_tracks(neutral, semantics['root'], destination['height_cm']*2), 'reference_helper_keys_invalid')
    require(unreal.EditorAssetLibrary.save_loaded_asset(neutral, False), 'reference_helper_save_failed')
    state['clips'].insert(0, dict(role='neutral', path=neutral.get_path_name(), source=None, duration_s=neutral.get_play_length(), frame_rate=[60, 1], keys=61, skeleton=mesh.skeleton.get_path_name()))
    passed(stage, dict(clips=state['clips'], validation='Saved asset type, skeleton, duration and key data; native finite/scale verification follows in fresh process'))
    state.update(status='PASS', destination=destination, semantics=semantics, output_namespace=B, next_required='fresh main-project native playback; dependency and preservation audit')
except Exception:
    state.update(status='FAIL', failed_stage=stage, error=traceback.format_exc())
    write(stage+'_failure.json', dict(status='FAIL', reason=state['error']))
write('authoring_result.json', state)
print('R2_AUTHORING', state['status'], state.get('error', ''))
