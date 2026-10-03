"""Existing native standard mapping and RetargetPoseFromMesh path, canonical derived rig only."""
import unreal,json,sys,traceback
from pathlib import Path
sys.dont_write_bytecode=True;R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/UnitCorrection';B='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/UnitCorrection';sys.path.insert(0,str(R/'Working/Phase3B'));from common import rig_snapshot,ret_snapshot
r=dict(status='running',scope=['neutral','idle','walk','run'],bakes_created=False)
try:
    d=json.loads((O/'canonicalisation.json').read_text());assert d['status']=='passed';mesh=unreal.load_asset(d['mesh']);sm=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');T=unreal.AssetToolsHelpers.get_asset_tools();assert not unreal.EditorAssetLibrary.does_asset_exist(B+'/Retarget/IK_Target')
    source=T.duplicate_asset('IK_Source',B+'/Retarget',unreal.load_asset('/Game/Characters/Mannequins/Rigs/IK_Mannequin'));sc=unreal.IKRigController.get_controller(source)
    for side,suf in [('Left','l'),('Right','r')]:
        if not any(str(x.chain_name)==side+'Foot' for x in sc.get_retarget_chains()):sc.add_retarget_chain(side+'Foot','ball_'+suf,'ball_'+suf,'')
    ik=T.create_asset('IK_Target',B+'/Retarget',unreal.IKRigDefinition,unreal.IKRigDefinitionFactory());ic=unreal.IKRigController.get_controller(ik);assert ic.set_skeletal_mesh(mesh);assert ic.apply_auto_generated_retarget_definition();assert ic.apply_auto_fbik();ic.set_retarget_root('pelvis');ic.set_root_motion_bone('root')
    if not any(str(x.chain_name)=='Root' for x in ic.get_retarget_chains()):ic.add_retarget_chain('Root','root','root','')
    for side,suf in [('Left','l'),('Right','r')]:ic.set_retarget_chain_end_bone(side+'Leg','ball_'+suf);assert ic.set_goal_bone(ic.get_retarget_chain_goal(side+'Leg'),'ball_'+suf)
    rt=T.create_asset('RTG_Canonical',B+'/Retarget',unreal.IKRetargeter,unreal.IKRetargetFactory());rc=unreal.IKRetargeterController.get_controller(rt)
    for st,rig,m in [(unreal.RetargetSourceOrTarget.SOURCE,source,sm),(unreal.RetargetSourceOrTarget.TARGET,ik,mesh)]:rc.set_ik_rig(st,rig);rc.set_preview_mesh(st,m)
    rc.remove_all_ops();rc.add_default_ops();rc.auto_map_chains(unreal.AutoMapChainType.EXACT,True)
    for i in range(rc.get_num_retarget_ops()):
        if str(rc.get_op_name(i)) in ['Root Motion','Speed Plant IK Goals','Stride Warp IK Goals']:rc.set_retarget_op_enabled(i,False)
    rc.reset_retarget_pose(rc.get_current_retarget_pose_name(unreal.RetargetSourceOrTarget.TARGET),[],unreal.RetargetSourceOrTarget.TARGET);rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET);mapping={str(x.chain_name):str(rc.get_source_chain(x.chain_name)) for x in ic.get_retarget_chains()};r['mapping']=mapping;r['target_rig']=rig_snapshot(ik);assert all(k==v for k,v in mapping.items()),mapping
    abp=T.duplicate_asset('ABP_CanonicalLive',B+'/Retarget',unreal.load_asset('/Game/ExampleContent/AnimationRetargeting/AnimBlueprints/ABP_StackOBot_Retargeting'));abp.set_editor_property('target_skeleton',mesh.skeleton);node=abp.get_nodes_of_class(unreal.AnimGraphNode_RetargetPoseFromMesh)[0];pins={str(p.get_pin_name()):p for p in node.list_input_pins()};assert pins['IKRetargeterAsset'].set_pin_value(rt.get_path_name())
    if 'CustomRetargetProfile' in pins:pins['CustomRetargetProfile'].break_pin_links();pins['CustomRetargetProfile'].set_pin_value(pins['CustomRetargetProfile'].get_pin_value().replace('bApplyChainSettings=True','bApplyChainSettings=False'))
    unreal.BlueprintEditorLibrary.compile_blueprint(abp);assert 'BS_UP_TO_DATE' in str(abp.get_editor_property('status'))
    bp=unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(B+'/Live/BP_LiveProof',unreal.Actor);ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);fn=unreal.SubobjectDataBlueprintFunctionLibrary;root=next(h for h in ss.k2_gather_subobject_data_for_blueprint(bp) if fn.is_default_scene_root(fn.get_data(h)))
    def component(name,parent,m,animclass=None):
        h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(blueprint_context=bp,new_class=unreal.SkeletalMeshComponent,parent_handle=parent));assert fn.is_handle_valid(h),reason;ss.rename_subobject(h,name);c=fn.get_object_for_blueprint(fn.get_data(h),bp);c.set_skeletal_mesh_asset(m);c.set_editor_property('visibility_based_anim_tick_option',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES);c.set_update_animation_in_editor(True);c.set_forced_lod(1)
        if animclass:c.set_anim_instance_class(animclass)
        else:c.override_animation_data(None,False,False,0,0)
        return h
    sh=component('SourceManny',root,sm);component('CanonicalTarget',sh,mesh,abp.generated_class());unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    for x in [source,ik,rt,abp,bp]:assert unreal.EditorAssetLibrary.save_loaded_asset(x,False)
    assert unreal.EditorLevelLibrary.new_level(B+'/Live/L_CanonicalProof');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actor=E.spawn_actor_from_class(bp.generated_class(),unreal.Vector());actor.set_actor_label('Unit canonicalisation live proof, actor scale 1')
    floor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-5));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(30,30,.1));E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,250),unreal.Rotator(pitch=-45,yaw=-45,roll=0));E.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,250));assert unreal.EditorLevelLibrary.save_current_level()
    r.update(status='passed',map=B+'/Live/L_CanonicalProof',live_blueprint=bp.get_path_name(),retargeter=rt.get_path_name(),mapping=mapping,source_rig=rig_snapshot(source),target_rig=rig_snapshot(ik),retarget_configuration=ret_snapshot(rt,list(d['bones'])),floor_z_cm=0,actor_scale=[1,1,1],component_scale=[1,1,1])
except Exception:r.update(status='failed',error=traceback.format_exc())
(O/'live_setup.json').write_text(json.dumps(r,indent=2));print('CANONICAL_LIVE_SETUP',r['status'],r.get('error',''))
