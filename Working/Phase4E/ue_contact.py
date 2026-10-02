"""UE 5.8 Floor Constraint experiment; authoring-only retargeter, no actor offset."""
import sys, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ue_common import *
result={'status':'running','samples':[]}
try:
    mesh=unreal.load_asset(B+'/Character/Candidates/SK_Lara_Refined');assert mesh
    path=B+'/Authoring/RTG_LaraFloor'
    ret=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else unreal.EditorAssetLibrary.duplicate_asset(B+'/Character/RTG_Manny_Lara',path);assert ret
    rc=unreal.IKRetargeterController.get_controller(ret);rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET,mesh)
    idx=rc.get_index_of_op_by_name('Floor Constraint')
    if idx<0:idx=rc.add_retarget_op('/Script/IKRig.IKRetargetFloorConstraintOp')
    ctl=rc.get_op_controller(idx);settings=ctl.get_settings();chains=list(settings.chains_to_affect)
    data=json.loads((W/'baseline_skin.json').read_text());v=data['geometry']['vertices'];bones=data['reference']['bones'];footprints={}
    for s,sign in [('l',1),('r',-1)]:
        pts=[p for p in v if p[0]*sign>8 and p[2]<2];ball=bones['ball_'+s]['component']['translation']
        xs=[sign*(p[0]-ball[0]) for p in pts];ys=[p[1]-ball[1] for p in pts]
        footprints[s]={'medial_offset':max(0,-min(xs)),'lateral_offset':max(0,max(xs)),'heel_offset':max(0,-min(ys)),'toe_offset':max(0,max(ys)),'vertical_offset':0.0}
    configured=[]
    for c in chains:
        n=str(c.target_chain_name)
        if n not in ['LeftLeg','RightLeg']:continue
        s='l' if n=='LeftLeg' else 'r';foot=c.foot;foot.set_editor_properties(footprints[s]);c.set_editor_properties({'enable_floor_constraint':True,'alpha':1.0,'maintain_height_offset':0.0,'use_foot':True,'use_toes':False,'foot':foot});configured.append(n)
    assert len(configured)==2,[(str(c.target_chain_name)) for c in chains]
    settings.set_editor_properties({'chains_to_affect':chains,'height_falloff_offset':8.,'height_falloff_distance':20.});ctl.set_settings(settings)
    assert unreal.EditorAssetLibrary.save_loaded_asset(ret,False)
    result['footprints']=footprints;result['ops']=[{'name':str(rc.get_op_name(i)),'controller':type(rc.get_op_controller(i)).__name__,'enabled':rc.get_retarget_op_enabled(i)} for i in range(rc.get_num_retarget_ops())]
    inp=unreal.IKRetargetBatchOperationInputs();src=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
    clips={'idle':'MM_Idle','walk':'MF_Walk_Fwd','run':'MM_Run_Fwd'}
    inp.set_editor_properties({'assets_to_retarget':[unreal.EditorAssetLibrary.find_asset_data('/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/'+n) for n in clips.values()],'source_mesh':src,'target_mesh':mesh,'ik_retarget_asset':ret,'target_path':B+'/Character/ContactAnimations','include_referenced_assets':False,'overwrite_existing_files':True})
    baked=unreal.IKRetargetBatchOperation.run_batch_retarget(inp);assert len(baked)==3
    opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_properties({'optional_skeletal_mesh':mesh,'incorporate_root_motion_into_pose':True})
    for asset in baked:
        anim=asset.get_asset();assert anim.get_skeleton()==mesh.skeleton;anim.set_preview_skeletal_mesh(mesh);unreal.EditorAssetLibrary.save_loaded_asset(anim,False)
        role=next(k for k,n in clips.items() if n==anim.get_name());duration=anim.get_play_length()
        for i in range(61):
            tm=duration*i/60;pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,tm,opts)
            result['samples'].append({'role':role,'time_s':tm,'fraction':i/60,'bones':{str(n):{'local':tr(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),'component':tr(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))} for n in pose.get_bone_names()}})
    result.update(status='passed',retargeter=ret.get_path_name(),clips=[a.get_asset().get_path_name() for a in baked],configured_chains=configured)
except Exception:result.update(status='failed',error=traceback.format_exc())
save('contact_ue_experiment.json',result);print('PHASE4E_CONTACT',result['status'],result.get('error'))
