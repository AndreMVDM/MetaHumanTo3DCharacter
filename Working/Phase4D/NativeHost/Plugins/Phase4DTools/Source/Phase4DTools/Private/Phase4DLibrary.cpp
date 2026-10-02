#include "Phase4DLibrary.h"
#include "Modules/ModuleManager.h"
#include "Animation/Skeleton.h"
#include "Misc/PackageName.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "ReferenceSkeleton.h"
#include "Engine/SkeletalMesh.h"
#include "UObject/Package.h"
IMPLEMENT_MODULE(FDefaultModuleImpl, Phase4DTools)
bool UPhase4DLibrary::SyncSkeletonReference(USkeletalMesh* Mesh) {
 if (!Mesh || !Mesh->GetSkeleton() || !Mesh->GetPathName().StartsWith(TEXT("/Game/MetaHumanTo3DCharacter/Phase4D/")) || !Mesh->GetSkeleton()->GetPathName().StartsWith(TEXT("/Game/MetaHumanTo3DCharacter/Phase4D/"))) return false;
 Mesh->GetSkeleton()->UpdateReferencePoseFromMesh(Mesh);Mesh->GetSkeleton()->MarkPackageDirty();return true;
}
bool UPhase4DLibrary::SetSkeletonPreviewMesh(USkeletalMesh* Mesh) {
 if (!Mesh || !Mesh->GetSkeleton() || !Mesh->GetPathName().StartsWith(TEXT("/Game/MetaHumanTo3DCharacter/Phase4D/")) || !Mesh->GetSkeleton()->GetPathName().StartsWith(TEXT("/Game/MetaHumanTo3DCharacter/Phase4D/"))) return false;
 Mesh->GetSkeleton()->SetPreviewMesh(Mesh);return true;
}
USkeleton* UPhase4DLibrary::CreateBlankSkeleton(const FString& AssetPath) {
 if (!AssetPath.StartsWith(TEXT("/Game/MetaHumanTo3DCharacter/Phase4D/")) || !FPackageName::IsValidLongPackageName(AssetPath) || FindPackage(nullptr,*AssetPath)) return nullptr;
 UPackage* Package=CreatePackage(*AssetPath);
 USkeleton* Skeleton=NewObject<USkeleton>(Package,*FPackageName::GetLongPackageAssetName(AssetPath),RF_Public|RF_Standalone);
 FReferenceSkeletonModifier Modifier(Skeleton);Modifier.Add(FMeshBoneInfo(TEXT("root"),TEXT("root"),INDEX_NONE),FTransform::Identity);
 FAssetRegistryModule::AssetCreated(Skeleton);Package->MarkPackageDirty();return Skeleton;
}
