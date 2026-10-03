"""Fresh main-project reload/all-assets validation and typed runtime closure."""
import unreal,json,sys,traceback,hashlib
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'Working/R4'));sys.path.insert(0,str(R/'Working/Phase4F/BenchmarkRuns/02_AegisNX7/R3'))
import animation_library as lib,runtime_appearance_closure as closure
C=json.loads((Path(__file__).parent/'profile.json').read_text());O=R/C['evidence_directory'];M=json.loads((O/'animation_library_manifest.json').read_text());V=json.loads((O/'review_build.json').read_text());D=dict(status='RUNNING',fresh_main_project=True,bridge_loaded=hasattr(unreal,'RiggedUnitBridgeLibrary'),animations=[])
try:
    lib.require(not D['bridge_loaded'],'fresh runtime loaded authoring bridge');lib.require(M['status']=='PASS' and V['status']=='PASS','authoring incomplete');mesh=unreal.load_asset(C['destination_mesh'])
    seeds={C['destination_mesh'],C['destination_skeleton']}|{v.split('.')[0] for v in V['assets'].values()}
    for row in M['entries']:
        if row.get('bake_result')!='PASS':continue
        a=unreal.load_asset(row['destination_path']);check=lib.validate(a,mesh,C['root_bone'],row['validation']['source_bound_root_deltas']);lib.require(abs(a.get_play_length()-row['duration_s'])<1e-5,'fresh duration mismatch');md=lib.metadata(a);lib.require(md==row['destination_metadata'],'metadata changed on reload');p=R/'Content'/a.get_path_name().split('.')[0].removeprefix('/Game/');file=p.with_suffix('.uasset');D['animations'].append(dict(path=a.get_path_name(),validation=check,metadata=md,sha256=hashlib.file_digest(file.open('rb'),'sha256').hexdigest()));seeds.add(a.get_path_name().split('.')[0])
    # Ground graph intentionally retains the three proven destination-native R3 bakes.
    abp=unreal.load_asset(V['assets']['anim_blueprint']);g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'AnimGraph');players=[]
    for n in g.list_all_nodes():
        if n.get_class().get_name()=='AnimGraphNode_SequencePlayer':
            seq=n.get_editor_property('node').get_editor_property('sequence');lib.require(seq.get_editor_property('skeleton')==mesh.skeleton,'review player foreign Skeleton');players.append(seq.get_path_name());seeds.add(seq.get_path_name().split('.')[0])
        lib.require(n.get_class().get_name() not in ['AnimGraphNode_RetargetPoseFromMesh','AnimGraphNode_CopyPoseFromMesh'],'live source animation node')
    reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=True,include_soft_management_references=True,include_hard_management_references=True);seen=set();edges={};todo=list(seeds)
    while todo:
        p=todo.pop()
        if p in seen:continue
        seen.add(p);edges[p]=[str(x) for x in reg.get_dependencies(p,opts)];todo.extend(edges[p])
    certificate=closure.certify_native(mesh,seeds,seen,edges,reg);lib.require(certificate['status']=='PASS','foreign runtime ownership '+str(certificate['foreign_game_packages']))
    authoring=[p for p in seen if 'RiggedUnitBridge' in p or '/Authoring/' in p or '/Retarget/' in p or '/Sources/' in p];lib.require(not authoring,'authoring dependency '+str(authoring))
    D.update(status='PASS',skeleton=mesh.skeleton.get_path_name(),height_cm=2*mesh.get_bounds().box_extent.z,review_sequence_players=players,runtime_dependency_closure=dict(certificate=certificate,packages=sorted(seen),edges=edges,authoring_packages=authoring),total=len(D['animations']))
except Exception:D.update(status='FAIL',error=traceback.format_exc())
(O/'fresh_validation.json').write_text(json.dumps(D,indent=2)+'\n');print('R4_FRESH_VALIDATION',D['status'],len(D['animations']),D.get('error',''))
