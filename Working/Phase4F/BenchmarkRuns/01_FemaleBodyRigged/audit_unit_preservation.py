"""Read-only preservation audit; no anatomy validation, fitting or event writes."""
import json,hashlib,sys,subprocess
from pathlib import Path
sys.dont_write_bytecode=True;R=Path(__file__).resolve().parents[4];O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';U=O/'UnitCorrection';sys.path.insert(0,str(R/'Working/Phase4F'));import benchmark_validator as bv
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();protected=json.loads((O/'protected_sha256.json').read_text());changed=[];missing=[]
for file,expected in protected.items():
    p=R/file
    if not p.exists():missing.append(file)
    elif sha(p)!=expected:changed.append(file)
before=json.loads((U/'original_pre_correction_reload.json').read_text());after=json.loads((O/'native_reload.json').read_text());keys=['hierarchy_bind_sha256','geometry_skin_sha256','mesh','skeleton','bone_count','bounds'];same={k:before[k]==after[k] for k in keys};bv.verify_freeze();bv.verify_dependencies();humans={n:bv.audit_human(R/('Working/Phase4F/'+n),R/('Documentation/Phase4F/'+n)) for n in ['John','Jane']}
git=lambda *args:subprocess.check_output(['git','-c','safe.directory='+R.as_posix(),*args],cwd=R,text=True).splitlines();tracked=git('status','--short','--untracked-files=no');cfg=json.loads((O/'run_config.json').read_text());new_tracked=[x for x in tracked if x not in cfg['git_tracked_before']];new_allowed='Working/Phase4F/rigged_unit_canonicalisation.py'
asset_files=[R/'Content'/Path(before[k].split('.')[0].removeprefix('/Game/')).with_suffix('.uasset') for k in ['mesh','skeleton']];asset_info=[dict(file=p.relative_to(R).as_posix(),sha256=sha(p),last_write_utc=p.stat().st_mtime) for p in asset_files]
out=dict(status='passed' if not changed and not missing and all(same.values()) and not new_tracked else 'failed',protected_count=len(protected),protected_changed=changed,protected_missing=missing,original_native_invariants=same,original_asset_files=asset_info,human_evidence=humans,frozen_validator_verified=True,git_head=git('rev-parse','HEAD')[0],git_tracked_after=tracked,new_tracked_changes=new_tracked,new_generic_source=new_allowed,additional_changes_scope='New Benchmark 1 folders and generic root-unit module only; earlier incomplete broad-run evidence retained, no subsequent broad test continued',benchmark_2_started=False)
(U/'preservation_audit.json').write_text(json.dumps(out,indent=2));print('PRESERVATION',out['status'],len(protected),changed,missing,new_tracked,[(n,len(x['confirmed_roles']),x['event_count']) for n,x in humans.items()])
