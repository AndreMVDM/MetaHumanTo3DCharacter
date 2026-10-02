import json
from pathlib import Path
import unreal

out = {}
world = unreal.EditorLevelLibrary.get_pie_worlds(False)[0]
controller = unreal.GameplayStatics.get_player_controller(world, 0)
out['controller'] = str(controller)
out['view_target'] = str(controller.get_view_target())
for label, getter in (
    ('pawn', lambda: controller.get_editor_property('pawn')),
    ('camera_location', lambda: controller.get_player_view_point()),
    ('camera_manager', lambda: controller.get_editor_property('player_camera_manager')),
):
    try:
        out[label] = str(getter())
    except Exception as exc:
        out[label] = 'ERROR: ' + str(exc)
out['camera_actors'] = []
for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.CameraActor):
    out['camera_actors'].append({'actor': str(actor), 'location': str(actor.get_actor_location()),
                                 'rotation': str(actor.get_actor_rotation()),
                                 'auto_activate': str(actor.get_editor_property('auto_activate_for_player'))})
Path(r'E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\camera_inspection.json').write_text(json.dumps(out, indent=2))
print('PHASE2_CAMERA_INSPECTION_DONE')
