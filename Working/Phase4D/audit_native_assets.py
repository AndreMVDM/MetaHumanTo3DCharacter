import sys,json,traceback
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common_d import *
B='/Game/MetaHumanTo3DCharacter/Phase4D';result={'status':'running','measured_results':{}}
try:
 mesh=unreal.load_asset(B+'/Character/SK_Lara');assert mesh
 dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD());geo=state(dm);ws,stats=weights(dm);original=json.loads((W/'accepted_skin.json').read_text())
 delta=max(abs(dict(a).get(k,0)-dict(b).get(k,0)) for a,b in zip(ws,original['weights']) for k in set(dict(a))|set(dict(b)))
 readback={'geometry_identical':geo['vertices']==original['geometry']['vertices'] and geo['triangles']==original['geometry']['triangles'],'uv_identical':geo['triangle_uv_sha256']==original['geometry']['triangle_uv_sha256'],'weights_identical':ws==original['weights'],'maximum_saved_weight_delta':delta,'weight_statistics':stats,'snapshot':mesh_snapshot(mesh)}
 assert readback['geometry_identical'] and readback['uv_identical'] and not stats['invalid_or_unweighted_vertices']
 registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True);deps=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False)
 seeds=[B+'/Character/SK_Lara',B+'/Character/SKEL_Lara',B+'/Character/BP_LaraNativePlayback',B+'/Maps/L_LaraNativePlayback']+[B+'/Character/Animations/'+n for n in ['MM_Idle','MF_Walk_Fwd','MM_Run_Fwd','JumpingJacks','MannyFingerIdentity']];seen=set();todo=seeds[:];edges={}
 while todo:
  p=todo.pop()
  if p in seen:continue
  seen.add(p);children=[str(x) for x in registry.get_dependencies(p,deps)];edges[p]=children;todo.extend(x for x in children if x not in seen)
 foreign=[p for p in seen if p.startswith('/Game/') and not p.startswith(B+'/')];authoring=[p for p in seen if '/Authoring/' in p or p.endswith('/IK_Lara') or p.endswith('/RTG_Manny_Lara') or p.endswith('/SK_Lara_Authoring')];helper=[p for p in seen if 'Phase4DTools' in p or 'Phase4ATools' in p]
 result.update(status='passed' if not foreign and not helper else 'failed',assets=seeds,measured_results={'closure':sorted(seen),'edges':edges,'foreign_game_packages':foreign,'authoring_preview_packages':authoring,'native_helper_dependencies':helper,'fresh_disk_readback':readback},limits='Hard/soft package closure and fresh UE commandlet reload; no clean-project migration or cooked executable test performed; retargeter/Manny authoring rig deliberately excluded from runtime seeds')
except Exception:result.update(status='failed',error=traceback.format_exc())
save('final_dependency_closure.json',result);print('PHASE4D_DEPENDENCY_DONE',result['status'],result.get('error'),result.get('measured_results',{}).get('foreign_game_packages'))
