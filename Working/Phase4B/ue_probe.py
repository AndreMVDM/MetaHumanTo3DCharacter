import unreal,json
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase4B'
terms=['landmark','keypoint','autorig','skeleton','symmetry','segment','poseestimate','bodyidentity','metahumancharacter','meshwrap','nne','rigmapper']
names=[n for n in dir(unreal) if any(t in n.lower() for t in terms)]
result={'engine_version':unreal.SystemLibrary.get_engine_version(),'classes':{},'relevant_names':names,'editor_world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()}
for name in names:
    cls=getattr(unreal,name)
    if any(t in name.lower() for t in ['metahumancharactereditorsubsystem','skeletonmodifier','geometryscript_bone','meshwrap','skeletalmeshfactory','skeletonfactory','planarsymmetry']):
        result['classes'][name]={'doc':cls.__doc__,'methods':{m:getattr(cls,m).__doc__ for m in dir(cls) if any(t in m.lower() for t in ['joint','bone','keypoint','conform','create','fit','symmetry'])}}
(O/'python_api_probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('PHASE4B_PROBE_DONE',result['engine_version'],len(names))
