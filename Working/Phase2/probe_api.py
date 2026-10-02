import json
from pathlib import Path
import unreal

names = ["IKRigDefinitionFactory", "IKRigFactory", "IKRetargeterFactory", "AnimBlueprintFactory",
         "AnimBlueprint", "AnimationBlueprintLibrary", "AnimGraphNode_RetargetPoseFromMesh",
         "EdGraph", "EdGraphNode", "EdGraphPin", "BlueprintEditorLibrary", "AnimGraphNode_Base",
         "K2Node", "K2Node_CallFunction", "KismetSystemLibrary", "Skeleton", "SkeletalMesh",
         "EditorAssetLibrary", "EditorLevelLibrary", "LevelEditorSubsystem"]
result = {}
result["matching_types"] = [x for x in dir(unreal) if ("Retarget" in x and "Factory" in x) or ("IKRig" in x and "Factory" in x) or ("Graph" in x and "Library" in x)]
for name in names:
    cls = getattr(unreal, name, None)
    result[name] = {"present": cls is not None, "members": [x for x in dir(cls) if not x.startswith("_")] if cls else []}
for class_name, methods in {
    "IKRigController": ["get_controller", "set_skeletal_mesh", "apply_auto_generated_retarget_definition", "apply_auto_fbik", "get_retarget_chains", "get_retarget_root", "get_root_motion_bone"],
    "IKRetargeterController": ["get_controller", "set_ik_rig", "set_preview_mesh", "auto_map_chains", "auto_align_all_bones", "add_default_ops", "get_source_chain", "set_source_chain", "get_retarget_poses", "get_rotation_offset_for_retarget_pose_bone"],
    "Skeleton": ["get_reference_pose"],
    "AnimationBlueprintLibrary": ["get_animation_blueprint_asset_data"],
    "BlueprintEditorLibrary": ["create_blueprint_asset_with_parent", "list_graphs", "find_graph", "compile_blueprint"],
}.items():
    cls = getattr(unreal, class_name, None)
    result[class_name + "_docs"] = {m: getattr(getattr(cls, m, None), "__doc__", None) for m in methods} if cls else None
for label in ("UE5", "Mixamo"):
    mesh = unreal.EditorAssetLibrary.load_asset(f"/Game/MetaHumanTo3DCharacter/Phase2/{label}/SK_Lara_{label}")
    skeleton = mesh.get_editor_property("skeleton")
    pose = skeleton.get_reference_pose()
    result[label] = {"mesh": str(mesh), "skeleton": str(skeleton),
                     "pose_members": [x for x in dir(pose) if not x.startswith("_")]}
Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\api_probe.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print("PHASE2_API_PROBE_DONE")
