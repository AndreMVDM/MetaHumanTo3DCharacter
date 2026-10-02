"""Read-only fresh-process verification of saved candidates and final runtime flags."""
import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
rows=json.loads((O/'scaled_candidates.json').read_text());out=[]
for row in rows:
    try:
        mesh=unreal.load_asset(row['snapshot']['mesh']);ic=unreal.IKRigController.get_controller(unreal.load_asset(row['ik_rig']));rc=unreal.IKRetargeterController.get_controller(unreal.load_asset(row['retargeter']))
        assert ic.get_num_solvers()==1 and ic.get_solver_enabled(0)
        assert rc.get_retarget_op_enabled(rc.get_index_of_op_by_name('Run IK Rig'))
        assert not rc.get_retarget_op_enabled(rc.get_index_of_op_by_name('Root Motion'))
        if row['rig']=='Mixamo':assert str(rc.get_source_chain('Root')) in ['', 'None']
        snap=mesh_snapshot(mesh);assert abs(snap['bounds']['height_cm']-row['requested_height_cm'])<.1
        assert all(abs(x-1)<.001 for b in snap['bones'].values() for tr in b.values() for x in tr['scale'])
        base=row['snapshot']['mesh'].split('.')[0].rsplit('/',1)[0];clips=[]
        for name in ['MM_Idle','MF_Walk_Fwd','MM_Run_Fwd','JumpingJacks','Manny_upperarm_r_anim']:
            asset=unreal.load_asset(base+'/Tests/InPlaceFull/'+name);assert asset.get_editor_property('skeleton')==mesh.skeleton
            if row['rig']=='Mixamo':assert not asset.get_editor_property('force_root_lock')
            clips.append(asset.get_path_name())
        out.append({'rig':row['rig'],'label':row['label'],'pass':True,'full_clips':clips})
    except Exception:out.append({'rig':row['rig'],'label':row['label'],'pass':False,'error':traceback.format_exc()})
save('saved_asset_verification.json',out)
print('PHASE3B_SAVED_VERIFIED',len(out),sum(x['pass'] for x in out))
