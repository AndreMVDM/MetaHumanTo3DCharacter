"""Read-only preservation audit for the interactive human review setup."""
import json,hashlib,subprocess
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/HumanReview/AegisMovement'
b=json.loads((O/'baseline.json').read_text());changed=[];missing=[]
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for n,h in b['protected'].items():
    p=R/n
    if not p.is_file():missing.append(n)
    elif sha(p)!=h:changed.append(n)
git=lambda *args:subprocess.check_output(['git','--no-optional-locks','-c','safe.directory='+R.as_posix(),*args],cwd=R,text=True).splitlines()
tracked=git('status','--short','--untracked-files=no')
ok=git('rev-parse','HEAD')[0]==b['git_head'] and tracked==b['git_tracked'] and sha(R/'.git/index')==b['git_index_sha256']
d=dict(status='PASS' if not changed and not missing and ok else 'FAIL',protected_count=len(b['protected']),changed=changed,missing=missing,git_preserved=ok,git_tracked=tracked,new_content_scope='/Game/MetaHumanTo3DCharacter/HumanReview/AegisMovement/',accepted_assets_modified=False if not changed else None)
(O/'preservation_audit.json').write_text(json.dumps(d,indent=2)+'\n')
print('HUMAN_REVIEW_PRESERVATION',d['status'],len(b['protected']),len(changed),len(missing),ok)
