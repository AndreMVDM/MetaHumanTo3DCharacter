import json
import traceback
from pathlib import Path
import unreal

ROOT = "/Game/MetaHumanTo3DCharacter/Phase2"
TEMPLATE = "/Game/ExampleContent/AnimationRetargeting/AnimBlueprints/ABP_StackOBot_Retargeting"
OUT = Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\anim_bp_build.json")
result = {"template": TEMPLATE, "variants": {}, "errors": []}
template = unreal.EditorAssetLibrary.load_asset(TEMPLATE)
result["template_class"] = template.get_class().get_name() if template else None

for label in ("UE5", "Mixamo"):
    stage = "init"
    item = {}
    result["variants"][label] = item
    try:
        base = ROOT + "/" + label
        path = base + "/ABP_Lara_" + label + "_Retarget"
        skeleton = unreal.EditorAssetLibrary.load_asset(base + "/SK_Lara_" + label + "_Skeleton")
        ret = unreal.EditorAssetLibrary.load_asset(base + "/RTG_Manny_Lara_" + label)
        assert template and skeleton and ret
        stage = "duplicate template"
        bp = unreal.EditorAssetLibrary.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
        if not bp:
            bp = unreal.EditorAssetLibrary.duplicate_asset(TEMPLATE, path)
        assert bp
        item["path"] = bp.get_path_name()
        item["old_skeleton"] = str(bp.get_editor_property("target_skeleton"))
        stage = "set skeleton"
        bp.set_editor_property("target_skeleton", skeleton)
        stage = "edit graph"
        nodes = bp.get_nodes_of_class(unreal.AnimGraphNode_RetargetPoseFromMesh)
        item["retarget_node_count"] = len(nodes)
        assert len(nodes) == 1, f"Expected one retarget node, found {len(nodes)}"
        graph_node = nodes[0]
        item["graph_node_members"] = [x for x in dir(graph_node) if not x.startswith("_")]
        input_pins = {str(pin.get_pin_name()): pin for pin in graph_node.list_input_pins()}
        assert "IKRetargeterAsset" in input_pins
        item["old_retargeter_pin"] = input_pins["IKRetargeterAsset"].get_pin_value()
        assert input_pins["IKRetargeterAsset"].set_pin_value(ret.get_path_name())
        item["retargeter_pin"] = input_pins["IKRetargeterAsset"].get_pin_value()
        profile_pin = input_pins.get("CustomRetargetProfile")
        if profile_pin:
            profile_pin.break_pin_links()
            current = profile_pin.get_pin_value()
            assert profile_pin.set_pin_value(current.replace("bApplyChainSettings=True", "bApplyChainSettings=False"))
            item["profile_pin"] = profile_pin.get_pin_value()
        stage = "compile"
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        item["status"] = str(bp.get_editor_property("status"))
        item["target_skeleton"] = bp.get_editor_property("target_skeleton").get_path_name()
        item["generated_class"] = str(bp.generated_class())
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
    except Exception:
        result["errors"].append({"variant": label, "stage": stage, "traceback": traceback.format_exc()})
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print("PHASE2_ANIM_BP_BUILD_DONE")
