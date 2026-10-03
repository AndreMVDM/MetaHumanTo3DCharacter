import unreal,json,traceback
from pathlib import Path
O=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/HumanReview/AegisMovement')
B='/Game/MetaHumanTo3DCharacter/HumanReview/AegisMovement'
A='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial'
T=unreal.AssetToolsHelpers.get_asset_tools()
def create(name,cls,factory):
    return unreal.load_asset(B+'/'+name) if unreal.EditorAssetLibrary.does_asset_exist(B+'/'+name) else T.create_asset(name,B,cls,factory)
result={}
try:
    f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Character)
    bp=create('BP_AegisMovementReviewCharacter',unreal.Blueprint,f)
    af=unreal.AnimBlueprintFactory();af.set_editor_property('target_skeleton',unreal.load_asset(A+'/Character/SKEL_Destination'))
    abp=create('ABP_AegisMovementReview',unreal.AnimBlueprint,af)
    result['graphs']={x.get_name():[str(n) for n in unreal.BlueprintEditorLibrary.list_graph_names(x)] for x in [bp,abp]}
    result['nodes']={}
    for obj,graph in [(bp,'EventGraph'),(abp,'AnimGraph'),(abp,'EventGraph')]:
        e=unreal.BlueprintGraphEditor.get_graph_editor_by_name(obj,graph)
        nodes=list(e.list_available_nodes([]))
        result['nodes'][obj.get_name()+'/'+graph]=[n for n in nodes if any(x in str(n).lower() for x in ['input','keyboard','tick','sequence','blend','updateanimation','velocity','pawnowner'])]
        result['existing_'+obj.get_name()+'/'+graph]=[dict(title=unreal.BlueprintEditorLibrary.get_node_title(n),cls=n.get_class().get_name(),pins=[str(p.get_pin_name()) for p in n.list_input_pins()+n.list_output_pins()]) for n in e.list_all_nodes()]
    result['classes']={n:hasattr(unreal,n) for n in ['EnhancedInputLocalPlayerSubsystem','InputMappingContextFactory','InputActionFactory','AnimGraphNode_SequencePlayer']}
    result['status']='PASS'
    for x in [bp,abp]:unreal.EditorAssetLibrary.save_loaded_asset(x,False)
except Exception:result.update(status='FAIL',error=traceback.format_exc())
(O/'api_probe.json').write_text(json.dumps(result,indent=2)+'\n')
