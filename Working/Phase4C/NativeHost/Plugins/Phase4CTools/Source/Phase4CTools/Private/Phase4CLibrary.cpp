#include "Phase4CLibrary.h"
#include "Modules/ModuleManager.h"
#include "DNAUtils.h"
#include "MetaHumanCoreTechMeshUtils.h"
#include "Serialization/JsonSerializer.h"
#include "Misc/Paths.h"
IMPLEMENT_MODULE(FDefaultModuleImpl, Phase4CTools)
static TArray<TSharedPtr<FJsonValue>> XYZ(const FVector& V) {
 return {MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y),MakeShared<FJsonValueNumber>(V.Z)};
}
FString UPhase4CLibrary::InspectPosedDNA(const FString& FilePath) {
 FString Full=FPaths::ConvertRelativePathToFull(FilePath);FPaths::NormalizeFilename(Full);FPaths::CollapseRelativeDirectories(Full);
 if(!Full.StartsWith(TEXT("E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4C/Donor/"))) return TEXT("{\"error\":\"outside Phase4C donor scope\"}");
 auto R=LoadDNAFromFile(Full,FDNAConfig::Source(ECoordinateSystemTransformPolicy::Transform));
 if(!R.IsValid()) return TEXT("{\"error\":\"DNA load failed\"}");
 auto World=UE::MetaHuman::GetJointWorldTranslations(R);
 if(World.Num()!=R->GetJointCount()) return TEXT("{\"error\":\"public joint extraction count mismatch\"}");
 auto Root=MakeShared<FJsonObject>(); Root->SetStringField(TEXT("api"),TEXT("LoadDNAFromFile(Source/Transform) + IDNAReader + UE::MetaHuman::GetJointWorldTranslations"));
 Root->SetStringField(TEXT("space"),TEXT("DNA source: +X left +Y up +Z front; world_cm swaps Y/Z to UE"));
 Root->SetNumberField(TEXT("translation_unit_enum"),(int)R->GetTranslationUnit());
 Root->SetNumberField(TEXT("rotation_unit_enum"),(int)R->GetRotationUnit());
 TArray<TSharedPtr<FJsonValue>> Joints;
 for(uint16 i=0;i<R->GetJointCount();++i) {
  auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("index"),i);J->SetStringField(TEXT("name"),R->GetJointName(i));
  J->SetNumberField(TEXT("parent_index"),R->GetJointParentIndex(i));J->SetArrayField(TEXT("world_cm"),XYZ(FVector(World[i])));
  J->SetArrayField(TEXT("local_translation_source_cm"),XYZ(R->GetNeutralJointTranslation(i)));
  J->SetArrayField(TEXT("local_rotation_source_deg"),XYZ(R->GetNeutralJointRotation(i)));
  Joints.Add(MakeShared<FJsonValueObject>(J));
 }
 Root->SetArrayField(TEXT("joints"),Joints);
 TArray<TSharedPtr<FJsonValue>> Meshes;
 // Only LOD0 surface, exposed through the public geometry reader; no model matrices.
 for(uint16 mi:R->GetMeshIndicesForLOD(0)) {
  auto M=MakeShared<FJsonObject>();M->SetStringField(TEXT("name"),R->GetMeshName(mi));M->SetNumberField(TEXT("index"),mi);
  TArray<TSharedPtr<FJsonValue>> V,F;
  for(uint32 vi=0;vi<R->GetVertexPositionCount(mi);++vi) {auto P=R->GetVertexPosition(mi,vi);V.Add(MakeShared<FJsonValueArray>(XYZ(FVector(P.X,P.Z,P.Y))));}
  for(uint32 fi=0;fi<R->GetFaceCount(mi);++fi) {
   TArray<TSharedPtr<FJsonValue>> Face;
   for(uint32 li:R->GetFaceVertexLayoutIndices(mi,fi)) Face.Add(MakeShared<FJsonValueNumber>(R->GetVertexLayout(mi,li).Position));
   F.Add(MakeShared<FJsonValueArray>(Face));
  }
  M->SetArrayField(TEXT("vertices_cm"),V);M->SetArrayField(TEXT("faces"),F);Meshes.Add(MakeShared<FJsonValueObject>(M));
 }
 Root->SetArrayField(TEXT("meshes_lod0"),Meshes);
 FString Out;FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Out));return Out;
}
