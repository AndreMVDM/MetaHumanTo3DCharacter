import unreal
B='/Game/MetaHumanTo3DCharacter/Phase4D'
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.load_level(B+'/Maps/L_LaraNativePlayback')
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(140,650,105),unreal.Rotator(pitch=0,yaw=-90,roll=0))
level.editor_play_simulate()
print('PHASE4D_FINAL_SCENE_OPEN: static source then idle, walk, run, JumpingJacks; direct Lara native clips; no source actor')
