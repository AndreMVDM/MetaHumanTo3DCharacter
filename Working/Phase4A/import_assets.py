import unreal,json,traceback
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4A';O=P/'Documentation/Phase4A';T=unreal.AssetToolsHelpers.get_asset_tools()
rows=[]
for case in ['MixamoRecovered','Unrigged']:
    row={'case':case};rows.append(row)
    try:
        base='/Game/MetaHumanTo3DCharacter/Phase4A/'+case
        options=unreal.FbxImportUI();options.set_editor_properties({'import_as_skeletal':False,'mesh_type_to_import':unreal.FBXImportType.FBXIT_STATIC_MESH,'import_animations':False,'import_materials':True,'import_textures':True})
        options.static_mesh_import_data.set_editor_properties({'convert_scene':True,'convert_scene_unit':True,'import_uniform_scale':1.0,'combine_meshes':True,'auto_generate_collision':False,'generate_lightmap_u_vs':False})
        task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(W/'Geometry'/case/'Lara_Geometry.fbx'),'destination_path':base+'/Geometry','destination_name':'SM_Lara','automated':True,'save':True,'replace_existing':True,'options':options,'factory':unreal.FbxFactory()})
        T.import_asset_tasks([task]);row['imported_paths']=list(task.imported_object_paths)
        mesh=next(unreal.load_asset(p) for p in task.imported_object_paths if isinstance(unreal.load_asset(p),unreal.StaticMesh));b=mesh.get_bounds();row.update({'mesh':mesh.get_path_name(),'bounds_cm':{'origin':[b.origin.x,b.origin.y,b.origin.z],'extent':[b.box_extent.x,b.box_extent.y,b.box_extent.z]},'height_cm':2*b.box_extent.z,'material_slots':[str(x.material_slot_name) for x in mesh.static_materials],'materials':[x.material_interface.get_path_name() if x.material_interface else None for x in mesh.static_materials]})
        dm=unreal.DynamicMesh();result=unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD());row['copy_outcome']=str(result[-1]);row['triangles']=dm.get_triangle_count();row['uv_channel_count']=unreal.GeometryScript_MeshQueries.get_num_uv_sets(dm)
        row['saved_assets']=[]
        for p in unreal.EditorAssetLibrary.list_assets(base+'/Geometry',recursive=True):
            a=unreal.load_asset(p);assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False);row['saved_assets'].append(p)
    except Exception:row['error']=traceback.format_exc()
    (O/'import_results.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
docs={}
for n in dir(unreal):
    if n.startswith('GeometryScript_') or n.startswith('Dataflow'):
        if any(x in n for x in ['UV','MeshQueries','MeshTransform','Dataflow']):
            c=getattr(unreal,n);docs[n]={'doc':c.__doc__,'methods':{k:getattr(c,k).__doc__ for k in dir(c) if any(x in k for x in ['uv','vertex','triangle','evaluate','graph','node'])}}
(O/'additional_python_apis.json').write_text(json.dumps(docs,indent=2),encoding='utf-8');print('PHASE4A_IMPORT_DONE',rows)
