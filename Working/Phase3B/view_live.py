import unreal,json
from pathlib import Path
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
unreal.SystemLibrary.execute_console_command(world,'viewmode unlit')
cam=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cam.set_level_viewport_camera_info(unreal.Vector(500,0,130),unreal.Rotator(pitch=0,yaw=180,roll=0))
Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/Phase3B/viewport_observation.json').write_text(json.dumps({'camera':str(cam.get_level_viewport_camera_info()),'method':'Temporary unlit viewing mode; no asset change'}))
