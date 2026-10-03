"""Reuse accepted R4 review design with exclusively Female destination assets."""
import unreal,json,traceback
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=Path(__file__).parent;C=json.loads((W/'profile.json').read_text());O=R/C['evidence_directory'];B=C['output_namespace']+'/ReviewV1';OLD='/Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/ReviewV2';T=unreal.AssetToolsHelpers.get_asset_tools();L=unreal.BlueprintEditorLibrary
D=dict(status='RUNNING',method='Duplicate accepted R4 review design; replace every destination binding before saving; source untouched')
def require(ok,msg):
    if not ok:raise ValueError(msg)
try:
    M=json.loads((O/'animation_library_manifest.json').read_text());require(M['status']=='PASS','library incomplete')
    if (O/'review_build.json').exists() and json.loads((O/'review_build.json').read_text()).get('status')=='PASS':raise SystemExit('Existing certified review retained')
    existing=unreal.EditorAssetLibrary.list_assets(B,True,False)
    require(not existing or all(p.split('.')[0] in [B+'/ABP_FemaleBodyMovementReview',B+'/BP_FemaleBodyMovementReviewCharacter'] for p in existing),'refuse overwrite unrelated review outputs')
    mesh=unreal.load_asset(C['destination_mesh']);height=2*mesh.get_bounds().box_extent.z;half=height*.5;radius=min(34,height*.19)
    def clip(name,folder):
        rows=[r for r in M['entries'] if r['name']==name and r.get('bake_result')=='PASS' and folder in r['source_path']];require(len(rows)==1,'source-role ambiguity '+name);return unreal.load_asset(rows[0]['destination_path'])
    clips={name:clip(name,'/InPlace/' if name in ['MM_Idle','MF_Walk_Fwd','MM_Run_Fwd'] else '/Anims/Unarmed/') for name in ['MM_Idle','MF_Walk_Fwd','MM_Run_Fwd','MM_Jump','MM_Fall_Loop','MM_Land']}
    abp=unreal.load_asset(B+'/ABP_FemaleBodyMovementReview') if existing else T.duplicate_asset('ABP_FemaleBodyMovementReview',B,unreal.load_asset(OLD+'/ABP_AegisMovementReview'));abp.set_editor_property('target_skeleton',mesh.skeleton)
    graph=unreal.BlueprintGraphEditor.get_graph_editor_by_name(abp,'AnimGraph');players=[]
    for node in graph.list_all_nodes():
        if node.get_class().get_name()=='AnimGraphNode_SequencePlayer':
            data=node.get_editor_property('node');old=data.get_editor_property('sequence');require(old.get_name() in clips,'unrecognised review sequence '+old.get_path_name());new=clips[old.get_name()];data.set_editor_property('sequence',new);node.set_editor_property('node',data);players.append(dict(old=old.get_path_name(),new=new.get_path_name()))
    require(len(players)==6,'review must have six sequence players');require(L.compile_blueprint(abp),'Female AnimBP compile')
    bp=unreal.load_asset(B+'/BP_FemaleBodyMovementReviewCharacter') if unreal.EditorAssetLibrary.does_asset_exist(B+'/BP_FemaleBodyMovementReviewCharacter') else T.duplicate_asset('BP_FemaleBodyMovementReviewCharacter',B,unreal.load_asset(OLD+'/BP_AegisMovementReviewCharacter'));require(L.compile_blueprint(bp),'Female Character compile');cdo=unreal.get_default_object(bp.generated_class());cdo.mesh.set_skeletal_mesh_asset(mesh);cdo.mesh.set_anim_instance_class(abp.generated_class());cdo.mesh.set_editor_property('relative_location',unreal.Vector(0,0,-half));cdo.capsule_component.set_capsule_size(radius,half,True);cdo.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0)
    for component in cdo.get_components_by_class(unreal.SpringArmComponent):component.set_editor_property('target_arm_length',height*400/179.91210982641414);component.set_editor_property('relative_location',unreal.Vector(0,0,height*20/179.91210982641414))
    gm=T.duplicate_asset('BP_FemaleBodyMovementReviewGameMode',B,unreal.load_asset(OLD+'/BP_AegisMovementReviewGameMode'));require(L.compile_blueprint(gm),'Female GameMode compile')
    for a in [abp,bp,gm]:require(unreal.EditorAssetLibrary.save_loaded_asset(a,False),'save review asset '+a.get_name())
    require(unreal.EditorLevelLibrary.load_level(OLD+'/L_AegisMovementReview'),'load generic review floor/environment');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);oldbp=unreal.load_asset(OLD+'/BP_AegisMovementReviewCharacter');actors=[a for a in E.get_all_level_actors() if a.get_class()==oldbp.generated_class()];require(len(actors)==1,'review template actor count');E.destroy_actor(actors[0]);pawn=E.spawn_actor_from_class(bp.generated_class(),unreal.Vector(0,0,half+2));pawn.set_editor_property('auto_possess_player',unreal.AutoReceiveInput.PLAYER0);pawn.set_actor_label('Female Body Rigged — WASD / mouse / Shift / Space');pawn.mesh.set_anim_instance_class(abp.generated_class())
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',gm.generated_class());level=B+'/L_FemaleBodyMovementReview';require(unreal.EditorLoadingAndSavingUtils.save_map(world,level),'save isolated review map')
    D.update(status='PASS',assets=dict(level=level,character=bp.get_path_name(),anim_blueprint=abp.get_path_name(),game_mode=gm.get_path_name()),sequence_players=players,clips={k:a.get_path_name() for k,a in clips.items()},reference_height_cm=height,capsule_half_height_cm=half,capsule_radius_cm=radius,spawn_z_cm=half+2,walk_cm_s=300,run_cm_s=600,jump_velocity_cm_s=420,floor_z_cm=0,scale=[1,1,1],original_review_assets_modified=False,geometry_or_stature_modified=False)
except Exception:D.update(status='FAIL',error=traceback.format_exc())
(O/'review_build.json').write_text(json.dumps(D,indent=2)+'\n');print('FEMALE_REVIEW',D['status'],D.get('error',''))
