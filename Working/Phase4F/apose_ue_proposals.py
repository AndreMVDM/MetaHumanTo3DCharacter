"""Established Phase4C/4D automatic donor route, with zero human acceptance."""
import unreal, sys, json, time, traceback, hashlib
from pathlib import Path
sys.dont_write_bytecode=True
P=Path('E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4F';O=P/'Documentation/Phase4F';B='/Game/MetaHumanTo3DCharacter/Phase4F'
def save(name,data):(O/name).write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')
def xyz(v):return [v.x,v.y,v.z]
sub=unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
results=[]
for character in ['John','Jane']:
    base=B+'/'+character;cw=W/character; r={'character':character,'stage':'started','human_reviews':0,'downstream_authorised':False};results.append(r)
    try:
        options=unreal.FbxImportUI();options.set_editor_properties({'import_as_skeletal':False,'mesh_type_to_import':unreal.FBXImportType.FBXIT_STATIC_MESH,'import_animations':False,'import_materials':True,'import_textures':True})
        options.static_mesh_import_data.set_editor_properties({'convert_scene':True,'convert_scene_unit':True,'import_uniform_scale':1.0,'combine_meshes':True,'auto_generate_collision':False,'generate_lightmap_u_vs':False})
        task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(cw/'Target180.fbx'),'destination_path':base+'/Geometry','destination_name':'SM_'+character+'180','automated':True,'save':True,'replace_existing':False,'options':options,'factory':unreal.FbxFactory()})
        suffix='_FrameVerified' if character=='Bill' else ''
        task.destination_name='SM_'+character+'180'+suffix
        path=base+'/Geometry/SM_'+character+'180'+suffix
        assert not unreal.EditorAssetLibrary.does_asset_exist(path),'Refuse silent proposal reimport'
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        mesh=unreal.load_asset(path);assert isinstance(mesh,unreal.StaticMesh)
        verts,indices=sub.get_mesh_data_for_conforming(mesh)
        (cw/'ue_target_geometry.json').write_text(json.dumps({'vertices_cm':[xyz(v) for v in verts],'triangle_indices':list(indices)}))
        r.update(target_mesh=path,vertices=len(verts),triangles=len(indices)//3,height_cm=2*mesh.get_bounds().box_extent.z)
        assert abs(r['height_cm']-180)<.02
        char=unreal.AssetToolsHelpers.get_asset_tools().create_asset('MHC_'+character+'Donor',base+'/Authoring',unreal.MetaHumanCharacter,unreal.MetaHumanCharacterFactoryNew())
        assert char and sub.try_add_object_to_edit(char)
        params=unreal.ConformTargetParams();target=unreal.ConformTargetMesh();target.target_parts_type=unreal.TargetPartsType.COMBINED;target.body_vertices=verts;target.body_vertex_indices=indices
        params.conform_target_mesh=target;params.auto_solve=True;params.estimate_body_joints_from_mesh=True
        settings=unreal.BodyConformSolveSettings();settings.pipeline_name='combined';settings.face_iterations=0;params.body_conform_solve_settings=settings
        key=unreal.MetaHumanCharacterTargetMeshKey();key.combined_mesh=mesh
        r['stage']='solving';save('APoseContinuation/automatic_proposal_execution.json',results);start=time.monotonic()
        r['solve_success']=bool(sub.conform_to_target_meshes(char,key,params));r['solve_seconds']=time.monotonic()-start
        assert r['solve_success'],'Donor solve returned false'
        assert unreal.EditorAssetLibrary.save_loaded_asset(char)
        donor=cw/'Donor';donor.mkdir(exist_ok=True)
        exp=unreal.MetaHumanPosedDNAExportParams();exp.target_mesh_key=key;exp.external_path=str(donor);exp.project_path='';exp.asset_name=character+'_Posed';exp.overwrite_existing_assets=False
        unreal.MetaHumanCharacterExportBlueprintLibrary.export_posed_dna(char,exp)
        dna=donor/(character+'_Posed.dna');assert dna.is_file()
        data=json.loads(unreal.Phase4CLibrary.inspect_posed_dna(str(dna)));assert not data.get('error'),data
        (cw/'donor_geometry_and_joints.json').write_text(json.dumps(data))
        code,joints,rots=sub.get_joints_for_body_conforming_from_dna(str(dna))
        assert len(joints)==len(data['joints'])
        delta=max(sum((a-b)**2 for a,b in zip(xyz(q),row['world_cm']))**.5 for q,row in zip(joints,data['joints']))
        assert delta<1e-6
        save(character+'/solved_donor_joints.json',{k:v for k,v in data.items() if k!='meshes_lod0'})
        r.update(stage='proposal_extracted',joint_count=len(data['joints']),python_api_code=str(code),python_native_max_cm=delta,dna_sha256=hashlib.sha256(dna.read_bytes()).hexdigest(),donor_asset=char.get_path_name())
        for a in unreal.EditorAssetLibrary.list_assets(base,recursive=True,include_folder=False):
            assert a.startswith(base+'/');unreal.EditorAssetLibrary.save_asset(a)
    except Exception:
        r['stage']='failed';r['error']=traceback.format_exc()
    save('APoseContinuation/automatic_proposal_execution.json',results)
    print('PHASE4F_PROPOSAL',r,flush=True)
if any(r['stage']=='failed' for r in results):raise RuntimeError('At least one automatic proposal failed; inspect evidence')
