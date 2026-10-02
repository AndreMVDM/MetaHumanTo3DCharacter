"""Fresh process disk reload; read-only final meshes and dependency closure."""
import sys,traceback,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common import *
B='/Game/MetaHumanTo3DCharacter/Phase4A';registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True);deps=unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False)
profile=os.environ.get('PHASE4A_JOINT_PROFILE','');suffix='_ball_forward' if profile=='BallForward' else '';folder='Assisted180'+profile;skin_suffix='_assisted_ball_forward_skin.json' if suffix else '_assisted_skin.json'
def closure(seed):
    todo=list(seed);seen=set();edges={}
    while todo:
        p=todo.pop()
        if p in seen:continue
        seen.add(p);ds=[str(n) for n in registry.get_dependencies(p,deps)];edges[p]=ds;todo.extend(ds)
    return sorted(seen),edges
rows=[];bakes=[]
for case in ['Unrigged','MixamoRecovered']:
    row={'case':case};rows.append(row)
    try:
        mesh=unreal.load_asset(B+'/'+case+'/'+folder+'/SK_Lara');dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD());s=state(dm);_,stats=weights(dm);ref=json.loads((W/(case+skin_suffix)).read_text())
        row.update({'snapshot':common.mesh_snapshot(mesh),'uv_equal_to_bound_dynamic_mesh':s['triangle_uv_sha256']==ref['geometry']['triangle_uv_sha256'],'geometry_equal_to_bound_dynamic_mesh':s['vertices']==ref['geometry']['vertices'] and s['triangles']==ref['geometry']['triangles'],'reload_state':{k:v for k,v in s.items() if k not in ['vertices','triangles']},'weight_stats':stats,'materials':[{'slot':str(x.material_slot_name),'material':x.material_interface.get_path_name() if x.material_interface else None} for x in mesh.materials]})
        seeds=[mesh.get_path_name().split('.')[0],mesh.skeleton.get_path_name().split('.')[0]]
        clips=[]
        for name in ['MM_Idle','MF_Walk_Fwd','MM_Run_Fwd','JumpingJacks']:
            anim=unreal.load_asset(B+'/'+case+'/'+folder+'/Diagnostics/Full/'+name);assert anim.get_editor_property('skeleton')==mesh.skeleton;seeds.append(anim.get_path_name().split('.')[0]);clips.append({'animation':anim.get_path_name(),'skeleton':anim.get_editor_property('skeleton').get_path_name(),'force_root_lock':anim.get_editor_property('force_root_lock')})
        all_deps,edges=closure(seeds);foreign=[d for d in all_deps if d.startswith('/Game/') and not d.startswith(B+'/')]
        bakes.append({'case':case,'clips':clips,'seeds':seeds,'closure':all_deps,'edges':edges,'foreign_game_packages':foreign,'native_plugin_dependencies':[d for d in all_deps if 'Phase4ATools' in d],'note':'AssetRegistry hard/soft package closure includes editor preview references; engine/script packages retained. Diagnostic map/BP deliberately excluded.'})
    except Exception:row['error']=traceback.format_exc()
save('disk_reload_validation'+suffix+'.json',rows);save('bake_dependencies'+suffix+'.json',bakes)
for case in ['Unrigged','MixamoRecovered']:
    for count in [64,128]:
        mesh=unreal.load_asset(B+'/'+case+'/Medial'+str(count)+'/SK_Lara');dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD());s=state(dm);ws,stats=weights(dm)
        (W/(case+'_Medial'+str(count)+'_skin.json')).write_text(json.dumps({'geometry':s,'weights':ws,'reference':common.mesh_snapshot(mesh)}))
print('DISK_AUDIT',[(r['case'],r.get('error'),r.get('uv_equal_to_bound_dynamic_mesh'),r.get('geometry_equal_to_bound_dynamic_mesh')) for r in rows]);print('FOREIGN_DEPENDENCIES',[(r['case'],r['foreign_game_packages']) for r in bakes])
