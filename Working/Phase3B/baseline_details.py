import sys,traceback
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
b=json.loads((O/'baseline_import.json').read_text())
for name,row in b['variants'].items():
    mesh=unreal.load_asset(row['mesh']);data=mesh.get_editor_property('asset_import_data')
    row['stored_pipelines']=[]
    for pipeline in data.get_pipelines():
        item=props(pipeline)
        for field in ['mesh_pipeline','common_skeletal_meshes_and_animations_properties','common_meshes_properties','animation_pipeline']:
            try:item[field]=props(pipeline.get_editor_property(field))
            except Exception:pass
        row['stored_pipelines'].append(item)
    c=unreal.new_object(unreal.SkeletalMeshComponent);c.set_skeletal_mesh_asset(mesh)
    row['hierarchy']={n:(str(c.get_parent_bone(n)) if str(c.get_parent_bone(n))!='None' else None) for n in row['bones']}
save('baseline_import.json',b)
