import unreal,json,runpy,sys
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase4D';W=P/'Working/Phase4D';sys.dont_write_bytecode=True
runpy.run_path(str(W/'ue_material_usage.py'),run_name='__main__')
mesh=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase4D/Character/SK_Lara');sk=mesh.skeleton;row={'asset':sk.get_path_name(),'intent':'Retarget Skeleton editor preview reference from authoring mesh to final Lara mesh; no bone/reference transform edit'}
try:
 row['before']=str(sk.get_editor_property('preview_skeletal_mesh'));sk.set_editor_property('preview_skeletal_mesh',mesh);assert unreal.EditorAssetLibrary.save_loaded_asset(sk,only_if_is_dirty=False);row['after']=str(sk.get_editor_property('preview_skeletal_mesh'));row['status']='saved'
except Exception as e:row.update(status='not_changed_if_unsupported',error=str(e))
(O/'preview_dependency_cleanup.json').write_text(json.dumps(row,indent=2));runpy.run_path(str(W/'audit_native_assets.py'),run_name='__main__')
