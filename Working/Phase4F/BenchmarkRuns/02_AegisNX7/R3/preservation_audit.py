"""Bounded R3 preservation audit; no validation fitting or asset authoring."""
import json, hashlib, sys, subprocess, datetime
from pathlib import Path
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent; R=W.parents[4]
O=R/'Documentation/Phase4F/Benchmark/Runs/02_AegisNX7/R3'
sha=lambda p: hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
base=json.loads((O/'baseline.json').read_text())
protected={**base['protected_sha256'],**json.loads((O/'original_import_protected.json').read_text())}
changed=[];missing=[]
for name,expected in protected.items():
    p=R/name
    if not p.is_file(): missing.append(name)
    elif sha(p)!=expected: changed.append(name)
git=lambda *args: subprocess.check_output(['git','--no-optional-locks','-c','safe.directory='+R.as_posix(),*args],cwd=R,text=True).splitlines()
tracked=git('status','--short','--untracked-files=no')
git_ok=tracked==base['git_tracked'] and git('rev-parse','HEAD')[0]==base['git_head'] and sha(R/'.git/index')==base['git_index_sha256']
sys.path.insert(0,str(R/'Working/Phase4F'))
import benchmark_validator as bv
bv.verify_freeze();bv.verify_dependencies()
humans={n:bv.audit_human(R/('Working/Phase4F/'+n),R/('Documentation/Phase4F/'+n)) for n in ['John','Jane']}
result=dict(status='PASS' if not changed and not missing and git_ok else 'FAIL',
    protected_count=len(protected),baseline_protected_count=len(base['protected_sha256']),original_import_and_extracted_source_count=6,
    changed=changed,missing=missing,git_preserved=git_ok,git_head=base['git_head'],git_tracked=tracked,
    human_evidence=humans,frozen_validator_and_dependencies_verified=True,
    accepted_R1_R2_code_assets_evidence_unchanged=not changed and not missing,
    source_archive_original_imports_unchanged=not changed and not missing,
    commits_staging_pushes=False,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(O/'preservation_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('R3_PRESERVATION',result['status'],'protected',len(protected),'changed',len(changed),'missing',len(missing),'git',git_ok)
