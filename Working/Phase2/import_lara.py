import json
import traceback
from pathlib import Path
import unreal

ROOT = Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter")
OUT = ROOT / "Working" / "Phase2" / "unreal_import.json"
result = {"variants": {}, "errors": []}

for label, file_name in (
    ("UE5", "tripo_convert_d5fc96b7-496c-4293-922d-2da2b1716bc5.fbx"),
    ("Mixamo", "tripo_convert_c86468c2-b692-4f02-a7aa-d0b57cca6741.fbx"),
):
    try:
        destination = "/Game/MetaHumanTo3DCharacter/Phase2/" + label
        options = unreal.FbxImportUI()
        options.set_editor_property("import_as_skeletal", True)
        options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
        options.set_editor_property("import_animations", False)
        options.set_editor_property("import_materials", True)
        options.set_editor_property("import_textures", False)
        options.set_editor_property("create_physics_asset", True)
        options.set_editor_property("skeleton", None)
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", str(ROOT / "Working" / "Phase2" / label / file_name))
        task.set_editor_property("destination_path", destination)
        task.set_editor_property("destination_name", "SK_Lara_" + label)
        task.set_editor_property("automated", True)
        task.set_editor_property("save", True)
        task.set_editor_property("replace_existing", False)
        task.set_editor_property("options", options)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        paths = list(task.get_editor_property("imported_object_paths"))
        assets = {}
        for path in paths:
            obj = unreal.EditorAssetLibrary.load_asset(path)
            assets[path] = {"class": obj.get_class().get_name() if obj else None}
            if obj and obj.get_class().get_name() == "SkeletalMesh":
                skeleton = obj.get_editor_property("skeleton")
                assets[path]["skeleton"] = skeleton.get_path_name() if skeleton else None
                assets[path]["mesh_members"] = [x for x in dir(obj) if "bone" in x or "skeleton" in x or "ref" in x]
                assets[path]["skeleton_members"] = [x for x in dir(skeleton) if "bone" in x or "skeleton" in x or "ref" in x] if skeleton else []
        result["variants"][label] = {"path": str(ROOT / "Working" / "Phase2" / label / file_name),
                                      "imported_paths": paths, "assets": assets}
    except Exception:
        result["errors"].append({"variant": label, "traceback": traceback.format_exc()})

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print("PHASE2_IMPORT_DONE")
