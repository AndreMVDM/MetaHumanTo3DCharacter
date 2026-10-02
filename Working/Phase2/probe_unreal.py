import json
import traceback
import unreal

out = {}
try:
    classes = ["AssetImportTask", "FbxImportUI", "FbxSkeletalMeshImportData", "IKRigController",
               "IKRetargeterController", "IKRigDefinition", "IKRetargeter", "AnimBlueprintFactory",
               "AnimBlueprint", "AnimationBlueprintLibrary", "AnimationGraph", "AnimGraphNode_RetargetPoseFromMesh",
               "AnimGraphNode_Root", "BlueprintEditorLibrary", "KismetEditorUtilities", "EditorAssetLibrary",
               "EditorLevelLibrary", "LevelEditorSubsystem", "EditorUtilityLibrary", "Skeleton",
               "SkeletalMesh", "SkeletalMeshEditorSubsystem", "FbxSceneImportFactory"]
    for name in classes:
        obj = getattr(unreal, name, None)
        out[name] = {"present": obj is not None,
                     "members": [x for x in dir(obj) if not x.startswith("_")] if obj else []}
    paths = ["/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple",
             "/Game/Characters/Mannequins/Meshes/SK_Mannequin",
             "/Game/Characters/Mannequins/Rigs/IK_Mannequin",
             "/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd"]
    out["assets"] = {path: str(unreal.EditorAssetLibrary.load_asset(path)) for path in paths}
except Exception:
    out["error"] = traceback.format_exc()
open(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\unreal_probe.json", "w", encoding="utf-8").write(json.dumps(out, indent=2))
print("PHASE2_PROBE_DONE")
