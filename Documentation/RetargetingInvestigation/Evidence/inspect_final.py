import unreal,json,pathlib,traceback
OUT=pathlib.Path(r'E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Documentation\RetargetingInvestigation\Evidence')
def v(x,depth=0):
    if x is None or isinstance(x,(bool,str,float,int)):return x
    if isinstance(x,unreal.Object):return x.get_path_name()
    if depth<7:
        try:return {str(k):v(z,depth+1) for k,z in x.items()}
        except Exception:pass
        try:return [v(z,depth+1) for z in x]
        except Exception:pass
        result={}
        for n in set(dir(x))|{'start_bone','end_bone','bone_name'}:
            if n.startswith('_'):continue
            try:result[n]=v(x.get_editor_property(n),depth+1)
            except Exception:pass
        if result:return result
    return str(x)
def call(x,n,*a):
    try:return v(getattr(x,n)(*a))
    except Exception as e:return {'error':str(e)}
try:
    result={'dirty_maps':v(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()),'dirty_content':v(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()),'reference_poses':{},'ops':{},'api':{}}
    seq=unreal.load_asset('/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd')
    result['animation']={}
    for n in ['enable_root_motion','root_motion_root_lock','force_root_lock','use_normalized_root_motion_scale','sequence_length','skeleton','retarget_source','retarget_source_asset']:
        try:result['animation'][n]=v(seq.get_editor_property(n))
        except Exception as e:result['animation'][n]={'error':str(e)}
    for p in ['/Game/Characters/Mannequins/Meshes/SK_Mannequin','/Game/Characters/Echo/Meshes/Echo_Skeleton']:
        pose=unreal.load_asset(p).get_reference_pose()
        result['api']['get_ref_bone_pose']=pose.get_ref_bone_pose.__doc__
        result['reference_poses'][p]={str(b):v(pose.get_ref_bone_pose(b,unreal.AnimPoseSpaces.LOCAL)) for b in pose.get_bone_names()}
    for p in ['/Game/ExampleContent/AnimationRetargeting/AnimBlueprints/RTG_Mannequin_StackOBot','/Game/Characters/Mannequin_UE4/Rigs/RTG_UE4Manny_UE5Manny']:
        c=unreal.IKRetargeterController.get_controller(unreal.load_asset(p))
        result['ops'][p]=[{'name':str(c.get_op_name(i)),'settings':v(c.get_op_controller(i).get_settings())} for i in range(c.get_num_retarget_ops())]
    result['dirty_maps_after_queries']=v(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    result['dirty_content_after_queries']=v(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    (OUT/'final_queries.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    unreal.log('READ_ONLY_FINAL_COMPLETE')
except Exception:
    (OUT/'final_error.txt').write_text(traceback.format_exc(),encoding='utf-8')
    (OUT/'final_queries.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
