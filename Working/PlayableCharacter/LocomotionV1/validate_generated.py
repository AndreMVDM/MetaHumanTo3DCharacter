"""Read-only fresh reload, generation contract and fail-closed controls."""
import unreal,json,sys,traceback,hashlib,copy
from pathlib import Path
W=Path(__file__).parent;R=W.parents[2];C=json.loads((W/'fresh_profile.json').read_text());O=Path(C['evidence_directory']);G=json.loads((O/'generation.json').read_text());sys.dont_write_bytecode=True;sys.path.insert(0,str(W));from generator import generate,VERSION,pins,pin,source
D=dict(status='RUNNING',fresh_process=True,checks=[],negative_controls=[])
def check(n,x):
    D['checks'].append(dict(name=n,status='PASS' if x else 'FAIL'))
    if not x:raise ValueError(n)
try:
    check('current implementation matches generation receipt',G['generator_sha256']==hashlib.sha256((W/'generator.py').read_bytes()).hexdigest());check('profile matches receipt',G['profile_sha256']==hashlib.sha256((W/'fresh_profile.json').read_bytes()).hexdigest())
    assets={k:unreal.load_asset(v) for k,v in G['assets'].items()};check('four generated assets reload',all(assets.values()));abp=assets['anim_blueprint'];bp=assets['character'];cdo=unreal.get_default_object(bp.generated_class());acd=unreal.get_default_object(abp.generated_class());mesh=unreal.load_asset(C['destination_mesh'])
    check('native destination binding',cdo.mesh.get_skeletal_mesh_asset()==mesh and cdo.mesh.get_editor_property('anim_class')==abp.generated_class() and abp.get_editor_property('target_skeleton')==mesh.skeleton);check('template version in native classes',str(acd.get_editor_property('LocomotionTemplateVersion'))==VERSION and str(cdo.get_editor_property('LocomotionTemplateVersion'))==VERSION)
    check('native configurable defaults',all(abs(float(acd.get_editor_property(k))-G['settings'][k])<1e-7 for k in ['IdleSpeedThreshold','LandingBlendDuration']) and all(abs(float(cdo.get_editor_property(k))-G['settings'][k])<1e-7 for k in ['WalkSpeed','RunSpeed']))
    ag=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'AnimGraph');ae=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'EventGraph');ge=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph');players=[]
    for n in ag.list_all_nodes():
        if n.get_class().get_name()=='AnimGraphNode_SequencePlayer':players.append(n.get_editor_property('node').get_editor_property('sequence').get_path_name())
        check('no live retarget/copy-pose '+n.get_name(),n.get_class().get_name() not in ['AnimGraphNode_RetargetPoseFromMesh','AnimGraphNode_CopyPoseFromMesh'])
    check('exact six configured native players',set(players)==set(C['animations'].values()) and len(players)==6)
    setter=next(n for n in ae.list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'Landing' in pins(n));condition=source(setter,'Landing');le=source(condition,'B');old=source(condition,'A');check('promoted speed guard on landing', ' <= ' in str(le.get_node_title()) and 'HorizontalSpeed' in pins(source(le,'A')) and 'IdleSpeedThreshold' in pins(source(le,'B')) and ' > ' in str(source(old,'A').get_node_title()))
    gt=[n for n in ag.list_all_nodes() if ' > ' in str(n.get_node_title())];check('same precise speed and idle threshold on ground',any('HorizontalSpeed' in pins(source(n,'A')) and 'IdleSpeedThreshold' in pins(source(n,'B')) for n in gt))
    speedset=next(n for n in ae.list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'HorizontalSpeed' in pins(n));check('horizontal speed comes directly from native velocity length',str(source(speedset,'HorizontalSpeed').get_node_title())=='Vector Length XY')
    legacy=unreal.load_asset(C['scaffold']['character']);lcd=unreal.get_default_object(legacy.generated_class());props=['max_acceleration','braking_deceleration_walking','ground_friction','braking_friction','braking_friction_factor','air_control','falling_lateral_friction','jump_z_velocity','orient_rotation_to_movement'];check('movement settings inherited unchanged',all(cdo.character_movement.get_editor_property(k)==lcd.character_movement.get_editor_property(k) for k in props))
    forbidden_functions=['Set Velocity','Stop Movement Immediately','Set Actor Location','Set World Location'];check('no velocity stop or teleport commands',not any(any(t in str(n.get_node_title()) for t in forbidden_functions) for n in ge.list_all_nodes()))
    reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=True,include_soft_management_references=True,include_hard_management_references=True);paths={v.split('.')[0] for v in G['assets'].values()};todo=list(paths);seen=set();edges={}
    while todo:
        p=todo.pop()
        if p in seen:continue
        seen.add(p);edges[p]=[str(x) for x in reg.get_dependencies(p,opts)];todo.extend(edges[p])
    prior=json.loads((R/'Documentation/FinalAcceptance/FemaleBodyRigged/fresh_validation.json').read_text());allowed=set(prior['runtime_dependency_closure']['packages'])|paths;unexpected=sorted(seen-allowed);check('runtime closure adds only generated scaffold',not unexpected);check('no source retarget or foreign subject dependencies',not any('/Sources/' in p or '/Retarget/' in p or 'RiggedUnitBridge' in p or '/John/' in p or '/Jane/' in p or '/Game/Characters/Mannequins' in p for p in seen))
    D['runtime_closure']=dict(packages=sorted(seen),edges=edges,unexpected=unexpected)
    tests=[]
    c=copy.deepcopy(C);c['scaffold']['anim_blueprint']='/Game/MetaHumanTo3DCharacter/ReviewFixes/RunJumpLand/Female/ABP_FemaleBodyMovementReview';tests.append(('already corrected scaffold cannot inherit stale threshold',c))
    c=copy.deepcopy(C);c['animations']['Land']='/Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/Animations/LibraryV1/Jump/MM_Land';tests.append(('foreign skeleton animation rejected',c))
    c=copy.deepcopy(C);del c['animations']['Fall'];tests.append(('missing required destination role rejected',c))
    for i,(name,c) in enumerate(tests):
        c['output_namespace']=C['output_namespace']+'_Rejected'+str(i)
        try:generate(c);raise AssertionError('negative control accepted')
        except ValueError as e:D['negative_controls'].append(dict(name=name,status='PASS',reason=str(e)));check('no partial output '+name,not unreal.EditorAssetLibrary.list_assets(c['output_namespace'],True,False))
    D['status']='PASS'
except Exception:D.update(status='FAIL',error=traceback.format_exc())
(O/'fresh_validation.json').write_text(json.dumps(D,indent=2)+'\n');print('GENERIC_FRESH_VALIDATION',D['status'],D.get('error',''))
