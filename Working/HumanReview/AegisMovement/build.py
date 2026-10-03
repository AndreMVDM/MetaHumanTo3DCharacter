"""Review-local playable Character and three-clip AnimBP; accepted assets read only."""
import unreal,json,traceback
from pathlib import Path
O=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/HumanReview/AegisMovement')
B='/Game/MetaHumanTo3DCharacter/HumanReview/AegisMovement'
A='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial'
T=unreal.AssetToolsHelpers.get_asset_tools(); L=unreal.BlueprintEditorLibrary
result={'status':'RUNNING','assets':{},'graph_nodes':[]}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def create(name,cls,factory):
    return unreal.load_asset(B+'/'+name) if unreal.EditorAssetLibrary.does_asset_exist(B+'/'+name) else T.create_asset(name,B,cls,factory)
def pins(n):return {str(p.get_pin_name()):p for p in n.list_all_pins()}
def pin(n,name):
    ps=pins(n);require(name in ps,str(n.get_node_title())+' missing '+name+': '+str(list(ps)));return ps[name]
def wire(a,ap,b,bp):require(pin(a,ap).try_create_connection(pin(b,bp)),'connect '+ap+' -> '+bp)
def val(n,p,v):require(pin(n,p).set_pin_value(str(v)),'default '+p+' '+str(v))
def call(g,cls,name):
    n=g.add_call_function_node('/Script/Engine.'+cls+':'+name)
    require(n is not None,'native function '+cls+'.'+name);return n
def node(g,name):
    n=g.create_node_from_name(name,unreal.Vector2D(),[])
    require(n is not None,'catalogue node '+name);return n
def compile(bp):
    require(L.compile_blueprint(bp),'compile '+bp.get_name())
    require(str(bp.get_editor_property('status'))!='<BlueprintStatus.BS_ERROR: 1>','blueprint errors')
    unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
try:
    f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Character)
    bp=create('BP_AegisMovementReviewCharacter',unreal.Blueprint,f)
    af=unreal.AnimBlueprintFactory();af.set_editor_property('target_skeleton',unreal.load_asset(A+'/Character/SKEL_Destination'))
    abp=create('ABP_AegisMovementReview',unreal.AnimBlueprint,af)
    # Rebuild only these newly authored review-local graphs on a failed build retry.
    ge=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    ae=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'EventGraph')
    ag=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'AnimGraph')
    for e in [ge,ae,ag]:
        e.remove_nodes([n for n in e.list_all_nodes() if n.get_class().get_name() not in ['AnimGraphNode_Root','K2Node_Event']])
    for name in ['WDown','SDown','ADown','DDown']:
        if name not in [str(x) for x in bp.list_member_variable_names(False)]:ge.add_member_variable(name,L.get_basic_type_by_name('bool'),'false')
    if 'Speed' not in [str(x) for x in abp.list_member_variable_names(False)]:ae.add_member_variable('Speed',L.get_basic_type_by_name('double'),'0')
    # Input lives only in this pawn, independent of global project mappings.
    for key in ['W','S','A','D']:
        ev=node(ge,'Input|KeyboardEvents|'+key)
        for out,value in [('Pressed','true'),('Released','false')]:
            st=ge.add_set_member_variable_node(key+'Down');val(st,key+'Down',value);wire(ev,out,st,'execute')
    cm=ge.add_get_member_variable_node('CharacterMovement','/Script/Engine.Character')
    shift=node(ge,'Input|KeyboardEvents|LeftShift')
    for out,speed in [('Pressed','600'),('Released','300')]:
        st=ge.add_set_member_variable_node('MaxWalkSpeed','/Script/Engine.CharacterMovementComponent')
        wire(cm,'CharacterMovement',st,'self');val(st,'MaxWalkSpeed',speed);wire(shift,out,st,'execute')
    # Mouse axes drive ordinary controller rotation and the spring-arm camera.
    for axis,fn,sign in [('MouseX','AddControllerYawInput','1'),('MouseY','AddControllerPitchInput','-1')]:
        ev=node(ge,'Input|MouseEvents|'+axis);mul=call(ge,'KismetMathLibrary','Multiply_DoubleDouble')
        wire(ev,'AxisValue',mul,'A');val(mul,'B',str(float(sign)*.5))
        look=call(ge,'Pawn',fn);wire(ev,'then',look,'execute');wire(mul,'ReturnValue',look,'Val')
    # Camera-relative horizontal movement; CharacterMovement handles acceleration.
    tick=ge.find_event_node('ReceiveTick')
    control=call(ge,'Pawn','GetControlRotation');br=call(ge,'KismetMathLibrary','BreakRotator');mr=call(ge,'KismetMathLibrary','MakeRotator')
    wire(control,'ReturnValue',br,'InRot');wire(br,'Yaw',mr,'Yaw');val(mr,'Pitch','0');val(mr,'Roll','0')
    prev=tick;prevpin='then'
    for plus,minus,direction in [('W','S','GetForwardVector'),('D','A','GetRightVector')]:
        values=[]
        for key in [plus,minus]:
            get=ge.add_get_member_variable_node(key+'Down');conv=call(ge,'KismetMathLibrary','Conv_BoolToDouble');wire(get,key+'Down',conv,'InBool');values.append(conv)
        sub=call(ge,'KismetMathLibrary','Subtract_DoubleDouble');wire(values[0],'ReturnValue',sub,'A');wire(values[1],'ReturnValue',sub,'B')
        vec=call(ge,'KismetMathLibrary',direction);wire(mr,'ReturnValue',vec,'InRot')
        move=call(ge,'Pawn','AddMovementInput');wire(prev,prevpin,move,'execute');wire(vec,'ReturnValue',move,'WorldDirection');wire(sub,'ReturnValue',move,'ScaleValue');prev=move
    # Speed-based animation selection, from the actual owning pawn velocity.
    update=ae.find_event_node('BlueprintUpdateAnimation');owner=call(ae,'AnimInstance','TryGetPawnOwner');velocity=call(ae,'Actor','GetVelocity');length=call(ae,'KismetMathLibrary','VSizeXY');st=ae.add_set_member_variable_node('Speed')
    wire(owner,'ReturnValue',velocity,'self');wire(velocity,'ReturnValue',length,'A');wire(length,'ReturnValue',st,'Speed');wire(update,'then',st,'execute')
    clips={role:unreal.load_asset(A+'/Animations/'+name) for role,name in [('Idle','MM_Idle'),('Walk','MF_Walk_Fwd'),('Run','MM_Run_Fwd')]}
    choices=list(ag.list_available_nodes([]))
    result['sequence_catalogue']=[x for x in choices if any(c.get_name() in x for c in clips.values())]
    players={}
    for role,anim in clips.items():
        candidates=[x for x in result['sequence_catalogue'] if x.endswith("|Play'"+anim.get_name()+"'")]
        require(len(candidates)==1,'sequence action '+role+' '+str(candidates))
        players[role]=node(ag,candidates[0])
        result['graph_nodes'].append(dict(role=role,pins=list(pins(players[role])),type=players[role].get_class().get_name()))
    moving=node(ag,'Animation|Blends|BlendPosesbybool');running=node(ag,'Animation|Blends|BlendPosesbybool')
    result['graph_nodes'].append(dict(blend_pins=list(pins(moving))))
    for blend,threshold in [(moving,5),(running,450)]:
        speed=ag.add_get_member_variable_node('Speed');gt=call(ag,'KismetMathLibrary','Greater_DoubleDouble');wire(speed,'Speed',gt,'A');val(gt,'B',threshold);wire(gt,'ReturnValue',blend,'bActiveValue')
        val(blend,'BlendTime_0','0.15');val(blend,'BlendTime_1','0.15')
    wire(players['Run'],'Pose',running,'BlendPose_0');wire(players['Walk'],'Pose',running,'BlendPose_1')
    wire(running,'Pose',moving,'BlendPose_0');wire(players['Idle'],'Pose',moving,'BlendPose_1')
    root=next(n for n in ag.list_all_nodes() if n.get_class().get_name()=='AnimGraphNode_Root');wire(moving,'Pose',root,'Result')
    compile(abp);compile(bp)
    cdo=unreal.get_default_object(bp.generated_class());mesh=unreal.load_asset(A+'/Character/SK_Destination')
    cdo.capsule_component.set_capsule_size(34,90)
    cdo.mesh.set_skeletal_mesh_asset(mesh);cdo.mesh.set_editor_properties(dict(relative_location=unreal.Vector(0,0,-90),relative_rotation=unreal.Rotator(pitch=0,yaw=-90,roll=0),relative_scale3d=unreal.Vector(1,1,1)));cdo.mesh.set_anim_instance_class(abp.generated_class())
    cdo.set_editor_property('use_controller_rotation_yaw',False)
    cdo.character_movement.set_editor_properties(dict(orient_rotation_to_movement=True,max_walk_speed=300,rotation_rate=unreal.Rotator(pitch=0,yaw=540,roll=0),max_acceleration=1500,braking_deceleration_walking=1500))
    cdo.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0)
    # Add review-local spring arm/camera, leaving the accepted mesh intact.
    ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
    handles=ss.k2_gather_subobject_data_for_blueprint(bp);rh=handles[0]
    def component(name,cls,parent):
        current=ss.k2_gather_subobject_data_for_blueprint(bp)
        for h in current:
            d=lib.get_data(h)
            if str(lib.get_variable_name(d))==name:return h,lib.get_object_for_blueprint(d,bp)
        h,err=ss.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=parent,new_class=cls,blueprint_context=bp))
        require(lib.is_handle_valid(h),'add component '+name+' '+str(err));ss.rename_subobject(h,name);ss.rename_subobject_member_variable(bp,h,name)
        return h,lib.get_object_for_blueprint(lib.get_data(h),bp)
    armh,arm=component('ReviewSpringArm',unreal.SpringArmComponent,rh)
    arm.set_editor_properties(dict(target_arm_length=400,use_pawn_control_rotation=True,do_collision_test=True,target_offset=unreal.Vector()))
    arm.set_editor_properties(dict(relative_location=unreal.Vector(0,0,20),relative_rotation=unreal.Rotator(pitch=-10,yaw=0,roll=0)))
    _,camera=component('ReviewCamera',unreal.CameraComponent,armh);camera.set_editor_property('use_pawn_control_rotation',False)
    camera.set_editor_property('field_of_view',75)
    compile(bp)
    gf=unreal.BlueprintFactory();gf.set_editor_property('parent_class',unreal.GameModeBase)
    gm=create('BP_AegisMovementReviewGameMode',unreal.Blueprint,gf);compile(gm)
    unreal.get_default_object(gm.generated_class()).set_editor_property('default_pawn_class',None);unreal.EditorAssetLibrary.save_loaded_asset(gm,False)
    map_path=B+'/L_AegisMovementReview';require(not unreal.EditorAssetLibrary.does_asset_exist(map_path),'review map already exists; refuse replacement')
    require(unreal.EditorLevelLibrary.new_level(map_path),'create level')
    E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor=E.spawn_actor_from_class(bp.generated_class(),unreal.Vector(0,0,92));actor.set_actor_label('Aegis — WASD / mouse / Shift run')
    actor.set_actor_scale3d(unreal.Vector(1,1,1));actor.mesh.set_update_animation_in_editor(True)
    floor=E.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-5));floor.set_actor_label('Review floor — top Z = 0')
    floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(50,50,.1));floor.static_mesh_component.set_collision_profile_name('BlockAll')
    sun=E.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,500),unreal.Rotator(pitch=-45,yaw=-35,roll=0));sun.light_component.set_editor_property('intensity',4)
    E.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,500))
    E.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector())
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',gm.generated_class())
    require(unreal.EditorLevelLibrary.save_current_level(),'save level')
    result.update(status='PASS',assets=dict(level=map_path,character=bp.get_path_name(),anim_blueprint=abp.get_path_name(),game_mode=gm.get_path_name()),walk_speed_cm_s=300,run_speed_cm_s=600,accepted_assets_modified=False)
except Exception:result.update(status='FAIL',error=traceback.format_exc())
(O/'build_result.json').write_text(json.dumps(result,indent=2)+'\n')
print('AEGIS_REVIEW_BUILD',result['status'],result.get('error',''))
