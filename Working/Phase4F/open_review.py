import sys,json
from pathlib import Path
import unreal
sys.dont_write_bytecode=True
P=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4F';sys.path.insert(0,str(W))
import ue_review
rigreview=ue_review.rigreview
rigreview.open('Bill')
(W/'interactive_review_ready.json').write_text(json.dumps({'map':rigreview.map,'character':'Bill','human_events':len(rigreview.state['events']),'reviews':len(rigreview.state['approvals'])}))
unreal.SystemLibrary.execute_console_command(None,'viewmode unlit')
