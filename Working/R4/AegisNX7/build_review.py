"""Extend copies of the working review graphs; preserve the accepted review baseline."""
import unreal,json,traceback,sys
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');C=json.loads((Path(__file__).parent/'profile.json').read_text());O=R/C['evidence_directory'];B=C['output_namespace']+'/ReviewV2';OLD=C['existing_review_namespace'];L=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
result=dict(status='RUNNING',scope='R4 copies of existing review assets; controls and ground graph retained')
def require(ok,msg):
    if not ok:raise ValueError(msg)
def pins(n):return {str(p.get_pin_name()):p for p in n.list_all_pins()}
def pin(n,k):require(k in pins(n),'missing pin '+k+' in '+str(n.get_node_title())+' '+str(list(pins(n))));return pins(n)[k]
def wire(a,ap,b,bp):require(pin(a,ap).try_create_connection(pin(b,bp)),'connection '+ap+' '+bp)
def val(n,k,v):require(pin(n,k).set_pin_value(str(v)),'pin value '+k)
def call(g,cls,name):
    n=g.add_call_function_node('/Script/Engine.'+cls+':'+name);require(n,'function '+cls+'.'+name);return n
def action(g,name):
    n=g.create_node_from_name(name,unreal.Vector2D(),[]);require(n,'action '+name);return n
def duplicate(name,source):
    if unreal.EditorAssetLibrary.does_asset_exist(B+'/'+name):return unreal.load_asset(B+'/'+name)
    return T.duplicate_asset(name,B,unreal.load_asset(source))
try:
    if (O/'review_build.json').exists():
        completed=json.loads((O/'review_build.json').read_text())
        if completed.get('status')=='PASS' and completed.get('assets',{}).get('level')==B+'/L_AegisMovementReview':
            print('R4_REVIEW_ALREADY_BUILT; saved graphs unchanged');sys.exit(0)
    M=json.loads((O/'animation_library_manifest.json').read_text());require(M['status']=='PASS','bake not certified')
    def clip(name):
        matches=[x for x in M['entries'] if x['name']==name and x.get('bake_result')=='PASS' and '/Sources/InstalledMannequins/Anims/Unarmed/' in x['source_path']]
        require(len(matches)==1,'unarmed source clip resolution '+name);return unreal.load_asset(matches[0]['destination_path'])
    clips={k:clip(n) for k,n in [('Jump','MM_Jump'),('Fall','MM_Fall_Loop'),('Land','MM_Land')]};result['clips']={k:a.get_path_name() for k,a in clips.items()}
    bp=duplicate('BP_AegisMovementReviewCharacter',OLD+'/BP_AegisMovementReviewCharacter');abp=duplicate('ABP_AegisMovementReview',OLD+'/ABP_AegisMovementReview');gm=duplicate('BP_AegisMovementReviewGameMode',OLD+'/BP_AegisMovementReviewGameMode')
    ge=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph');ae=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'EventGraph');ag=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'AnimGraph')
    # Use pristine copies and save graph edits only after successful compilation.
    space=action(ge,'Input|KeyboardEvents|SpaceBar');jump=call(ge,'Character','Jump');stop=call(ge,'Character','StopJumping');wire(space,'Pressed',jump,'execute');wire(space,'Released',stop,'execute')
    for name,type_name,value in [('Airborne','bool','false'),('WasAirborne','bool','false'),('JumpStart','bool','false'),('Landing','bool','false'),('AirTime','real','0'),('LandTime','real','0')]:
        if name not in [str(x) for x in abp.list_member_variable_names(False)]:require(ae.add_member_variable(name,L.get_basic_type_by_name(type_name),value),'variable '+name)
    get=lambda name:ae.add_get_member_variable_node(name)
    setv=lambda name:ae.add_set_member_variable_node(name)
    update=ae.find_event_node('BlueprintUpdateAnimation');speed_set=next(n for n in ae.list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'Speed' in pins(n))
    pin(speed_set,'then').break_pin_links();owner=call(ae,'AnimInstance','TryGetPawnOwner');movement=call(ae,'Pawn','GetMovementComponent');fall=call(ae,'NavMovementComponent','IsFalling');wire(owner,'ReturnValue',movement,'self');wire(movement,'ReturnValue',fall,'self')
    airset=setv('Airborne');wire(speed_set,'then',airset,'execute');wire(fall,'ReturnValue',airset,'Airborne')
    add=call(ae,'KismetMathLibrary','Add_DoubleDouble');wire(get('AirTime'),'AirTime',add,'A');wire(update,'DeltaTimeX',add,'B');airselect=call(ae,'KismetMathLibrary','SelectFloat');wire(add,'ReturnValue',airselect,'A');val(airselect,'B',0);wire(get('Airborne'),'Airborne',airselect,'bPickA');airtime=setv('AirTime');wire(airset,'then',airtime,'execute');wire(airselect,'ReturnValue',airtime,'AirTime')
    notfall=call(ae,'KismetMathLibrary','Not_PreBool');wire(get('Airborne'),'Airborne',notfall,'A');justland=call(ae,'KismetMathLibrary','BooleanAND');wire(get('WasAirborne'),'WasAirborne',justland,'A');wire(notfall,'ReturnValue',justland,'B')
    subtract=call(ae,'KismetMathLibrary','Subtract_DoubleDouble');wire(get('LandTime'),'LandTime',subtract,'A');wire(update,'DeltaTimeX',subtract,'B');maximum=call(ae,'KismetMathLibrary','FMax');wire(subtract,'ReturnValue',maximum,'A');val(maximum,'B',0)
    landselect=call(ae,'KismetMathLibrary','SelectFloat');val(landselect,'A',clips['Land'].get_play_length());wire(maximum,'ReturnValue',landselect,'B');wire(justland,'ReturnValue',landselect,'bPickA');landtime=setv('LandTime');wire(airtime,'then',landtime,'execute');wire(landselect,'ReturnValue',landtime,'LandTime')
    landgreater=call(ae,'KismetMathLibrary','Greater_DoubleDouble');wire(get('LandTime'),'LandTime',landgreater,'A');val(landgreater,'B',0);landbool=call(ae,'KismetMathLibrary','BooleanAND');wire(landgreater,'ReturnValue',landbool,'A');wire(notfall,'ReturnValue',landbool,'B');landset=setv('Landing');wire(landtime,'then',landset,'execute');wire(landbool,'ReturnValue',landset,'Landing')
    velocity=call(ae,'Actor','GetVelocity');wire(owner,'ReturnValue',velocity,'self');breakv=call(ae,'KismetMathLibrary','BreakVector');wire(velocity,'ReturnValue',breakv,'InVec');rising=call(ae,'KismetMathLibrary','Greater_DoubleDouble');wire(breakv,'Z',rising,'A');val(rising,'B',0)
    early=call(ae,'KismetMathLibrary','Less_DoubleDouble');wire(get('AirTime'),'AirTime',early,'A');val(early,'B',clips['Jump'].get_play_length());earlyrising=call(ae,'KismetMathLibrary','BooleanAND');wire(early,'ReturnValue',earlyrising,'A');wire(rising,'ReturnValue',earlyrising,'B');startbool=call(ae,'KismetMathLibrary','BooleanAND');wire(earlyrising,'ReturnValue',startbool,'A');wire(get('Airborne'),'Airborne',startbool,'B');startset=setv('JumpStart');wire(landset,'then',startset,'execute');wire(startbool,'ReturnValue',startset,'JumpStart');was=setv('WasAirborne');wire(startset,'then',was,'execute');wire(get('Airborne'),'Airborne',was,'WasAirborne')
    root=next(n for n in ag.list_all_nodes() if n.get_class().get_name()=='AnimGraphNode_Root');ground=pin(root,'Result').list_connected_pins()[0];pin(root,'Result').break_pin_links()
    # Sequence properties are assigned explicitly; no ambiguous same-basename catalogue lookup.
    players={}
    for name,anim in clips.items():
        n=action(ag,"Animation|Sequences|Play'MM_Idle'");data=n.get_editor_property('node');data.set_editor_properties(dict(sequence=anim,loop_animation=name=='Fall'));n.set_editor_property('node',data);players[name]=n
    def blend(variable):
        n=action(ag,'Animation|Blends|BlendPosesbybool');data=n.get_editor_property('node');data.set_editor_property('child_upate_mode',unreal.BlendListChildUpdateMode.RESET_CHILD_ON_ACTIVATE);n.set_editor_property('node',data);val(n,'BlendTime_0',.1);val(n,'BlendTime_1',.1);wire(ag.add_get_member_variable_node(variable),variable,n,'bActiveValue');return n
    airblend=blend('JumpStart');wire(players['Jump'],'Pose',airblend,'BlendPose_0');wire(players['Fall'],'Pose',airblend,'BlendPose_1')
    landblend=blend('Landing');wire(players['Land'],'Pose',landblend,'BlendPose_0');require(ground.try_create_connection(pin(landblend,'BlendPose_1')),'retained ground connection')
    final=blend('Airborne');wire(airblend,'Pose',final,'BlendPose_0');wire(landblend,'Pose',final,'BlendPose_1');wire(final,'Pose',root,'Result')

    require(L.compile_blueprint(abp),'AnimBP compile');require(L.compile_blueprint(bp),'Character compile');cdo=unreal.get_default_object(bp.generated_class());cdo.mesh.set_anim_instance_class(abp.generated_class());cdo.character_movement.set_editor_property('jump_z_velocity',420)
    for a in [abp,bp,gm]:require(unreal.EditorAssetLibrary.save_loaded_asset(a,False),'save '+a.get_name())
    map_path=B+'/L_AegisMovementReview';require(unreal.EditorLevelLibrary.load_level(OLD+'/L_AegisMovementReview'),'load working level')
    E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);oldbp=unreal.load_asset(OLD+'/BP_AegisMovementReviewCharacter');actor=next(a for a in E.get_all_level_actors() if a.get_class()==oldbp.generated_class());transform=actor.get_actor_transform();E.destroy_actor(actor);pawn=E.spawn_actor_from_class(bp.generated_class(),transform.translation,transform.rotation.rotator());pawn.set_actor_scale3d(transform.scale3d);pawn.mesh.set_anim_instance_class(abp.generated_class());pawn.set_actor_label('Aegis R4 — WASD / mouse / Shift / Space')
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',gm.generated_class());require(unreal.EditorLoadingAndSavingUtils.save_map(world,map_path),'save review as R4 map')
    result.update(status='PASS',assets=dict(level=map_path,character=bp.get_path_name(),anim_blueprint=abp.get_path_name(),game_mode=gm.get_path_name()),controls='WASD / mouse / Shift run / Space jump',jump_velocity_cm_s=420,ground_graph='Existing speed-based idle/walk/run preserved',air_flow='IsFalling + rising velocity and sequence-duration guard: jump -> fall; airborne-to-ground edge: land for clip duration -> locomotion',original_review_assets_modified=False)
except Exception:result.update(status='FAIL',error=traceback.format_exc())
(O/'review_build.json').write_text(json.dumps(result,indent=2)+'\n');print('R4_REVIEW_BUILD',result['status'],result.get('error',''))
