import unreal,json,pathlib,traceback,time
OUT=pathlib.Path(r'E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Documentation\RetargetingInvestigation\Evidence')
def val(x):
    if isinstance(x,unreal.Object):return x.get_path_name()
    if x is None or isinstance(x,(str,int,float,bool)):return x
    try:return {str(k):val(v) for k,v in x.items()}
    except Exception:pass
    try:return [val(y) for y in x]
    except Exception:return str(x)
def props(o):
    r={}
    for n in dir(o):
        if n.startswith('_'):continue
        try:r[n]=val(o.get_editor_property(n))
        except Exception:pass
    return r
def safe_call(obj,n,*args):
    try:return val(getattr(obj,n)(*args))
    except Exception as e:return {'error':str(e)}
try:
    data={'rigs':{},'retargeters':{},'reference_poses':{},'control_rigs':{}}
    assets=json.loads((OUT/'assets.json').read_text())
    for p,a in assets.items():
        obj=unreal.load_asset(p)
        if a['class'].endswith('.IKRigDefinition'):
            c=unreal.IKRigController.get_controller(obj)
            r={n:safe_call(c,n) for n in ['get_skeletal_mesh','get_retarget_root','get_root_motion_bone','get_retarget_chains','get_all_goals','get_num_solvers']}
            r['chains']=[props(x) for x in c.get_retarget_chains()]
            r['goals']=[props(x) for x in c.get_all_goals()]
            r['solvers']=[]
            for i in range(c.get_num_solvers()):
                sc=c.get_solver_controller(i)
                r['solvers'].append({'controller':sc.get_class().get_path_name(),'enabled':c.get_solver_enabled(i),'start':str(c.get_start_bone(i)),'end':str(c.get_end_bone(i)),'settings':safe_call(sc,'get_solver_settings'),'dir':dir(sc)})
            data['rigs'][p]=r
        if a['class'].endswith('.IKRetargeter'):
            c=unreal.IKRetargeterController.get_controller(obj)
            r={'ops':[]}
            for side in [unreal.RetargetSourceOrTarget.SOURCE,unreal.RetargetSourceOrTarget.TARGET]:
                r[str(side)]={n:safe_call(c,n,side) for n in ['get_ik_rig','get_preview_mesh','get_current_retarget_pose_name','get_retarget_poses']}
            for i in range(c.get_num_retarget_ops()):
                oc=c.get_op_controller(i)
                r['ops'].append({'index':i,'name':str(c.get_op_name(i)),'enabled':c.get_retarget_op_enabled(i),'controller':oc.get_class().get_path_name(),'settings':safe_call(oc,'get_settings')})
            data['retargeters'][p]=r
    for p in ['/Game/Characters/Mannequins/Meshes/SK_Mannequin','/Game/Characters/Echo/Meshes/Echo_Skeleton']:
        obj=unreal.load_asset(p); pose=obj.get_reference_pose()
        data['reference_poses'][p]={'value':val(pose),'properties':props(pose),'dir':dir(pose)}
    for p in ['/Game/Characters/Echo/Rig/Echo_Twist_CtrlRig','/Game/Characters/Echo/Rig/Echo_Helpers_CtrlRig']:
        obj=unreal.load_asset(p); r={'models':[]}
        for g in obj.get_all_models():
            nodes=[]
            for n in g.get_nodes():
                nd={'name':n.get_name(),'class':n.get_class().get_path_name(),'properties':props(n),'pins':[]}
                for pin in n.get_pins():
                    nd['pins'].append({'name':pin.get_name(),'default':pin.get_default_value(),'direction':str(pin.get_direction()),'links':val(pin.get_linked_source_pins())})
                if hasattr(n,'get_script_struct'):nd['unit']=val(n.get_script_struct())
                nodes.append(nd)
            r['models'].append({'path':g.get_path_name(),'nodes':nodes})
        data['control_rigs'][p]=r
    (OUT/'support.json').write_text(json.dumps(data,indent=2),encoding='utf-8'); unreal.log('READ_ONLY_SUPPORT_COMPLETE')
except Exception:
    (OUT/'support_error.txt').write_text(traceback.format_exc(),encoding='utf-8')
    (OUT/'support.json').write_text(json.dumps(data,indent=2),encoding='utf-8')

# Observe two transient PIE frames. This callback does not change any project object.
samples=[]; first_time=None; registration_time=time.monotonic()
def observe_pie(delta):
    global first_time
    try:
        world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if world and (first_time is None or time.monotonic()-first_time>0.8):
            cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ExampleContent/AnimationRetargeting/Blueprints/BP_CopyPoseFromMesh')
            actors=unreal.GameplayStatics.get_all_actors_of_class(world,cls)
            if actors:
                a=actors[0]; s={'world':world.get_path_name(),'actor':a.get_path_name(),'components':[],'time':time.monotonic()}
                for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
                    ce={'name':c.get_name(),'mesh':val(c.get_skeletal_mesh_asset()),'anim_class':val(c.get_editor_property('anim_class')),'parent':val(c.get_attach_parent()),'pose':{}}
                    for bone in ['root','pelvis','spine_03','head','hand_l','foot_l','lowerarm_twist_01_l','C_Scarf_A_Joint1_Jnt']:
                        if c.get_bone_index(bone)>=0:ce['pose'][bone]=val(c.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT))
                    ai=c.get_anim_instance()
                    if ai:ce['instance']=ai.get_class().get_path_name();ce['time']=safe_call(ai,'get_current_time')
                    pp=c.get_post_process_instance()
                    if pp:ce['post_process']=pp.get_class().get_path_name()
                    s['components'].append(ce)
                samples.append(s);first_time=time.monotonic()
                (OUT/'runtime.json').write_text(json.dumps(samples,indent=2),encoding='utf-8')
        if len(samples)>=2 or time.monotonic()-registration_time>180:
            unreal.unregister_slate_post_tick_callback(callback_handle)
    except Exception:
        (OUT/'runtime_error.txt').write_text(traceback.format_exc(),encoding='utf-8');unreal.unregister_slate_post_tick_callback(callback_handle)
callback_handle=unreal.register_slate_post_tick_callback(observe_pie)
unreal.log('READ_ONLY_PIE_OBSERVER_READY')
