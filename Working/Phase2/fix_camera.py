"""Keep the spawned default pawn behind the comparison camera."""
import json
import traceback
from pathlib import Path
import unreal

out = {'errors': []}
try:
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = subsystem.get_all_level_actors()
    camera = next(a for a in actors if a.get_actor_label() == 'Phase 2 Comparison Camera')
    start = next(a for a in actors if a.get_actor_label() == 'Phase 2 PlayerStart')
    camera.set_actor_location(unreal.Vector(650.0, 0.0, 115.0), False, False)
    camera.set_actor_rotation(unreal.Rotator(pitch=0.0, yaw=180.0, roll=0.0), False)
    start.set_actor_location(unreal.Vector(900.0, 0.0, 115.0), False, False)
    out['camera_location'] = str(camera.get_actor_location())
    out['camera_rotation'] = str(camera.get_actor_rotation())
    out['player_start_location'] = str(start.get_actor_location())
    out['saved'] = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    out['errors'].append(traceback.format_exc())
Path(r'E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase2\camera_fix.json').write_text(json.dumps(out, indent=2))
print('PHASE2_CAMERA_FIX_DONE')
