import sys, traceback
from common import *
import evaluate_candidates as ev

def fresh_ret(mesh, ik, base, name, unmap_root=False):
    path = base + '/' + name
    rt = unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else T.create_asset(name, base, unreal.IKRetargeter, unreal.IKRetargetFactory())
    rc = unreal.IKRetargeterController.get_controller(rt)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source)
    rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, ik)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, ev.S)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, mesh)
    rc.remove_all_ops()
    rc.add_default_ops()
    rc.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    if unmap_root:
        assert rc.set_source_chain('', 'Root')
    for i in range(rc.get_num_retarget_ops()):
        if str(rc.get_op_name(i)) == 'Root Motion':
            rc.set_retarget_op_enabled(i, False)
    rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
    return (rt, rc)

def run(row, states, mesh, ik, rt, clips):
    ic = unreal.IKRigController.get_controller(ik)
    rc = unreal.IKRetargeterController.get_controller(rt)
    idx = rc.get_index_of_op_by_name('Run IK Rig')
    for state in states:
        suffix = state.split('_')[-1]
        rc.set_retarget_op_enabled(idx, suffix != 'FK')
        for i in range(ic.get_num_solvers()):
            ic.set_solver_enabled(i, suffix == 'Full' or suffix == 'Solver' + str(i))
        r = ev.bake_and_sample(row, state, mesh, rt, clips)
        r['configuration'] = rig_snapshot(ik)
        rows.append(r)
        save('control_results.json', rows)
        save('control_samples.json', {'samples': ev.samples})
    for i in range(ic.get_num_solvers()):
        ic.set_solver_enabled(i, True)
    rc.set_retarget_op_enabled(idx, True)