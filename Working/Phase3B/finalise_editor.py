"""Run locally in editor after ending PIE; avoids Windows package locks."""
import runpy,json,traceback
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter')
out={'steps':[],'errors':[]}
try:
    for name in ['build_candidates.py','repair_live.py','evaluate_candidates.py']:
        runpy.run_path(str(P/'Working/Phase3B'/name),run_name='__main__')
        out['steps'].append(name)
except Exception:out['errors'].append(traceback.format_exc())
(P/'Documentation/Phase3B/finalise_editor.json').write_text(json.dumps(out,indent=2))
print('PHASE3B_FINALISE_EDITOR_DONE')
