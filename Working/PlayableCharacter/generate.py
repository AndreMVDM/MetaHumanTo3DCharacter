"""Default playable generation front door; frozen version routing only."""
import json,runpy,hashlib
from pathlib import Path
root=Path(__file__).parent;registry=json.loads((root/'default_template.json').read_text());entry=root/registry['entry_point'];implementation=root/registry['implementation']
assert hashlib.sha256(implementation.read_bytes()).hexdigest()==registry['implementation_sha256'],'Default generator implementation hash changed; version the registry deliberately.'
runpy.run_path(str(entry),run_name='__main__')
