"""Default profile-driven playable-scaffold generator; no bake or subject logic."""
import math
import unreal
VERSION='phase4f.rigged-playable-locomotion/1.0.0'
DEFAULTS={'IdleSpeedThreshold':5.0,'WalkSpeed':300.0,'RunSpeed':600.0,'LandingBlendDuration':0.1}
ROLES=('Idle','Walk','Run','Jump','Fall','Land')
def require(ok,message):
    if not ok:raise ValueError(message)
def pins(n):return {str(p.get_pin_name()):p for p in n.list_all_pins()}
def pin(n,k):require(k in pins(n),'missing pin '+k+' on '+str(n.get_node_title()));return pins(n)[k]
def wire(a,ap,b,bp):require(pin(a,ap).try_create_connection(pin(b,bp)),'connect '+ap+' -> '+bp)
def source(n,k):
    connected=pin(n,k).list_connected_pins();require(len(connected)==1,'unique source '+k);return connected[0].get_owning_node()
def variable_blend(graph,variable):
    matches=[n for n in graph.list_all_nodes() if n.get_class().get_name()=='AnimGraphNode_BlendListByBool' and variable in pins(source(n,'bActiveValue'))]
    require(len(matches)==1,'unique blend '+variable);return matches[0]
def inspect_scaffold(abp):
    ag=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'AnimGraph');air=variable_blend(ag,'JumpStart');land=variable_blend(ag,'Landing');final=variable_blend(ag,'Airborne')
    guards=[n for n in ag.list_all_nodes() if ' > ' in str(n.get_node_title()) and 'B' in pins(n) and 'Speed' in pins(source(n,'A'))]
    require(len(guards)==2,'two ground speed selectors');guards.sort(key=lambda n:float(pin(n,'B').get_pin_value()));moving,running=guards
    require(float(pin(moving,'B').get_pin_value())==5 and float(pin(running,'B').get_pin_value())==450,'unsupported scaffold defaults')
    def driven_blend(guard):
        links=pin(guard,'ReturnValue').list_connected_pins();require(len(links)==1,'unique speed blend');return links[0].get_owning_node()
    moveblend=driven_blend(moving);runblend=driven_blend(running)
    players={'Idle':source(moveblend,'BlendPose_1'),'Walk':source(runblend,'BlendPose_1'),'Run':source(runblend,'BlendPose_0'),'Jump':source(air,'BlendPose_0'),'Fall':source(air,'BlendPose_1'),'Land':source(land,'BlendPose_0')}
    require(all(n.get_class().get_name()=='AnimGraphNode_SequencePlayer' for n in players.values()),'six direct semantic sequence players required')
    require(len({n.get_path_name() for n in players.values()})==6,'unique role players');require(source(land,'BlendPose_1')==moveblend,'land/ground topology');require(source(final,'BlendPose_1')==land,'air/land topology')
    eg=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'EventGraph');setter=next(n for n in eg.list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'Landing' in pins(n));predicate=source(setter,'Landing')
    require('A' in pins(predicate) and 'B' in pins(predicate),'legacy landing predicate')
    timer=source(predicate,'A');not_air=source(predicate,'B')
    require(' > ' in str(timer.get_node_title()) and 'LandTime' in pins(source(timer,'A')) and not pin(timer,'B').list_connected_pins() and float(pin(timer,'B').get_pin_value() or '0')==0,'unmodified legacy timer guard required')
    require('Airborne' in pins(source(not_air,'A')),'unmodified legacy grounded guard required; corrected/generated scaffolds cannot be re-promoted')
    return dict(graph=ag,players=players,moving=moving,running=running,land=land,final=final)
def generate(config):
    """The sole supported v1 entry: destination binding + policy installation before save."""
    settings=DEFAULTS|config.get('locomotion',{})
    require(set(settings)==set(DEFAULTS),'unknown locomotion setting')
    require(all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in settings.values()),'finite numeric settings required')
    require(0<=settings['IdleSpeedThreshold']<settings['WalkSpeed']<settings['RunSpeed'],'ordered locomotion speeds required');require(settings['LandingBlendDuration']>=0,'nonnegative blend duration')
    B=config['output_namespace'];require(B.startswith('/Game/') and not B.endswith('/'),'new Game output namespace required');require(not unreal.EditorAssetLibrary.list_assets(B,True,False),'output namespace must be empty; no overwrite')
    scaffold=config['scaffold'];require(all(not v.split('.')[0].startswith(B+'/') for v in scaffold.values()),'scaffold/output overlap')
    require(set(config['animations'])==set(ROLES),'all six destination animation roles required')
    mesh=unreal.load_asset(config['destination_mesh']);require(isinstance(mesh,unreal.SkeletalMesh),'destination SkeletalMesh required')
    clips={r:unreal.load_asset(config['animations'][r]) for r in ROLES};require(all(isinstance(a,unreal.AnimSequence) and a.get_editor_property('skeleton')==mesh.skeleton for a in clips.values()),'destination native sequences with identical skeleton required')
    originals={k:unreal.load_asset(v) for k,v in scaffold.items()};require(all(originals.values()),'missing scaffold');require(set(originals)=={'character','anim_blueprint','game_mode','level'},'four scaffold roles required')
    layout=inspect_scaffold(originals['anim_blueprint']);T=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.BlueprintEditorLibrary
    # Unfixed legacy scaffold is input only. The policy is installed unconditionally,
    # so callers cannot accidentally opt into the old full-clip moving hold.
    abp=T.duplicate_asset('ABP_PlayableLocomotion',B,originals['anim_blueprint']);bp=T.duplicate_asset('BP_PlayableCharacter',B,originals['character']);gm=T.duplicate_asset('BP_PlayableGameMode',B,originals['game_mode']);layout=inspect_scaffold(abp);abp.set_editor_property('target_skeleton',mesh.skeleton)
    for role,n in layout['players'].items():
        data=n.get_editor_property('node');data.set_editor_property('sequence',clips[role]);n.set_editor_property('node',data)
    ae=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'EventGraph');ge=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph');real=L.get_basic_type_by_name('real')
    # Keep legacy Speed telemetry intact; precise configurable boundaries use
    # continuous horizontal speed directly from the existing VSizeXY calculation.
    require(ae.add_member_variable('HorizontalSpeed',real,'0'),'horizontal speed variable')
    old_speed_set=next(n for n in ae.list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'Speed' in pins(n))
    outgoing=pin(old_speed_set,'then').list_connected_pins()[0];trunc=source(old_speed_set,'Speed');require(str(trunc.get_node_title())=='Truncate','expected historical speed conversion');length_pin=pin(trunc,'A').list_connected_pins()[0]
    speed_set=ae.add_set_member_variable_node('HorizontalSpeed');pin(old_speed_set,'then').break_pin_links();wire(old_speed_set,'then',speed_set,'execute');require(pin(speed_set,'then').try_create_connection(outgoing),'speed continuation');require(length_pin.try_create_connection(pin(speed_set,'HorizontalSpeed')),'continuous horizontal speed')
    for graph,name,value in [(ae,'IdleSpeedThreshold',settings['IdleSpeedThreshold']),(ae,'RunSpeedThreshold',(settings['WalkSpeed']+settings['RunSpeed'])/2),(ae,'LandingBlendDuration',settings['LandingBlendDuration']),(ge,'WalkSpeed',settings['WalkSpeed']),(ge,'RunSpeed',settings['RunSpeed'])]:
        require(graph.add_member_variable(name,real,str(value)),'add config '+name)
    for graph in [ae,ge]:require(graph.add_member_variable('LocomotionTemplateVersion',L.get_basic_type_by_name('string'),VERSION),'record template version')
    # Ground selection and landing support share exactly the same idle boundary.
    ag=layout['graph']
    for guard,var in [(layout['moving'],'IdleSpeedThreshold'),(layout['running'],'RunSpeedThreshold')]:
        output=pin(guard,'ReturnValue').list_connected_pins()[0];old_get=source(guard,'A');greater=ag.add_call_function_node('/Script/Engine.KismetMathLibrary:Greater_DoubleDouble');wire(ag.add_get_member_variable_node('HorizontalSpeed'),'HorizontalSpeed',greater,'A');wire(ag.add_get_member_variable_node(var),var,greater,'B');require(pin(greater,'ReturnValue').try_create_connection(output),'configured ground selector');ag.remove_nodes([guard,old_get])
    for blend in [layout['land'],layout['final']]:
        for key in ['BlendTime_0','BlendTime_1']:wire(ag.add_get_member_variable_node('LandingBlendDuration'),'LandingBlendDuration',blend,key)
    nodes=ae.list_all_nodes();setter=next(n for n in nodes if n.get_class().get_name()=='K2Node_VariableSet' and 'Landing' in pins(n));old_input=pin(setter,'Landing').list_connected_pins();require(len(old_input)==1,'original landing predicate')
    less=ae.add_call_function_node('/Script/Engine.KismetMathLibrary:LessEqual_DoubleDouble');wire(ae.add_get_member_variable_node('HorizontalSpeed'),'HorizontalSpeed',less,'A');wire(ae.add_get_member_variable_node('IdleSpeedThreshold'),'IdleSpeedThreshold',less,'B');both=ae.add_call_function_node('/Script/Engine.KismetMathLibrary:BooleanAND');require(old_input[0].try_create_connection(pin(both,'A')),'retain original landing predicate');wire(less,'ReturnValue',both,'B');pin(setter,'Landing').break_pin_links();wire(both,'ReturnValue',setter,'Landing')
    # Bind existing guards to destination clip durations. Never assume template
    # Jump/Land lengths also describe the configured destination clips.
    rebound={'Jump':0,'Land':0}
    for n in nodes:
        if 'bPickA' in pins(n) and 'A' in pins(n) and pin(n,'A').get_pin_value() and not pin(n,'A').list_connected_pins():
            outputs=pin(n,'ReturnValue').list_connected_pins()
            if any('LandTime' in pins(p.get_owning_node()) for p in outputs):
                require(pin(n,'A').set_pin_value(str(clips['Land'].get_play_length())),'Land duration');rebound['Land']+=1
        if ' < ' in str(n.get_node_title()) and 'A' in pins(n) and 'AirTime' in pins(source(n,'A')):
            require(pin(n,'B').set_pin_value(str(clips['Jump'].get_play_length())),'Jump duration');rebound['Jump']+=1
    require(rebound=={'Jump':1,'Land':1},'unique destination timing guards required')
    speed_sets=[n for n in ge.list_all_nodes() if n.get_class().get_name()=='K2Node_VariableSet' and 'MaxWalkSpeed' in pins(n)];require(len(speed_sets)==2,'two Shift speed setters')
    for n in speed_sets:
        old_speed=float(pin(n,'MaxWalkSpeed').get_pin_value());require(old_speed in [300,600],'unsupported scaffold movement speeds');var='WalkSpeed' if old_speed==300 else 'RunSpeed';wire(ge.add_get_member_variable_node(var),var,n,'MaxWalkSpeed')
    require(L.compile_blueprint(abp),'AnimBP compilation');require(L.compile_blueprint(bp),'Character compilation');require(L.compile_blueprint(gm),'GameMode compilation')
    cdo=unreal.get_default_object(bp.generated_class());original_cdo=unreal.get_default_object(originals['character'].generated_class());height=2*mesh.get_bounds().box_extent.z;template_height=2*original_cdo.mesh.get_skeletal_mesh_asset().get_bounds().box_extent.z;half=height/2;radius=min(original_cdo.capsule_component.get_unscaled_capsule_radius(),height*.19)
    cdo.mesh.set_skeletal_mesh_asset(mesh);cdo.mesh.set_anim_instance_class(abp.generated_class());cdo.mesh.set_editor_property('relative_location',unreal.Vector(0,0,-half));cdo.capsule_component.set_capsule_size(radius,half,True);cdo.character_movement.set_editor_property('max_walk_speed',settings['WalkSpeed']);cdo.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0)
    for arm in cdo.get_components_by_class(unreal.SpringArmComponent):
        arm.set_editor_property('target_arm_length',arm.target_arm_length*height/template_height);tr=arm.get_editor_property('relative_location');arm.set_editor_property('relative_location',tr*(height/template_height))
    for a in [abp,bp,gm]:
        unreal.EditorAssetLibrary.set_metadata_tag(a,'LocomotionTemplateVersion',VERSION);require(unreal.EditorAssetLibrary.save_loaded_asset(a,False),'save output '+a.get_name())
    require(unreal.EditorLevelLibrary.load_level(scaffold['level'].split('.')[0]),'load scaffold level');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);characters=[a for a in E.get_all_level_actors() if isinstance(a,unreal.Character)];require(len(characters)==1 and characters[0].get_class()==originals['character'].generated_class(),'one scaffold character required');E.destroy_actor(characters[0]);pawn=E.spawn_actor_from_class(bp.generated_class(),unreal.Vector(0,0,half+2));pawn.set_actor_scale3d(unreal.Vector(1,1,1));pawn.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0);pawn.mesh.set_anim_instance_class(abp.generated_class());pawn.set_actor_label('Generated playable review — WASD / mouse / Shift / Space')
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',gm.generated_class());MAP=B+'/L_PlayableReview';require(unreal.EditorLoadingAndSavingUtils.save_map(world,MAP),'save generated map')
    return dict(status='PASS',version=VERSION,source_scaffold=scaffold,source_scaffold_is_read_only=True,settings=settings,run_selection_threshold=(settings['WalkSpeed']+settings['RunSpeed'])/2,animations=config['animations'],destination_mesh=mesh.get_path_name(),assets=dict(level=MAP,character=bp.get_path_name(),anim_blueprint=abp.get_path_name(),game_mode=gm.get_path_name()),stature_cm=height,capsule_half_height_cm=half,animation_rebakes=0,landing_rule_installed_during_generation=True,post_generation_manual_edits=0)

