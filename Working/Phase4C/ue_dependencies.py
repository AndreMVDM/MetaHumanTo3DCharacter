import unreal,json,traceback
from pathlib import Path
P=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase4C'
r={'authoring_only':True,'final_lara_package_created':False,'runtime_dependency_closure_status':'not testable: anatomy rejected, no final Phase4C Lara package', 'no_cloud_solve_call_in_phase4c_script':True,'offline_disconnect_test_performed':False}
try:
    path='/Game/MetaHumanTo3DCharacter/Phase4C/Donor/MHC_LaraDonor_combined'
    asset=unreal.load_asset(path);r['saved_donor_fresh_process_reload']=asset is not None;r['saved_donor_class']=asset.get_class().get_name() if asset else None
    reg=unreal.AssetRegistryHelpers.get_asset_registry();options=unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False)
    pending=[path];seen=set();edges={}
    while pending and len(seen)<5000:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);deps=[str(x) for x in reg.get_dependencies(p,options)];edges[p]=deps
        pending.extend(q for q in deps if q.startswith('/Game/MetaHumanTo3DCharacter/Phase4C') and q not in seen)
    r['authoring_package_dependency_edges']=edges;r['authoring_dependencies_traversal_scope']='Phase4C packages, with direct external package edges recorded'
    r['phase4c_assets']=[str(x) for x in unreal.EditorAssetLibrary.list_assets('/Game/MetaHumanTo3DCharacter/Phase4C',recursive=True,include_folder=False)]
except Exception:r['error']=traceback.format_exc()
(O/'dependency_evidence.json').write_text(json.dumps(r,indent=2));print('PHASE4C_DEPENDENCIES',r)
