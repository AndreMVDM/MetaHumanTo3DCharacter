import json
from pathlib import Path
import unreal

ret = unreal.EditorAssetLibrary.load_asset("/Game/MetaHumanTo3DCharacter/Phase2/UE5/RTG_Manny_Lara_UE5")
ctl = unreal.IKRetargeterController.get_controller(ret)
index = ctl.get_index_of_op_by_name("Run IK Rig")
ctl.set_retarget_op_enabled(index, False)
unreal.EditorAssetLibrary.save_loaded_asset(ret)
Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\ik_isolation.json").write_text(
    json.dumps({"op": "Run IK Rig", "enabled": ctl.get_retarget_op_enabled(index)}), encoding="utf-8")
