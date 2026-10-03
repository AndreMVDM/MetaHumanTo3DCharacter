import json,hashlib,subprocess,sys
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/PlayableCharacter/LocomotionV1';W=R/'Working/PlayableCharacter/LocomotionV1'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
git=lambda *a:subprocess.check_output(['git','--no-optional-locks','-c','safe.directory='+R.as_posix(),*a],cwd=R,text=True).splitlines()
if '--baseline' in sys.argv:
    assert not (O/'baseline.json').exists()
    paths=set(json.loads((R/'Documentation/ReviewFixes/RunJumpLand/baseline.json').read_text())['protected'])
    for folder in ['Content','Documentation','Config','Characters','Reference','Working']:
        paths.update(p.relative_to(R).as_posix() for p in (R/folder).rglob('*') if p.is_file() and not p.is_relative_to(O) and not p.is_relative_to(W) and '__pycache__' not in p.parts)
    paths.add('MHTo3DCharacter.uproject')
    protected={n:dict(sha256=sha(R/n),bytes=(R/n).stat().st_size,runtime_append_allowed=n.startswith('Working/') and n.endswith('.log')) for n in sorted(paths) if (R/n).is_file()}
    d=dict(protected=protected,git_head=git('rev-parse','HEAD')[0],git_tracked=git('status','--short','--untracked-files=no'),git_all=git('status','--short'),git_index_sha256=sha(R/'.git/index'))
    (O/'baseline.json').write_text(json.dumps(d,indent=2)+'\n');print('BASELINE',len(protected))
else:
    b=json.loads((O/'baseline.json').read_text());changed=[];missing=[];appended=[]
    for n,old in b['protected'].items():
        p=R/n
        if not p.exists():missing.append(n)
        elif sha(p)!=old['sha256']:
            if old['runtime_append_allowed'] and p.stat().st_size>=old['bytes'] and hashlib.sha256(p.open('rb').read(old['bytes'])).hexdigest()==old['sha256']:appended.append(n)
            else:changed.append(n)
    git_ok=b['git_head']==git('rev-parse','HEAD')[0] and b['git_tracked']==git('status','--short','--untracked-files=no') and b['git_index_sha256']==sha(R/'.git/index')
    d=dict(status='PASS' if not changed and not missing and git_ok else 'FAIL',protected_count=len(b['protected']),changed=changed,missing=missing,runtime_appends=appended,git_preserved=git_ok,git_before=b['git_all'],git_after=git('status','--short'))
    (O/'preservation_audit.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items() if not k.startswith('git_')},indent=2))

