from pathlib import Path
P=Path(__file__).resolve().parent
s=(P/'live_verify.py').read_text().replace('/Assisted180/','/Assisted180BallForward/').replace('independence_live.json','independence_live_ball_forward.json').replace('native_playback.png','native_playback_ball_forward.png')
s=s.replace("data['manny_destroyed']=True","""data['manny_destroyed']=True
            for c in components:
                if c.get_name() in ['Unrigged','MixamoRecovered']:c.set_skeletal_mesh_asset(unreal.load_asset(B+'/'+c.get_name()+'/Assisted180BallForward/SK_Lara'))
            unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(70,650,100),unreal.Rotator(pitch=0,yaw=-90,roll=0))""")
(P/'live_verify_forward.py').write_text(s)
s=(P/'final_preservation.py').read_text();s=s[:s.index('try:\n    src=')]+s[s.index('try:\n    static='):]
(P/'validate_uv_import.py').write_text(s.replace("save('final_material_preservation.json',out)","save('uv_import_validation.json',out)"))
