"""Authoritative fresh native SingleNode component samples, 60Hz plus original keys."""
import unreal,json,gzip,sys,math,traceback
from pathlib import Path
sys.dont_write_bytecode=True;R=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=R/'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged';B='/Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged';r={'status':'running','method':'USkeletalMeshComponent.OverrideAnimationData -> TickAnimation(0) + RefreshBoneTransforms; actual native component transforms, fresh disk assets','clips':[]};rows=[]
def tr(t):return [[t.translation.x,t.translation.y,t.translation.z],[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],[t.scale3d.x,t.scale3d.y,t.scale3d.z]]
try:
    assert unreal.EditorLevelLibrary.load_level(B+'/Maps/L_BenchmarkReference');E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);a=next(a for a in E.get_all_level_actors() if isinstance(a,unreal.SkeletalMeshActor));c=a.skeletal_mesh_component;c.set_update_animation_in_editor(True);d=json.loads((O/'native_reload.json').read_text());names=list(d['bones']);a.set_actor_location(unreal.Vector(),False,False)
    captures={x['task_id']:x for x in json.loads((O/'native_destination_review.json').read_text())['captures']}
    for row in json.loads((O/'native_bake.json').read_text())['clips']:
        anim=unreal.load_asset(row['path']);model=anim.get_editor_property('data_model_interface');rate=model.get_frame_rate();hz=rate.numerator/rate.denominator;duration=anim.get_play_length();times=sorted(set([min(duration,i/60) for i in range(math.ceil(duration*60)+1)]+[min(duration,i/hz) for i in range(model.get_number_of_keys())]+[duration]));frames=[]
        for tm in times:
            c.override_animation_data(anim,False,True,tm,0);bs=[]
            for n in names:
                component=c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT);parent=d['bones'][n]['parent'];local=unreal.MathLibrary.make_relative_transform(component,c.get_socket_transform(parent,unreal.RelativeTransformSpace.RTS_COMPONENT)) if parent else component
                bs.append([tr(local),tr(component)])
            frames.append([tm,bs])
        c.override_animation_data(anim,False,True,duration*.5,0)
        error=max(math.dist(tr(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT))[0],captures[row['task_id']]['native_bones'][n]) for n in names) if row['variant']=='Final' else None
        rows.append(dict(**row,pose_data=dict(bones=names,frames=frames,duration_s=duration,sample_count=len(frames))));r['clips'].append(dict(task_id=row['task_id'],variant=row['variant'],samples=len(frames),editor_capture_bone_max_difference_cm=error))
    reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);opts=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=True,include_soft_management_references=True,include_hard_management_references=True);seeds=[d['mesh'].split('.')[0],d['skeleton'].split('.')[0]]+[x['path'].split('.')[0] for x in json.loads((O/'native_bake.json').read_text())['clips'] if x['variant']=='Final'];todo=seeds[:];seen=set();edges={}
    while todo:
        p=todo.pop()
        if p in seen:continue
        seen.add(p);dep=[str(x) for x in reg.get_dependencies(p,opts)];edges[p]=dep;todo.extend(x for x in dep if x not in seen)
    r['dependency_closure']=dict(seeds=seeds,packages=sorted(seen),edges=edges,foreign_game_packages=[p for p in seen if p.startswith('/Game/') and not p.startswith(B+'/')],authoring_packages=[p for p in seen if '/Retarget/' in p])
    r['status']='passed'
except Exception:r.update(status='failed',error=traceback.format_exc())
with gzip.open(O/'native_component_samples.json.gz','wt') as f:json.dump(rows,f)
(O/'native_component_audit.json').write_text(json.dumps(r,indent=2));print('NATIVE_COMPONENT_SAMPLES',r['status'],r.get('error',''))
