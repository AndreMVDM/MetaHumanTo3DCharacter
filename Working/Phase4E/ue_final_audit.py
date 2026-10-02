"""Fresh disk, read-only invariants, evaluated animation preservation and runtime closure."""
import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ue_common import *
r={'status':'running'}
try:
    baseline=unreal.load_asset(B+'/Character/SK_Lara');final=unreal.load_asset(B+'/Character/Candidates/SK_Lara_Refined');srcmesh=unreal.load_asset(D+'/Character/SK_Lara')
    expected=json.loads((W/'baseline_skin.json').read_text());actual=state(dm_from(final));assert actual==expected['geometry'];assert reference(final)==expected['reference']['bones'];assert reference(srcmesh)==reference(final)
    ws=weights(dm_from(final));want=json.loads((W/'saved_Refined_weights.json').read_text());assert ws==want
    bws=weights(dm_from(baseline));sw=weights(dm_from(srcmesh));delta=max(abs(dict(a).get(k,0)-dict(b).get(k,0)) for a,b in zip(bws,sw) for k in set(dict(a))|set(dict(b)));assert delta==0
    r['fresh_disk_readback']={'geometry_topology_uv_reference_identical':True,'bone_count':len(reference(final)),'baseline_weight_max_delta':delta,'final_saved_weights_identical':True,'statistics':stats(ws),'height_cm':max(v[2] for v in actual['vertices'])-min(v[2] for v in actual['vertices'])}
    clips=[]
    for name in ['MM_Idle','MF_Walk_Fwd','MM_Run_Fwd','JumpingJacks','MannyFingerIdentity']:
        a=unreal.load_asset(D+'/Character/Animations/'+name);b=unreal.load_asset(B+'/Character/NativeAnimations/'+name);oa=unreal.AnimPoseEvaluationOptions();ob=unreal.AnimPoseEvaluationOptions();oa.set_editor_property('optional_skeletal_mesh',srcmesh);ob.set_editor_property('optional_skeletal_mesh',baseline)
        es=[];angles=[]
        for f in range(121):
            tm=min(a.get_play_length(),b.get_play_length())*f/120;pa=unreal.AnimPoseExtensions.get_anim_pose_at_time(a,tm,oa);pb=unreal.AnimPoseExtensions.get_anim_pose_at_time(b,tm,ob)
            for n in pa.get_bone_names():
                ta=pa.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD);tb=pb.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD);es.append((ta.translation-tb.translation).length());qa=tr(ta)['rotation_xyzw'];qb=tr(tb)['rotation_xyzw'];dot=abs(sum(x*y for x,y in zip(qa,qb)))/math.sqrt(sum(x*x for x in qa)*sum(x*x for x in qb));angles.append(math.degrees(2*math.acos(min(1,dot))))
        clips.append({'name':name,'poses_compared':121,'source_duration_s':a.get_play_length(),'copy_duration_s':b.get_play_length(),'max_component_position_error_cm':max(es),'max_component_rotation_error_deg':max(angles),'destination_skeleton':b.get_skeleton().get_path_name()})
    r['evaluated_animation_preservation']=clips
    registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True);options=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False)
    seeds=[B+'/Character/SK_Lara',B+'/Character/Candidates/SK_Lara_Refined',B+'/Character/SKEL_Lara',B+'/Character/BP_QualityPlayback',B+'/Maps/L_QualityComparison']
    for folder in ['NativeAnimations','SurfaceContactAnimations','StressAnimations']:
        seeds.extend(p.split('.')[0] for p in unreal.EditorAssetLibrary.list_assets(B+'/Character/'+folder,True,False))
    todo=seeds[:];seen=set();edges={}
    while todo:
        p=todo.pop()
        if p in seen:continue
        seen.add(p);edges[p]=[str(x) for x in registry.get_dependencies(p,options)];todo.extend(x for x in edges[p] if x not in seen)
    foreign=[p for p in seen if p.startswith('/Game/') and not p.startswith(B+'/')];authoring=[p for p in seen if '/Authoring/' in p or p.endswith('/IK_Lara') or p.endswith('/RTG_Manny_Lara')];helper=[p for p in seen if 'Phase4DTools' in p or 'Phase4ATools' in p or '/MetaHumans/' in p or p.startswith('/MetaHuman/')]
    r.update(status='passed' if not foreign and not authoring and not helper else 'failed',seeds=seeds,closure=sorted(seen),edges=edges,foreign_game_packages=foreign,authoring_packages=authoring,helper_dependencies=helper,limits='Package closure and fresh UE reload, not clean-project migration or cooked executable. Evaluated sampled animation copy is not raw-track byte identity.')
except Exception:r.update(status='failed',error=traceback.format_exc())
save('final_dependency_closure.json',r);print('FINAL_AUDIT',r['status'],r.get('error'),r.get('foreign_game_packages'))
