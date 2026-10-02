from pathlib import Path
import runpy
W=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
for name in ['baseline_details.py','fix_baked_root_lock.py','root_motion_final.py']:
    runpy.run_path(str(W/name),run_name='__main__')
print('PHASE3B_RUNTIME_REPAIRS_DONE')
