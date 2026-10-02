"""Non-human viewport/preview/capture checks; never records a trial edit."""
import builtins,sys,time,traceback,json
from pathlib import Path
import unreal
W=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4D');O=W.parents[1]/'Documentation/Phase4D';sys.path.insert(0,str(W));sys.dont_write_bytecode=True
import core
tool=builtins.phase4d_tool
before=core.digest(tool.state);tests=[]
def check(name,ok):
    assert ok,name;tests.append({'name':name,'pass':True})
try:
    tool.process({'action':'select','role':'pelvis','provenance':'agent_ui_test'});check('body_selection',tool.selected()==['pelvis'])
    a=tool.controls['pelvis'];original=a.get_actor_location();a.set_actor_location(original+unreal.Vector(0,1,2),False,False);check('viewport_marker_position_readback','pelvis' in tool.positions())
    preview=json.loads(json.dumps(tool.state));preview['body_overrides']['pelvis']=[original.x,original.y+1,original.z+2];core.rebuild(preview);tool.redraw(preview)
    moved=[r for r in preview['joints'] if r.get('dependency_recomputation')];check('live_preview_five_dependencies',len(moved)==5)
    check('preview_does_not_record_correction',core.digest(tool.state)==before)
    tool.redraw();check('preview_restored',not tool.positions());tool.A.set_selected_level_actors([])
    tool.process({'action':'preview_track','side':'l','track_id':'digit_branch_1_l','provenance':'agent_ui_test'});check('track_highlight',len(tool.A.get_selected_level_actors())==6)
    tool.A.set_selected_level_actors([]);tool.view('front');check('no_human_events',len(tool.state['events'])==0)
    check('no_approvals',not tool.state['approvals']);check('state_unchanged',core.digest(tool.state)==before)
    assert tool.L.save_current_level()
    core.save(O/'ue_mechanics_validation.json',{'tests':tests,'passed':True,'synthetic_preview_only':True,'human_trial_started':False,'corrections_recorded':0,'saved_map':tool.U.get_editor_world().get_path_name()})
except Exception:
    tool.redraw();core.save(O/'ue_mechanics_validation.json',{'tests':tests,'passed':False,'error':traceback.format_exc()});raise
views=['front','side','pelvis','arms','knees','feet','left hand','right hand'];stage=0;started=time.monotonic()
def capture(dt):
    global stage,started
    if time.monotonic()-started<1.5:return
    if stage>=len(views)*2:
        tool.view('front');tool.publish('Ready for human correction trial. No trial edits or approvals recorded.');unreal.unregister_slate_post_tick_callback(handle);return
    view=views[stage//2]
    if stage%2==0:tool.view(view)
    else:
        path=O/('ue_pre_'+view.replace(' ','_')+'.png');unreal.SystemLibrary.execute_console_command(tool.U.get_editor_world(),'HighResShot 1920x1080 filename="'+str(path).replace('\\','/')+'"')
    stage+=1;started=time.monotonic()
handle=unreal.register_slate_post_tick_callback(capture)
