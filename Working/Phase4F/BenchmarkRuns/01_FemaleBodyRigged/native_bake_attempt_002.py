"""Existing native batch-retarget/bake APIs, common frozen sources, immutable attempt 001."""
import unreal,sys,json,gzip,traceback,math
from pathlib import Path
sys.dont_write_bytecode=True;R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';B='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged'
def tr(x):return [[x.translation.x,x.translation.y,x.translation.z],[x.rotation.x,x.rotation.y,x.rotation.z,x.rotation.w],[x.scale3d.x,x.scale3d.y,x.scale3d.z]]
r={'status':'running','attempt_id':'bake-002','retry_reason':'Inspection harness used unavailable get_data_model; existing 13 native bakes retained and reloaded, no algorithm tuning','method':'UE IKRetargetBatchOperation, destination-native AnimSequence; no track editing/rig repair','clips':[]};samples=[]
try:
    assert json.loads((O/'frozen_input_gate.json').read_text())['downstream_authorised'] is True
    mesh=unreal.load_asset(B+'/Character/SK_FemaleBodyRigged');sm=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');sources=json.loads((R/'Documentation/Phase4F/Benchmark/SourceReadinessAmendment/source_readiness.json').read_text())['effective_sources'];sources=[x for x in sources if x['task_id']!='P00'];names=[str(n) for n in mesh.skeleton.get_reference_pose().get_bone_names()]
    def sample(anim,m,ns):
        opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_properties({'optional_skeletal_mesh':m,'retrieve_additive_as_full_pose':True,'incorporate_root_motion_into_pose':True})
        duration=anim.get_editor_property('sequence_length');model=anim.get_editor_property('data_model_interface');rate=model.get_frame_rate();hz=rate.numerator/rate.denominator;count=model.get_number_of_keys()
        times=sorted(set([min(duration,i/60) for i in range(math.ceil(duration*60)+1)]+[min(duration,i/hz) for i in range(count)]+[duration]))
        out=[]
        for tm in times:
            pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,tm,opts)
            bs=[[tr(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),tr(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))] for n in ns]
            assert all(math.isfinite(x) for b in bs for t in b for a in t for x in a)
            out.append([tm,bs])
        return dict(bones=ns,frames=out,duration_s=duration,frame_rate=[rate.numerator,rate.denominator],key_count=count,sample_count=len(times))
    for variant in ['Final','FKDiagnostic']:
        for group in ['InPlace','RootMotion']:
            selected=[s for s in sources if (s['task_id']=='P14')==(group=='RootMotion')]
            rt=unreal.load_asset(B+'/Retarget/RTG_'+('FKDiagnostic' if variant=='FKDiagnostic' else group));target=B+'/Animations/'+variant+'/'+group
            inp=unreal.IKRetargetBatchOperationInputs();inp.set_editor_properties({'assets_to_retarget':[unreal.EditorAssetLibrary.find_asset_data(s['object_path']) for s in selected],'source_mesh':sm,'target_mesh':mesh,'ik_retarget_asset':rt,'target_path':target,'include_referenced_assets':False,'overwrite_existing_files':False})
            existing=unreal.EditorAssetLibrary.list_assets(target,True,False)
            if existing:
                assert len(existing)==len(selected),'partial asset set: inspect, do not overwrite';byname={unreal.load_asset(p).get_name():unreal.load_asset(p) for p in existing}
            else:
                baked=unreal.IKRetargetBatchOperation.run_batch_retarget(inp);assert len(baked)==len(selected),(len(baked),len(selected))
                byname={d.get_asset().get_name():d.get_asset() for d in baked}
            for s in selected:
                src=unreal.load_asset(s['object_path']);anim=byname[src.get_name()];assert anim.get_editor_property('skeleton')==mesh.skeleton
                if s['task_id']=='P14' and variant=='Final':anim.set_editor_properties({'enable_root_motion':True,'force_root_lock':False})
                assert unreal.EditorAssetLibrary.save_loaded_asset(anim,only_if_is_dirty=False)
                data=sample(anim,mesh,names);row=dict(task_id=s['task_id'],variant=variant,source=src.get_path_name(),path=anim.get_path_name(),skeleton=mesh.skeleton.get_path_name(),retargeter=rt.get_path_name(),duration_s=data['duration_s'],frame_rate=data['frame_rate'],key_count=data['key_count'],sample_count=data['sample_count'],root_flags={k:str(anim.get_editor_property(k)) for k in ['enable_root_motion','force_root_lock','root_motion_root_lock']})
                samples.append(dict(**row,pose_data=data));r['clips'].append(row)
                if variant=='Final' and s['task_id'] in ['P11','P14']:
                    samples.append(dict(task_id=s['task_id'],variant='SourceControl',source=src.get_path_name(),pose_data=sample(src,sm,names)))
    r['status']='passed'
except Exception:r.update(status='failed',error=traceback.format_exc())
with gzip.open(O/'baked_pose_samples.json.gz','wt') as f:json.dump(samples,f)
(O/'native_bake.json').write_text(json.dumps(r,indent=2));print('BENCHMARK_BAKE',r['status'],r.get('error',''),len(r['clips']))
