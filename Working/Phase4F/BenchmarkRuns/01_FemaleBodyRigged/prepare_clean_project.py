"""Copy destination dependency closure only; protected project/source assets stay present and untouched."""
import json,hashlib,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True;R=Path(__file__).resolve().parents[4];W=Path(__file__).resolve().parent;O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';C=W/'CleanProject';assert not C.exists(),'refuse overwrite';C.mkdir()
a=json.loads((O/'native_component_audit.json').read_text())['dependency_closure'];assert not a['foreign_game_packages'] and not a['authoring_packages']
files=[]
for package in a['packages']:
    if not package.startswith('/Game/'):continue
    relative='Content/'+package.removeprefix('/Game/')
    for ext in ['.uasset','.ubulk','.uexp','.uptnl']:
        src=R/(relative+ext)
        if not src.exists():continue
        dst=C/(relative+ext);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);h=hashlib.sha256(src.read_bytes()).hexdigest();assert hashlib.sha256(dst.read_bytes()).hexdigest()==h;files.append(dict(file=dst.relative_to(C).as_posix(),sha256=h,bytes=src.stat().st_size))
(C/'Benchmark1Smoke.uproject').write_text(json.dumps(dict(FileVersion=3,EngineAssociation='5.8',Category='Benchmark diagnostic',Description='Isolated destination-only Benchmark 1 engine smoke; no final product integration claim',Plugins=[dict(Name='PythonScriptPlugin',Enabled=True),dict(Name='EditorScriptingUtilities',Enabled=True),dict(Name='GeometryScripting',Enabled=True)]),indent=2))
(O/'clean_project_copy.json').write_text(json.dumps(dict(status='passed',project=str(C/'Benchmark1Smoke.uproject'),original_source_packages_unavailable=True,files=files,source_archive_included=False,retargeter_included=False,source_fixtures_included=False),indent=2));print('CLEAN_PROJECT_COPY',len(files),sum(x['bytes'] for x in files))
