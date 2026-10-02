"""Make the textureless comparison visible without changing source Skeletal Mesh assets."""
import json
import traceback
from pathlib import Path
import unreal

out = {"materials": [], "lights": [], "errors": []}
try:
    base = "/Game/MetaHumanTo3DCharacter/Phase2"
    bp = unreal.EditorAssetLibrary.load_asset(base + "/BP_Phase2_RetargetTest")
    neutral = unreal.EditorAssetLibrary.load_asset("/Engine/EngineMaterials/DefaultMaterial")
    assert bp and neutral
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    func = unreal.SubobjectDataBlueprintFunctionLibrary
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(bp):
        obj = func.get_object_for_blueprint(func.get_data(handle), bp)
        if isinstance(obj, unreal.SkeletalMeshComponent):
            for slot in range(obj.get_num_materials()):
                obj.set_material(slot, neutral)
            out["materials"].append({"component": obj.get_name(), "slots": obj.get_num_materials(),
                                     "override": neutral.get_path_name()})
    assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level.load_level(base + "/Maps/L_Phase2_RetargetTest")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    floor = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == "Phase 2 Floor")
    floor.get_editor_property("static_mesh_component").set_material(0, neutral)
    for side, y in (("Left", -400), ("Right", 400)):
        light = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(450, y, 300), unreal.Rotator())
        light.set_actor_label("Phase 2 " + side + " Fill")
        comp = light.get_editor_property("point_light_component")
        comp.set_editor_property("intensity", 50000.0)
        comp.set_editor_property("attenuation_radius", 1800.0)
        out["lights"].append(light.get_path_name())
    assert level.save_current_level()
except Exception:
    out["errors"].append(traceback.format_exc())
Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\presentation_update.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
