"""Generate Phase 2 IK Rigs and retargeters using UE 5.8 editor controllers."""
import json
import traceback
from pathlib import Path
import unreal

ROOT = "/Game/MetaHumanTo3DCharacter/Phase2"
OUT = Path(r"E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\retarget_build.json")
result = {"source": {}, "variants": {}, "errors": []}
tools = unreal.AssetToolsHelpers.get_asset_tools()
source_rig = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Mannequins/Rigs/IK_Mannequin")
source_mesh = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple")
source_ctl = unreal.IKRigController.get_controller(source_rig)
result["source"] = {"rig": source_rig.get_path_name(), "mesh": source_mesh.get_path_name(),
                    "chains": [str(x) for x in source_ctl.get_retarget_chains()],
                    "retarget_root": str(source_ctl.get_retarget_root()),
                    "root_motion_bone": str(source_ctl.get_root_motion_bone())}
source_chain_names = {str(x.chain_name) for x in source_ctl.get_retarget_chains()}

def chains_for(label):
    if label == "UE5":
        return {
            "Root": ("root", "root"), "Spine": ("spine_01", "spine_03"),
            "Neck": ("neck_01", "neck_01"), "Head": ("head", "head"),
            "LeftClavicle": ("clavicle_l", "clavicle_l"), "LeftArm": ("upperarm_l", "hand_l"),
            "RightClavicle": ("clavicle_r", "clavicle_r"), "RightArm": ("upperarm_r", "hand_r"),
            "LeftLeg": ("thigh_l", "ball_l"), "RightLeg": ("thigh_r", "ball_r"),
            **{side + finger: (finger.lower() + "_01_" + suffix, finger.lower() + "_03_" + suffix)
               for side, suffix in (("Left", "l"), ("Right", "r"))
               for finger in ("Thumb", "Index", "Middle", "Ring", "Pinky")},
        }, "pelvis", "root"
    # Interchange strips FBX namespace prefixes from imported bone names.
    prefix = ""
    return {
        "Root": (prefix + "Hips", prefix + "Hips"),
        "Spine": (prefix + "Spine", prefix + "Spine2"),
        "Neck": (prefix + "Neck", prefix + "Neck"),
        "Head": (prefix + "Head", prefix + "Head"),
        **{side + "Clavicle": (prefix + side + "Shoulder", prefix + side + "Shoulder")
           for side in ("Left", "Right")},
        **{side + "Arm": (prefix + side + "Arm", prefix + side + "Hand")
           for side in ("Left", "Right")},
        **{side + "Leg": (prefix + side + "UpLeg", prefix + side + "ToeBase")
           for side in ("Left", "Right")},
        **{side + finger: (prefix + side + "Hand" + finger + "1", prefix + side + "Hand" + finger + "3")
           for side in ("Left", "Right")
           for finger in ("Thumb", "Index", "Middle", "Ring", "Pinky")},
    }, prefix + "Hips", prefix + "Hips"

for label in ("UE5", "Mixamo"):
    stage = "init"
    item = {"corrections": []}
    result["variants"][label] = item
    try:
        base = ROOT + "/" + label
        mesh = unreal.EditorAssetLibrary.load_asset(base + "/SK_Lara_" + label)
        skeleton = mesh.get_editor_property("skeleton")
        item["mesh"] = mesh.get_path_name()
        item["skeleton"] = skeleton.get_path_name()
        imported_names = {str(x) for x in skeleton.get_reference_pose().get_bone_names()}
        item["imported_bone_count"] = len(imported_names)
        item["imported_bones"] = sorted(imported_names)
        stage = "create IK Rig"
        rig_path = base + "/IK_Lara_" + label
        rig = unreal.EditorAssetLibrary.load_asset(rig_path)
        if not rig:
            rig = tools.create_asset("IK_Lara_" + label, base, unreal.IKRigDefinition,
                                     unreal.IKRigDefinitionFactory())
        assert rig, "IK Rig creation failed"
        ctl = unreal.IKRigController.get_controller(rig)
        assert ctl.set_skeletal_mesh(mesh), "Cannot set target mesh on IK Rig"
        item["rig"] = rig.get_path_name()
        stage = "auto rig"
        item["auto_retarget_definition"] = bool(ctl.apply_auto_generated_retarget_definition())
        item["auto_chains"] = [str(x) for x in ctl.get_retarget_chains()]
        item["auto_retarget_root"] = str(ctl.get_retarget_root())
        item["auto_fbik"] = bool(ctl.apply_auto_fbik())
        item["auto_solver_count"] = ctl.get_num_solvers()
        stage = "correct IK Rig"
        expected, pelvis, root_bone = chains_for(label)
        assert all(start in imported_names and end in imported_names for start, end in expected.values()), "Expected bone absent from imported skeleton"
        if str(ctl.get_retarget_root()) != pelvis:
            assert ctl.set_retarget_root(pelvis), "Cannot set retarget root"
            item["corrections"].append({"type": "retarget_root", "to": pelvis})
        if str(ctl.get_root_motion_bone()) != root_bone:
            assert ctl.set_root_motion_bone(root_bone), "Cannot set root motion bone"
            item["corrections"].append({"type": "root_motion_bone", "to": root_bone})
        present = {str(x.chain_name): x for x in ctl.get_retarget_chains()}
        for name, (start, end) in expected.items():
            if name in present:
                current_start = str(ctl.get_retarget_chain_start_bone(name))
                current_end = str(ctl.get_retarget_chain_end_bone(name))
                if (current_start, current_end) != (start, end):
                    assert ctl.set_retarget_chain_start_bone(name, start)
                    assert ctl.set_retarget_chain_end_bone(name, end)
                    item["corrections"].append({"type": "chain_endpoint", "chain": name,
                                                "from": [current_start, current_end], "to": [start, end]})
            else:
                actual = ctl.add_retarget_chain(name, start, end, "")
                assert str(actual) == name, f"Failed to create {name}: {actual}"
                item["corrections"].append({"type": "missing_chain", "chain": name,
                                            "start": start, "end": end})
        item["final_chains"] = [str(x) for x in ctl.get_retarget_chains()]
        item["final_retarget_root"] = str(ctl.get_retarget_root())
        item["final_root_motion_bone"] = str(ctl.get_root_motion_bone())
        unreal.EditorAssetLibrary.save_loaded_asset(rig)
        stage = "create retargeter"
        ret_path = base + "/RTG_Manny_Lara_" + label
        ret = unreal.EditorAssetLibrary.load_asset(ret_path)
        if not ret:
            ret = tools.create_asset("RTG_Manny_Lara_" + label, base, unreal.IKRetargeter,
                                     unreal.IKRetargetFactory())
        assert ret, "Retargeter creation failed"
        ret_ctl = unreal.IKRetargeterController.get_controller(ret)
        ret_ctl.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_rig)
        ret_ctl.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, rig)
        ret_ctl.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, source_mesh)
        ret_ctl.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, mesh)
        ret_ctl.add_default_ops()
        item["retargeter"] = ret.get_path_name()
        item["default_ops"] = [str(ret_ctl.get_op_name(i)) for i in range(ret_ctl.get_num_retarget_ops())]
        stage = "auto map"
        ret_ctl.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
        item["auto_mapping"] = {name: str(ret_ctl.get_source_chain(name)) for name in expected}
        stage = "correct map"
        for name in expected:
            if name in source_chain_names and str(ret_ctl.get_source_chain(name)) != name:
                assert ret_ctl.set_source_chain(name, name), f"Cannot map {name}"
                item["corrections"].append({"type": "chain_mapping", "chain": name, "source": name})
        item["final_mapping"] = {name: str(ret_ctl.get_source_chain(name)) for name in expected}
        # MM_Run_Fwd is an in-place clip; do not synthesize root motion or enable speed planting.
        for i in range(ret_ctl.get_num_retarget_ops()):
            name = str(ret_ctl.get_op_name(i))
            if name in ("Root Motion", "Speed Plant IK Goals", "Stride Warp IK Goals"):
                ret_ctl.set_retarget_op_enabled(i, False)
        item["ops"] = [{"name": str(ret_ctl.get_op_name(i)),
                        "enabled": bool(ret_ctl.get_retarget_op_enabled(i))}
                       for i in range(ret_ctl.get_num_retarget_ops())]
        stage = "align pose"
        ret_ctl.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
        item["pose_offsets"] = {name: str(ret_ctl.get_rotation_offset_for_retarget_pose_bone(name, unreal.RetargetSourceOrTarget.TARGET))
                                for name in imported_names}
        unreal.EditorAssetLibrary.save_loaded_asset(ret)
    except Exception:
        result["errors"].append({"variant": label, "stage": stage, "traceback": traceback.format_exc()})
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

print("PHASE2_RETARGET_BUILD_DONE")
