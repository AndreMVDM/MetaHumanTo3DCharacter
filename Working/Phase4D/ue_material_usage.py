import unreal,json
from pathlib import Path
O=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Documentation/Phase4D');m=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase4D/Materials/M_LaraOriginal');assert m
before=m.get_editor_property('used_with_skeletal_mesh');m.set_editor_property('used_with_skeletal_mesh',True);assert m.get_editor_property('used_with_skeletal_mesh');assert unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
(O/'material_usage_correction.json').write_text(json.dumps({'asset':m.get_path_name(),'before_in_memory':before,'after':True,'reason':'UE automatically enabled SkeletalMesh usage on load and emitted a save-required map warning. Persist the Phase4D-only usage flag. Original texture/shader graph unchanged.'},indent=2));print('PHASE4D_MATERIAL_USAGE_SAVED')
