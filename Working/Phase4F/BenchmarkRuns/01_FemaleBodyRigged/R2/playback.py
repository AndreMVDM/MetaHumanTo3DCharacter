"""Fresh main-project native destination-only proof; no authoring host/bridge loaded.

Creates and saves a destination-only proof map, reloads it from disk, then runs PIE.
Samples compact native transforms and skinned bounds, rather than duplicate meshes.
"""
import unreal, json, sys, math, time, traceback
from pathlib import Path

sys.dont_write_bytecode = True
W = Path(__file__).resolve().parent
R = W.parents[4]
O = R / 'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/R2_EndToEnd'
A = json.loads((O/'authoring_result.json').read_text())
assert A['status'] == 'PASS'
B = A['output_namespace']
D = A['destination']
root = A['semantics']['root']
pelvis = A['semantics']['pelvis']
moving = [A['semantics']['chains'][s+'Arm']['end'] for s in ['Left', 'Right']] + [A['semantics']['chains'][s+'Foot']['start'] for s in ['Left', 'Right']]
names = list(D['bones'])
lookup = {n.casefold(): n for n in names}
moving = [lookup[n.casefold()] for n in moving]
VIS = O/'NativePlayback'
VIS.mkdir(exist_ok=True)
result = dict(status='RUNNING', fresh_main_project_process=True, native_game_world=True, authoring_bridge_loaded=hasattr(unreal, 'RiggedUnitBridgeLibrary'), phases=[], assets=A['assets'], saved_assets_loaded=[], source_actor_count=None, live_retarget_node_count=None)
unreal.EditorPythonScripting.set_keep_python_script_alive(True)


def write():
    (O/'native_playback.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')


def v(x):
    return [float(x.x), float(x.y), float(x.z)]


def serial_transform(t):
    return dict(translation=v(t.translation), rotation=[t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w], scale=v(t.scale3d))


def require(ok, message):
    if not ok:
        raise ValueError(message)


try:
    require(not result['authoring_bridge_loaded'], 'main project loaded authoring bridge')
    mesh = unreal.load_asset(A['assets']['mesh'])
    skeleton = unreal.load_asset(A['assets']['skeleton'])
    require(isinstance(mesh, unreal.SkeletalMesh) and mesh.skeleton == skeleton, 'saved destination ownership invalid')
    for path in [A['assets']['mesh'], A['assets']['skeleton']] + [c['path'] for c in A['clips']]:
        asset = unreal.load_asset(path)
        require(asset is not None, 'saved_asset_load_failed: '+path)
        result['saved_assets_loaded'].append(path)
    for row in A['clips']:
        anim = unreal.load_asset(row['path'])
        require(isinstance(anim, unreal.AnimSequence) and anim.get_editor_property('skeleton') == skeleton, 'saved animation not destination-native')
    require(abs(2*mesh.get_bounds().box_extent.z-D['height_cm']) < .001, 'fresh bind size changed')
    ref = skeleton.get_reference_pose()
    require(all(abs(x-1) < 1e-6 for x in v(ref.get_bone_pose(root, unreal.AnimPoseSpaces.LOCAL).scale3d)), 'fresh reference root not canonical')

    E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    U = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    map_path = B+'/Playback/L_DestinationProof'
    if not unreal.EditorAssetLibrary.does_asset_exist(map_path):
        require(unreal.EditorLevelLibrary.new_level(map_path), 'new proof level failed')
        actor = E.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector())
        actor.set_actor_label('R2 destination-native character')
        component = actor.skeletal_mesh_component
        component.set_skeletal_mesh_asset(mesh)
        component.set_forced_lod(1)
        component.set_update_animation_in_editor(True)
        component.set_editor_property('visibility_based_anim_tick_option', unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
        component.play_animation(unreal.load_asset(A['clips'][0]['path']), True)
        floor = E.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, -5))
        floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
        floor.set_actor_scale3d(unreal.Vector(30, 30, .1))
        E.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 250), unreal.Rotator(pitch=-45, yaw=-45, roll=0))
        E.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 250))
        require(unreal.EditorLevelLibrary.save_current_level(), 'save proof failed')
    require(unreal.EditorLevelLibrary.load_level(map_path), 'freshly load saved proof failed')
    result['playback_map'] = map_path
    height = D['height_cm']
    eye = unreal.Vector(0, height*1.6, height*.55)
    U.set_level_viewport_camera_info(eye, unreal.MathLibrary.find_look_at_rotation(eye, unreal.Vector(0, 0, height*.5)))
    unreal.EditorLevelLibrary.editor_set_game_view(True)
    unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_UNLIT)
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    reg.search_all_assets(True)
    opts = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True, include_searchable_names=True, include_soft_management_references=True, include_hard_management_references=True)
    seeds = [map_path, A['assets']['mesh'].split('.')[0], A['assets']['skeleton'].split('.')[0]]+[c['path'].split('.')[0] for c in A['clips']]
    seen, edges, todo = set(), {}, seeds[:]
    while todo:
        p = todo.pop()
        if p in seen:
            continue
        seen.add(p)
        edges[p] = [str(x) for x in reg.get_dependencies(p, opts)]
        todo.extend(edges[p])
    # An already-canonical input is deliberately consumed as the destination;
    # its explicitly validated mesh/Skeleton seeds need not live under B.
    destination_seeds = {A['assets'][k].split('.')[0] for k in ['mesh', 'skeleton']}
    foreign = [p for p in seen if p.startswith('/Game/') and not p.startswith(B+'/') and p not in destination_seeds]
    authoring = [p for p in seen if '/Retarget/' in p or 'RiggedUnitBridge' in p]
    require(not foreign and not authoring, 'unintended runtime dependency')
    result['runtime_dependency_closure'] = dict(seeds=seeds, packages=sorted(seen), edges=edges, foreign_game_packages=foreign, authoring_packages=authoring)
    write()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_play_simulate()
except Exception:
    result.update(status='FAIL', error=traceback.format_exc())
    write()
    unreal.SystemLibrary.quit_editor()
    raise

ready = False
phase_index = 0
phase_started = False
settle = 0
rows = []
shots = set()
geometry = None
last_position = None
advanced_seconds = 0
started = time.perf_counter()
busy = False


def tick(delta):
    global ready, actor, component, phase_index, phase_started, settle, rows, shots, geometry, last_position, advanced_seconds, busy
    if busy:
        return
    busy = True
    try:
        require(time.perf_counter()-started < 300, 'native playback timeout')
        if not ready:
            world = U.get_game_world()
            if not world:
                return
            actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.SkeletalMeshActor)
            require(len(actors) == 1, 'unexpected source/character actor')
            actor = actors[0]
            component = actor.skeletal_mesh_component
            require(component.get_anim_instance().get_class().get_name() == 'AnimSingleNodeInstance', 'unexpected live animation blueprint')
            result['source_actor_count'] = 0
            result['live_retarget_node_count'] = 0
            ready = True
        row = A['clips'][phase_index]
        if not phase_started:
            component.play_animation(unreal.load_asset(row['path']), True)
            component.set_play_rate(1)
            component.set_position(0, False)
            settle = 3
            rows, shots, geometry, last_position, advanced_seconds = [], set(), None, None, 0
            phase_started = True
            return
        if settle:
            settle -= 1
            return
        position = component.get_position()
        if last_position is not None:
            change = position-last_position
            if change < -row['duration_s']*.5:
                change += row['duration_s']
            if change > 0:
                advanced_seconds += change
        last_position = position
        transforms = {n: serial_transform(component.get_socket_transform(n, unreal.RelativeTransformSpace.RTS_COMPONENT)) for n in names}
        require(all(math.isfinite(x) for t in transforms.values() for a in t.values() for x in a), 'nonfinite native bone transform')
        root_scale = transforms[root]['scale']
        component_scale = v(component.get_world_transform().scale3d)
        actor_scale = v(actor.get_actor_scale3d())
        require(max(abs(x-1) for x in root_scale+component_scale+actor_scale) < 1e-4, 'native root/component/actor scale regression')
        points = {n: t['translation'] for n, t in transforms.items()}
        lengths = {n: math.dist(points[n], points[b['parent']]) for n, b in D['bones'].items() if b['parent'] and b['parent'] != root}
        limb_error = max(abs(length-math.dist(D['bones'][n]['component']['translation'], D['bones'][D['bones'][n]['parent']]['component']['translation'])) for n, length in lengths.items())
        require(limb_error < .01, 'native limb scale regression')
        require(max(math.dist(t['translation'], D['bones'][n]['component']['translation']) for n, t in transforms.items()) < height*2, 'native placement/size explosion')
        rows.append(dict(position_s=position, observed_advance_s=advanced_seconds, moving={n: points[n] for n in moving}, pelvis=points[pelvis], root=transforms[root], component_scale=component_scale, actor_scale=actor_scale, actor_location=v(actor.get_actor_location()), max_limb_error_cm=limb_error))
        total = row['duration_s']*(2 if row['role'] in ['walk', 'run'] else 1)
        for fraction in [.25, .65]:
            if advanced_seconds >= total*fraction and fraction not in shots:
                file = VIS/(row['role']+'_'+str(fraction)+'.png')
                require(unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, str(file)), 'native screenshot request failed')
                shots.add(fraction)
        if advanced_seconds >= total*.5 and geometry is None:
            dm = unreal.DynamicMesh()
            opts = unreal.GeometryScriptCopyMeshFromComponentOptions()
            opts.set_editor_property('requested_lod', unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL, lod_index=0))
            _, _, outcome = unreal.GeometryScript_SceneUtils.copy_mesh_from_component(component, dm, opts, True)
            require(outcome == unreal.GeometryScriptOutcomePins.SUCCESS, 'native posed geometry copy failed')
            Q = unreal.GeometryScript_MeshQueries
            pts = [v(Q.get_vertex_position(dm, i)[0]) for i in range(Q.get_num_vertex_i_ds(dm))]
            require(pts and all(math.isfinite(x) for p in pts for x in p), 'nonfinite native skin deformation')
            mins, maxs = [min(p[j] for p in pts) for j in range(3)], [max(p[j] for p in pts) for j in range(3)]
            geometry = dict(position_s=position, bounds_cm=[mins, maxs], finite=True, vertex_count=len(pts), triangle_count=Q.get_num_triangle_i_ds(dm))
            require(maxs[2] < height*2 and mins[2] > -height, 'native surface placement explosion')
            if row['role'] == 'neutral':
                require(abs(maxs[2]-mins[2]-height) < .001, 'native neutral physical height changed')
        if advanced_seconds >= total:
            # Slate callbacks can precede the game animation evaluation after a
            # clip switch. Never count that transition as the clip's own motion.
            steady = [x for x in rows if x['observed_advance_s'] >= .25]
            require(len(steady) >= 3, 'insufficient settled native observation')
            excursion = {n: max(math.dist(x['moving'][n], steady[0]['moving'][n]) for x in steady) for n in moving}
            require(geometry is not None and len(rows) >= 3, 'insufficient native observation')
            require(row['role'] == 'neutral' or max(excursion.values()) > .001, 'animation time advanced but no representative bone motion')
            result['phases'].append(dict(role=row['role'], status='PASS', animation_time_advanced_s=advanced_seconds, sample_count=len(rows), settled_sample_count=len(steady), root_scale=[1, 1, 1], component_scale=[1, 1, 1], actor_scale=[1, 1, 1], pelvis_z_range_cm=[min(x['pelvis'][2] for x in steady), max(x['pelvis'][2] for x in steady)], motion_excursion_cm=excursion, maximum_limb_error_cm=max(x['max_limb_error_cm'] for x in rows), geometry=geometry, samples=rows))
            phase_index += 1
            phase_started = False
            write()
            if phase_index == len(A['clips']):
                result.update(status='PASS', conclusion='Four saved destination-native animations advance independently in fresh main-project native PIE; no live source/retarget/bridge required')
                write()
                unreal.unregister_slate_post_tick_callback(handle)
                unreal.SystemLibrary.quit_editor()
    except Exception:
        result.update(status='FAIL', error=traceback.format_exc())
        write()
        unreal.unregister_slate_post_tick_callback(handle)
        unreal.SystemLibrary.quit_editor()
    finally:
        busy = False


handle = unreal.register_slate_post_tick_callback(tick)
