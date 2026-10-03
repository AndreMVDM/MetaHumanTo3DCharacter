#include "RiggedUnitBridgeLibrary.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"
#include "Misc/PackageName.h"
#include "UObject/Package.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Modules/ModuleManager.h"
IMPLEMENT_MODULE(FDefaultModuleImpl, RiggedUnitBridge)
USkeleton* URiggedUnitBridgeLibrary::AttachIsolatedSkeleton(USkeletalMesh* Mesh, const FString& Path, const FString& Namespace) {
 if (!Mesh || !Mesh->GetSkeleton() || !Namespace.StartsWith(TEXT("/Game/")) || !Namespace.EndsWith(TEXT("/")) || !Mesh->GetPathName().StartsWith(Namespace) || !Path.StartsWith(Namespace) || !FPackageName::IsValidLongPackageName(Path) || FindPackage(nullptr,*Path)) return nullptr;
 UPackage* Package=CreatePackage(*Path);
 USkeleton* Skeleton=DuplicateObject<USkeleton>(Mesh->GetSkeleton(),Package,*FPackageName::GetLongPackageAssetName(Path));
 if (!Skeleton) return nullptr;
 Skeleton->SetFlags(RF_Public|RF_Standalone);Mesh->SetSkeleton(Skeleton);Skeleton->SetPreviewMesh(Mesh);
 FAssetRegistryModule::AssetCreated(Skeleton);Package->MarkPackageDirty();Mesh->MarkPackageDirty();return Skeleton;
}
bool URiggedUnitBridgeLibrary::SyncDerivedReference(USkeletalMesh* Mesh,const FString& Namespace) {
 if (!Mesh || !Mesh->GetSkeleton() || !Namespace.StartsWith(TEXT("/Game/")) || !Namespace.EndsWith(TEXT("/")) || !Mesh->GetPathName().StartsWith(Namespace) || !Mesh->GetSkeleton()->GetPathName().StartsWith(Namespace)) return false;
 Mesh->GetSkeleton()->UpdateReferencePoseFromMesh(Mesh);Mesh->GetSkeleton()->SetPreviewMesh(Mesh);Mesh->GetSkeleton()->MarkPackageDirty();return true;
}
