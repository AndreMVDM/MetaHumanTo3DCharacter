import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
out={'components':[],'errors':[]}
try:
    bp=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase3B/BP_Phase3B_LiveTest')
    ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);fn=unreal.SubobjectDataBlueprintFunctionLibrary
    rows=json.loads((O/'live_scene.json').read_text())['components']
    for handle in ss.k2_gather_subobject_data_for_blueprint(bp):
        d=fn.get_data(handle);c=fn.get_object_for_blueprint(d,bp)
        if not isinstance(c,unreal.SkeletalMeshComponent):continue
        name=str(fn.get_variable_name(d));row=next((r for r in rows if r['name']==name),None)
        if not row:continue
        before=str(c.get_skeletal_mesh_asset());mesh=unreal.load_asset(row['mesh']);c.set_skeletal_mesh_asset(mesh)
        assert c.get_skeletal_mesh_asset()==mesh
        if row['clip']:c.override_animation_data(unreal.load_asset(row['clip']),True,True,0,1)
        elif row['anim_bp']:c.set_anim_instance_class(unreal.load_asset(row['anim_bp']).generated_class())
        out['components'].append({'name':name,'before':before,'after':str(c.get_skeletal_mesh_asset())})
    unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
except Exception:out['errors'].append(traceback.format_exc())
save('live_repair.json',out)
