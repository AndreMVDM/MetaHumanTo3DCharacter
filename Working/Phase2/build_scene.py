"""Create the reusable runtime comparison actor and a dedicated Phase 2 level."""
import json
import traceback
from pathlib import Path
import unreal

ROOT = "/Game/MetaHumanTo3DCharacter/Phase2"
OUT = Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\scene_build.json")
result = {"errors": [], "components": []}
stage = "init"
try:
    actor_path = ROOT + "/BP_Phase2_RetargetTest"
    stage = "create actor Blueprint"
    bp = (unreal.EditorAssetLibrary.load_asset(actor_path)
          if unreal.EditorAssetLibrary.does_asset_exist(actor_path) else
          unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(actor_path, unreal.Actor))
    assert bp, "Actor Blueprint creation failed"
    result["actor_blueprint"] = bp.get_path_name()
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    func = unreal.SubobjectDataBlueprintFunctionLibrary
    handles = subsystem.k2_gather_subobject_data_for_blueprint(bp)
    result["initial_handles"] = [str(func.get_display_name(func.get_data(h))) for h in handles]
    root_handle = next((h for h in handles if func.is_default_scene_root(func.get_data(h))), None)
    assert root_handle, "No default scene root"

    def component(name, parent, mesh, anim_bp=None, run=None, offset=0):
        params = unreal.AddNewSubobjectParams(blueprint_context=bp,
                                              new_class=unreal.SkeletalMeshComponent,
                                              parent_handle=parent)
        handle, reason = subsystem.add_new_subobject(params)
        assert func.is_handle_valid(handle), str(reason)
        assert subsystem.rename_subobject(handle, name), "Cannot name " + name
        template = func.get_object_for_blueprint(func.get_data(handle), bp)
        assert template, "No component template: " + name
        template.set_editor_property("skeletal_mesh_asset", mesh)
        template.set_editor_property("visibility_based_anim_tick_option",
                                     unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
        template.set_editor_property("relative_location", unreal.Vector(0, offset, 0))
        if run:
            template.override_animation_data(run, True, True, 0.0, 1.0)
        else:
            template.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
            template.set_editor_property("anim_class", anim_bp.generated_class())
        result["components"].append({"name": name, "template": template.get_path_name(),
                                      "mesh": mesh.get_path_name(),
                                      "animation": run.get_path_name() if run else anim_bp.get_path_name(),
                                      "relative_y": offset})
        return handle

    source_mesh = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
    run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd")
    source_handle = component("Manny_Source", root_handle, source_mesh, run=run, offset=-250)
    for label, offset in (("UE5", 250), ("Mixamo", 500)):
        base = ROOT + "/" + label
        mesh = unreal.EditorAssetLibrary.load_asset(base + "/SK_Lara_" + label)
        anim = unreal.EditorAssetLibrary.load_asset(base + "/ABP_Lara_" + label + "_Retarget")
        component("Lara_" + label + "_Target", source_handle, mesh, anim_bp=anim, offset=offset)
    stage = "compile actor"
    assert unreal.BlueprintEditorLibrary.compile_blueprint(bp), "Actor Blueprint compilation failed"
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    result["actor_status"] = str(bp.get_editor_property("status"))
    stage = "create map"
    map_path = ROOT + "/Maps/L_Phase2_RetargetTest"
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level.new_level(map_path), "Cannot create Phase 2 level"
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    demo = actors.spawn_actor_from_class(bp.generated_class(), unreal.Vector(0, 0, 0), unreal.Rotator())
    demo.set_actor_label("Manny and Lara Retarget Comparison")
    result["actor_instance"] = demo.get_path_name()
    camera = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(650, 0, 115), unreal.Rotator(0, 180, 0))
    camera.set_actor_label("Phase 2 Comparison Camera")
    camera.get_editor_property("camera_component").set_editor_property("field_of_view", 65.0)
    camera.set_editor_property("auto_activate_for_player", unreal.PlayerIndex.PLAYER0)
    result["camera"] = camera.get_path_name()
    floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, -3), unreal.Rotator())
    floor.set_actor_label("Phase 2 Floor")
    floor_mesh = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    floor.get_editor_property("static_mesh_component").set_static_mesh(floor_mesh)
    floor.set_actor_scale3d(unreal.Vector(12, 12, 1))
    light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(200, -300, 500), unreal.Rotator(-45, 30, 0))
    light.set_actor_label("Phase 2 Key Light")
    result["map"] = map_path + ".L_Phase2_RetargetTest"
    assert level.save_current_level(), "Cannot save Phase 2 level"
except Exception:
    result["errors"].append({"stage": stage, "traceback": traceback.format_exc()})
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print("PHASE2_SCENE_BUILD_DONE")
