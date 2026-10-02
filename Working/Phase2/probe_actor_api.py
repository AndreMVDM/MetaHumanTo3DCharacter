import json
from pathlib import Path
import unreal

classes = ["BlueprintFactory", "SubobjectDataSubsystem", "SubobjectDataHandle", "AddNewSubobjectParams",
           "SubobjectDataBlueprintFunctionLibrary", "EditorLevelLibrary", "LevelEditorSubsystem",
           "SkeletalMeshComponent", "SceneComponent", "Actor", "CameraComponent", "CameraActor",
           "EditorActorSubsystem", "AnimSingleNodeInstance", "SingleAnimationPlayData"]
out = {}
for name in classes:
    obj = getattr(unreal, name, None)
    out[name] = {"present": obj is not None,
                 "members": [x for x in dir(obj) if not x.startswith("_")] if obj else []}
for class_name, methods in {
    "BlueprintEditorLibrary": ["create_blueprint_asset_with_parent", "compile_blueprint"],
    "SubobjectDataSubsystem": ["k2_gather_subobject_data_for_blueprint", "add_new_subobject", "rename_subobject", "attach_subobject", "get_object"],
    "SubobjectDataBlueprintFunctionLibrary": ["get_object", "get_data", "get_class", "get_blueprint"],
    "SubobjectDataBlueprintFunctionLibrary": ["get_object", "get_object_for_blueprint", "get_associated_object", "get_data", "is_root_component", "is_default_scene_root"],
    "LevelEditorSubsystem": ["new_level", "save_current_level", "editor_request_begin_play"],
    "EditorLevelLibrary": ["new_level", "save_current_level", "spawn_actor_from_class"],
    "Actor": ["add_component_by_class", "add_instance_component"],
    "SkeletalMeshComponent": ["set_skeletal_mesh", "set_anim_instance_class", "set_animation", "play_animation", "set_animation_mode", "override_animation_data"],
}.items():
    obj = getattr(unreal, class_name, None)
    out[class_name + "_docs"] = {m: getattr(getattr(obj, m, None), "__doc__", None) for m in methods} if obj else None
Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\actor_api.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
