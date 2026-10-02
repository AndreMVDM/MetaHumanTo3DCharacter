using UnrealBuildTool;
public class Phase4DTools : ModuleRules {
 public Phase4DTools(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.NoPCHs;
  PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","AssetRegistry"});
 }
}
