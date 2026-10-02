import json
import traceback
from pathlib import Path
import unreal

out = {}
for label in ("UE5", "Mixamo"):
    base = f"/Game/MetaHumanTo3DCharacter/Phase2/{label}"
    bp = unreal.EditorAssetLibrary.load_asset(base + f"/ABP_Lara_{label}_Retarget")
    ret = unreal.EditorAssetLibrary.load_asset(base + f"/RTG_Manny_Lara_{label}")
    node = bp.get_nodes_of_class(unreal.AnimGraphNode_RetargetPoseFromMesh)[0]
    item = {"ret": str(ret), "before": str(node.get_editor_property("node"))}
    item["pins"] = [{"str": str(p), "name": str(p.get_pin_name()), "value": str(p.get_pin_value()),
                     "set_doc": p.set_pin_value.__doc__,
                     "members": [x for x in dir(p) if not x.startswith("_")]}
                    for p in node.list_input_pins()]
    try:
        struct = node.get_editor_property("node")
        struct.set_editor_property("ik_retargeter_asset", ret)
        item["after_struct"] = str(struct)
        item["after_graph"] = str(node.get_editor_property("node"))
        node.set_editor_property("node", struct)
        item["after_graph_set"] = str(node.get_editor_property("node"))
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        item["after_compile"] = str(node.get_editor_property("node"))
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
    except Exception:
        item["error"] = traceback.format_exc()
    out[label] = item
Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\node_probe.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
