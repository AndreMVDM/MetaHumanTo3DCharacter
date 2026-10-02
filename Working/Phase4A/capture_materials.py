import unreal,time,json
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase4A'
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);level.editor_request_end_play()
stage=0;start=time.monotonic()
def tick(dt):
    global stage,start
    if time.monotonic()-start<2:return
    if stage==0:
        unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-40,-400,100),unreal.Rotator(pitch=0,yaw=90,roll=0))
        w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();unreal.SystemLibrary.execute_console_command(w,'viewmode unlit')
        m=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase4A/Unrigged/Geometry/SM_Lara').static_materials[0].material_interface
        (O/'material_render_probe.json').write_text(json.dumps({'used_textures':[t.get_path_name() for t in unreal.MaterialEditingLibrary.get_material_used_textures(m)],'camera':'x=-40,y=-400,z=100; explicit yaw90,pitch0; Unlit'},indent=2));stage=1;start=time.monotonic()
    else:
        unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'HighResShot 1920x1080 filename="E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4A/texture_before_after.png"')
        unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
