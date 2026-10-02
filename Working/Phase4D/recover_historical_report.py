"""Reconstruct the pre-trial generator text explicitly, without claiming an original hash."""
import sys,ast,hashlib,json
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));import core
O=core.O
snap=core.W/'HumanTrialFinalisation/InputSnapshot';src=snap/'before_finalise.py';tree=ast.parse(src.read_text());expr=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='report' for t in n.targets))
state=core.rebuild(core.fresh_state());metrics=core.metrics(state);points={r['role']:r['position_cm'] for r in state['joints']};comparisons=[]
for phase,filename,key in [('Phase4B','automatic_fit_v2.json','position_cm'),('Phase4C','automatic_fit_v2.json','position_cm'),('Phase4A','../Phase4B/manual_control_comparison_v2.json','control_in_inferred_frame_cm')]:
 data=core.read(core.P/'Documentation'/phase/filename);ds=[core.norm(core.sub(points[r['role']],r[key])) for r in data['joints']];comparisons.append({'mean_difference_cm':sum(ds)/len(ds),'max_difference_cm':max(ds)})
gate={'checks':[None]*106,'failed':[None]*38,'downstream_authorised':False};before=core.read(core.O/'protected_before.json')['files'];changed=[];missing=[];added=[];checks=core.read(core.O/'mechanics_validation.json');uechecks=core.read(core.O/'ue_mechanics_validation.json')
report=eval(compile(ast.Expression(expr),str(src),'eval'));dest=snap/'reconstructed_pretrial_report.md';dest.write_text(report,encoding='utf-8')
provenance={'method':'Deterministic reconstruction from preserved original finalise report template and immutable automatic starting proposal; initial zero-event metrics, documented initial 106 checks/38 failures and 2515-file baseline','original_before_first_refresh_bytes_available':False,'original_hash_claimed':False,'reconstructed_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'first_refresh_report_preserved':'initial_finaliser_Phase4DGuidedLandmarkCorrection.md','purpose':'Restore the historical prototype narrative and original zero-event metrics; human finalisation appended separately'}
core.save(core.O/'historical_report_recovery.json',provenance)
target=core.O/'Phase4DGuidedLandmarkCorrection.md'
assert '## 29.' not in target.read_text(), 'Do not overwrite a finalised report'
target.write_text(report,encoding='utf-8');print('Historical report reconstructed explicitly; current trial will be appended')
