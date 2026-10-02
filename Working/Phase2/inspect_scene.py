import json
import traceback
from pathlib import Path
import unreal

out = {"meshes": {}, "components": {}, "errors": []}
for label, path in (
    ("Manny", "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"),
    ("UE5", "/Game/MetaHumanTo3DCharacter/Phase2/UE5/SK_Lara_UE5"),
    ("Mixamo", "/Game/MetaHumanTo3DCharacter/Phase2/Mixamo/SK_Lara_Mixamo"),
):
    try:
        mesh = unreal.EditorAssetLibrary.load_asset(path)
        out["meshes"][label] = {"path": mesh.get_path_name(),
                                "bounds_members": [x for x in dir(mesh) if "bound" in x.lower()],
                                "get_bounds": str(mesh.get_bounds()) if hasattr(mesh, "get_bounds") else None}
    except Exception:
        out["errors"].append({"label": label, "traceback": traceback.format_exc()})
try:
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level.load_level("/Game/MetaHumanTo3DCharacter/Phase2/Maps/L_Phase2_RetargetTest")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    demo = next(a for a in actors if a.get_actor_label() == "Manny and Lara Retarget Comparison")
    for comp in demo.get_components_by_class(unreal.SkeletalMeshComponent):
        out["components"][comp.get_name()] = {"mesh": str(comp.get_skeletal_mesh_asset()),
                                                "relative_location": str(comp.get_relative_transform().translation),
                                                "world_location": str(comp.get_world_location()),
                                                "bounds_members": [x for x in dir(comp) if "bound" in x.lower()],
                                                "animation_mode": str(comp.get_animation_mode()),
                                                "anim_class": str(comp.get_editor_property("anim_class")),
                                                "attach_parent": str(comp.get_attach_parent())}
except Exception:
    out["errors"].append({"label": "scene", "traceback": traceback.format_exc()})
Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\scene_inspection.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
