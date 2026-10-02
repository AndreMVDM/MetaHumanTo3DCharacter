"""Phase4E-only interactive test harness, inbox-driven at editor tick boundaries."""
import unreal,sys,json,traceback,time
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4E';O=P/'Documentation/Phase4E';B='/Game/MetaHumanTo3DCharacter/Phase4E'
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);U=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert L.load_level(B+'/Maps/L_QualityComparison')
U.set_level_viewport_camera_info(unreal.Vector(70,650,108),unreal.Rotator(pitch=0,yaw=-90,roll=0));L.editor_play_simulate()
last='';frames=0
def tick(delta):
    global last,frames
    frames+=1
    if frames%10:return
    p=W/'live_request.json'
    if not p.exists():return
    req=json.loads(p.read_text());token=req['token']
    if token==last:return
    last=token
    try:
        if req['action']=='exec':
            script=Path(req['path']).resolve();assert script.is_relative_to(W.resolve())
            exec(compile(script.read_text(),str(script),'exec'),{'__name__':'__main__'})
        else:raise ValueError(req['action'])
        (W/'live_response.json').write_text(json.dumps({'token':token,'status':'passed'}))
    except Exception:(W/'live_response.json').write_text(json.dumps({'token':token,'status':'failed','error':traceback.format_exc()}))
handle=unreal.register_slate_post_tick_callback(tick)
(W/'live_ready.json').write_text(json.dumps({'map':B+'/Maps/L_QualityComparison','status':'ready'}))
