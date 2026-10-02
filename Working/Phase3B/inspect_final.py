import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
from solver_sanity import validate_reference
rows=json.loads((O/'scaled_candidates.json').read_text());dcc=json.loads((O/'dcc_candidates.json').read_text())
results=[];migration=[]
registry=unreal.AssetRegistryHelpers.get_asset_registry()
options=unreal.AssetRegistryDependencyOptions(True,True,False,False,False)
for row in rows:
    try:
        mesh=unreal.load_asset(row['snapshot']['mesh']);c=unreal.new_object(unreal.SkeletalMeshComponent);c.set_skeletal_mesh_asset(mesh)
        expected=next(d for d in dcc if d['rig']==row['rig'] and d['label']==row['label'])['hierarchy']
        expected={n.removeprefix('mixamorig:').casefold():(p.removeprefix('mixamorig:').casefold() if p else None) for n,p in expected.items()}
        hierarchy={n.casefold():(str(c.get_parent_bone(n)).casefold() if str(c.get_parent_bone(n))!='None' else None) for n in row['snapshot']['bones']}
        ctl=unreal.IKRigController.get_controller(unreal.load_asset(row['ik_rig']))
        goals=[v(g.get_editor_property('initial_transform').translation) for g in ctl.get_all_goals()]
        issues=validate_reference(row['requested_height_cm'],row['snapshot']['bounds']['height_cm'],row['snapshot']['bones'],goals)
        if hierarchy!=expected:issues.append('hierarchy_mismatch')
        results.append({'rig':row['rig'],'label':row['label'],'hierarchy':hierarchy,'hierarchy_unchanged':hierarchy==expected,'goal_reference_positions_cm':goals,'reference_gate_failures':issues})
        base=row['snapshot']['mesh'].split('.')[0].rsplit('/',1)[0]
        assets=unreal.EditorAssetLibrary.list_assets(base+'/Tests/InPlaceFull',recursive=True,include_folder=False)
        for path in assets:
            asset=unreal.load_asset(path)
            if not isinstance(asset,unreal.AnimSequence):continue
            root=str(unreal.EditorAssetLibrary.find_asset_data(path).package_name)
            seen=set();todo=[root]
            while todo:
                name=todo.pop()
                if name in seen:continue
                seen.add(name);todo.extend(str(n) for n in registry.get_dependencies(name,options))
            foreign=[n for n in seen if n.startswith('/Game/') and '/Phase3B/' not in n]
            migration.append({'rig':row['rig'],'label':row['label'],'animation':path,'skeleton':asset.get_editor_property('skeleton').get_path_name(),'package_dependency_closure':sorted(seen),'foreign_game_dependencies':foreign,'root_motion_enabled':asset.get_editor_property('enable_root_motion'),'force_root_lock':asset.get_editor_property('force_root_lock')})
    except Exception:results.append({'rig':row['rig'],'label':row['label'],'error':traceback.format_exc()})
save('reference_validation.json',results);save('bake_dependencies.json',migration)
print('PHASE3B_FINAL_INSPECTION_DONE')
