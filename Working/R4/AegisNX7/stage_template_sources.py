"""Preserve byte-identical installed template source candidates in isolated R4 scope."""
import json,hashlib,shutil
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');S=Path(r'D:/Epic Games/UE_5.8/Templates/TemplateResources/High/Characters/Content/Mannequins')
B=R/'Content/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/Sources/InstalledMannequins';O=R/'Documentation/R4/AegisNX7';rows=[]
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for folder in ['Anims','Animations']:
    for p in sorted((S/folder).rglob('*.uasset')):
        q=B/p.relative_to(S);q.parent.mkdir(parents=True,exist_ok=True)
        if q.exists():assert sha(q)==sha(p),'Never overwrite changed source candidate'
        else:shutil.copy2(p,q)
        rows.append(dict(installed_source=str(p),original_package='/Game/Characters/Mannequins/'+p.relative_to(S).with_suffix('').as_posix(),staged_package='/Game/'+q.relative_to(R/'Content').with_suffix('').as_posix(),sha256=sha(p),bytes=p.stat().st_size))
(O/'installed_source_provenance.json').write_text(json.dumps(dict(status='PASS',source_root=str(S),copies=rows,originals_unchanged=True,classification_pending_native_inventory=True),indent=2)+'\n');print('R4_TEMPLATE_CANDIDATES',len(rows))
