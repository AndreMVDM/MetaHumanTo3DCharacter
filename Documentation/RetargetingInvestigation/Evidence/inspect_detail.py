import unreal, json, pathlib, traceback
OUT=pathlib.Path(r'E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Documentation\RetargetingInvestigation\Evidence')
def val(x):
    if isinstance(x,unreal.Object): return x.get_path_name()
    if x is None or isinstance(x,(str,int,float,bool)): return x
    try: return {str(k):val(v) for k,v in x.items()}
    except Exception: pass
    try: return [val(y) for y in x]
    except Exception: return str(x)
def props(obj,names=None):
    r={}
    for n in names or [n for n in dir(obj) if not n.startswith('_')]:
        try:r[n]=val(obj.get_editor_property(n))
        except Exception:pass
    return r
def export(obj,name):
    t=unreal.AssetExportTask(); t.object=obj; t.filename=str(OUT/(name+'.t3d')); t.exporter=unreal.ObjectExporterT3D(); t.automated=True; t.prompt=False; t.replace_identical=True
    return unreal.Exporter.run_asset_export_task(t)
try:
    result={'dirty_maps':val(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()),'dirty_content':val(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())}
    bp=unreal.load_asset('/Game/ExampleContent/AnimationRetargeting/AnimBlueprints/ABP_CopyPoseFromMesh')
    result['abp']={'path':bp.get_path_name(),'properties':props(bp)}; export(bp,'ABP_CopyPoseFromMesh')
    cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(bp.get_path_name()))
    result['cdo']=props(cdo); export(cdo,'ABP_CopyPoseFromMesh_CDO')
    for p in ['/Game/Characters/Mannequins/Meshes/SK_Mannequin','/Game/Characters/Echo/Meshes/Echo_Skeleton']:
        o=unreal.load_asset(p); export(o,'Skeleton_'+p.split('/')[-2]+'_'+o.get_name()); result[p]={'dir':dir(o),'properties':props(o)}
    registry=unreal.AssetRegistryHelpers.get_asset_registry()
    opt=unreal.AssetRegistryDependencyOptions(True,True,False,False,False)
    result['abp_dependencies']=val(registry.get_dependencies(bp.get_path_name().split('.')[0],opt))
    actor=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='BP_CopyPoseFromMesh')
    result['actor_properties']=props(actor)
    result['components']=[]
    for c in actor.get_components_by_class(unreal.ActorComponent):
        ce={'name':c.get_name(),'class':c.get_class().get_path_name(),'properties':props(c)}
        if isinstance(c,unreal.SkeletalMeshComponent):
            ce['bones']=[{'name':str(n),'parent':str(c.get_parent_bone(n))} for n in c.get_all_socket_names() if c.get_bone_index(n)>=0]
            inst=c.get_anim_instance()
            if inst:ce['anim_instance']={'path':inst.get_path_name(),'properties':props(inst)}
            pp=c.get_post_process_instance()
            if pp:ce['post_process']={'path':pp.get_path_name(),'properties':props(pp)}
        result['components'].append(ce)
    result['asset_defaults']={}
    for n in ['AnimNode_CopyPoseFromMesh','AnimNode_RetargetPoseFromMesh','AnimNode_ControlRig','AnimNode_RigidBody']:
        try:result['asset_defaults'][n]=props(getattr(unreal,n)())
        except Exception as e:result['asset_defaults'][n]=str(e)
    (OUT/'detail.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); unreal.log('READ_ONLY_DETAIL_COMPLETE')
except Exception:
    (OUT/'detail_error.txt').write_text(traceback.format_exc(),encoding='utf-8'); raise
