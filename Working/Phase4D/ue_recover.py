"""Remove obsolete Phase4D-only reload callbacks, then show its local panel."""
import gc,builtins,unreal
from pathlib import Path
tool=builtins.phase4d_tool;removed=0
for obj in gc.get_objects():
    try:
        if obj is not tool and type(obj).__name__=='Phase4DTool' and hasattr(obj,'handle'):
            unreal.unregister_slate_post_tick_callback(obj.handle);removed+=1
    except (ReferenceError,RuntimeError):pass
tool.publish('Ready for human review. No corrections or anatomical approvals recorded.')
print('Removed obsolete Phase4D callbacks:',removed)
exec(Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4D/ue_launch_panel.py').read_text())
