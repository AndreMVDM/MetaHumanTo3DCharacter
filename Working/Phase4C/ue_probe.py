import unreal,json,traceback
from pathlib import Path
O=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/Phase4C')
r={'engine':unreal.SystemLibrary.get_engine_version(),'names':[n for n in dir(unreal) if any(s in n for s in ['MetaHumanCharacter','ConformTarget','TargetParts','PosedDNA'])]}
try:
    sub=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
    r['subsystem']=str(sub)
    r['methods']={n:getattr(sub,n).__doc__ for n in dir(sub) if any(s in n for s in ['conform','body','edit','export','pose','mesh'])}
    r['exports']={n:getattr(unreal.MetaHumanCharacterExportBlueprintLibrary,n).__doc__ for n in dir(unreal.MetaHumanCharacterExportBlueprintLibrary) if 'export' in n}
    r['template']=str(unreal.load_asset('/MetaHumanCharacter/Body/IdentityTemplate/SKM_Body'))
    r['params']=str(unreal.ConformTargetParams())
except Exception:
    r['error']=traceback.format_exc()
(O/'python_api_probe.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print('PHASE4C_PROBE',r.get('subsystem'),r.get('error'))
