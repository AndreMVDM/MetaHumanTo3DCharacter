"""Generic runtime ownership certificate; no character names or folder allowances.

Only explicit playback seeds and typed appearance dependencies reachable from
the destination mesh's actual material slots may own project packages. Registry
edges through Engine/plugin parents are traversed too: an indirect dependency
on a foreign rig/animation/mesh is never concealed by a material parent.
"""
VERSION = 'phase4f.rigged-runtime-appearance-closure/1.0.0'
APPEARANCE_TYPES = frozenset({
    'Material', 'MaterialInstanceConstant', 'Texture2D', 'TextureCube',
    'Texture2DArray', 'TextureCubeArray', 'VolumeTexture',
    'MaterialFunction', 'MaterialFunctionInstance',
    'MaterialFunctionMaterialLayer', 'MaterialFunctionMaterialLayerBlend',
    'MaterialParameterCollection', 'PhysicalMaterial', 'SubsurfaceProfile',
})
MATERIAL_TYPES = frozenset({'Material', 'MaterialInstanceConstant'})


def certify(seeds, packages, edges, material_roots, classes):
    seeds, packages, roots = set(seeds), set(packages), set(material_roots)
    errors = []
    for root in sorted(roots):
        if root not in packages or set(classes.get(root, [])) - MATERIAL_TYPES or not classes.get(root):
            errors.append({'package': root, 'reason': 'invalid_or_unclassified_material_slot'})
    visited, todo = set(), list(roots)
    while todo:
        p = todo.pop()
        if p in visited:
            continue
        visited.add(p)
        if p not in edges:
            errors.append({'package': p, 'reason': 'missing_dependency_graph_node'})
            continue
        # Explicit destination assets may not enter through an appearance edge.
        # A material must not hide an otherwise allowed animation/character seed.
        # UE's non-persistent transient package and script modules are graph
        # containers, not exported runtime content. Still traverse every edge.
        if p == '/Engine/Transient' and classes.get(p):
            errors.append({'package': p, 'reason': 'unexpected_persisted_transient_export'})
        if not p.startswith('/Script/') and p != '/Engine/Transient':
            types = set(classes.get(p, []))
            if not types or not types <= APPEARANCE_TYPES:
                errors.append({'package': p, 'reason': 'unsupported_or_unclassified_appearance_dependency', 'types': sorted(types)})
        todo.extend(edges[p])
    owned = {p for p in visited if p.startswith('/Game/') and classes.get(p) and set(classes[p]) <= APPEARANCE_TYPES}
    foreign = sorted(p for p in packages if p.startswith('/Game/') and p not in seeds and p not in owned)
    foreign = sorted(set(foreign) | {e['package'] for e in errors})
    return dict(version=VERSION, status='PASS' if not foreign else 'FAIL',
                explicit_runtime_seeds=sorted(seeds), bound_material_roots=sorted(roots),
                appearance_packages=sorted(visited), owned_project_appearance=sorted(owned),
                classes={p: classes.get(p, []) for p in sorted(visited) if not p.startswith('/Script/')},
                errors=errors, foreign_game_packages=foreign)


def certify_native(mesh, seeds, packages, edges, registry):
    roots = [slot.material_interface.get_path_name().split('.')[0] for slot in mesh.materials if slot.material_interface]
    classes = {}
    for p in packages:
        if not p.startswith('/Script/'):
            classes[p] = sorted({str(a.asset_class_path.asset_name) for a in registry.get_assets_by_package_name(p)})
    return certify(seeds, packages, edges, roots, classes)
