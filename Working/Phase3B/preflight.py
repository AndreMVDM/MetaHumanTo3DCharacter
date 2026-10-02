from pathlib import Path
import hashlib, json
P=Path(__file__).resolve().parents[2]
O=P/'Documentation/Phase3B';O.mkdir(parents=True,exist_ok=True)
paths=[P/'MHTo3DCharacter.uproject']
for folder in ['Characters','Config','Content','Reference','Working/Phase2','Documentation/Phase2','Documentation/Phase3']:
    paths += [p for p in (P/folder).rglob('*') if p.is_file() and 'Phase3B' not in p.parts]
out={str(p.relative_to(P)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)}
(O/'protected_before.json').write_text(json.dumps(out,indent=2))
print('Protected files:',len(out))
