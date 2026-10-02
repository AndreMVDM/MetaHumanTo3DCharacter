"""Author only Phase4B STATIC debug assets. Never constructs a rejected skeletal rig."""
import unreal,json,traceback,hashlib
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4B';O=P/'Documentation/Phase4B'
B='/Game/MetaHumanTo3DCharacter/Phase4B';T=unreal.AssetToolsHelpers.get_asset_tools();result={'errors':[],'skeletal_assets_authored':0,'proposal':'automatic_fit_v2.json'}
try:
    gate=json.loads((O/'anatomical_validation_v2.json').read_text());assert not gate['downstream_authorised'],'This script is a rejected-proposal static visualisation only'
    mesh=unreal.load_asset(B+'/Geometry/SM_Lara180')
    if True: # Reimport exclusively this Phase4B working asset after coordinate repair.
        options=unreal.FbxImportUI();options.set_editor_properties({'automated_import_should_detect_type':False,'import_as_skeletal':False,'mesh_type_to_import':unreal.FBXImportType.FBXIT_STATIC_MESH,'import_animations':False,'import_materials':False,'import_textures':False})
        options.static_mesh_import_data.set_editor_properties({'convert_scene':True,'convert_scene_unit':True,'import_uniform_scale':1.0,'combine_meshes':True,'auto_generate_collision':False,'generate_lightmap_u_vs':False})
        task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(W/'Lara_180_DebugGeometry.fbx'),'destination_path':B+'/Geometry','destination_name':'SM_Lara180','automated':True,'save':True,'replace_existing':True,'options':options,'factory':unreal.FbxFactory()});T.import_asset_tasks([task])
        mesh=next(unreal.load_asset(p) for p in task.imported_object_paths if isinstance(unreal.load_asset(p),unreal.StaticMesh))
    assert isinstance(mesh,unreal.StaticMesh)
    tex=unreal.load_asset(B+'/Materials/T_LaraOriginal')
    if not tex:
        src=next((W/'Inputs').rglob('*.jpg'),None) or next((W/'Inputs').rglob('*.png'))
        task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(src),'destination_path':B+'/Materials','destination_name':'T_LaraOriginal','automated':True,'save':True,'replace_existing':False});T.import_asset_tasks([task]);tex=unreal.load_asset(B+'/Materials/T_LaraOriginal')
        result['texture_source']=str(src);result['texture_source_sha256']=hashlib.sha256(src.read_bytes()).hexdigest()
    ML=unreal.MaterialEditingLibrary
    def material(name,colour=None,texture=None,opacity=None):
        path=B+'/Materials/'+name;m=unreal.load_asset(path)
        if not m:
            m=T.create_asset(name,B+'/Materials',unreal.Material,unreal.MaterialFactoryNew());m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);m.set_editor_property('two_sided',True)
            if texture:
                node=ML.create_material_expression(m,unreal.MaterialExpressionTextureSample,0,0);node.set_editor_property('texture',texture);ML.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
            else:
                node=ML.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,0,0);node.set_editor_property('constant',unreal.LinearColor(*colour,1));ML.connect_material_property(node,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
            if opacity is not None:
                m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);node=ML.create_material_expression(m,unreal.MaterialExpressionConstant,0,150);node.set_editor_property('r',opacity);ML.connect_material_property(node,'',unreal.MaterialProperty.MP_OPACITY)
            ML.recompile_material(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
        return m
    original=material('M_LaraOriginal',texture=tex);ghost=material('M_Ghost',(.45,.55,.65),opacity=.15);green=material('M_Accepted',(.03,.7,.2));amber=material('M_Ambiguous',(.95,.45,.015));edge=material('M_Edges',(.12,.3,.5))
    for i in range(len(mesh.static_materials)):mesh.set_material(i,original)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
    # Numerical readback of UE source geometry with build settings disabled.
    dm=unreal.DynamicMesh();opts=unreal.GeometryScriptCopyMeshFromAssetOptions();opts.set_editor_property('apply_build_settings',False);unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dm,opts,unreal.GeometryScriptMeshReadLOD())
    Q=unreal.GeometryScript_MeshQueries;vertices=[]
    for i in range(Q.get_num_vertex_i_ds(dm)):
        p,ok=Q.get_vertex_position(dm,i)
        if ok:vertices.append([p.x,p.y,p.z])
    (W/'ue_debug_vertices.json').write_text(json.dumps(vertices))
    b=mesh.get_bounds();result.update({'mesh':mesh.get_path_name(),'height_cm':2*b.box_extent.z,'triangles':dm.get_triangle_count(),'uv_sets':Q.get_num_uv_sets(dm),'vertex_count':len(vertices),'material':original.get_path_name(),'geometry_scale_baked':True})
    assert abs(result['height_cm']-180)<.02
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(B+'/Maps/L_SemanticFitDebug'):assert level.load_level(B+'/Maps/L_SemanticFitDebug')
    else:assert level.new_level(B+'/Maps/L_SemanticFitDebug')
    A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(B+'/Maps/')
    for old in A.get_all_level_actors():assert A.destroy_actor(old)
    def actor(label,asset,pos,scale,mat):
        a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos),unreal.Rotator());a.set_actor_label(label);a.static_mesh_component.set_static_mesh(asset);a.static_mesh_component.set_material(0,mat);a.set_actor_scale3d(unreal.Vector(*scale));return a
    actor('Original textured surface - normalised 180cm',mesh,[-65,0,0],[1,1,1],original)
    actor('REJECTED proposal - translucent surface',mesh,[65,0,0],[1,1,1],ghost)
    sphere=unreal.load_asset('/Engine/BasicShapes/Sphere');cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder');fit=json.loads((O/'automatic_fit_v2.json').read_text());j={r['role']:r for r in fit['joints']}
    for n,r in j.items():
        pos=r['position_cm'];actor(n+' - '+r['status'],sphere,[pos[0]+65,pos[1],pos[2]],[.018]*3,green if r['status']=='automatically_accepted' else amber)
        if r['parent_role']:
            parent=j[r['parent_role']]['position_cm'];delta=unreal.Vector(*(pos[k]-parent[k] for k in range(3)));length=delta.length();mid=[(pos[k]+parent[k])/2 for k in range(3)];mid[0]+=65;a=actor('debug edge '+r['parent_role']+' to '+n,cylinder,mid,[.005,.005,length/100],edge);a.set_actor_rotation(unreal.MathLibrary.make_rot_from_z(delta),False)
    result['map']=B+'/Maps/L_SemanticFitDebug';result['debug_actor_count']=len(A.get_all_level_actors());assert level.save_current_level()
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(0,340,90),unreal.Rotator(pitch=0,yaw=-90,roll=0))
    result['assets']=list(unreal.EditorAssetLibrary.list_assets(B,recursive=True))
except Exception:result['errors'].append(traceback.format_exc())
(O/'ue_debug_scene.json').write_text(json.dumps(result,indent=2));print('PHASE4B_DEBUG_SCENE',result)
