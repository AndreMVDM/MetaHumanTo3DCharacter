import json
import traceback
from pathlib import Path
import unreal

map_path = "/Game/MetaHumanTo3DCharacter/Phase2/Maps/L_Phase2_RetargetTest"
actor_path = "/Game/MetaHumanTo3DCharacter/Phase2/BP_Phase2_RetargetTest"
out = {"map": map_path + ".L_Phase2_RetargetTest", "actors": [], "errors": []}
try:
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level.load_level(map_path)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    bp = unreal.EditorAssetLibrary.load_asset(actor_path)
    demo = actors.spawn_actor_from_class(bp.generated_class(), unreal.Vector(0, 0, 0), unreal.Rotator())
    demo.set_actor_label("Manny and Lara Retarget Comparison")
    out["actors"].append({"label": demo.get_actor_label(), "path": demo.get_path_name()})
    camera = actors.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(650, 0, 115), unreal.Rotator(0, 180, 0))
    camera.set_actor_label("Phase 2 Comparison Camera")
    camera.get_editor_property("camera_component").set_editor_property("field_of_view", 65.0)
    camera.set_editor_property("auto_activate_for_player", unreal.AutoReceiveInput.PLAYER0)
    out["actors"].append({"label": camera.get_actor_label(), "path": camera.get_path_name()})
    floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, -3), unreal.Rotator())
    floor.set_actor_label("Phase 2 Floor")
    floor.get_editor_property("static_mesh_component").set_static_mesh(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane"))
    floor.set_actor_scale3d(unreal.Vector(12, 12, 1))
    out["actors"].append({"label": floor.get_actor_label(), "path": floor.get_path_name()})
    light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(200, -300, 500), unreal.Rotator(-45, 30, 0))
    light.set_actor_label("Phase 2 Key Light")
    out["actors"].append({"label": light.get_actor_label(), "path": light.get_path_name()})
    start = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(600, 0, 115), unreal.Rotator(0, 180, 0))
    start.set_actor_label("Phase 2 PlayerStart")
    out["actors"].append({"label": start.get_actor_label(), "path": start.get_path_name()})
    assert level.save_current_level()
except Exception:
    out["errors"].append(traceback.format_exc())
Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\scene_finish.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
