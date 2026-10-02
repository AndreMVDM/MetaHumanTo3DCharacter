"""Fresh actual asset readback; no prior asset save, fitting or ledger replay."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ue_common import *
result={'status':'running'}
try:
    source=unreal.load_asset(D+'/Character/SK_Lara');assert source
    dm=dm_from(source);geo=state(dm);ws=weights(dm);ref=reference(source)
    recorded=json.loads((W/'baseline_recorded_skin.json').read_text())
    assert geo==recorded['geometry']
    delta=max(abs(dict(a).get(b,0)-dict(c).get(b,0)) for a,c in zip(ws,recorded['weights']) for b in set(dict(a))|set(dict(c)))
    result['recorded_vs_disk_weight_max_delta']=delta
    result['recorded_vs_disk_weight_first_mismatch']=next(({'vertex':i,'disk':a,'recorded':c} for i,(a,c) in enumerate(zip(ws,recorded['weights'])) if a!=c),None)
    # The disk readback is authoritative. Retain any serialisation discrepancy as evidence.
    assert ref==recorded['reference']['bones']
    assets=unreal.EditorAssetLibrary.list_assets(D+'/Character',recursive=True,include_folder=False)
    result['source_assets']=[str(p) for p in assets]
    result['baseline']={'geometry_identical':True,'weights_identical':delta==0,'reference_identical':True,'statistics':stats(ws),'bone_count':len(ref)}
    (W/'baseline_skin.json').write_text(json.dumps({**recorded,'weights':ws,'geometry':geo},allow_nan=False))
    # Duplicate a complete character/visual authoring set. Remap explicit object references.
    extras=unreal.EditorAssetLibrary.list_assets(D+'/Materials',True,False)+unreal.EditorAssetLibrary.list_assets(D+'/Geometry',True,False)
    copies={}
    for p in list(extras)+list(assets):
        p=str(p); dest=p.replace(D,B,1).split('.')[0]
        if p.endswith('BP_LaraNativePlayback.BP_LaraNativePlayback') or '/Animations/' in p or '/SK_Lara.' in p or '/SK_Lara_Authoring.' in p:continue
        if not unreal.EditorAssetLibrary.does_asset_exist(dest):
            a=unreal.EditorAssetLibrary.duplicate_asset(p,dest);assert a,dest
        else:a=unreal.load_asset(dest)
        copies[p]=a
    sk=copies[D+'/Character/SKEL_Lara.SKEL_Lara']
    if unreal.EditorAssetLibrary.does_asset_exist(B+'/Character/SK_Lara'):mesh=unreal.load_asset(B+'/Character/SK_Lara')
    else:
        opts=unreal.GeometryScriptCreateNewSkeletalMeshAssetOptions();opts.set_editor_properties({'materials':{x.material_slot_name:copies.get(x.material_interface.get_path_name(),x.material_interface) for x in source.materials},'use_original_vertex_order':True,'use_mesh_bone_proportions':True})
        mesh,outcome=unreal.GeometryScript_NewAssetUtils.create_new_skeletal_mesh_asset_from_mesh(dm,sk,B+'/Character/SK_Lara',opts);assert mesh,outcome
    copies[D+'/Character/SK_Lara.SK_Lara']=mesh
    result['apis']={n:[s for s in dir(getattr(unreal,n)) if any(k in s for k in ['preview','skeleton','smooth','weight','pose'])] for n in ['Skeleton','AnimSequence','SkinWeightModifier','AnimationLibrary','AnimationEditorLibrary'] if hasattr(unreal,n)}
    for p,a in copies.items():
        if isinstance(a,unreal.SkeletalMesh):
            assert a.skeleton==sk
            mats=list(a.materials)
            for m in mats:
                if m.material_interface and m.material_interface.get_path_name() in copies:m.material_interface=copies[m.material_interface.get_path_name()]
            a.set_editor_property('materials',mats)
    # Exposed preview/rig controllers are probed before remapping.
    result['apis']['skeleton_preview_property']=(type(sk).__doc__ or '')
    sk.set_skeleton_preview_mesh(mesh)
    result['apis']['factory']=unreal.AnimSequenceFactory.__doc__
    clips=[]
    for name in ['MM_Idle','MF_Walk_Fwd','MM_Run_Fwd','JumpingJacks','MannyFingerIdentity']:
        src=unreal.load_asset(D+'/Character/Animations/'+name);dest=B+'/Character/NativeAnimations/'+name
        if unreal.EditorAssetLibrary.does_asset_exist(dest):anim=unreal.load_asset(dest)
        else:
            fac=unreal.AnimSequenceFactory();fac.set_editor_property('target_skeleton',sk)
            anim=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,B+'/Character/NativeAnimations',unreal.AnimSequence,fac);assert anim
        opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_property('optional_skeletal_mesh',source)
        frames=round(src.get_play_length()*30);poses=[unreal.AnimPoseExtensions.get_anim_pose_at_time(src,f/30,opts) for f in range(frames+1)]
        ctl=anim.get_editor_property('controller');ctl.open_bracket('Identical skeleton Phase4E native copy',False);ctl.remove_all_bone_tracks(False);ctl.set_frame_rate(unreal.FrameRate(30,1),False);ctl.set_number_of_frames(unreal.FrameNumber(frames),False)
        for n in sk.get_reference_pose().get_bone_names():
            ts=[pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL) for pose in poses];ctl.add_bone_track(n,False);assert ctl.set_bone_track_keys(n,[t.translation for t in ts],[t.rotation for t in ts],[t.scale3d for t in ts],False)
        ctl.close_bracket(False);anim.set_preview_skeletal_mesh(mesh);assert unreal.EditorAssetLibrary.save_loaded_asset(anim,False)
        clips.append({'source':src.get_path_name(),'destination':anim.get_path_name(),'frames':frames,'duration_s':anim.get_play_length(),'skeleton':anim.get_skeleton().get_path_name()})
    result['native_clips']=clips
    rig=unreal.load_asset(B+'/Character/IK_Lara');unreal.IKRigController.get_controller(rig).set_skeletal_mesh(mesh)
    ret=unreal.load_asset(B+'/Character/RTG_Manny_Lara');rc=unreal.IKRetargeterController.get_controller(ret);rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET,rig)
    rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET,mesh)
    for p,a in copies.items():
        # Texture graph remap on duplicated material only.
        if isinstance(a,unreal.Material):
            for expr in unreal.MaterialEditingLibrary.get_material_expressions(a):
                if isinstance(expr,unreal.MaterialExpressionTextureSample):
                    tex=expr.get_editor_property('texture')
                    if tex and tex.get_path_name() in copies:expr.set_editor_property('texture',copies[tex.get_path_name()])
        if isinstance(a,unreal.StaticMesh):
            mats=list(a.static_materials)
            for mat in mats:
                if mat.material_interface and mat.material_interface.get_path_name() in copies:mat.material_interface=copies[mat.material_interface.get_path_name()]
            a.set_editor_property('static_materials',mats)
        assert a.get_path_name().startswith(B+'/')
        unreal.EditorAssetLibrary.save_loaded_asset(a,False)
    result.update(status='passed',copies=[a.get_path_name() for a in copies.values()],working_mesh=mesh.get_path_name(),working_skeleton=sk.get_path_name())
    assert reference(mesh)==ref
except Exception:result.update(status='failed',error=traceback.format_exc())
save('baseline_asset_readback.json',result);print('PHASE4E_BASELINE',result['status'],result.get('error'))
