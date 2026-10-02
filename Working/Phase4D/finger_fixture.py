"""Authoring-only Manny fixture: one digit flexes at a time; batch bake to Lara."""
import sys,traceback
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common_d import *
B='/Game/MetaHumanTo3DCharacter/Phase4D';row={'status':'running','measured_results':{},'anatomical_edits':[]};samples=[]
try:
 assert json.loads((O/'animation_bake_results.json').read_text())['status']=='passed'
 T=unreal.AssetToolsHelpers.get_asset_tools();src=T.duplicate_asset('MannyFingerIdentity',B+'/Authoring',unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/MM_Idle'));assert src
 source_mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple');mesh=unreal.load_asset(B+'/Character/SK_Lara');rt=unreal.load_asset(B+'/Character/RTG_Manny_Lara')
 opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_property('optional_skeletal_mesh',source_mesh);baseline=unreal.AnimPoseExtensions.get_anim_pose_at_time(src,0,opts);names=baseline.get_bone_names()
 controller=src.get_editor_property('controller');controller.open_bracket('Phase4D independent digit diagnostic',False);controller.remove_all_bone_tracks(False);controller.set_frame_rate(unreal.FrameRate(30,1),False);controller.set_number_of_frames(unreal.FrameNumber(330),False)
 digits=[d+'_'+s for s in ['l','r'] for d in ['thumb','index','middle','ring','pinky']]
 for n in names:
  tr=baseline.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL);key=str(n);rotations=[]
  for f in range(331):
   active=int(f/30)-1;angle=0
   if 0<=active<10:
    digit,side=digits[active].split('_')
    if key.startswith(digit+'_0') and key.endswith('_'+side):angle=math.radians(45)*math.sin(math.pi*((f%30)/30))
   rotations.append(tr.rotation.multiply(unreal.Quat(0,0,math.sin(angle/2),math.cos(angle/2))))
  controller.add_bone_track(n,False);assert controller.set_bone_track_keys(n,[tr.translation]*331,rotations,[tr.scale3d]*331,False),str(n)
 controller.close_bracket(False);assert unreal.EditorAssetLibrary.save_loaded_asset(src,only_if_is_dirty=False)
 inp=unreal.IKRetargetBatchOperationInputs();inp.set_editor_properties({'assets_to_retarget':[unreal.EditorAssetLibrary.find_asset_data(src.get_path_name())],'source_mesh':source_mesh,'target_mesh':mesh,'ik_retarget_asset':rt,'target_path':B+'/Character/Animations','include_referenced_assets':False,'overwrite_existing_files':False});baked=unreal.IKRetargetBatchOperation.run_batch_retarget(inp);assert len(baked)==1;anim=baked[0].get_asset();assert anim.get_editor_property('skeleton')==mesh.skeleton;assert unreal.EditorAssetLibrary.save_loaded_asset(anim,only_if_is_dirty=False)
 opts.set_editor_property('optional_skeletal_mesh',mesh)
 for tm in [0]+[1.5+i for i in range(10)]+[float(i) for i in range(1,12)]:
  pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,tm,opts);bones={str(n):{'local':t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),'component':t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))} for n in pose.get_bone_names()};samples.append({'time_s':tm,'active_digit':digits[int(tm)-1] if tm%1==.5 else None,'bones':bones})
 row.update(status='passed',assets=[anim.get_path_name()],source_fixture=src.get_path_name(),measured_results={'samples':len(samples),'duration_s':anim.get_editor_property('sequence_length'),'digit_order':digits,'source_rotation':'45 degree sinusoidal local-Z flex of each three-phalange chain, one digit at a time; other tracks held at idle pose'},meaning='diagnostic capability and identity probe, not a human correction or production finger animation')
except Exception:row.update(status='failed',error=traceback.format_exc())
save('finger_animation_bake.json',row);save('finger_pose_samples.json',{'samples':samples});print('PHASE4D_FINGER_FIXTURE_DONE',row['status'],row.get('error'))
