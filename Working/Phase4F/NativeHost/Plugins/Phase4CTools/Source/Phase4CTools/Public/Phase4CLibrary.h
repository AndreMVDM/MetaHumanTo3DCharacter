#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Phase4CLibrary.generated.h"
UCLASS()
class PHASE4CTOOLS_API UPhase4CLibrary : public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable,Category="Phase4C")
 static FString InspectPosedDNA(const FString& FilePath);
};
