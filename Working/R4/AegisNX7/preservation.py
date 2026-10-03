"""R4 baseline and final read-only protected-file audit."""
import sys,json,hashlib,subprocess
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/R4/AegisNX7';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
git=lambda *a:subprocess.check_output(['git','--no-optional-locks','-c','safe.directory='+R.as_posix(),*a],cwd=R,text=True).splitlines()
if '--baseline' in sys.argv:
    assert not (O/'baseline.json').exists(),'Preserve existing baseline'
    previous=json.loads((R/'Documentation/HumanReview/AegisMovement/baseline.json').read_text());protected=previous['protected']
    for folder in ['Content','Documentation','Working/HumanReview/AegisMovement']:
        for p in (R/folder).rglob('*'):
            if p.is_file() and not p.is_relative_to(O):protected[p.relative_to(R).as_posix()]=sha(p)
    b=dict(protected=protected,git_head=git('rev-parse','HEAD')[0],git_tracked=git('status','--short','--untracked-files=no'),git_index_sha256=sha(R/'.git/index'))
    (O/'baseline.json').write_text(json.dumps(b,indent=2)+'\n');print('R4_BASELINE',len(protected))
else:
    b=json.loads((O/'baseline.json').read_text());changed=[];missing=[]
    for n,h in b['protected'].items():
        p=R/n
        if not p.is_file():missing.append(n)
        elif sha(p)!=h:changed.append(n)
    git_ok=b['git_head']==git('rev-parse','HEAD')[0] and b['git_tracked']==git('status','--short','--untracked-files=no') and b['git_index_sha256']==sha(R/'.git/index')
    d=dict(status='PASS' if not changed and not missing and git_ok else 'FAIL',protected_count=len(b['protected']),changed=changed,missing=missing,git_preserved=git_ok)
    (O/'preservation_audit.json').write_text(json.dumps(d,indent=2)+'\n');print('R4_PRESERVATION',d['status'],len(changed),len(missing),git_ok)
