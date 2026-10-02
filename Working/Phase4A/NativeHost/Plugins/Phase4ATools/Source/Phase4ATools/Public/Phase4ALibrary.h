#pragma once
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Phase4ALibrary.generated.h"
class UDynamicMesh;
class USkeleton;
class USkeletalMesh;
UCLASS()
class PHASE4ATOOLS_API UPhase4ALibrary : public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) static USkeleton* CreateBlankSkeleton(const FString& AssetPath);
 UFUNCTION(BlueprintCallable) static bool SyncSkeletonReference(USkeletalMesh* Mesh);
 UFUNCTION(BlueprintCallable) static bool GenerateMedialRig(UDynamicMesh* Mesh, int32 MaxSpheres, double ErrorThreshold, int32 MaxInfluences, bool bGeodesic, int32 VoxelResolution);
};
