#pragma once
#include "Kismet/BlueprintFunctionLibrary.h"
#include "RiggedUnitBridgeLibrary.generated.h"
class USkeletalMesh;
class USkeleton;
UCLASS()
class RIGGEDUNITBRIDGE_API URiggedUnitBridgeLibrary : public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable, Category="Rigged Unit Conversion")
 static USkeleton* AttachIsolatedSkeleton(USkeletalMesh* DerivedMesh, const FString& NewSkeletonPath, const FString& DerivedNamespace);
 UFUNCTION(BlueprintCallable, Category="Rigged Unit Conversion")
 static bool SyncDerivedReference(USkeletalMesh* DerivedMesh, const FString& DerivedNamespace);
};
