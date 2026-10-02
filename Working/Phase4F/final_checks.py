"""Review delivery consistency without generating human judgement."""
import sys
sys.dont_write_bytecode = True
import json, re
from pathlib import Path

P = Path(__file__).resolve().parents[2]
O = P / 'Documentation/Phase4F'
W = P / 'Working/Phase4F'
report = (O / 'Phase4FQualityGeneralisationGate.md').read_text(encoding='utf-8')
sections = re.findall(r'^## (\d+)\.', report, re.M)
assert sections == [str(i) for i in range(1, 24)], sections
missing = []
for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', report):
    if '://' not in target and not (O / target.split('#')[0]).exists():
        missing.append(target)
assert not missing, missing
native = json.loads((O / 'native_review_fresh_readback.json').read_text())
assert native['status'] == 'passed'
counts = {}
for character in ('Bill', 'Jill'):
    state = json.loads((W / character / 'session.json').read_text())
    assert state['events'] == [] and state['approvals'] == {}, character
    counts[character] = {'actual_events': 0, 'actual_approvals': 0}
status = json.loads((O / 'phase_status.json').read_text())
assert not status['decision_complete'] and not status['phase5_authorised']
result = {'status': 'passed', 'required_report_sections': len(sections),
          'broken_report_links': missing, 'human_counts': counts,
          'fresh_native_authoring_readback': native['status'],
          'decision_complete': False, 'phase5_authorised': False}
(O / 'final_delivery_checks.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
