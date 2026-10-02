import unreal,time
stage=0;start=time.monotonic()
def tick(dt):
    global stage,start
    if time.monotonic()-start<3:return
    if stage==0:
        w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(w,'HighResShot 1920x1080 filename="E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4A/texture_before_after_unlit.png"');stage=1;start=time.monotonic()
    elif stage==1:
        unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-40,400,100),unreal.Rotator(pitch=0,yaw=-90,roll=0));stage=2;start=time.monotonic()
    elif stage==2:
        unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'HighResShot 1920x1080 filename="E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4A/texture_front_unlit.png"');stage=3;start=time.monotonic()
    else:
        unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
