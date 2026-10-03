"""Read-only source/destination UV, material and final dependency certification."""
import unreal, json, hashlib, sys, traceback
from pathlib import Path
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent; R=W.parents[4]
O=R/'Documentation/Phase4F/Benchmark/Runs/02_AegisNX7/R3'
sys.path.insert(0,str(W))
from runtime_appearance_closure import certify_native
result=dict(status='RUNNING',assets_saved=False)
try:
    A=json.loads((O/'Initial/authoring_result.json').read_text())
    source=json.loads((O/'import_inspection.json').read_text())['native']['mesh']
    def uv(mesh):
        dm=unreal.DynamicMesh()
        unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dm,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL,lod_index=0))
        count=unreal.GeometryScript_MeshQueries.get_num_uv_sets(dm)
        triangles=unreal.GeometryScript_MeshQueries.get_num_triangle_i_ds(dm)
        hashes=[]
        for layer in range(count):
            data=[]
            for i in range(triangles):
                a,b,c,ok=unreal.GeometryScript_MeshQueries.get_triangle_u_vs(dm,layer,i)
                assert ok,'missing triangle UV'
                data.append([[p.x,p.y] for p in [a,b,c]])
            hashes.append(hashlib.sha256(json.dumps(data).encode()).hexdigest())
        slots=[dict(name=str(s.material_slot_name),material=s.material_interface.get_path_name() if s.material_interface else None) for s in mesh.materials]
        return dict(uv_sets=count,triangle_uv_sha256=hashes,material_slots=slots)
    src=uv(unreal.load_asset(source)); dst=uv(unreal.load_asset(A['assets']['mesh']))
    assert src==dst,'appearance data changed'
    reg=unreal.AssetRegistryHelpers.get_asset_registry(); reg.search_all_assets(True)
    certificates={}
    for run in ['Corrected','FemaleRegression']:
        N=json.loads((O/run/'native_playback.json').read_text())
        C=N['runtime_dependency_closure']
        cert=certify_native(unreal.load_asset(N['assets']['mesh']),C['seeds'],C['packages'],C['edges'],reg)
        assert cert['status']=='PASS',cert
        certificates[run]=cert
    result.update(status='PASS',source=src,destination=dst,appearance_exactly_preserved=True,final_policy_certificates=certificates,helper_sha256=hashlib.sha256((W/'runtime_appearance_closure.py').read_bytes()).hexdigest())
except Exception:
    result.update(status='FAIL',error=traceback.format_exc())
(O/'appearance_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print('R3_APPEARANCE_AUDIT',result['status'],result.get('error',''))
