import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
out={'variants':{},'errors':[],'unit':'cm','engine':unreal.SystemLibrary.get_engine_version()}
for rig in ['UE5','Mixamo']:
    try:
        base='/Game/MetaHumanTo3DCharacter/Phase2/'+rig
        mesh=unreal.load_asset(base+'/SK_Lara_'+rig)
        snap=mesh_snapshot(mesh)
        snap['ik_rig']=rig_snapshot(unreal.load_asset(base+'/IK_Lara_'+rig))
        snap['retargeter']=ret_snapshot(unreal.load_asset(base+'/RTG_Manny_Lara_'+rig),snap['bones'])
        out['variants'][rig]=snap
    except Exception:out['errors'].append(traceback.format_exc())
try:
    unreal.EditorLoadingAndSavingUtils.load_map('/Game/MetaHumanTo3DCharacter/Phase2/Maps/L_Phase2_RetargetTest')
    out['scene']=[]
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        comps=actor.get_components_by_class(unreal.SkeletalMeshComponent)
        if comps:out['scene'].append({'actor':actor.get_actor_label(),'actor_transform':t(actor.get_actor_transform()),'components':[{'name':c.get_name(),'mesh':str(c.get_editor_property('skeletal_mesh')),'relative_transform':t(c.get_relative_transform()),'world_transform':t(c.get_world_transform())} for c in comps]})
except Exception:out['errors'].append(traceback.format_exc())
save('baseline_import.json',out)
results=[]
dcc=json.loads((O/'dcc_candidates.json').read_text())
for item in [x for x in dcc if x['label']=='OriginalHeight']:
    rig=item['rig'];label=item['label'];base='/Game/MetaHumanTo3DCharacter/Phase3B/'+rig+'/'+label
    try:
        options=unreal.FbxImportUI();options.import_as_skeletal=True;options.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
        options.import_animations=False;options.import_materials=True;options.import_textures=False;options.create_physics_asset=False;options.skeleton=None
        imp=options.skeletal_mesh_import_data
        imp.convert_scene=True;imp.convert_scene_unit=True;imp.import_uniform_scale=1.0;imp.import_translation=unreal.Vector();imp.import_rotation=unreal.Rotator()
        imp.set_editor_properties({'use_t0_as_ref_pose':False,'update_skeleton_reference_pose':False})
        task=unreal.AssetImportTask();task.filename=item['fbx'];task.destination_path=base;task.destination_name='SK_Lara_'+rig;task.automated=True;task.save=True;task.replace_existing=False;task.options=options;task.factory=unreal.FbxFactory()
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        paths=list(task.imported_object_paths)
        mesh=next(unreal.load_asset(p) for p in paths if isinstance(unreal.load_asset(p),unreal.SkeletalMesh))
        results.append({'rig':rig,'label':label,'import_settings_requested':props(imp),'paths':paths,'snapshot':mesh_snapshot(mesh)})
    except Exception:results.append({'rig':rig,'error':traceback.format_exc()})
    save('original_candidates.json',results)
print('PHASE3B_BASELINE_IMPORT_DONE')
