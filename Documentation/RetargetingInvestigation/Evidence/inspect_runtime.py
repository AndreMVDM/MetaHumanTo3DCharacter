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
# Observe two transient PIE frames. This callback does not change any project object.
samples=[]; first_time=None; registration_time=time.monotonic()
def observe_pie(delta):
    global first_time
    try:
        world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if world and (first_time is None or time.monotonic()-first_time>0.8):
            cls=unreal.load_class(None,'/Game/ExampleContent/AnimationRetargeting/Blueprints/BP_CopyPoseFromMesh.BP_CopyPoseFromMesh_C')
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


