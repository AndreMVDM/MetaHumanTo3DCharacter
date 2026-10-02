"""Append a live PIE sample for each source and target skeletal component."""
import json
import time
import traceback
from pathlib import Path
import unreal

path = Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\pie_samples.json")
data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"samples": []}
sample = {"time": time.time(), "components": [], "errors": []}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    sample["world"] = str(world)
    demo = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
                if a.get_actor_label() == "Manny and Lara Retarget Comparison")
    for comp in demo.get_components_by_class(unreal.SkeletalMeshComponent):
        item = {"name": comp.get_name(), "visible": comp.is_visible(),
                "location": str(comp.get_world_location()),
                "animation_mode": str(comp.get_editor_property("animation_mode")),
                "mesh": str(comp.get_editor_property("skeletal_mesh")),
                "anim_instance": str(comp.get_anim_instance())}
        for bone in ("pelvis", "Hips", "head", "Head", "hand_l", "LeftHand", "foot_l", "LeftFoot"):
            if comp.get_bone_index(bone) >= 0:
                item[bone] = str(comp.get_socket_location(bone))
        sample["components"].append(item)
except Exception:
    sample["errors"].append(traceback.format_exc())
data["samples"].append(sample)
path.write_text(json.dumps(data, indent=2), encoding="utf-8")
