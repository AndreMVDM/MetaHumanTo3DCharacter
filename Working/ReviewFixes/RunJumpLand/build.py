"""Isolated review correction: reserve planted landing for existing idle-speed range."""
import unreal,json,traceback,re
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/ReviewFixes/RunJumpLand';T=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.BlueprintEditorLibrary
subject_filter=re.search(r'-BuildSubject=(\w+)',unreal.SystemLibrary.get_command_line()).group(1)
D=dict(status='RUNNING',subjects={},correction='Landing = original LandTime>0 AND !Airborne AND Speed<=5; grounded speed boundary matches retained idle/walk selector. Existing 0.1 s air/ground and landing blends retained.',animation_rebakes=0)
def require(x,msg):
    if not x:raise ValueError(msg)
def pins(n):return {str(p.get_pin_name()):p for p in n.list_all_pins()}
def p(n,key):return pins(n)[key]
def wire(a,ap,b,bp):require(p(a,ap).try_create_connection(p(b,bp)),'wire '+ap+' -> '+bp)
try:
    for subject,old,name in [('Female','/Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/ReviewV1','FemaleBody'),('Aegis','/Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/ReviewV2','Aegis')]:
        if subject!=subject_filter:continue
        B='/Game/MetaHumanTo3DCharacter/ReviewFixes/RunJumpLand/'+subject
        existing=unreal.EditorAssetLibrary.list_assets(B,True,False);require(not existing or len(existing)==3,'refuse overwrite completed or unrelated bugfix assets')
        def copy(prefix):return unreal.load_asset(B+'/'+prefix+name+'MovementReview'+('Character' if prefix=='BP_' else '')) if existing else T.duplicate_asset(prefix+name+'MovementReview'+('Character' if prefix=='BP_' else ''),B,unreal.load_asset(old+'/'+prefix+name+'MovementReview'+('Character' if prefix=='BP_' else '')))
        abp=copy('ABP_');bp=copy('BP_');gm=unreal.load_asset(B+'/BP_'+name+'MovementReviewGameMode') if existing else T.duplicate_asset('BP_'+name+'MovementReviewGameMode',B,unreal.load_asset(old+'/BP_'+name+'MovementReviewGameMode'))
        graph=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'EventGraph');sets=[n for n in graph.list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'Landing' in pins(n)];require(len(sets)==1,'unique Landing setter');setter=sets[0];old_input=p(setter,'Landing').list_connected_pins();require(len(old_input)==1,'unique original landing predicate')
        # Verify the existing grounded selector's exact boundary before reusing it.
        ag=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'AnimGraph');speed_guards=[n for n in ag.list_all_nodes() if ' > ' in str(n.get_node_title()) and 'B' in pins(n) and p(n,'B').get_pin_value()=='5'];require(len(speed_guards)==1,'existing walk boundary must be 5')
        less=graph.add_call_function_node('/Script/Engine.KismetMathLibrary:LessEqual_DoubleDouble');speed=graph.add_get_member_variable_node('Speed');wire(speed,'Speed',less,'A');require(p(less,'B').set_pin_value('5'),'idle threshold')
        both=graph.add_call_function_node('/Script/Engine.KismetMathLibrary:BooleanAND');require(old_input[0].try_create_connection(p(both,'A')),'retain original predicate');wire(less,'ReturnValue',both,'B');p(setter,'Landing').break_pin_links();wire(both,'ReturnValue',setter,'Landing')
        require(L.compile_blueprint(abp),'ABP compile');require(L.compile_blueprint(bp),'BP compile');cdo=unreal.get_default_object(bp.generated_class());cdo.mesh.set_anim_instance_class(abp.generated_class());require(L.compile_blueprint(gm),'GM compile')
        for a in [abp,bp,gm]:require(unreal.EditorAssetLibrary.save_loaded_asset(a,False),'save '+a.get_name())
        require(unreal.EditorLevelLibrary.load_level(old+'/L_'+name+'MovementReview'),'load original review map');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);oldbp=unreal.load_asset(old+'/BP_'+name+'MovementReviewCharacter');actors=[a for a in E.get_all_level_actors() if a.get_class()==oldbp.generated_class()];require(len(actors)==1,'unique placed character');actor=actors[0];tr=actor.get_actor_transform();E.destroy_actor(actor);pawn=E.spawn_actor_from_class(bp.generated_class(),tr.translation,tr.rotation.rotator());pawn.set_actor_scale3d(tr.scale3d);pawn.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0);pawn.mesh.set_anim_instance_class(abp.generated_class());pawn.set_actor_label(name+' — Run Jump Land Fix — WASD / Shift / Space')
        world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',gm.generated_class());MAP=B+'/L_'+name+'MovementReview';require(unreal.EditorLoadingAndSavingUtils.save_map(world,MAP),'save isolated map')
        D['subjects'][subject]=dict(level=MAP,character=bp.get_path_name(),anim_blueprint=abp.get_path_name(),game_mode=gm.get_path_name(),mesh=pawn.mesh.get_skeletal_mesh_asset().get_path_name(),stature_cm=2*pawn.mesh.get_skeletal_mesh_asset().get_bounds().box_extent.z,original_predicate_node=old_input[0].get_owning_node().get_path_name(),speed_guard=5)
    D['status']='PASS'
except Exception:D.update(status='FAIL',error=traceback.format_exc())
(O/('build_'+subject_filter+'.json')).write_text(json.dumps(D,indent=2)+'\n');print('SKID_BUILD',D['status'],D.get('error',''))


