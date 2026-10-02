"""Correct UE5 FBX root-scale translation and comparison-map lighting."""
import json
import traceback
from pathlib import Path
import unreal

root = "/Game/MetaHumanTo3DCharacter/Phase2"
out = {"errors": [], "changes": []}
try:
    ret = unreal.EditorAssetLibrary.load_asset(root + "/UE5/RTG_Manny_Lara_UE5")
    ctl = unreal.IKRetargeterController.get_controller(ret)
    pelvis = ctl.get_op_controller(ctl.get_index_of_op_by_name("Pelvis Motion"))
    settings = pelvis.get_settings()
    out["before"] = str(settings)
    # FBX has a 100x scale on the root bone. Translation produced in centimetres
    # by Pelvis Motion is inherited through that root and must be divided by 100.
    settings.scale_horizontal = 0.01
    settings.scale_vertical = 0.01
    pelvis.set_settings(settings)
    out["after"] = str(pelvis.get_settings())
    out["changes"].append("UE5 Pelvis Motion scale horizontal and vertical 0.01")
    assert unreal.EditorAssetLibrary.save_loaded_asset(ret)

    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level.load_level(root + "/Maps/L_Phase2_RetargetTest")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for actor in actors:
        label = actor.get_actor_label()
        if label in ("Phase 2 Left Fill", "Phase 2 Right Fill"):
            comp = actor.get_editor_property("point_light_component")
            comp.set_editor_property("intensity", 1200.0)
            comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
            out["changes"].append(label + ": intensity 1200, movable")
        elif label == "Phase 2 Key Light":
            comp = actor.get_editor_property("directional_light_component")
            comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
            out["changes"].append(label + ": movable")
    assert level.save_current_level()
except Exception:
    out["errors"].append(traceback.format_exc())
Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\runtime_correction.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
