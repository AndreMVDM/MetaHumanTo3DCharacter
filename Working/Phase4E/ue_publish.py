"""Publish isolated measured weight candidates, verify disk snapshots, create playback map."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ue_common import *
result={'status':'running','candidates':[]}
try:
    baseline=unreal.load_asset(B+'/Character/SK_Lara');assert baseline;sk=baseline.skeleton
    material=unreal.load_asset(B+'/Materials/M_LaraOriginal');texture=unreal.load_asset(B+'/Materials/T_LaraOriginal')
    for expr in unreal.MaterialEditingLibrary.get_material_expressions(material):
        if isinstance(expr,unreal.MaterialExpressionTextureSample):expr.set_editor_property('texture',texture)
    unreal.EditorAssetLibrary.save_loaded_asset(material,False)
    names=[str(n) for n in sk.get_reference_pose().get_bone_names()]
    expected=json.loads((W/'baseline_skin.json').read_text())
    for label,file in [('RootOnly','root_to_pelvis_weights.json'),('Semantic','semantic_1_1_weights.json'),('Refined','selected_weights.json')]:
        dest=B+'/Character/Candidates/SK_Lara_'+label
        candidate=unreal.load_asset(dest) if unreal.EditorAssetLibrary.does_asset_exist(dest) else unreal.EditorAssetLibrary.duplicate_asset(baseline.get_path_name(),dest);assert candidate
        target=json.loads((W/file).read_text());mod=unreal.SkinWeightModifier();assert mod.set_skeletal_mesh(candidate);assert mod.get_num_vertices()==len(target)
        for i,ws in enumerate(target):assert mod.set_vertex_weights(i,{names[b]:weight for b,weight in ws},True)
        assert mod.commit_weights_to_skeletal_mesh();assert unreal.EditorAssetLibrary.save_loaded_asset(candidate,False)
        dm=dm_from(candidate);geo=state(dm);ws=weights(dm)
        assert geo==expected['geometry'];assert reference(candidate)==expected['reference']['bones']
        delta=max(abs(dict(a).get(b,0)-dict(c).get(b,0)) for a,c in zip(ws,target) for b in set(dict(a))|set(dict(c)))
        (W/('saved_'+label+'_weights.json')).write_text(json.dumps(ws))
        result['candidates'].append({'label':label,'asset':candidate.get_path_name(),'statistics':stats(ws),'input_to_saved_max_weight_delta':delta,'geometry_uv_reference_identical':True})
    final=unreal.load_asset(B+'/Character/Candidates/SK_Lara_Refined')
    # Baseline/reference/candidates all use identical native animation data.
    bp_path=B+'/Character/BP_QualityPlayback'
    bp=unreal.load_asset(bp_path) if unreal.EditorAssetLibrary.does_asset_exist(bp_path) else unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(bp_path,unreal.Actor)
    ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);fn=unreal.SubobjectDataBlueprintFunctionLibrary
    handles=ss.k2_gather_subobject_data_for_blueprint(bp);root=next(h for h in handles if fn.is_default_scene_root(fn.get_data(h)))
    existing={fn.get_object_for_blueprint(fn.get_data(h),bp).get_name():h for h in handles if fn.get_object_for_blueprint(fn.get_data(h),bp)}
    for i,(label,mesh) in enumerate([('Baseline',baseline),('Refined',final)]):
        if label in existing:h=existing[label]
        else:
            h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(blueprint_context=bp,new_class=unreal.SkeletalMeshComponent,parent_handle=root));assert fn.is_handle_valid(h),reason;ss.rename_subobject(h,label)
        c=fn.get_object_for_blueprint(fn.get_data(h),bp);c.set_skeletal_mesh_asset(mesh);c.set_editor_properties({'relative_location':unreal.Vector(i*140,0,0),'visibility_based_anim_tick_option':unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES});c.override_animation_data(unreal.load_asset(B+'/Character/NativeAnimations/JumpingJacks'),True,True,0,1)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.new_level(B+'/Maps/L_QualityComparison');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    demo=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector(),unreal.Rotator());demo.set_actor_label('Phase4E quality comparison')
    floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(70,0,0),unreal.Rotator());floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Plane'));floor.set_actor_scale3d(unreal.Vector(8,8,1))
    light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,-200,400),unreal.Rotator(pitch=-45,yaw=90,roll=0));light.get_editor_property('directional_light_component').set_editor_properties({'mobility':unreal.ComponentMobility.MOVABLE,'intensity':4.0})
    fill=actors.spawn_actor_from_class(unreal.PointLight,unreal.Vector(70,250,250),unreal.Rotator());fill.get_editor_property('point_light_component').set_editor_properties({'mobility':unreal.ComponentMobility.MOVABLE,'intensity':30000,'attenuation_radius':1600})
    assert level.save_current_level();result.update(status='passed',playback_assets=[bp.get_path_name(),B+'/Maps/L_QualityComparison'])
except Exception:result.update(status='failed',error=traceback.format_exc())
save('candidate_asset_publication.json',result);print('PHASE4E_PUBLISH',result['status'],result.get('error'))
