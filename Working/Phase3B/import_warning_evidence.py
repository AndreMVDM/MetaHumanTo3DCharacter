from pathlib import Path
import json,re
P=Path(__file__).resolve().parents[2];current=None;rows=[]
for line in (P/'Working/Phase3B/build_final.log').read_text(errors='replace').splitlines():
    if 'Loading FBX Scene from' in line:
        current={'fbx':line.split('Loading FBX Scene from ',1)[1],'warnings':[],'bind_pose_messages':[]};rows.append(current)
    if current and ('LogFbx:' in line or 'FBXImport:' in line):
        msg=line.split(']',2)[-1].strip()
        if 'Warning:' in line:current['warnings'].append(msg)
        if 'bind pose' in line.lower():current['bind_pose_messages'].append(msg)
(P/'Documentation/Phase3B/import_warnings.json').write_text(json.dumps(rows,indent=2))
