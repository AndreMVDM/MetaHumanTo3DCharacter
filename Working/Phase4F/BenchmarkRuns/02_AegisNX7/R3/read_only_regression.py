"""Read-only replay of accepted Female inspection/unit/semantic functions."""
import unreal, ast, json, math, hashlib, sys, traceback
from pathlib import Path
sys.dont_write_bytecode = True
W = Path(__file__).resolve().parent
R = W.parents[4]
O = R/'Documentation/Phase4F/Benchmark/Runs/02_AegisNX7/R3'
F = R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/R2_EndToEnd'
P = R/'Working/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2/author.py'
tree = ast.parse(P.read_text())
helpers = ast.Module(body=[n for n in tree.body if (isinstance(n,ast.FunctionDef) and n.name in ['require','v','tr','inspect','bone_name','chain_path','analyse']) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REQUIRED' for t in n.targets))],type_ignores=[])
exec(compile(helpers,str(P),'exec'),globals())
sys.path.insert(0,str(R/'Working/Phase4F'))
from rigged_unit_canonicalisation import plan, VERSION
result = dict(status='RUNNING', assets_saved=False, assets_reauthored=False, accepted_R2_source_sha256=hashlib.sha256(P.read_bytes()).hexdigest())
try:
    expected = json.loads((F/'input_validation.json').read_text())
    inp = inspect(unreal.load_asset(expected['input']['mesh']))
    sem = analyse(unreal.load_asset(inp['mesh']),inp['bones'])
    unit = plan(inp['bones'])
    a = json.loads((F/'authoring_result.json').read_text())
    dest = inspect(unreal.load_asset(a['assets']['mesh']))
    ds = analyse(unreal.load_asset(a['assets']['mesh']),dest['bones'])
    checks = dict(input_geometry_skin=inp['geometry_skin_sha256']==expected['input']['geometry_skin_sha256'],
        input_height=inp['height_cm']==expected['input']['height_cm'],input_bones=inp['bones']==expected['input']['bones'],
        input_semantics=sem==expected['automatic_analysis'],unit_factor=abs(unit['factor']-100)<1e-9,
        unchanged_R1_version=VERSION=='phase4f.rigged-unit-canonicalisation/1.0.0',
        destination_geometry_skin=dest['geometry_skin_sha256']==a['destination']['geometry_skin_sha256'],
        destination_height=dest['height_cm']==a['destination']['height_cm'],destination_bones=dest['bones']==a['destination']['bones'],
        destination_semantics=ds==a['semantics'])
    require(all(checks.values()),'Female read-only replay regression')
    result.update(status='PASS',checks=checks,input=inp,unit_classifier=dict(version=VERSION,factor=unit['factor'],classification='canonicalisation_required'),input_semantics=sem,destination=dest,destination_semantics=ds)
except Exception:
    result.update(status='FAIL',error=traceback.format_exc())
(O/'FemaleRegression/read_only_replay.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print('R3_FEMALE_READ_ONLY_REGRESSION',result['status'],result.get('error',''))
