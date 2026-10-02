import unreal,json
from pathlib import Path
unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous(['/Game/MetaHumanTo3DCharacter/Phase3B'],force_rescan=True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level() # Current map is Phase3B only.
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/MetaHumanTo3DCharacter/Phase3B/Maps/L_Phase3B_LiveTest')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_play_simulate()
Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/Phase3B/live_started.json').write_text(json.dumps({'started':True}))
def phase3b_wait_for_world(delta):
    if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world():
        unreal.unregister_slate_post_tick_callback(phase3b_wait_handle)
        exec(Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B/live_capture.py').read_text(),globals())
phase3b_wait_handle=unreal.register_slate_post_tick_callback(phase3b_wait_for_world)
