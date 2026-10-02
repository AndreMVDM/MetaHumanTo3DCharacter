import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ue_common import *
result={'status':'running','samples':[]}
try:
    mesh=unreal.load_asset(B+'/Character/Candidates/SK_Lara_Refined');sk=mesh.skeleton;keys=json.loads((W/'contact_bake_keys.json').read_text());clips=[]
    for role,meta in keys['clips'].items():
        name=meta['name'];path=B+'/Character/SurfaceContactAnimations';dest=path+'/'+name
        if unreal.EditorAssetLibrary.does_asset_exist(dest):anim=unreal.load_asset(dest)
        else:
            fac=unreal.AnimSequenceFactory();fac.set_editor_property('target_skeleton',sk);anim=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,path,unreal.AnimSequence,fac);assert anim
        ctl=anim.get_editor_property('controller');ctl.open_bracket('Surface-aware flat-floor authoring contact IK',False);ctl.remove_all_bone_tracks(False);ctl.set_frame_rate(unreal.FrameRate(meta['fps'],1),False);ctl.set_number_of_frames(unreal.FrameNumber(meta['frames']),False)
        frames=[r for r in keys['frames'] if r['role']==role];assert len(frames)==meta['frames']+1
        for b,n in enumerate(keys['bone_names']):
            ts=[]
            for row in frames:
                mat=row['local_matrices'][b];cols=[[mat[j][i] for j in range(3)] for i in range(3)];rot=unreal.MathLibrary.make_rot_from_xy(unreal.Vector(*cols[0]),unreal.Vector(*cols[1]));ts.append(unreal.Transform(location=unreal.Vector(*[mat[j][3] for j in range(3)]),rotation=rot,scale=unreal.Vector(1,1,1)))
            ctl.add_bone_track(n,False);assert ctl.set_bone_track_keys(n,[t.translation for t in ts],[t.rotation for t in ts],[t.scale3d for t in ts],False)
        ctl.close_bracket(False);anim.set_preview_skeletal_mesh(mesh);assert unreal.EditorAssetLibrary.save_loaded_asset(anim,False);clips.append(anim.get_path_name())
        opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_properties({'optional_skeletal_mesh':mesh,'incorporate_root_motion_into_pose':True})
        # Dense evaluation includes halfway interpolation between keys.
        for f in range(meta['frames']*2+1):
            tm=f/(meta['fps']*2);pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,tm,opts);result['samples'].append({'role':role,'time_s':tm,'frame_fraction':f/2,'bones':{str(n):{'local':tr(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),'component':tr(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))} for n in pose.get_bone_names()}})
    result.update(status='passed',clips=clips,source='UE native frames + bounded sole-aware authoring two-bone IK',actor_offset_cm=[0,0,0])
except Exception:result.update(status='failed',error=traceback.format_exc())
save('surface_contact_native_bake.json',result);print('PHASE4E_SURFACE_BAKE',result['status'],result.get('error'))
