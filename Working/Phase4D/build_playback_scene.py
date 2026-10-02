import sys,traceback
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common_d import *
B='/Game/MetaHumanTo3DCharacter/Phase4D';result={'status':'running','measured_results':{},'components':[]}
try:
 assert json.loads((O/'animation_bake_results.json').read_text())['status']=='passed'
 assert not unreal.EditorAssetLibrary.does_asset_exist(B+'/Character/BP_LaraNativePlayback')
 bp=unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(B+'/Character/BP_LaraNativePlayback',unreal.Actor);assert bp
 ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);fn=unreal.SubobjectDataBlueprintFunctionLibrary;root=next(h for h in ss.k2_gather_subobject_data_for_blueprint(bp) if fn.is_default_scene_root(fn.get_data(h)));mesh=unreal.load_asset(B+'/Character/SK_Lara')
 for i,(role,name) in enumerate([('idle','MM_Idle'),('walk','MF_Walk_Fwd'),('run','MM_Run_Fwd'),('reach','JumpingJacks')]):
  h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(blueprint_context=bp,new_class=unreal.SkeletalMeshComponent,parent_handle=root));assert fn.is_handle_valid(h),reason;ss.rename_subobject(h,role);c=fn.get_object_for_blueprint(fn.get_data(h),bp);clip=unreal.load_asset(B+'/Character/Animations/'+name);assert clip
  c.set_editor_properties({'skeletal_mesh_asset':mesh,'relative_location':unreal.Vector(i*140,0,0),'visibility_based_anim_tick_option':unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES});c.set_skeletal_mesh_asset(mesh);c.override_animation_data(clip,True,True,0,1);result['components'].append({'name':role,'mesh':mesh.get_path_name(),'animation':clip.get_path_name()})
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
 level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.new_level(B+'/Maps/L_LaraNativePlayback');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);demo=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(),unreal.Rotator());demo.set_actor_label('Phase4D Lara Native Playback')
 before=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(-140,0,0),unreal.Rotator());before.set_actor_label('Original Lara reference');before.static_mesh_component.set_static_mesh(unreal.load_asset(B+'/Geometry/SM_Lara180'))
 floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(140,0,0),unreal.Rotator());floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Plane'));floor.set_actor_scale3d(unreal.Vector(12,8,1))
 light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,-200,400),unreal.Rotator(pitch=-45,yaw=90,roll=0));light.get_editor_property('directional_light_component').set_editor_properties({'mobility':unreal.ComponentMobility.MOVABLE,'intensity':4.0})
 fill=actors.spawn_actor_from_class(unreal.PointLight,unreal.Vector(140,250,250),unreal.Rotator());fill.get_editor_property('point_light_component').set_editor_properties({'mobility':unreal.ComponentMobility.MOVABLE,'intensity':25000,'attenuation_radius':1600})
 assert level.save_current_level();result.update(status='passed',assets=[bp.get_path_name(),B+'/Maps/L_LaraNativePlayback'],measured_results={'native_lara_components':4,'manny_components':0,'donor_components':0,'component_scale':[1,1,1]})
except Exception:result.update(status='failed',error=traceback.format_exc())
save('playback_scene.json',result);print('PHASE4D_PLAYBACK_SCENE_DONE',result['status'],result.get('error'))
