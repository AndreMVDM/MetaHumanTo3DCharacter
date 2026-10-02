"""Launch the interactive panel on Unreal's desktop, using existing Python."""
import subprocess,builtins,time,json
from pathlib import Path
runtime=Path(r'C:/Users/Andre/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/pythonw.exe')
panel=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4D/panel.py')
assert runtime.is_file() and panel.is_file()
builtins.phase4d_panel_process=subprocess.Popen([str(runtime),str(panel)],cwd=str(panel.parent),creationflags=subprocess.CREATE_NO_WINDOW)
(panel.parent/'panel_process.json').write_text(json.dumps({'pid':builtins.phase4d_panel_process.pid,'runtime':str(runtime),'panel':str(panel),'started_epoch':time.time(),'desktop':'Unreal Editor process desktop'}))
print('Phase4D interactive panel PID',builtins.phase4d_panel_process.pid)
