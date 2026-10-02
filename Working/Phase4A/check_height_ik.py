import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common import *
B='/Game/MetaHumanTo3DCharacter/Phase4A';T=unreal.AssetToolsHelpers.get_asset_tools();rows=[]
for test in json.loads((O/'height_ordering_results.json').read_text()):
    row={'case':test['case'],'route':test['route'],'height_cm':175};rows.append(row)
    try:
        mesh=unreal.load_asset(test['snapshot']['mesh']);base=mesh.get_path_name().split('.')[0].rsplit('/',1)[0]
        ik=T.create_asset('IK_Lara',base,unreal.IKRigDefinition,unreal.IKRigDefinitionFactory());assert ik
        ic=unreal.IKRigController.get_controller(ik);assert ic.set_skeletal_mesh(mesh);assert ic.apply_auto_generated_retarget_definition();assert ic.apply_auto_fbik();assert ic.get_num_solvers()==1
        ic.set_retarget_root('pelvis');ic.set_root_motion_bone('root')
        if not any(str(c.chain_name)=='Root' for c in ic.get_retarget_chains()):ic.add_retarget_chain('Root','root','root','')
        for side,limb in [('Left','l'),('Right','r')]:ic.set_retarget_chain_end_bone(side+'Leg','ball_'+limb);assert ic.set_goal_bone(ic.get_retarget_chain_goal(side+'Leg'),'ball_'+limb)
        assert unreal.EditorAssetLibrary.save_loaded_asset(ik,only_if_is_dirty=False)
        row['snapshot']=common.rig_snapshot(ik);row['limitation']='New IK/FBIK and goals generated from final 175cm reference state; no 175cm retarget/bake quality test.'
    except Exception:row['error']=traceback.format_exc()
save('height_ik_results.json',rows);print('HEIGHT_IK_DONE',[(r['case'],r['route'],r.get('error')) for r in rows])
