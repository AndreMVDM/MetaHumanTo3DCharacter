using UnrealBuildTool;
public class RiggedUnitBridge : ModuleRules {
 public RiggedUnitBridge(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.NoPCHs;
  PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","AssetRegistry"});
 }
}
