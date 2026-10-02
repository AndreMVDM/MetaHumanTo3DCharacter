import sys,traceback
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common_d import *
base='/Game/MetaHumanTo3DCharacter/Phase4D/Character';T=unreal.AssetToolsHelpers.get_asset_tools();row={'status':'running','measured_results':{},'corrections':[]};samples=[]
try:
 assert json.loads((O/'skinning_results.json').read_text())['status']=='passed'
 mesh=unreal.load_asset(base+'/SK_Lara');original_source=unreal.load_asset('/Game/Characters/Mannequins/Rigs/IK_Mannequin');source_mesh=unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
 source=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase4D/Authoring/IK_MannySource') if unreal.EditorAssetLibrary.does_asset_exist('/Game/MetaHumanTo3DCharacter/Phase4D/Authoring/IK_MannySource') else T.duplicate_asset('IK_MannySource','/Game/MetaHumanTo3DCharacter/Phase4D/Authoring',original_source);assert source
 sc=unreal.IKRigController.get_controller(source);row['original_source_rig']=rig_snapshot(original_source)
 for side,suffix in [('Left','l'),('Right','r')]:
  assert str(sc.get_retarget_chain_end_bone(side+'Leg')).lower()=='ball_'+suffix
  if not any(str(c.chain_name)==side+'Foot' for c in sc.get_retarget_chains()):sc.add_retarget_chain(side+'Foot','ball_'+suffix,'ball_'+suffix,'')
 row['corrections'].append({'kind':'Fresh Phase4D Manny authoring IK copy: add explicit ball chains; existing source legs already end at ball; original source unchanged'})
 ik=unreal.load_asset(base+'/IK_Lara') if unreal.EditorAssetLibrary.does_asset_exist(base+'/IK_Lara') else T.create_asset('IK_Lara',base,unreal.IKRigDefinition,unreal.IKRigDefinitionFactory());ic=unreal.IKRigController.get_controller(ik);assert ic.set_skeletal_mesh(mesh)
 for i in reversed(range(ic.get_num_solvers())):ic.remove_solver(i)
 row['auto_characterisation']=ic.apply_auto_generated_retarget_definition();assert row['auto_characterisation'];assert ic.apply_auto_fbik();assert ic.get_num_solvers()==1
 ic.set_retarget_root('pelvis');ic.set_root_motion_bone('root')
 if not any(str(c.chain_name)=='Root' for c in ic.get_retarget_chains()):ic.add_retarget_chain('Root','root','root','')
 for side,suffix in [('Left','l'),('Right','r')]:
  old=str(ic.get_retarget_chain_end_bone(side+'Leg'));ic.set_retarget_chain_end_bone(side+'Leg','ball_'+suffix)
  goal_name=ic.get_retarget_chain_goal(side+'Leg');goal=next(g for g in ic.get_all_goals() if str(g.get_editor_property('goal_name'))==str(goal_name))
  if str(goal.get_editor_property('bone_name')).lower()!='ball_'+suffix:assert ic.set_goal_bone(goal_name,'ball_'+suffix)
  assert str(goal.get_editor_property('bone_name')).lower()=='ball_'+suffix
  row['corrections'].append({'chain':side+'Leg','from_end':old,'to_end':'ball_'+suffix,'goal_end_matched':True,'kind':'established ball endpoint policy; no anatomical edit'})
 rig=rig_snapshot(ik);row['rig']=rig
 expected={'Root':('root','root'),'Spine':('spine_01','spine_03'),'Neck':('neck_01','neck_01'),'Head':('head','head'),'LeftClavicle':('clavicle_l','clavicle_l'),'RightClavicle':('clavicle_r','clavicle_r'),'LeftFoot':('ball_l','ball_l'),'RightFoot':('ball_r','ball_r'),'LeftArm':('upperarm_l','hand_l'),'RightArm':('upperarm_r','hand_r'),'LeftLeg':('thigh_l','ball_l'),'RightLeg':('thigh_r','ball_r')}
 expected.update({side+digit.capitalize(): (digit+'_01_'+suffix,digit+'_03_'+suffix) for side,suffix in [('Left','l'),('Right','r')] for digit in ['thumb','index','middle','ring','pinky']})
 byname={c['name']:c for c in rig['chains']};row['expected_chain_checks']={n: n in byname and (byname[n]['start'].lower(),byname[n]['end'].lower())==pair for n,pair in expected.items()}
 # Auto characterisation can name the neck chain Head; inspect rather than assume.
 if 'Neck' not in byname and 'Head' in byname:
  row['expected_chain_checks'].pop('Neck');row['expected_chain_checks']['Head']=(byname['Head']['start'],byname['Head']['end'])==('neck_01','head')
 assert all(row['expected_chain_checks'].values()),row['expected_chain_checks']
 rt=unreal.load_asset(base+'/RTG_Manny_Lara') if unreal.EditorAssetLibrary.does_asset_exist(base+'/RTG_Manny_Lara') else T.create_asset('RTG_Manny_Lara',base,unreal.IKRetargeter,unreal.IKRetargetFactory());rc=unreal.IKRetargeterController.get_controller(rt)
 rc.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE,source);rc.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET,ik);rc.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE,source_mesh);rc.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET,mesh);rc.remove_all_ops();rc.add_default_ops();rc.auto_map_chains(unreal.AutoMapChainType.EXACT,True)
 for i in range(rc.get_num_retarget_ops()):
  if str(rc.get_op_name(i)) in ['Root Motion','Speed Plant IK Goals','Stride Warp IK Goals']:rc.set_retarget_op_enabled(i,False)
 rc.reset_retarget_pose(rc.get_current_retarget_pose_name(unreal.RetargetSourceOrTarget.TARGET),[],unreal.RetargetSourceOrTarget.TARGET);rc.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
 mapping={str(c.chain_name):str(rc.get_source_chain(c.chain_name)) for c in ic.get_retarget_chains()};assert all(mapping[n]==n for n in row['expected_chain_checks']),mapping
 row['mapping']=mapping;row['retargeter']=ret_snapshot(rt,list(mesh_snapshot(mesh)['bones']))
 for a in [ik,rt,source]:assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
 save('ik_retarget_results.json',dict(row,status='passed',assets=[ik.get_path_name(),rt.get_path_name()],measured_results={'rig':rig,'mapping':mapping,'retargeter':row['retargeter']}))
 clips={role:'/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/'+n for role,n in [('idle','MM_Idle'),('walk','MF_Walk_Fwd'),('run','MM_Run_Fwd'),('reach','JumpingJacks')]}
 inp=unreal.IKRetargetBatchOperationInputs();inp.set_editor_properties({'assets_to_retarget':[unreal.EditorAssetLibrary.find_asset_data(p) for p in clips.values()],'source_mesh':source_mesh,'target_mesh':mesh,'ik_retarget_asset':rt,'target_path':base+'/Animations','include_referenced_assets':False,'overwrite_existing_files':True});baked=unreal.IKRetargetBatchOperation.run_batch_retarget(inp);assert len(baked)==4
 paths={a.get_asset().get_name():a.get_asset() for a in baked};opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_properties({'optional_skeletal_mesh':mesh,'retrieve_additive_as_full_pose':True,'incorporate_root_motion_into_pose':True});row['clips']={}
 for role,src in clips.items():
  anim=paths[src.rsplit('/',1)[-1]];assert anim.get_editor_property('skeleton')==mesh.skeleton;assert unreal.EditorAssetLibrary.save_loaded_asset(anim,only_if_is_dirty=False);duration=anim.get_editor_property('sequence_length');row['clips'][role]={'path':anim.get_path_name(),'destination_skeleton':mesh.skeleton.get_path_name(),'duration_s':duration,'samples':61,'finite':True}
  for frame in range(61):
   pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(anim,duration*frame/60,opts);bones={str(n):{'local':t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.LOCAL)),'component':t(pose.get_bone_pose(n,unreal.AnimPoseSpaces.WORLD))} for n in pose.get_bone_names()};finite=all(math.isfinite(x) for b in bones.values() for values in b['component'].values() for x in values);assert finite
   samples.append({'role':role,'animation':anim.get_path_name(),'time_s':duration*frame/60,'fraction':frame/60,'bones':bones})
 row.update(status='passed',assets=[a.get_path_name() for a in paths.values()],measured_results={'clips':row['clips'],'pose_samples':len(samples),'all_finite':True})
except Exception:row.update(status='failed',error=traceback.format_exc())
save('animation_bake_results.json',row);save('runtime_samples.json',{'method':'Actual destination-native UE AnimPose evaluation; no live playback inferred','samples':samples})
if row['status']=='failed' and not (O/'ik_retarget_results.json').exists():save('ik_retarget_results.json',row)
out={}
for cls,methods in [('AnimationDataController',['set_number_of_frames','set_frame_rate','add_bone_track','set_bone_track_keys','remove_all_bone_tracks','open_bracket','close_bracket']),('AnimSequence',['get_controller']),('Quat',['multiply','rotator']),('AnimationBlueprintLibrary',['get_num_frames'])]:
 obj=getattr(unreal,cls,None)
 out[cls]={m:getattr(obj,m).__doc__ if obj and hasattr(obj,m) else None for m in methods}
probe_anim=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase3B/SourceAnimations/InPlace/MM_Idle')
if hasattr(probe_anim,'get_controller'):
 obj=probe_anim.get_controller();out['actual_controller']={'class':type(obj).__name__,**{m:getattr(obj,m).__doc__ if hasattr(obj,m) else None for m in ['set_number_of_frames','set_frame_rate','add_bone_track','set_bone_track_keys','remove_all_bone_tracks','open_bracket','close_bracket']}}
save('finger_animation_api.json',out)
save('animation_edit_api.json',{n:{'doc':getattr(unreal,n).__doc__,'methods':{m:getattr(getattr(unreal,n),m).__doc__ for m in dir(getattr(unreal,n)) if any(k in m for k in ['controller','model'])}} for n in ['AnimSequence','AnimationDataController']})
print('PHASE4D_RETARGET_DONE',row['status'],row.get('error'))
