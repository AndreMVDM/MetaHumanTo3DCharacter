"""Create Phase3B-only live retarget and direct-baked comparison scene."""
import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
out={'components':[],'errors':[]};B='/Game/MetaHumanTo3DCharacter/Phase3B';template='/Game/ExampleContent/AnimationRetargeting/AnimBlueprints/ABP_StackOBot_Retargeting'
try:
    unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous([B],force_rescan=True)
    bp=unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(B+'/BP_Phase3B_LiveTest',unreal.Actor)
    assert bp
    ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);fn=unreal.SubobjectDataBlueprintFunctionLibrary
    root=next(h for h in ss.k2_gather_subobject_data_for_blueprint(bp) if fn.is_default_scene_root(fn.get_data(h)))
    def component(name,parent,mesh,anim_bp=None,clip=None,offset=0):
        h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(blueprint_context=bp,new_class=unreal.SkeletalMeshComponent,parent_handle=parent));assert fn.is_handle_valid(h),reason
        ss.rename_subobject(h,name);c=fn.get_object_for_blueprint(fn.get_data(h),bp)
        c.set_editor_properties({'skeletal_mesh_asset':mesh,'relative_location':unreal.Vector(0,offset,0),'visibility_based_anim_tick_option':unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES})
        c.set_skeletal_mesh_asset(mesh) # Setter synchronises the component's skinned asset.
        if clip:c.override_animation_data(clip,True,True,0.0,1.0)
        else:c.set_editor_properties({'animation_mode':unreal.AnimationMode.ANIMATION_BLUEPRINT,'anim_class':anim_bp.generated_class()})
        out['components'].append({'name':name,'mesh':mesh.get_path_name(),'anim_bp':anim_bp.get_path_name() if anim_bp else None,'clip':clip.get_path_name() if clip else None,'offset_y':offset})
        return h
    def animbp(name,base,mesh,ret):
        path=base+'/'+name
        abp=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else unreal.EditorAssetLibrary.duplicate_asset(template,path)
        abp.set_editor_property('target_skeleton',mesh.skeleton)
        node=abp.get_nodes_of_class(unreal.AnimGraphNode_RetargetPoseFromMesh)[0];pins={str(p.get_pin_name()):p for p in node.list_input_pins()}
        assert pins['IKRetargeterAsset'].set_pin_value(ret.get_path_name())
        pin=pins.get('CustomRetargetProfile')
        if pin:pin.break_pin_links();pin.set_pin_value(pin.get_pin_value().replace('bApplyChainSettings=True','bApplyChainSettings=False'))
        unreal.BlueprintEditorLibrary.compile_blueprint(abp);assert str(abp.get_editor_property('status')).endswith('BS_UP_TO_DATE: 0>') or 'BS_UP_TO_DATE' in str(abp.get_editor_property('status'))
        unreal.EditorAssetLibrary.save_loaded_asset(abp);return abp
    source_mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');run=unreal.load_asset('/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd')
    source_h=component('Manny_Source',root,source_mesh,clip=run,offset=-750)
    candidates=json.loads((O/'scaled_candidates.json').read_text())
    for i,row in enumerate(candidates):
        mesh=unreal.load_asset(row['snapshot']['mesh']);rt=unreal.load_asset(row['retargeter']);base=rt.get_path_name().split('.')[0].rsplit('/',1)[0]
        abp=animbp('ABP_Lara_'+row['rig'],base,mesh,rt)
        component(row['rig']+'_'+row['label'],source_h,mesh,anim_bp=abp,offset=150*(i+1))
    # Reproduce original runtime solver configuration without touching Phase2 assets.
    rawmesh=unreal.load_asset(B+'/UE5/RawLegacy/SK_Lara_UE5');controlbase=B+'/UE5/LiveControls'
    for state in ['FK','Solver0','Solver1','Full']:
        ik=unreal.EditorAssetLibrary.duplicate_asset('/Game/MetaHumanTo3DCharacter/Phase2/UE5/IK_Lara_UE5',controlbase+'/IK_'+state)
        ic=unreal.IKRigController.get_controller(ik);ic.set_skeletal_mesh(rawmesh)
        for i in range(ic.get_num_solvers()):ic.set_solver_enabled(i,state=='Full' or state=='Solver'+str(i))
        rt=unreal.EditorAssetLibrary.duplicate_asset('/Game/MetaHumanTo3DCharacter/Phase2/UE5/RTG_Manny_Lara_UE5',controlbase+'/RTG_'+state)
        rc=unreal.IKRetargeterController.get_controller(rt);rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET,ik);rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET,rawmesh);rc.set_retarget_op_enabled(rc.get_index_of_op_by_name('Run IK Rig'),state!='FK')
        unreal.EditorAssetLibrary.save_loaded_asset(ik);unreal.EditorAssetLibrary.save_loaded_asset(rt)
        component('RawUE5_'+state,source_h,rawmesh,anim_bp=animbp('ABP_'+state,controlbase,rawmesh,rt),offset=2200+len(out['components'])*150)
    for rig in ['UE5','Mixamo']:
        base=B+'/'+rig+'/Height180';mesh=unreal.load_asset(base+'/SK_Lara_'+rig);clip=unreal.load_asset(base+'/Tests/InPlaceFull/MM_Run_Fwd')
        component('Baked_'+rig,root,mesh,clip=clip,offset=1100 if rig=='UE5' else 1300)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp);unreal.EditorAssetLibrary.save_loaded_asset(bp)
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.new_level(B+'/Maps/L_Phase3B_LiveTest')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);demo=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(),unreal.Rotator());demo.set_actor_label('Phase3B Live and Baked Validation')
    camera=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(900,0,150),unreal.Rotator(0,180,0));camera.set_actor_label('Phase3B Camera');camera.set_editor_property('auto_activate_for_player',unreal.AutoReceiveInput.PLAYER0);camera.get_editor_property('camera_component').set_editor_property('field_of_view',80)
    floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-1),unreal.Rotator());floor.get_editor_property('static_mesh_component').set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Plane'));floor.set_actor_scale3d(unreal.Vector(10,100,1))
    light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(100,-100,500),unreal.Rotator(-45,25,0));light.get_editor_property('directional_light_component').set_editor_properties({'mobility':unreal.ComponentMobility.MOVABLE,'intensity':3.0})
    sky=actors.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,500),unreal.Rotator());sky.get_editor_property('light_component').set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
    actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(1500,0,150),unreal.Rotator())
    assert level.save_current_level();out['map']=B+'/Maps/L_Phase3B_LiveTest';out['actor_bp']=bp.get_path_name()
except Exception:out['errors'].append(traceback.format_exc())
save('live_scene.json',out)
print('PHASE3B_LIVE_BUILD_DONE')
