import json
from pathlib import Path
import unreal

base = "/Game/MetaHumanTo3DCharacter/Phase2/UE5"
mesh = unreal.EditorAssetLibrary.load_asset(base + "/SK_Lara_UE5")
ret = unreal.EditorAssetLibrary.load_asset(base + "/RTG_Manny_Lara_UE5")
ctl = unreal.IKRetargeterController.get_controller(ret)
skel = mesh.get_editor_property("skeleton")
ref = skel.get_reference_pose()
out = {
    "ret_ctl_ops_methods": [x for x in dir(ctl) if "op" in x.lower()],
    "ref_methods": [x for x in dir(ref) if "bone" in x.lower() or "pose" in x.lower()],
    "mesh_bounds": str(mesh.get_bounds()),
}
for i in range(ctl.get_num_retarget_ops()):
    op_ctl = ctl.get_op_controller(i)
    out[f"op_{i}"] = {"name": str(ctl.get_op_name(i)), "controller": str(op_ctl),
                     "methods": [x for x in dir(op_ctl) if not x.startswith("_")]}
    if hasattr(op_ctl, "get_settings"):
        settings = op_ctl.get_settings()
        out[f"op_{i}"]["settings"] = str(settings)
        out[f"op_{i}"]["settings_methods"] = [x for x in dir(settings) if not x.startswith("_")]
for bone in ("root", "pelvis", "spine_01"):
    try:
        out[bone] = str(ref.get_bone_pose(bone))
    except Exception as e:
        out[bone] = repr(e)
Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\root_probe.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
