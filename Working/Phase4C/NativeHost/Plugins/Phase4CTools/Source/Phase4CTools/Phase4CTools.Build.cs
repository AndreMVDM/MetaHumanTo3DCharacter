using UnrealBuildTool;
public class Phase4CTools : ModuleRules {
 public Phase4CTools(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","Json","RigLogicModule","MetaHumanCoreTechLib"});
 }
}
