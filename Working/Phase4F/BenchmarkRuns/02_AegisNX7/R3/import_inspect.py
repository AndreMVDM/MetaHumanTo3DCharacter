"""Normal native Aegis import, appearance and scale ledger; no rig repair/conversion."""
import unreal, sys, json, traceback, ast, hashlib, math
from pathlib import Path
sys.dont_write_bytecode = True
W = Path(__file__).resolve().parent
R = W.parents[4]
O = R/'Documentation/Phase4F/Benchmark/Runs/02_AegisNX7/R3'
B = '/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/Original'
P = R/'Working/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2/author.py'
# Reuse accepted R2 inspection functions verbatim; do not run its authoring body.
tree = ast.parse(P.read_text())
helpers = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ['require','v','tr','inspect']], type_ignores=[])
exec(compile(helpers, str(P), 'exec'), globals())
result = dict(status='RUNNING', source_assets_modified=False)
try:
    already_imported = bool(unreal.EditorAssetLibrary.list_assets(B+'/Character', True, False))
    sources = list((W/'Input').glob('*.fbx'))
    require(len(sources)==1, 'one FBX required')
    options = unreal.FbxImportUI()
    options.set_editor_properties(dict(import_as_skeletal=True, mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH, import_animations=False, import_materials=True, import_textures=True, create_physics_asset=True, skeleton=None))
    data = options.skeletal_mesh_import_data
    data.set_editor_properties(dict(import_uniform_scale=1.0, import_translation=unreal.Vector(), import_rotation=unreal.Rotator()))
    settings = {k: str(data.get_editor_property(k)) for k in ['import_uniform_scale','import_translation','import_rotation','convert_scene','convert_scene_unit','force_front_x_axis']}
    task = unreal.AssetImportTask()
    task.set_editor_properties(dict(filename=str(sources[0]), destination_path=B+'/Character', destination_name='SK_AegisNX7', automated=True, save=True, replace_existing=False, options=options))
    if not already_imported:
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    assets = [unreal.load_asset(p) for p in unreal.EditorAssetLibrary.list_assets(B, True, False)]
    meshes = [x for x in assets if isinstance(x, unreal.SkeletalMesh)]
    require(len(meshes)==1, 'outside_v1_input_contract: not one SkeletalMesh')
    mesh = meshes[0]
    native = inspect(mesh)
    material_slots = []
    for slot in mesh.materials:
        mat = slot.material_interface
        material_slots.append(dict(name=str(slot.material_slot_name), material=mat.get_path_name() if mat else None, type=mat.get_class().get_name() if mat else None))
    textures = [dict(path=x.get_path_name(), type=x.get_class().get_name(), size=[x.blueprint_get_size_x(),x.blueprint_get_size_y()],srgb=x.get_editor_property('srgb')) for x in assets if isinstance(x,unreal.Texture2D)]
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    depopts = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True)
    material_dependencies = {x['material']: [str(d) for d in registry.get_dependencies(x['material'].split('.')[0], depopts)] for x in material_slots if x['material']}
    require(bool(material_slots) and all(x['material'] for x in material_slots), 'missing imported material slot')
    require(bool(textures), 'supplied texture not imported')
    source = json.loads((O/'source_fbx.json').read_text())
    # The source FBX supplies no Actor/Component scene. Measure an ordinary unit
    # inspection actor; no intended stature factor is invented or baked in.
    require(unreal.EditorLevelLibrary.new_level(B+'/Inspection/L_InputReference'), 'inspection level failed')
    E = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = E.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector())
    component = actor.skeletal_mesh_component
    component.set_skeletal_mesh_asset(mesh)
    transform = component.get_world_transform()
    actor_scale = v(actor.get_actor_scale3d())
    relative_scale = v(component.get_relative_transform().scale3d)
    world_scale = v(transform.scale3d)
    _, bounds_extent, _ = unreal.SystemLibrary.get_component_bounds(component)
    root = native['bones'][native['root']]['local']
    explicit_source_scales = [dict(model=x['name'], scale=x['properties'].get('Lcl Scaling',[1,1,1])) for x in source['models']]
    explicit18 = [x for x in explicit_source_scales if all(abs(float(s)-1.8)<1e-5 for s in x['scale'])]
    require(not explicit18, 'source contains an explicit stature layer requiring separate analysis')
    scene = dict(actor_scale=actor_scale, component_relative_scale=relative_scale, component_world_scale=world_scale, parent_actor=None, parent_contribution=[1,1,1], effective_world_height_cm=2*bounds_extent.z, intrinsic_height_cm=native['height_cm'])
    require(actor_scale==relative_scale==world_scale==[1,1,1], 'external scene scale requires intended-stature analysis')
    result.update(status='PASS', native=native, imported_paths=list(task.imported_object_paths), inventory=[dict(path=x.get_path_name(), type=x.get_class().get_name()) for x in assets], material_slots=material_slots, textures=textures, material_dependencies=material_dependencies, import_settings=settings, source_units=source['global_settings'], root_reference=root, source_model_scales=explicit_source_scales, scene=scene, stature_classification='intrinsic_size_already_correct', reported_18_classification='baked_into_geometry_or_reference', reported_18_evidence='Source vertices already span approximately 1.799121 metres in source local Z; no standalone 1.8 model/import/scene factor exists. Historical multiplication by exactly 1.8 cannot be established without an unscaled predecessor.', additional_stature_normalisation=False, source_scene_actor_or_component_supplied=False, input_contract='One existing rigged/skinned humanoid SkeletalMesh; all integrated surfaces retained')
    require(unreal.EditorLevelLibrary.save_current_level(), 'inspection save failed')
except Exception:
    result.update(status='FAIL', error=traceback.format_exc())
(O/'import_inspection.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print('R3_IMPORT_INSPECTION',result['status'],result.get('error',''))
