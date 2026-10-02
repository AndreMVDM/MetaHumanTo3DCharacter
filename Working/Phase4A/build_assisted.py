"""Geometry-landmark control: manually authored joint positions, UE skeleton authoring and automatic weights.
This is an assisted control and MUST NOT be reported as automatic humanoid joint placement.
"""
import sys,traceback,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common import *
T=unreal.AssetToolsHelpers.get_asset_tools();rows=[];target_height=float(os.environ.get('PHASE4A_TARGET_HEIGHT_CM','180'));assert 20<=target_height<=300 and math.isfinite(target_height)
profile=os.environ.get('PHASE4A_JOINT_PROFILE','');assert profile in ['', 'BallForward'];suffix='_ball_forward' if profile else ''
def landmarks(height):
    f=height/180;out=[('pelvis','root',(0,0,100)),('spine_01','pelvis',(0,0,112)),('spine_02','spine_01',(0,0,125)),('spine_03','spine_02',(0,0,138)),('neck_01','spine_03',(0,0,150)),('head','neck_01',(0,0,161))]
    for side,s in [('l',1),('r',-1)]:
        out += [('clavicle_'+side,'spine_03',(s*9,0,141)),('upperarm_'+side,'clavicle_'+side,(s*18,0,139)),('lowerarm_'+side,'upperarm_'+side,(s*25,0,121)),('hand_'+side,'lowerarm_'+side,(s*31,0,102)),('thigh_'+side,'pelvis',(s*11,0,97)),('calf_'+side,'thigh_'+side,(s*16,1,55)),('foot_'+side,'calf_'+side,(s*18,0,12)),('ball_'+side,'foot_'+side,(s*18,-10,4))]
        for finger,x in [('thumb',29),('index',30.5),('middle',32),('ring',33.5),('pinky',35)]:
            for j,z in enumerate([96,91,87],1):out.append((finger+'_%02d_'%j+side,'hand_'+side if j==1 else finger+'_%02d_'%(j-1)+side,(s*x,-2 if finger=='thumb' else 0,z)))
    if profile=='BallForward':out=[(n,p,(xyz[0],10,xyz[2]) if n.startswith('ball_') else xyz) for n,p,xyz in out]
    return [(n,p,tuple(v*f for v in xyz)) for n,p,xyz in out]
for case in ['Unrigged','MixamoRecovered']:
    row={'case':case,'height_cm':target_height,'method':'ASSISTED CONTROL: manually chosen geometry landmarks, independent 53-bone hierarchy; UE SkeletonModifier and GeodesicVoxel skinning; no imported rig/weights'};rows.append(row)
    try:
        base='/Game/MetaHumanTo3DCharacter/Phase4A/'+case+'/Assisted'+format(target_height,'g')+profile;static=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase4A/'+case+'/Geometry/SM_Lara');dm=copy_static(static);factor=target_height/(2*static.get_bounds().box_extent.z);unreal.GeometryScript_MeshTransforms.scale_mesh(dm,unreal.Vector(factor,factor,factor));before=state(dm);row['before']={k:v for k,v in before.items() if k not in ['vertices','triangles']}
        sk=unreal.Phase4ALibrary.create_blank_skeleton(base+'/SKEL_Lara');unreal.GeometryScript_BoneWeights.copy_bones_from_skeleton(sk,dm);unreal.GeometryScript_BoneWeights.compute_smooth_bone_weights(dm,sk,unreal.GeometryScriptSmoothBoneWeightsOptions())
        options=unreal.GeometryScriptCreateNewSkeletalMeshAssetOptions();options.set_editor_properties({'materials':{x.material_slot_name:x.material_interface for x in static.static_materials},'use_original_vertex_order':True})
        mesh,outcome=unreal.GeometryScript_NewAssetUtils.create_new_skeletal_mesh_asset_from_mesh(dm,sk,base+'/SK_Lara_Authoring',options);assert mesh,outcome
        mod=unreal.SkeletonModifier();assert mod.set_skeletal_mesh(mesh);coords={'root':(0,0,0)};lm=landmarks(row['height_cm']);row['authored_landmarks_cm']=lm
        for n,p,xyz in lm:
            coords[n]=xyz;local=tuple(x-y for x,y in zip(xyz,coords[p]));assert mod.add_bone(n,p,unreal.Transform(location=unreal.Vector(*local)))
        orient=unreal.OrientOptions();orient.set_editor_property('orient_children',True);assert mod.orient_bone('pelvis',orient);assert mod.commit_skeleton_to_skeletal_mesh()
        dm=unreal.DynamicMesh();unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD())
        bind=unreal.GeometryScriptSmoothBoneWeightsOptions();bind.set_editor_properties({'distance_weighing_type':unreal.GeometryScriptSmoothBoneWeightsType.GEODESIC_VOXEL,'max_influences':5,'voxel_resolution':128,'stiffness':0.2});unreal.GeometryScript_BoneWeights.compute_smooth_bone_weights(dm,mesh.skeleton,bind)
        after=state(dm);row['after']={k:v for k,v in after.items() if k not in ['vertices','triangles']};row['geometry_identical']=before['vertices']==after['vertices'] and before['triangles']==after['triangles'];row['uv_identical']=before['triangle_uv_sha256']==after['triangle_uv_sha256'];assert row['geometry_identical'] and row['uv_identical']
        skin,stats=weights(dm);row['weight_statistics']=stats
        options.set_editor_property('use_mesh_bone_proportions',True);final,outcome=unreal.GeometryScript_NewAssetUtils.create_new_skeletal_mesh_asset_from_mesh(dm,mesh.skeleton,base+'/SK_Lara',options);assert final,outcome
        row['snapshot']=common.mesh_snapshot(final);row['parents']={str(n):str(mod.get_parent_name(n)) for n in mod.get_all_bone_names()};row['material_slots']=[str(s.material_slot_name) for s in final.materials];row['materials']=[s.material_interface.get_path_name() if s.material_interface else None for s in final.materials]
        for a in [mesh,final,final.skeleton]:assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
        (W/(case+'_assisted'+suffix+'_skin.json')).write_text(json.dumps({'geometry':after,'weights':skin,'reference':row['snapshot'],'parents':row['parents']}))
    except Exception:row['error']=traceback.format_exc()
    save('assisted_candidates'+suffix+'.json',rows)
print('ASSISTED_DONE',[(r['case'],r.get('error')) for r in rows])
