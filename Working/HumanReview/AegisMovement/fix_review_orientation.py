"""Correct only the new review component/camera setup after capture self-review."""
import unreal,json
from pathlib import Path
B='/Game/MetaHumanTo3DCharacter/HumanReview/AegisMovement'
bp=unreal.load_asset(B+'/BP_AegisMovementReviewCharacter');cdo=unreal.get_default_object(bp.generated_class())
def rotation(r):return dict(pitch=r.pitch,yaw=r.yaw,roll=r.roll)
before=dict(cdo_mesh=rotation(cdo.mesh.get_editor_property('relative_rotation')),cdo_movement=rotation(cdo.character_movement.rotation_rate))
cdo.mesh.set_editor_property('relative_rotation',unreal.Rotator(pitch=0,yaw=-90,roll=0))
cdo.character_movement.set_editor_property('rotation_rate',unreal.Rotator(pitch=0,yaw=540,roll=0))
ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
    d=lib.get_data(h)
    if str(lib.get_variable_name(d))=='ReviewSpringArm':
        arm=lib.get_object_for_blueprint(d,bp);arm.set_editor_properties(dict(target_offset=unreal.Vector(),relative_rotation=unreal.Rotator(pitch=-10,yaw=0,roll=0)))
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
# Set inherited native-component defaults after the final compile as well.
cdo=unreal.get_default_object(bp.generated_class())
cdo.mesh.set_editor_property('relative_rotation',unreal.Rotator(pitch=0,yaw=-90,roll=0))
cdo.character_movement.set_editor_property('rotation_rate',unreal.Rotator(pitch=0,yaw=540,roll=0))
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
assert unreal.EditorLevelLibrary.load_level(B+'/L_AegisMovementReview')
E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for actor in E.get_all_level_actors():
    if isinstance(actor,unreal.DirectionalLight):actor.set_actor_rotation(unreal.Rotator(pitch=-45,yaw=-35,roll=0),False)
    if actor.get_class()==bp.generated_class():
        before['placed_mesh']=rotation(actor.mesh.get_editor_property('relative_rotation'))
        actor.mesh.set_editor_property('relative_rotation',unreal.Rotator(pitch=0,yaw=-90,roll=0))
        actor.character_movement.set_editor_property('rotation_rate',unreal.Rotator(pitch=0,yaw=540,roll=0))
        for arm in actor.get_components_by_class(unreal.SpringArmComponent):
            arm.set_editor_properties(dict(target_offset=unreal.Vector(),relative_rotation=unreal.Rotator(pitch=-10,yaw=0,roll=0)))
        after=dict(placed_mesh=rotation(actor.mesh.get_editor_property('relative_rotation')),placed_movement=rotation(actor.character_movement.rotation_rate),cdo_mesh=rotation(cdo.mesh.get_editor_property('relative_rotation')))
assert unreal.EditorLevelLibrary.save_current_level()
Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/HumanReview/AegisMovement/review_orientation_correction.json').write_text(json.dumps(dict(scope='New review Blueprint/component/lighting only',before=before,after=after,cause='UE Python Rotator constructor uses roll,pitch,yaw; prior positional calls tilted the review mesh and used the wrong movement rotation axis',correction='Explicit named yaw=-90 mesh / yaw=540 CharacterMovement; camera centred for full-body review',accepted_assets_modified=False),indent=2)+'\n')
