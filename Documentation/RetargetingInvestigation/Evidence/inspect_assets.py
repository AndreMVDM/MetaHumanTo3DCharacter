import unreal, pathlib, json, traceback
OUT=pathlib.Path(r'E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Documentation\RetargetingInvestigation\Evidence')
def val(x):
    if isinstance(x,unreal.Object): return x.get_path_name()
    if x is None or isinstance(x,(str,int,float,bool)): return x
    try: return {str(k):val(v) for k,v in x.items()}
    except Exception: pass
    try: return [val(y) for y in x]
    except Exception: return str(x)
def props(obj,names=None):
    result={}
    for n in names or [n for n in dir(obj) if not n.startswith('_')]:
        try: result[n]=val(obj.get_editor_property(n))
        except Exception: pass
    return result
def export(obj,name):
    task=unreal.AssetExportTask()
    task.object=obj; task.filename=str(OUT/(name+'.t3d')); task.exporter=unreal.ObjectExporterT3D()
    task.automated=True; task.prompt=False; task.replace_identical=True; task.write_empty_files=False
    try: return {'ok':unreal.Exporter.run_asset_export_task(task),'errors':val(task.errors)}
    except Exception as e: return {'error':str(e)}
try:
    registry=unreal.AssetRegistryHelpers.get_asset_registry()
    options=unreal.AssetRegistryDependencyOptions(True,True,False,False,False)
    scene=json.loads((OUT/'scene.json').read_text())
    packages={a['class'].split('.')[0] for a in scene['actors'] if '/ExampleContent/AnimationRetargeting/' in a['class']}
    todo=list(packages); dependencies={}
    while todo:
        p=todo.pop()
        if p in dependencies: continue
        deps=[str(d) for d in registry.get_dependencies(p,options)]
        dependencies[p]=deps
        for d in deps:
            if d.startswith('/Game/') and d not in dependencies: todo.append(d)
    inventory=[]; assets={}
    for p in sorted(dependencies):
        ad=registry.get_assets_by_package_name(p)
        for d in ad:
            cls=str(d.asset_class_path.asset_name)
            entry={'package':p,'class':cls,'asset_name':str(d.asset_name)}
            inventory.append(entry)
            if cls in ['Blueprint','AnimBlueprint','IKRigDefinition','IKRetargeter','Skeleton','SkeletalMesh','AnimSequence','ControlRigBlueprint']:
                obj=d.get_asset(); name=obj.get_name()
                info={'path':obj.get_path_name(),'class':obj.get_class().get_path_name(),'properties':props(obj),'dir':dir(obj)}
                if cls in ['Blueprint','AnimBlueprint']:
                    info['export']=export(obj,name)
                    try:
                        gc=unreal.EditorAssetLibrary.load_blueprint_class(p)
                        cdo=unreal.get_default_object(gc)
                        info['cdo_properties']=props(cdo)
                        info['cdo_export']=export(cdo,name+'_CDO')
                    except Exception as e: info['cdo_error']=str(e)
                else: info['export']=export(obj,name)
                assets[p]=info
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for a in actors:
        if 'CopyPoseFromMesh' in a.get_actor_label(): export(a,'AuthoritativeActor')
    (OUT/'assets.json').write_text(json.dumps(assets,indent=2),encoding='utf-8')
    (OUT/'dependencies.json').write_text(json.dumps(dependencies,indent=2),encoding='utf-8')
    (OUT/'inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
    (OUT/'python_api.json').write_text(json.dumps({n:dir(getattr(unreal,n)) for n in ['BlueprintEditorLibrary','IKRigController','IKRetargeterController','ObjectExporterT3D','AnimNode_CopyPoseFromMesh','AnimNode_RetargetPoseFromMesh']},indent=2),encoding='utf-8')
    unreal.log('READ_ONLY_ASSET_INSPECTION_COMPLETE')
except Exception:
    (OUT/'asset_error.txt').write_text(traceback.format_exc(),encoding='utf-8'); raise
