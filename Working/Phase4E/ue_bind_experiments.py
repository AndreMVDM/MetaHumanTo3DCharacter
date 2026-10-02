import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ue_common import *
result={'status':'running','candidates':[]}
try:
    mesh=unreal.load_asset(B+'/Character/SK_Lara');assert mesh
    # Bone indices and reference geometry remain those of accepted Lara.
    configs=[('direct_02_5',False,128,.2,5),('direct_08_4',False,128,.8,4),('geo128_08_4',True,128,.8,4),('geo256_02_5',True,256,.2,5),('geo256_06_4',True,256,.6,4),('geo128_02_8',True,128,.2,8)]
    for name,geodesic,res,stiff,count in configs:
        out=W/(name+'_weights.json')
        if out.exists():continue
        dm=dm_from(mesh);opt=unreal.GeometryScriptSmoothBoneWeightsOptions()
        opt.set_editor_properties({'distance_weighing_type':unreal.GeometryScriptSmoothBoneWeightsType.GEODESIC_VOXEL if geodesic else unreal.GeometryScriptSmoothBoneWeightsType.DIRECT_DISTANCE,'voxel_resolution':res,'stiffness':stiff,'max_influences':count})
        start=time.monotonic();unreal.GeometryScript_BoneWeights.compute_smooth_bone_weights(dm,mesh.skeleton,opt);ws=weights(dm)
        out.write_text(json.dumps(ws,allow_nan=False));row={'name':name,'seconds':time.monotonic()-start,'method':'GEODESIC_VOXEL' if geodesic else 'DIRECT_DISTANCE','resolution':res,'stiffness':stiff,'max_influences':count,'stats':stats(ws)}
        result['candidates'].append(row);save('ue_binding_experiments.json',result);print('BIND_CANDIDATE',name,row['seconds'])
    result['status']='passed'
except Exception:result.update(status='failed',error=traceback.format_exc())
save('ue_binding_experiments.json',result);print('PHASE4E_BIND',result['status'],result.get('error'))
