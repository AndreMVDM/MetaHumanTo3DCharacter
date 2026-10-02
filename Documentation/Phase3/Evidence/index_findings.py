"""Build auditable local source/API indexes; never invokes Unreal."""
from collect_evidence import ENGINE, OUT, PROJECT, save, protected
import hashlib, json, re
MH='Plugins/MetaHuman/'
CH=MH+'MetaHumanCharacter/'
CORE=MH+'MetaHumanCoreTechLib/Source/MetaHumanCoreTechLib/'
IK='Plugins/Animation/IKRig/Source/'
SOURCE=[
 ('S01','Build/Build.version',[(1,12)]),
 ('S02',CH+'Source/MetaHumanCharacterEditor/Public/MetaHumanCharacterEditorSubsystem.h',[(490,550),(1345,1357),(1653,1744),(1786,1839),(1888,1939)]),
 ('S03',CH+'Source/MetaHumanCharacterEditor/Private/MetaHumanCharacterEditorSubsystem.cpp',[(7408,7590),(7740,7805),(8136,8152),(8211,8264)]),
 ('S04',CORE+'Private/MetaHumanCharacterBodyIdentity.cpp',[(234,325),(442,491),(592,654),(1333,1436)]),
 ('S05',CORE+'Private/api/MetaHumanCreatorBodyAPI.cpp',[(142,188),(320,337),(1284,1354),(1568,1579)]),
 ('S06',CORE+'Private/bodyshapeeditor/src/BodyShapeEditor.cpp',[(2603,2661),(5241,5262),(5328,5419)]),
 ('S07',CORE+'Public/MetaHumanConformTargetParams.h',[(1,107)]),
 ('S08',CORE+'Public/MetaHumanConformSolverSettings.h',[(35,103)]),
 ('S09',CH+'Content/Python/examples/example_conform_from_custom_mesh.py',[(1,31),(90,128),(180,224)]),
 ('S10',CH+'Content/Python/examples/example_sculpt_body.py',[(1,60)]),
 ('S11',MH+'MetaHumanSDK/Source/MetaHumanSDKRuntime/Public/MetaHumanBodyType.h',[(1,36)]),
 ('S12','Source/Editor/UnrealEd/Classes/Factories/FbxAssetImportData.h',[(1,145)]),
 ('S13','Plugins/Interchange/Runtime/Source/Pipelines/Public/InterchangeGenericAssetsPipeline.h',[(63,89)]),
 ('S14','Plugins/Interchange/Runtime/Source/Pipelines/Private/InterchangeGenericAssetsPipeline.cpp',[(1287,1317)]),
 ('S15','Plugins/Interchange/Runtime/Source/Import/Private/Mesh/InterchangeSkeletonHelper.cpp',[(309,360)]),
 ('S16',IK+'IKRig/Private/Retargeter/IKRetargetProcessor.cpp',[(28,89)]),
 ('S17',IK+'IKRig/Private/AnimNodes/AnimNode_RetargetPoseFromMesh.cpp',[(175,210)]),
 ('S18',IK+'IKRig/Private/Retargeter/RetargetOps/RunIKRigOp.cpp',[(281,321)]),
 ('S19',IK+'IKRig/Private/Rig/Solvers/IKRigFullBodyIK.cpp',[(36,138)]),
 ('S20','Plugins/Experimental/FullBodyIK/Source/PBIK/Private/Core/PBIKSolver.cpp',[(964,1005)]),
 ('S21',IK+'IKRig/Private/Retargeter/RetargetOps/PelvisMotionOp.cpp',[(202,227)]),
 ('S22',IK+'IKRigEditor/Private/RigEditor/IKRigAutoFBIK.cpp',[(13,85)]),
 ('S23','Plugins/Experimental/MeshResizing/Source/MeshResizingNodes/Public/MeshResizing/MeshWrapNode.h',[(17,58),(115,181)]),
 ('S24','Plugins/Experimental/MeshResizing/Source/MeshResizingNodes/Private/MeshResizing/MeshWrapNode.cpp',[(189,239)]),
 ('S25','Plugins/Experimental/MeshResizing/Source/MeshResizingNodes/Private/MeshResizing/RBFInterpolationNodes.h',[(62,122)]),
 ('S26','Plugins/Runtime/MeshModelingToolset/Source/SkeletalMeshModifiers/Public/SkeletonModifier.h',[(127,149),(179,194)]),
 ('S27',IK+'IKRig/Public/Retargeter/RetargetOps/ScaleSourceOp.h',[(20,65)]),
 ('S28','Plugins/Interchange/Runtime/Source/Parsers/Fbx/Private/Ufbx/UfbxParser.cpp',[(99,125)]),
 ('S29',CH+'Content/Python/examples/example_auto_rig.py',[(1,37)]),
 ('S30',MH+'MetaHumanAnimator/Source/MetaHumanIdentity/Public/MetaHumanIdentityParts.h',[(90,142)])]
def main():
    rows=[];md=['# Installed source evidence','', 'Excerpts retain original one-based line numbers. Source paths and SHA-256 identify the inspected installation. No Unreal API was executed.','']
    for ident,rel,ranges in SOURCE:
        path=ENGINE/rel;raw=path.read_bytes();lines=raw.decode('utf-8-sig',errors='replace').splitlines()
        excerpts=[{'first_line':a,'last_line':min(b,len(lines)),'lines':lines[a-1:b]} for a,b in ranges]
        rows.append({'id':ident,'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'excerpts':excerpts})
        md.extend([f'## {ident}', '', f'[{path.name}](<{path.as_posix()}>): '+str(path),''])
        for e in excerpts:
            md.extend(f'    {i}: {line}' for i,line in enumerate(e['lines'],e['first_line']));md.append('')
    save('source_evidence.json',rows);(OUT/'source_evidence.md').write_text('\n'.join(md),encoding='utf-8')
    h=ENGINE/CH/'Source/MetaHumanCharacterEditor/Public/MetaHumanCharacterEditorSubsystem.h';hl=h.read_text().splitlines()
    names=['TryAddObjectToEdit','RemoveObjectToEdit','GetMeshDataForConforming','ConformToTargetMeshes','AlignToTargetMeshes','TrackFaceLandmarksFromImage','CommitPosedStateAsAPose','GetPresetBodyKeyPoints','ConformBodyToTarget','GetMeshForBodyConformingFromTemplate','GetJointsForBodyConformingFromTemplate','GetMeshForBodyConformingFromDNA','GetJointsForBodyConformingFromDNA','SetBodyMesh','SetBodyJoints','ImportBodyWholeRig','GetBodyConstraints','SetBodyConstraints','RequestAutoRigging']
    apis=[]
    for name in names:
        found=[i for i,l in enumerate(hl) if re.search(r'\b'+name+r'\s*\(',l) and ';' in l and not l.strip().startswith('*')]
        assert found,name
        i=found[-1];apis.append({'class':'UMetaHumanCharacterEditorSubsystem','function':name,'header':str(h),'line':i+1,'declaration':hl[i].strip(),'module':'MetaHumanCharacterEditor','plugin':'MetaHumanCharacter','scope':'Editor','api_status':'public reflected API','blueprint_callable':'BlueprintCallable' in '\n'.join(hl[max(0,i-3):i]),'python':'reflected; shipped examples for main conform paths; not runtime-probed here'})
    save('api_inventory.json',apis)
    systems=[
      ('custom_mesh_conform','UMetaHumanCharacterEditorSubsystem',CH+'Source/MetaHumanCharacterEditor/Public/MetaHumanCharacterEditorSubsystem.h','MetaHumanCharacterEditor','Editor','public Blueprint/Python/C++','usable_with_preprocessing','arbitrary human surface input; MetaHuman output, source rig not preserved'),
      ('template_conform','FMetaHumanCharacterBodyIdentity::FState',CORE+'Public/MetaHumanCharacterBodyIdentity.h','MetaHumanCoreTechLib','Editor','public C++ wrapper','metahuman_topology_only','body/combined vertex correspondence required'),
      ('identity_face','UMetaHumanIdentityFace',MH+'MetaHumanAnimator/Source/MetaHumanIdentity/Public/MetaHumanIdentityParts.h','MetaHumanIdentity','Editor authoring','public reflected Conform','identity_workflow','face fit; not general body resize'),
      ('face_conformer','UE::Wrappers::FMetaHumanConformer',CORE+'Public/MetaHumanConformer.h','MetaHumanCoreTechLib','Editor','public C++ wrapper','identity_workflow','scan/depth, face landmarks and cameras'),
      ('fbx_uniform_scale','UFbxAssetImportData','Source/Editor/UnrealEd/Classes/Factories/FbxAssetImportData.h','UnrealEd','Editor','public reflected property','direct_uniform_scaling','ImportUniformScale; validate effective importer/output transforms'),
      ('interchange_uniform_scale','UInterchangeGenericAssetsPipeline','Plugins/Interchange/Runtime/Source/Pipelines/Public/InterchangeGenericAssetsPipeline.h','InterchangePipelines','import pipeline; project authoring here','public reflected property','direct_uniform_scaling','ImportOffsetUniformScale; no unit-root guarantee'),
      ('ik_rig_setup','UIKRigController',IK+'IKRigEditor/Public/RigEditor/IKRigController.h','IKRigEditor','Editor','public reflected controller','direct_animation_adaptation','does not resize mesh'),
      ('retarget_setup','UIKRetargeterController',IK+'IKRigEditor/Public/RetargetEditor/IKRetargeterController.h','IKRigEditor','Editor','public reflected controller','direct_animation_adaptation','chain/pose/operation authoring'),
      ('source_pose_scale','FIKRetargetScaleSourceOp',IK+'IKRig/Public/Retargeter/RetargetOps/ScaleSourceOp.h','IKRig','Runtime','public reflected struct/controller','pose_only','scales source pose and goals, not target neutral asset'),
      ('skeleton_edit','USkeletonModifier','Plugins/Runtime/MeshModelingToolset/Source/SkeletalMeshModifiers/Public/SkeletonModifier.h','SkeletalMeshModifiers','asset commit authoring requires editor checks','public Blueprint/C++','custom_integration','not automatic anatomy normalisation'),
      ('mesh_wrap','FMeshWrapNode','Plugins/Experimental/MeshResizing/Source/MeshResizingNodes/Public/MeshResizing/MeshWrapNode.h','MeshResizingDataflowNodes','Runtime Dataflow; Editor landmark tools','public Dataflow struct; Experimental','usable_with_preprocessing','matched source/target landmarks; geometry output'),
      ('wrap_operation','UE::Geometry::FWrapMesh','Plugins/Runtime/GeometryProcessing/Source/DynamicMesh/Public/Operations/WrapMesh.h','DynamicMesh','Runtime geometry','public C++','custom_integration','wrap source topology to supplied target shape'),
      ('rbf_deformation','UE::MeshResizing::FRBFInterpolation','Plugins/Experimental/MeshResizing/Source/MeshResizingCore/Public/MeshResizing/RBFInterpolation.h','MeshResizingCore','Runtime','public exported C++; Experimental','usable_with_preprocessing','prepared samples and corresponding driver positions'),
      ('proxy_deformation','UE::MeshResizing::FBaseBodyTools','Plugins/Experimental/MeshResizing/Source/MeshResizingCore/Public/MeshResizing/BaseBodyTools.h','MeshResizingCore','Runtime','public exported C++; Experimental','usable_with_preprocessing','vertex mapping proxy data'),
      ('regional_deformation','UE::MeshResizing::FCustomRegionResizing','Plugins/Experimental/MeshResizing/Source/MeshResizingCore/Public/MeshResizing/CustomRegionResizing.h','MeshResizingCore','Runtime','public exported C++; Experimental','usable_with_preprocessing','prepared custom region data'),
      ('dynamic_mesh_transform','UGeometryScriptLibrary_MeshTransformFunctions','Plugins/Runtime/GeometryScripting/Source/GeometryScriptingCore/Public/GeometryScript/MeshTransformFunctions.h','GeometryScriptingCore','Runtime dynamic mesh','public reflected Blueprint library','custom_integration','ScaleMesh/TransformMesh; no complete skeletal maintenance'),
      ('character_factory','UMetaHumanCharacterFactoryNew',CH+'Source/MetaHumanCharacterEditor/Public/MetaHumanCharacterFactoryNew.h','MetaHumanCharacterEditor','Editor','public asset factory','metahuman_output_creation','used by shipped conform example'),
      ('internal_body_api','MetaHumanCreatorBodyAPI',CORE+'Private/api/MetaHumanCreatorBodyAPI.h','MetaHumanCoreTechLib','Editor','private internal C++','not_plugin_boundary','use public subsystem'),
      ('internal_shape_solver','BodyShapeEditor',CORE+'Private/bodyshapeeditor/include/bodyshapeeditor/BodyShapeEditor.h','MetaHumanCoreTechLib','Editor','private internal C++','not_plugin_boundary','PCA/pose/scale/ICP/refinement solver')]
    system_rows=[]
    for ident,cls,rel,module,scope,status,classification,notes in systems:
        sp=ENGINE/rel;assert sp.is_file(),sp
        system_rows.append(dict(id=ident,cpp_class=cls,header=str(sp),module=module,scope=scope,api_status=status,tripo_classification=classification,notes=notes,sha256=hashlib.sha256(sp.read_bytes()).hexdigest(),executed=False))
    save('systems_inventory.json',system_rows)
    save('web_sources.json',{'review_date_local':'2026-09-30','purpose':'Epic primary-source corroboration; installed 5.8.3 source remains main evidence','urls':[
      'https://dev.epicgames.com/documentation/metahuman/metahuman-5-8-release-notes-in-unreal-engine',
      'https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-custom-mesh-tool-in-unreal-engine',
      'https://dev.epicgames.com/documentation/metahuman/metahuman-creator-python-scripting-in-unreal-engine',
      'https://dev.epicgames.com/documentation/en-us/metahuman/from-template-mesh',
      'https://forums.unrealengine.com/t/metahuman-conform-topology-asset-pack-released/2609293',
      'https://dev.epicgames.com/documentation/metahuman/metahuman-creator-body-params-tool-in-unreal-engine',
      'https://www.metahuman.com/news/metahuman-5-7-brings-major-improvements-to-body-conforming-with-more-to-come']})
    pipelines=ENGINE/CH/'Content/Body/IdentityTemplate/pipeline_presets.json';p=json.loads(pipelines.read_text())
    save('pipeline_presets_structure.json',{'path':str(pipelines),'sha256':hashlib.sha256(pipelines.read_bytes()).hexdigest(),'structure':p})
    save('protected_after.json',protected())
    before=json.loads((OUT/'protected_before.json').read_text());after=protected();changes=[k for k in sorted(before.keys()|after.keys()) if before.get(k)!=after.get(k)]
    source_changes=[r['path'] for r in rows if hashlib.sha256(__import__('pathlib').Path(r['path']).read_bytes()).hexdigest()!=r['sha256']]
    report=PROJECT/'Documentation/Phase3/MetaHumanResizeConformInvestigation.md';report_text=report.read_text(encoding='utf-8')
    sections=[int(n) for n in re.findall(r'^## (\d+)\.',report_text,re.M)]
    missing_links=[]
    for link in re.findall(r'\]\((Evidence/[^)]+)\)',report_text):
        if not (report.parent/link).exists():missing_links.append(link)
    assert sections==list(range(1,16)),sections
    assert not missing_links,missing_links
    save('validation.json',{'protected_files':len(before),'changed_protected_files':changes,'indexed_source_files':len(rows),'source_hash_mismatches_on_recheck':source_changes,'report_sections':sections,'missing_local_evidence_links':missing_links,'editor_apis_executed':False,'unreal_assets_created':False,'scope':'Only Documentation/Phase3 written by investigation scripts','git':'No repository at project path; no commit or push'})
    print(json.dumps({'source_files':len(rows),'metahuman_api_entries':len(apis),'protected_files':len(before),'changed_protected_files':changes}))
if __name__=='__main__':main()
