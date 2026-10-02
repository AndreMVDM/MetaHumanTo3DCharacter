from pathlib import Path
import importlib.util,json,sys
sys.dont_write_bytecode=True # Read-only reuse must not write into the older evidence namespace.
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase3B'
spec=importlib.util.spec_from_file_location('old_readonly_parser',P/'Documentation/Phase3/Evidence/collect_evidence.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
dcc=json.loads((O/'dcc_candidates.json').read_text());inputs={d['source_fbx'] for d in dcc}|{d['fbx'] for d in dcc}
result=[m.fbx(Path(p)) for p in sorted(inputs)]
(O/'fbx_units_and_bind_data.json').write_text(json.dumps(result,indent=2))
print('FBX_FILES_PARSED',len(result))
