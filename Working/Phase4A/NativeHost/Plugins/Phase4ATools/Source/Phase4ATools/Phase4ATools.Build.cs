using UnrealBuildTool;
public class Phase4ATools : ModuleRules {
 public Phase4ATools(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","GeometryFramework","GeometryCore","GeometryAlgorithms","DynamicMesh","MeshDescription","SkeletalMeshDescription","AssetRegistry"});
 }
}
