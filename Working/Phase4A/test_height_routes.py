"""Compare re-binding after scale against coordinated scaling of already bound own assets."""
import sys,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common import *
T=unreal.AssetToolsHelpers.get_asset_tools();B='/Game/MetaHumanTo3DCharacter/Phase4A';rows=[]
def run(case,height,route):
    r={'case':case,'height_cm':height,'route':route};rows.append(r)
    try:
        source=unreal.load_asset(B+'/'+case+'/Assisted180/SK_Lara');f=height/(2*source.get_bounds().box_extent.z);base=B+'/'+case+'/HeightOrdering/Corrected'+route+str(height)
        sk=T.duplicate_asset('SKEL_Lara',base,source.skeleton);assert sk
        dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(source,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD());before=state(dm);before_weights,_=weights(dm)
        initial_options=unreal.GeometryScriptCreateNewSkeletalMeshAssetOptions();initial_options.set_editor_properties({'materials':{s.material_slot_name:s.material_interface for s in source.materials},'use_original_vertex_order':True,'use_mesh_bone_proportions':True})
        author,outcome=unreal.GeometryScript_NewAssetUtils.create_new_skeletal_mesh_asset_from_mesh(dm,sk,base+'/SK_Lara_Authoring',initial_options);assert author,outcome
        mod=unreal.SkeletonModifier();assert mod.set_skeletal_mesh(author);names=mod.get_all_bone_names();transforms=[]
        for n in names:
            tr=mod.get_bone_transform(n,False);tr.translation=tr.translation*f;transforms.append(tr)
        assert mod.set_bones_transforms(names,transforms,True);assert mod.commit_skeleton_to_skeletal_mesh()
        assert unreal.Phase4ALibrary.sync_skeleton_reference(author)
        unreal.GeometryScript_MeshTransforms.scale_mesh(dm,unreal.Vector(f,f,f));unreal.GeometryScript_BoneWeights.copy_bones_from_skeleton(author.skeleton,dm)
        if route=='ScaleThenBind':
            bind=unreal.GeometryScriptSmoothBoneWeightsOptions();bind.set_editor_properties({'distance_weighing_type':unreal.GeometryScriptSmoothBoneWeightsType.GEODESIC_VOXEL,'max_influences':5,'voxel_resolution':128,'stiffness':.2});unreal.GeometryScript_BoneWeights.compute_smooth_bone_weights(dm,author.skeleton,bind)
        after=state(dm);ws,stats=weights(dm);opts=unreal.GeometryScriptCreateNewSkeletalMeshAssetOptions();opts.set_editor_properties({'materials':{s.material_slot_name:s.material_interface for s in source.materials},'use_original_vertex_order':True,'use_mesh_bone_proportions':True})
        final,outcome=unreal.GeometryScript_NewAssetUtils.create_new_skeletal_mesh_asset_from_mesh(dm,author.skeleton,base+'/SK_Lara',opts);assert final,outcome
        for a in [final,author,final.skeleton]:assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
        snap=common.mesh_snapshot(final);original=common.mesh_snapshot(source);bone_error=max(math.dist([x*f for x in original['bones'][n]['component']['translation']],snap['bones'][n]['component']['translation']) for n in original['bones']);assert bone_error<.001
        r.update({'snapshot':snap,'max_bone_translation_scale_error_cm':bone_error,'uv_identical':before['triangle_uv_sha256']==after['triangle_uv_sha256'],'triangles_identical':before['triangles']==after['triangles'],'weight_stats':stats,'weights_identical':before_weights==ws,'max_geometry_scale_error_cm':max(math.dist([v*f for v in a],b) for a,b in zip(before['vertices'],after['vertices'])),'weight_max_absolute_delta':max(abs(dict(a).get(k,0)-dict(b).get(k,0)) for a,b in zip(before_weights,ws) for k in set(dict(a))|set(dict(b)))})
    except Exception:r['error']=traceback.format_exc()
    save('height_ordering_results.json',rows)
for case in ['Unrigged','MixamoRecovered']:
    for route in ['ScaleThenBind','BindThenScale']:run(case,175,route)
print('HEIGHT_ROUTES_DONE',[(r['case'],r['route'],r.get('error')) for r in rows])
