from pathlib import Path
import unreal, json, traceback
O=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/Phase3B')
out={}
for name in ['AnimPose','AnimPoseEvaluationOptions','AnimPoseSpaces','AnimPoseExtensions','AnimationLibrary','AnimationBlueprintLibrary','SkeletalMesh','Skeleton','IKRigController','IKRetargeterController','IKRetargetBatchOperation','IKRetargetBatchOperationInputs','FbxImportUI','FbxSkeletalMeshImportData','InterchangeGenericAssetsPipeline','SkeletalMeshEditorSubsystem']:
    obj=getattr(unreal,name,None)
    out[name]={'doc':obj.__doc__ if obj else None,'members':{x:getattr(obj,x).__doc__ for x in dir(obj) if not x.startswith('_') and any(s in x for s in ['pose','bone','solver','goal','import','batch','mesh','animation','vert','weight'])} if obj else {}}
mesh=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase2/UE5/SK_Lara_UE5')
ref=mesh.skeleton.get_reference_pose()
out['ref_doc']={x:getattr(ref,x).__doc__ for x in dir(ref) if 'pose' in x or 'bone' in x}
out['animations']=[str(a.package_name) for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game/Characters',recursive=True) if str(a.asset_class_path.asset_name)=='AnimSequence']
(O/'api_probe.json').write_text(json.dumps(out,indent=2))
print('PHASE3B_PROBE_DONE')
