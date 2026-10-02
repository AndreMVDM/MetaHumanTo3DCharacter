import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common import *
B='/Game/MetaHumanTo3DCharacter/Phase4A';result={'components':[],'errors':[]}
try:
    existing=unreal.EditorAssetLibrary.does_asset_exist(B+'/BP_NativePlayback');bp=unreal.load_asset(B+'/BP_NativePlayback') if existing else unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(B+'/BP_NativePlayback',unreal.Actor);assert bp
    ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);fn=unreal.SubobjectDataBlueprintFunctionLibrary;root=next(h for h in ss.k2_gather_subobject_data_for_blueprint(bp) if fn.is_default_scene_root(fn.get_data(h)))
    entries=[('Unrigged',B+'/Unrigged/Assisted180/SK_Lara',B+'/Unrigged/Assisted180/Diagnostics/Full/MM_Run_Fwd',0),('MixamoRecovered',B+'/MixamoRecovered/Assisted180/SK_Lara',B+'/MixamoRecovered/Assisted180/Diagnostics/Full/MM_Run_Fwd',100),('Phase3B_Mixamo','/Game/MetaHumanTo3DCharacter/Phase3B/Mixamo/Height180/SK_Lara_Mixamo','/Game/MetaHumanTo3DCharacter/Phase3B/Mixamo/Height180/Tests/InPlaceFull/MM_Run_Fwd',200),('Manny_Source','/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple','/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/MM_Run_Fwd',350)]
    for name,mp,ap,x in ([] if existing else entries):
        h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(blueprint_context=bp,new_class=unreal.SkeletalMeshComponent,parent_handle=root));assert fn.is_handle_valid(h),reason;ss.rename_subobject(h,name);c=fn.get_object_for_blueprint(fn.get_data(h),bp);mesh=unreal.load_asset(mp);clip=unreal.load_asset(ap);assert mesh and clip;c.set_editor_properties({'skeletal_mesh_asset':mesh,'relative_location':unreal.Vector(x,0,0),'visibility_based_anim_tick_option':unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES});c.set_skeletal_mesh_asset(mesh);c.override_animation_data(clip,True,True,0,1);result['components'].append({'name':name,'mesh':mp,'animation':ap})
    unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.new_level(B+'/Maps/L_VerifiedNativePlayback');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);demo=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(),unreal.Rotator());demo.set_actor_label('Phase4A Native Diagnostic Playback')
    before=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(-100,0,0),unreal.Rotator());before.set_actor_label('Textured source before rigging');before.static_mesh_component.set_static_mesh(unreal.load_asset(B+'/Unrigged/Geometry/SM_Lara'))
    floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(100,0,-1),unreal.Rotator());floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Plane'));floor.set_actor_scale3d(unreal.Vector(12,8,1))
    light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,-200,400),unreal.Rotator(-45,90,0));light.get_editor_property('directional_light_component').set_editor_properties({'mobility':unreal.ComponentMobility.MOVABLE,'intensity':4.0})
    fill=actors.spawn_actor_from_class(unreal.PointLight,unreal.Vector(100,-250,250),unreal.Rotator());fill.get_editor_property('point_light_component').set_editor_properties({'mobility':unreal.ComponentMobility.MOVABLE,'intensity':25000,'attenuation_radius':1200})
    assert level.save_current_level();result['map']=B+'/Maps/L_VerifiedNativePlayback'
except Exception:result['errors'].append(traceback.format_exc())
save('live_scene.json',result);print('SCENE_DONE',result['errors'])
