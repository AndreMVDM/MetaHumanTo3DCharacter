"""Fresh reload, structural self-review and runtime dependency delta certification."""
import unreal,json,sys,traceback,hashlib
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/ReviewFixes/RunJumpLand';sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'Working/R4'));import animation_library as A
D=dict(status='RUNNING',fresh_process=True,subjects={})
def require(x,msg):
    if not x:raise ValueError(msg)
def graph(asset,graphname):
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(asset,graphname)
    return [dict(id=n.get_name(),title=str(n.get_node_title()),type=n.get_class().get_name(),pins=[dict(name=str(p.get_pin_name()),value=str(p.get_pin_value()),links=sorted(q.get_owning_node().get_name()+':'+str(q.get_pin_name()) for q in p.list_connected_pins())) for p in n.list_all_pins()]) for n in g.list_all_nodes()]
try:
    reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=True,include_soft_management_references=True,include_hard_management_references=True)
    for subject,folder,old,name in [('Female','FinalAcceptance/FemaleBodyRigged','/Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/ReviewV1','FemaleBody'),('Aegis','R4/AegisNX7','/Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/ReviewV2','Aegis')]:
        B='/Game/MetaHumanTo3DCharacter/ReviewFixes/RunJumpLand/'+subject;paths=[B+'/L_'+name+'MovementReview',B+'/ABP_'+name+'MovementReview',B+'/BP_'+name+'MovementReviewCharacter',B+'/BP_'+name+'MovementReviewGameMode'];assets={p:unreal.load_asset(p) for p in paths};require(all(assets.values()),'missing saved fix asset')
        abp=assets[paths[1]];bp=assets[paths[2]];oldabp=unreal.load_asset(old+'/ABP_'+name+'MovementReview');oldbp=unreal.load_asset(old+'/BP_'+name+'MovementReviewCharacter');cdo=unreal.get_default_object(bp.generated_class());oldcdo=unreal.get_default_object(oldbp.generated_class());mesh=cdo.mesh.get_skeletal_mesh_asset();require(mesh==oldcdo.mesh.get_skeletal_mesh_asset(),'mesh changed');require(cdo.mesh.get_editor_property('anim_class')==abp.generated_class(),'ABP binding');require(abp.get_editor_property('target_skeleton')==mesh.skeleton,'skeleton')
        # AnimGraph and Character input/movement graph must be byte-structurally equivalent after ownership-path normalisation.
        old_ag=graph(oldabp,'AnimGraph');new_ag=graph(abp,'AnimGraph');require(old_ag==new_ag,'AnimGraph changed beyond predicate');require(graph(oldbp,'EventGraph')==graph(bp,'EventGraph'),'controller graph changed')
        old_eg=graph(oldabp,'EventGraph');new_eg=graph(abp,'EventGraph');old_ids={n['id'] for n in old_eg};new_nodes=[n for n in new_eg if n['id'] not in old_ids]
        require(any(' <= ' in n['title'] for n in new_nodes),'missing speed guard');require(any(p['value']=='5' for n in new_nodes for p in n['pins']),'wrong speed threshold')
        altered=[]
        for n in old_eg:
            new=next(x for x in new_eg if x['id']==n['id'])
            if n!=new:altered.append(dict(before=n,after=new))
        require(len(altered)==2,'unexpected original EventGraph modifications '+str(len(altered)))
        cmc_props=['max_walk_speed','braking_deceleration_walking','ground_friction','braking_friction','braking_friction_factor','use_separate_braking_friction','air_control','falling_lateral_friction','jump_z_velocity'];require(all(cdo.character_movement.get_editor_property(k)==oldcdo.character_movement.get_editor_property(k) for k in cmc_props),'CMC changed')
        sequences=[]
        ag=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'AnimGraph')
        for n in ag.list_all_nodes():
            if n.get_class().get_name()=='AnimGraphNode_SequencePlayer':
                seq=n.get_editor_property('node').get_editor_property('sequence');require(seq.get_editor_property('skeleton')==mesh.skeleton,'foreign sequence skeleton');sequences.append(dict(path=seq.get_path_name(),validation=A.validate(seq,mesh,'root'),metadata=A.metadata(seq)))
            require(n.get_class().get_name() not in ['AnimGraphNode_RetargetPoseFromMesh','AnimGraphNode_CopyPoseFromMesh'],'live source node')
        require(len(sequences)==6,'sequence count')
        seen=set();edges={};todo=list(paths)
        while todo:
            p=todo.pop()
            if p in seen:continue
            seen.add(p);edges[p]=[str(x) for x in reg.get_dependencies(p,opts)];todo.extend(edges[p])
        prior=json.loads((R/'Documentation'/folder/'fresh_validation.json').read_text());prior_closure=set(prior['runtime_dependency_closure']['packages']);unexpected=sorted(p for p in seen if p not in prior_closure and p not in paths);require(not unexpected,'unexpected runtime dependency '+str(unexpected));forbidden=[p for p in seen if '/Sources/' in p or '/Retarget/' in p or 'RiggedUnitBridge' in p or '/John/' in p or '/Jane/' in p or '/Game/Characters/Mannequins' in p];require(not forbidden,'foreign live dependencies')
        D['subjects'][subject]=dict(status='PASS',assets=paths,stature_cm=2*mesh.get_bounds().box_extent.z,anim_graph_unchanged=True,controller_graph_unchanged=True,movement_settings_unchanged=True,new_event_nodes=new_nodes,original_node_diffs=altered,sequences=sequences,runtime_closure=dict(packages=sorted(seen),edges=edges,unexpected=unexpected,forbidden=forbidden),originals_saved=False)
    D['status']='PASS'
except Exception:D.update(status='FAIL',error=traceback.format_exc())
(O/'fresh_validation.json').write_text(json.dumps(D,indent=2)+'\n');print('SKID_FRESH',D['status'],D.get('error',''))

