import unreal,json,traceback
from pathlib import Path
O=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/Phase4A')
names=['SkeletonModifier','SkinWeightModifier','SkeletonFromStaticMeshFactory','SkeletalMeshFromStaticMeshFactory','GeometryScript_NewAssetUtils','GeometryScript_AssetUtils','GeometryScriptLibrary_MeshBoneWeightFunctions','GeometryScript_BoneWeights','GeometryScript_MeshBoneWeights','GeometryScript_MeshQueries','GeometryScript_MeshUVs','GeometryScript_MeshTransforms','GeometryScriptSmoothBoneWeightsOptions','StaticMeshToSkeletalMeshConvertOptions']
out={'engine_version':unreal.SystemLibrary.get_engine_version(),'classes':{},'related_names':[n for n in dir(unreal) if any(x in n for x in ['BoneWeight','Skeleton','Medial','MeshUV','SkeletalMeshFrom','StaticMeshTo'])]}
for n in names:
    c=getattr(unreal,n,None)
    if c:out['classes'][n]={'doc':c.__doc__,'methods':{k:getattr(c,k).__doc__ for k in dir(c) if any(x in k for x in ['skeleton','bone','weight','mesh','uv','transform'])}}
(O/'python_api_probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('PHASE4A_PROBE_DONE',out['related_names'])
