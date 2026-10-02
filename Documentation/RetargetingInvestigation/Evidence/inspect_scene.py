import unreal, json, pathlib, traceback
OUT = pathlib.Path(r'E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Documentation\RetargetingInvestigation\Evidence')
def val(x):
    if isinstance(x, unreal.Object): return x.get_path_name()
    if isinstance(x, (bool,int,float,str)) or x is None: return x
    try: return [val(y) for y in x]
    except Exception: return str(x)
def props(obj, names):
    result={}
    for n in names:
        try: result[n]=val(obj.get_editor_property(n))
        except Exception: pass
    return result
try:
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    data={'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),'actors':[],'python_types':[x for x in dir(unreal) if any(t in x for t in ['Exporter','Blueprint','IKRetarget','IKRig'])]}
    for a in actors:
        entry={'name':a.get_name(),'label':a.get_actor_label(),'path':a.get_path_name(),'class':a.get_class().get_path_name(),'location':val(a.get_actor_location()),'rotation':val(a.get_actor_rotation()),'forward':val(a.get_actor_forward_vector())}
        entry['components']=[]
        for c in a.get_components_by_class(unreal.ActorComponent):
            if isinstance(c,(unreal.SkeletalMeshComponent,unreal.TextRenderComponent)):
                ce={'name':c.get_name(),'class':c.get_class().get_path_name(),'properties':props(c,['skeletal_mesh','skeletal_mesh_asset','animation_mode','anim_class','animation_data','leader_pose_component','visibility_based_anim_tick_option','text','relative_location','relative_rotation','component_tags','hidden_in_game'])}
                if isinstance(c,unreal.SceneComponent):
                    ce['parent']=val(c.get_attach_parent()); ce['world_location']=val(c.get_world_location())
                entry['components'].append(ce)
        data['actors'].append(entry)
    (OUT/'scene.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    unreal.log('READ_ONLY_SCENE_INSPECTION_COMPLETE')
except Exception:
    (OUT/'inspection_error.txt').write_text(traceback.format_exc(),encoding='utf-8')
    raise
