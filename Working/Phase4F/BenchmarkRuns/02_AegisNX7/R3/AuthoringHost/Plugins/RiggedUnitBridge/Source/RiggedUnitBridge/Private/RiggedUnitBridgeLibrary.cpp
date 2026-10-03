#include "RiggedUnitBridgeLibrary.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"
#include "Misc/PackageName.h"
#include "UObject/Package.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Modules/ModuleManager.h"
#include "Retargeter/IKRetargetProcessor.h"
#include "Retargeter/IKRetargeter.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimData/IAnimationDataModel.h"
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
bool URiggedUnitBridgeLibrary::ValidateRetargetInitialisation(USkeletalMesh* SourceMesh, USkeletalMesh* TargetMesh, UIKRetargeter* Retargeter) {
 if (!SourceMesh || !TargetMesh || !Retargeter) return false;
 FIKRetargetProcessor Processor;
 FRetargetInitParameters Params;
 Params.SourceSkeletalMesh=SourceMesh; Params.TargetSkeletalMesh=TargetMesh; Params.RetargeterAsset=Retargeter;
 Processor.Initialize(Params);
 return Processor.IsInitialized();
}
bool URiggedUnitBridgeLibrary::ValidateBakedTracks(UAnimSequence* Animation, FName RootBone, double MaximumLocalTranslation) {
 if (!Animation || !FMath::IsFinite(MaximumLocalTranslation) || MaximumLocalTranslation<=0) return false;
 const IAnimationDataModel* Model=Animation->GetDataModel();
 if (!Model || Model->GetNumberOfKeys()<1) return false;
 TArray<FName> Names; Model->GetBoneTrackNames(Names);
 if (!Names.Contains(RootBone)) return false;
 for (FName Name:Names) for (int32 Key=0;Key<Model->GetNumberOfKeys();++Key) {
  const FTransform T=Model->GetBoneTrackTransform(Name,FFrameNumber(Key));
  if (T.ContainsNaN() || T.GetTranslation().Length()>MaximumLocalTranslation) return false;
  if (Name==RootBone && !T.GetScale3D().Equals(FVector::OneVector,0.0001)) return false;
 }
 return true;
}
