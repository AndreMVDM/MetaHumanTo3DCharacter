"""Agent-only navigation check. Cannot submit human evidence-writing actions."""
import argparse
import json
import time
import uuid
from pathlib import Path

RUNTIME = Path(__file__).resolve().parent / 'runtime'
parser = argparse.ArgumentParser()
parser.add_argument('action', choices=('step', 'select', 'view', 'refresh', 'open', 'track'))
parser.add_argument('args', nargs='?', default='{}', help='JSON navigation arguments')
options = parser.parse_args()
status = json.loads((RUNTIME / 'status.json').read_text(encoding='utf-8'))
if time.time() - status['heartbeat'] > 5:
    raise SystemExit('Editor heartbeat is stale')
command = {k: status[k] for k in ('bridge_id', 'character', 'session_id', 'revision')}
command.update(action=options.action, args=json.loads(options.args), expires=time.time()+12)
key = uuid.uuid4().hex
path = RUNTIME / 'validation' / (key + '.json')
temp = path.with_suffix('.tmp')
temp.write_text(json.dumps(command), encoding='utf-8')
temp.replace(path)
result = RUNTIME / 'results' / path.name
for attempt in range(80):
    if result.exists():
        data = json.loads(result.read_text(encoding='utf-8'))
        print(json.dumps(data))
        raise SystemExit(0 if data['ok'] else 1)
    time.sleep(.2)
raise SystemExit('No acknowledgement. Claimed commands must never be replayed automatically.')
