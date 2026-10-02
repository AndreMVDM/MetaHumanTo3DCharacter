#include "Phase4ALibrary.h"
#include "UDynamicMesh.h"
#include "DynamicMesh/DynamicMeshAABBTree3.h"
#include "Spatial/FastWinding.h"
#include "Skeletonization/MeshMedialAxisSampling.h"
#include "Operations/MedialSkeletonSkinBinding.h"
#include "SkeletalMeshAttributes.h"
#include "Modules/ModuleManager.h"
#include "Animation/Skeleton.h"
#include "Misc/PackageName.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "ReferenceSkeleton.h"
#include "Engine/SkeletalMesh.h"
IMPLEMENT_MODULE(FDefaultModuleImpl, Phase4ATools)
bool UPhase4ALibrary::SyncSkeletonReference(USkeletalMesh* Mesh) {
 if (!Mesh || !Mesh->GetSkeleton() || !Mesh->GetPathName().StartsWith(TEXT("/Game/MetaHumanTo3DCharacter/Phase4A/")) || !Mesh->GetSkeleton()->GetPathName().StartsWith(TEXT("/Game/MetaHumanTo3DCharacter/Phase4A/"))) return false;
 Mesh->GetSkeleton()->UpdateReferencePoseFromMesh(Mesh);Mesh->GetSkeleton()->MarkPackageDirty();return true;
}
USkeleton* UPhase4ALibrary::CreateBlankSkeleton(const FString& AssetPath) {
 if (!AssetPath.StartsWith(TEXT("/Game/MetaHumanTo3DCharacter/Phase4A/")) || !FPackageName::IsValidLongPackageName(AssetPath)) return nullptr;
 UPackage* Package=CreatePackage(*AssetPath);
 USkeleton* Skeleton=NewObject<USkeleton>(Package,*FPackageName::GetLongPackageAssetName(AssetPath),RF_Public|RF_Standalone);
 FReferenceSkeletonModifier Modifier(Skeleton);Modifier.Add(FMeshBoneInfo(TEXT("root"),TEXT("root"),INDEX_NONE),FTransform::Identity);
 FAssetRegistryModule::AssetCreated(Skeleton);Package->MarkPackageDirty();return Skeleton;
}
bool UPhase4ALibrary::GenerateMedialRig(UDynamicMesh* Mesh, int32 MaxSpheres, double ErrorThreshold, int32 MaxInfluences, bool bGeodesic, int32 VoxelResolution) {
 if (!Mesh || MaxSpheres<2 || MaxSpheres>512 || MaxInfluences<1 || MaxInfluences>12 || VoxelResolution<8 || VoxelResolution>512 || !FMath::IsFinite(ErrorThreshold) || ErrorThreshold<=0) return false;
 using namespace UE::Geometry;
 FDynamicMesh3& Dyn=Mesh->GetMeshRef();
 if (!Dyn.TriangleCount()) return false;
 FDynamicMeshAABBTree3 Spatial(&Dyn);
 TFastWindingTree<FDynamicMesh3> Winding(&Spatial);
 MedialAxis::FSkeletonViaSampling Sampling;
 Sampling.MaxSpheres=MaxSpheres; Sampling.MinClusterErrorToSplit=ErrorThreshold;
 auto Medial=Sampling.ComputeSkeleton(Spatial,1e-4,&Winding);
 SkinBinding::FBindMedialSkeletonSettings Settings;
 Settings.AnimationSkeletonOptions.SelectRootMethod=MedialAxis::FMedialSkeletonToTreeSkeletonOptions::ESelectRootMethod::ClosestToBoundsCenter;
 Settings.AnimationSkeletonOptions.CustomRootPosition=FVector3d::ZeroVector;
 Settings.BindSettings.MaxInfluences=MaxInfluences;
 Settings.BindSettings.VoxelResolution=VoxelResolution;
 Settings.BindSettings.BindType=bGeodesic?ESkinBindingType::GeodesicVoxel:ESkinBindingType::DirectDistance;
 bool Compatible=false;
 const bool Success=SkinBinding::CreateSkinWeightsFromMedialSkeleton(Medial,Dyn,Compatible,FSkeletalMeshAttributes::DefaultSkinWeightProfileName,Settings);
 UE_LOG(LogTemp,Display,TEXT("PHASE4A_MEDIAL spheres=%d success=%d compatible=%d"),Medial.Spheres.Num(),Success,Compatible);
 return Success && Compatible;
}
