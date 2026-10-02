import unreal,json,traceback,sys,hashlib,collections
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4A';O=P/'Documentation/Phase4A'
sys.dont_write_bytecode=True;sys.path.insert(0,str(P/'Working/Phase3B'));import common
T=unreal.AssetToolsHelpers.get_asset_tools();rows=[]
def save(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
def snapshot(dm):
    Q=unreal.GeometryScript_MeshQueries;U=unreal.GeometryScript_UVs
    info={'vertex_id_count':Q.get_num_vertex_i_ds(dm),'triangles':dm.get_triangle_count(),'uv_sets':Q.get_num_uv_sets(dm)}
    uv=[]
    if info['uv_sets']:
        for i in range(dm.get_triangle_count()):
            _,ids,valid=U.get_mesh_triangle_uv_element_i_ds(dm,0,i)
            if valid:
                uv.append([[round(U.get_mesh_uv_element_position(dm,0,j)[1].x,7),round(U.get_mesh_uv_element_position(dm,0,j)[1].y,7)] for j in [ids.x,ids.y,ids.z]])
    info['triangle_uv_sha256']=hashlib.sha256(json.dumps(uv).encode()).hexdigest();return info
for case in ['Unrigged','MixamoRecovered']:
    for count in [64,128]:
        row={'case':case,'max_spheres':count,'method':'Installed FSkeletonViaSampling.ComputeSkeleton and CreateSkinWeightsFromMedialSkeleton; thin native wrapper, no authored bone locations or source skeleton'};rows.append(row)
        try:
            base='/Game/MetaHumanTo3DCharacter/Phase4A/'+case+'/Medial'+str(count);static=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase4A/'+case+'/Geometry/SM_Lara')
            dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(static,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD());row['before']=snapshot(dm)
            row['generated']=unreal.Phase4ALibrary.generate_medial_rig(dm,count,0.1,5,False,128);assert row['generated'];row['after']=snapshot(dm);assert row['before']==row['after']
            bones=unreal.GeometryScript_BoneWeights.get_all_bones_info(dm)[1];row['bone_info']=[str(b) for b in bones]
            sk=unreal.Phase4ALibrary.create_blank_skeleton(base+'/SKEL_Lara');assert sk
            options=unreal.GeometryScriptCreateNewSkeletalMeshAssetOptions();options.set_editor_properties({'use_mesh_bone_proportions':True,'use_original_vertex_order':True,'materials':{x.material_slot_name:x.material_interface for x in static.static_materials}})
            mesh,outcome=unreal.GeometryScript_NewAssetUtils.create_new_skeletal_mesh_asset_from_mesh(dm,sk,base+'/SK_Lara',options);assert mesh,outcome
            unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False);unreal.EditorAssetLibrary.save_loaded_asset(sk,only_if_is_dirty=False)
            row['snapshot']=common.mesh_snapshot(mesh);mod=unreal.SkeletonModifier();mod.set_skeletal_mesh(mesh);row['parents']={str(n):str(mod.get_parent_name(n)) for n in mod.get_all_bone_names()}
            weights=[];hist=collections.Counter();bad=[]
            for vid in range(row['before']['vertex_id_count']):
                _,ws,valid=unreal.GeometryScript_BoneWeights.get_vertex_bone_weights(dm,vid);pairs=[[x.bone_index,x.weight] for x in ws];weights.append(pairs);hist[len(pairs)]+=1
                if not valid or abs(sum(x[1] for x in pairs)-1)>0.001:bad.append(vid)
            row['weights']={'influence_histogram':dict(hist),'invalid_or_unweighted_vertices':bad};(W/(case+'_Medial'+str(count)+'_weights.json')).write_text(json.dumps(weights))
            ik=T.create_asset('IK_Lara',base,unreal.IKRigDefinition,unreal.IKRigDefinitionFactory());ic=unreal.IKRigController.get_controller(ik);ic.set_skeletal_mesh(mesh);row['auto_characterisation']=ic.apply_auto_generated_retarget_definition();row['auto_fbik']=ic.apply_auto_fbik() if row['auto_characterisation'] else False;row['ik_snapshot']=common.rig_snapshot(ik);unreal.EditorAssetLibrary.save_loaded_asset(ik,only_if_is_dirty=False)
        except Exception:row['error']=traceback.format_exc()
        save('medial_trials.json',rows)
print('PHASE4A_MEDIAL_DONE',[(r['case'],r['max_spheres'],r.get('auto_characterisation'),r.get('error')) for r in rows])
