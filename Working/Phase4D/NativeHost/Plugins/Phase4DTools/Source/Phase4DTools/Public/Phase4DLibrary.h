#pragma once
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Phase4DLibrary.generated.h"
class USkeleton;
class USkeletalMesh;
UCLASS()
class PHASE4DTOOLS_API UPhase4DLibrary : public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) static USkeleton* CreateBlankSkeleton(const FString& AssetPath);
 UFUNCTION(BlueprintCallable) static bool SyncSkeletonReference(USkeletalMesh* Mesh);
 UFUNCTION(BlueprintCallable) static bool SetSkeletonPreviewMesh(USkeletalMesh* Mesh);
};
