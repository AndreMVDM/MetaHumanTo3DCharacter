import unreal, json, re, math
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase3B'
def save(name,data): (O/name).write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')
def v(x):return [float(x.x),float(x.y),float(x.z)]
def q(x):return [float(x.x),float(x.y),float(x.z),float(x.w)]
def t(x):return {'translation':v(x.translation),'rotation_xyzw':q(x.rotation),'scale':v(x.scale3d)}
def props(obj):
    if obj is None:return None
    out={'type':type(obj).__name__,'text':str(obj)}
    for name in re.findall(r'- ``([^`]+)``',type(obj).__doc__ or ''):
        try:out[name]=str(obj.get_editor_property(name))
        except Exception:pass
    return out
def mesh_snapshot(mesh):
    sk=mesh.skeleton;pose=sk.get_reference_pose();names=[str(n) for n in pose.get_bone_names()]
    b=mesh.get_bounds()
    result={'mesh':mesh.get_path_name(),'skeleton':sk.get_path_name(),'bounds':{'origin':v(b.origin),'extent':v(b.box_extent),'height_cm':2*b.box_extent.z},'bones':{n:{'local':t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),'component':t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))} for n in names}}
    try:
        data=mesh.get_editor_property('asset_import_data');result['import_data']=props(data)
        result['import_data_methods']=[x for x in dir(data) if any(s in x for s in ['pipeline','translator','source','option'])]
        if hasattr(data,'get_stored_pipelines'):result['stored_pipelines']=[props(x) for x in data.get_stored_pipelines()]
        if hasattr(data,'get_pipelines'):result['stored_pipelines']=[props(x) for x in data.get_pipelines()]
        if hasattr(data,'get_translator_settings'):result['translator_settings']=props(data.get_translator_settings())
    except Exception as e:result['import_data_error']=str(e)
    return result
def rig_snapshot(rig):
    ctl=unreal.IKRigController.get_controller(rig)
    solvers=[]
    names=[str(n) for n in ctl.get_skeletal_mesh().skeleton.get_reference_pose().get_bone_names()]
    for i in range(ctl.get_num_solvers()):
        s=ctl.get_solver_controller(i)
        row={'index':i,'enabled':ctl.get_solver_enabled(i),'start':str(ctl.get_start_bone(i)),'controller':props(s),'settings':props(s.get_solver_settings()) if hasattr(s,'get_solver_settings') else None}
        if hasattr(s,'get_goal_settings'):row['goal_settings']={str(g.get_editor_property('goal_name')):props(s.get_goal_settings(g.get_editor_property('goal_name'))) for g in ctl.get_all_goals()}
        if hasattr(s,'get_bone_settings'):row['bone_settings']={n:props(s.get_bone_settings(n)) for n in names}
        solvers.append(row)
    return {'path':rig.get_path_name(),'retarget_root':str(ctl.get_retarget_root()),'root_motion_bone':str(ctl.get_root_motion_bone()),'chains':[{'name':str(c.chain_name),'start':str(ctl.get_retarget_chain_start_bone(c.chain_name)),'end':str(ctl.get_retarget_chain_end_bone(c.chain_name)),'goal':str(ctl.get_retarget_chain_goal(c.chain_name))} for c in ctl.get_retarget_chains()],'solvers':solvers,'goals':[props(g) for g in ctl.get_all_goals()]}
def ret_snapshot(ret,names):
    ctl=unreal.IKRetargeterController.get_controller(ret)
    return {'path':ret.get_path_name(),'ops':[{'index':i,'name':str(ctl.get_op_name(i)),'enabled':ctl.get_retarget_op_enabled(i),'settings':props(ctl.get_op_controller(i).get_settings()) if hasattr(ctl.get_op_controller(i),'get_settings') else None} for i in range(ctl.get_num_retarget_ops())],'pose_offsets':{n:q(ctl.get_rotation_offset_for_retarget_pose_bone(n,unreal.RetargetSourceOrTarget.TARGET)) for n in names}}
