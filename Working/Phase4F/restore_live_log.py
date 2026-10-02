"""Restore only a proven unchanged prefix after the old live editor has closed."""
import sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F';O=P/'Documentation/Phase4F'
path=P/'Working/Phase4E/editor_native.log';before=json.loads((O/'protected_before.json').read_text())['files']['Working/Phase4E/editor_native.log']
current=path.read_bytes();prefix=current[:before['bytes']]
assert hashlib.sha256(prefix).hexdigest()==before['sha256'],'Not a pure append; refuse any restoration'
backup=W/'prior_live_editor_log_full_capture.log';backup.write_bytes(current)
path.write_bytes(prefix)
assert hashlib.sha256(path.read_bytes()).hexdigest()==before['sha256']
(O/'live_log_preservation_repair.json').write_text(json.dumps({'scope':'Only already-running Phase4E editor log; restore unchanged captured prefix after normal shutdown',
    'baseline_bytes':before['bytes'],'observed_live_bytes':len(current),'appended_bytes':len(current)-len(prefix),'restored_sha256':before['sha256'],'restored_exact':True,
    'full_execution_log_retained':'Working/Phase4F/prior_live_editor_log_full_capture.log','prior_assets_or_ledgers_restored_or_modified':False},indent=2))
print('Restored exact protected live-log prefix; retained append evidence in Phase4F.')
