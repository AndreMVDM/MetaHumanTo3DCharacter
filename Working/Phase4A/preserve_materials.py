import unreal,json,traceback
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4A';O=P/'Documentation/Phase4A';T=unreal.AssetToolsHelpers.get_asset_tools();rows=[]
for case in ['Unrigged','MixamoRecovered']:
    row={'case':case};rows.append(row)
    try:
        base='/Game/MetaHumanTo3DCharacter/Phase4A/'+case+'/PreservedSource'
        src=next((W/'Inputs'/case).glob('*.fbx'))
        options=unreal.FbxImportUI();options.set_editor_properties({'import_as_skeletal':False,'mesh_type_to_import':unreal.FBXImportType.FBXIT_STATIC_MESH,'import_animations':False,'import_materials':True,'import_textures':True})
        options.static_mesh_import_data.set_editor_properties({'convert_scene':True,'convert_scene_unit':True,'import_uniform_scale':1.0,'combine_meshes':True,'auto_generate_collision':False,'generate_lightmap_u_vs':False})
        task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(src),'destination_path':base,'destination_name':'SM_Lara_Source','automated':True,'save':False,'replace_existing':False,'options':options,'factory':unreal.FbxFactory()});T.import_asset_tasks([task]);mesh=next(unreal.load_asset(p) for p in task.imported_object_paths if isinstance(unreal.load_asset(p),unreal.StaticMesh));row['source_mesh']=mesh.get_path_name();row['materials']=[]
        slots=mesh.static_materials
        for slot in slots:
            m=slot.material_interface;assert m
            tex=unreal.MaterialEditingLibrary.get_used_textures(m);row['materials'].append({'slot':str(slot.material_slot_name),'material':m.get_path_name(),'textures':[t.get_path_name() for t in tex]})
            for t in tex:assert unreal.EditorAssetLibrary.save_loaded_asset(t,only_if_is_dirty=False)
            assert unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
        target=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase4A/'+case+'/Geometry/SM_Lara');target.set_editor_property('static_materials',slots);assert unreal.EditorAssetLibrary.save_loaded_asset(target,only_if_is_dirty=False)
        row['height_mesh']=target.get_path_name();row['source_height_cm']=2*mesh.get_bounds().box_extent.z
    except Exception:row['error']=traceback.format_exc()
    (O/'material_import_results.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('MATERIAL_PRESERVATION',rows)
