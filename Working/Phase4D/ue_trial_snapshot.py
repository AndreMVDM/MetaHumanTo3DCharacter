"""Read the retained real trial from the editor without changing it."""
import builtins,json,hashlib,sys
from pathlib import Path
W=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4D')
dest=W/'HumanTrialFinalisation/InputSnapshot';dest.mkdir(parents=True,exist_ok=True)
s=builtins.phase4d_tool.state
assert len(s['events'])==159 and s['trial_finished_at'] is not None
for e in s['events']:
    assert json.loads((W/'InteractionEvidence'/f"event_{e['id']:05}.json").read_text())==e
payload=json.dumps(s,indent=2,allow_nan=False)
(dest/'session_from_editor.json').write_text(payload,encoding='utf-8')
(dest/'editor_snapshot_provenance.json').write_text(json.dumps({'source':'retained builtins.phase4d_tool.state; read only','python_version':sys.version,'events':len(s['events']),'approvals':len(s['approvals']),'finished_epoch':s['trial_finished_at'],'event_files_all_match':True,'sha256':hashlib.sha256((dest/'session_from_editor.json').read_bytes()).hexdigest()},indent=2))
print('PHASE4D_HUMAN_TRIAL_SNAPSHOT',len(s['events']),len(s['approvals']))
