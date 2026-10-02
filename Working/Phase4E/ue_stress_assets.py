import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ue_common import *
result={'status':'running','assets':[]}
try:
    mesh=unreal.load_asset(B+'/Character/Candidates/SK_Lara_Refined');sk=mesh.skeleton;keys=json.loads((W/'stress_native_keys.json').read_text())
    for row in keys['poses']:
        name='Stress_'+row['name'];path=B+'/Character/StressAnimations';dest=path+'/'+name
        if unreal.EditorAssetLibrary.does_asset_exist(dest):anim=unreal.load_asset(dest)
        else:
            fac=unreal.AnimSequenceFactory();fac.set_editor_property('target_skeleton',sk);anim=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,path,unreal.AnimSequence,fac);assert anim
        ctl=anim.get_editor_property('controller');ctl.open_bracket('Reference-pivot stress fixture',False);ctl.remove_all_bone_tracks(False);ctl.set_frame_rate(unreal.FrameRate(30,1),False);ctl.set_number_of_frames(unreal.FrameNumber(30),False)
        for b,n in enumerate(keys['bone_names']):
            mat=row['local_matrices'][b];rot=unreal.MathLibrary.make_rot_from_xy(unreal.Vector(*[mat[j][0] for j in range(3)]),unreal.Vector(*[mat[j][1] for j in range(3)]));t=unreal.Transform(location=unreal.Vector(*[mat[j][3] for j in range(3)]),rotation=rot,scale=unreal.Vector(1,1,1));ctl.add_bone_track(n,False);assert ctl.set_bone_track_keys(n,[t.translation]*31,[t.rotation]*31,[t.scale3d]*31,False)
        ctl.close_bracket(False);anim.set_preview_skeletal_mesh(mesh);assert unreal.EditorAssetLibrary.save_loaded_asset(anim,False);result['assets'].append(anim.get_path_name())
    result['status']='passed'
except Exception:result.update(status='failed',error=traceback.format_exc())
save('native_stress_assets.json',result)
