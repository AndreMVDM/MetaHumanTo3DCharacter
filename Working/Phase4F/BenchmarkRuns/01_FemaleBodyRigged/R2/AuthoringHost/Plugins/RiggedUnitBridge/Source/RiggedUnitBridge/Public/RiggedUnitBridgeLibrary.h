#pragma once
#include "Kismet/BlueprintFunctionLibrary.h"
#include "RiggedUnitBridgeLibrary.generated.h"
class USkeletalMesh;
class USkeleton;
class UIKRetargeter;
class UAnimSequence;
UCLASS()
class RIGGEDUNITBRIDGE_API URiggedUnitBridgeLibrary : public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable, Category="Rigged Unit Conversion")
 static USkeleton* AttachIsolatedSkeleton(USkeletalMesh* DerivedMesh, const FString& NewSkeletonPath, const FString& DerivedNamespace);
 UFUNCTION(BlueprintCallable, Category="Rigged Unit Conversion")
 static bool SyncDerivedReference(USkeletalMesh* DerivedMesh, const FString& DerivedNamespace);
 UFUNCTION(BlueprintCallable, Category="Rigged Character Validation")
 static bool ValidateRetargetInitialisation(USkeletalMesh* SourceMesh, USkeletalMesh* TargetMesh, UIKRetargeter* Retargeter);
 UFUNCTION(BlueprintCallable, Category="Rigged Character Validation")
 static bool ValidateBakedTracks(UAnimSequence* Animation, FName RootBone, double MaximumLocalTranslation);
};
