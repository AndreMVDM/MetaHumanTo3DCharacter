import unreal,json,math,traceback,sys
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/ReviewFixes/RunJumpLand';sys.path.insert(0,str(R/'Working/R4'));import animation_library as A
D=dict(status='RUNNING',subjects={})
try:
    for subject,folder,B,name in [('Female','FinalAcceptance/FemaleBodyRigged','/Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/ReviewV1','FemaleBody'),('Aegis','R4/AegisNX7','/Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/ReviewV2','Aegis')]:
        M=json.loads((R/'Documentation'/folder/'animation_library_manifest.json').read_text());rows=[x for x in M['entries'] if x['name']=='MM_Land' and '/Anims/Unarmed/' in x['source_path']];assert len(rows)==1;entry=rows[0];mesh=unreal.load_asset(M['destination_mesh']);abp=unreal.load_asset(B+'/ABP_'+name+'MovementReview');bp=unreal.load_asset(B+'/BP_'+name+'MovementReviewCharacter');cdo=unreal.get_default_object(bp.generated_class())
        result=dict(land={},graphs={},CMC={k:str(cdo.character_movement.get_editor_property(k)) for k in ['max_walk_speed','braking_deceleration_walking','ground_friction','braking_friction','braking_friction_factor','use_separate_braking_friction','air_control','falling_lateral_friction','jump_z_velocity']})
        for label,path in [('source',entry['source_path']),('destination',entry['destination_path'])]:
            anim=unreal.load_asset(path);md=A.metadata(anim);options=unreal.AnimPoseEvaluationOptions(should_retarget=False,incorporate_root_motion_into_pose=True);model=anim.get_editor_property('data_model_interface');rate=model.get_frame_rate();poses=[]
            for i in range(model.get_number_of_keys()):
                t=min(anim.get_play_length(),i*rate.denominator/rate.numerator);pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,t,options)
                poses.append(dict(t=t,root=A.vector(pose.get_bone_pose('root',unreal.AnimPoseSpaces.WORLD).translation),pelvis=A.vector(pose.get_bone_pose('pelvis',unreal.AnimPoseSpaces.WORLD).translation)))
            result['land'][label]=dict(path=path,metadata=md,trajectory=poses,root_excursion_cm=max(math.dist(x['root'],poses[0]['root']) for x in poses),pelvis_excursion_cm=max(math.dist(x['pelvis'],poses[0]['pelvis']) for x in poses))
        for asset,graphname in [(abp,'EventGraph'),(abp,'AnimGraph'),(bp,'EventGraph')]:
            graph=unreal.BlueprintGraphEditor.get_graph_editor_by_name(asset,graphname);nodes=[]
            for n in graph.list_all_nodes():
                nodes.append(dict(path=n.get_path_name(),title=str(n.get_node_title()),type=n.get_class().get_name(),pins=[dict(name=str(p.get_pin_name()),value=str(p.get_pin_value()),direction=str(p.get_pin_direction()),links=[str(q.get_owning_node().get_path_name())+':'+str(q.get_pin_name()) for q in p.list_connected_pins()]) for p in n.list_all_pins()]))
            result['graphs'][asset.get_name()+':'+graphname]=nodes
        D['subjects'][subject]=result
    D['status']='PASS'
except Exception:D.update(status='FAIL',error=traceback.format_exc())
(O/'inspection.json').write_text(json.dumps(D,indent=2)+'\n');print('SKID_INSPECTION',D['status'],D.get('error',''))
