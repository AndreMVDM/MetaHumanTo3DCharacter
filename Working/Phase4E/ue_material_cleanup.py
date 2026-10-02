import sys
from pathlib import Path
sys.path.insert(0,'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4E')
from ue_common import *
r={'status':'running'}
try:
    mat=unreal.load_asset(B+'/Materials/M_LaraOriginal');tex=unreal.load_asset(B+'/Materials/T_LaraOriginal')
    expressions=unreal.MaterialEditingLibrary.get_material_expressions(mat)
    for e in expressions:
        if isinstance(e,unreal.MaterialExpressionTextureSample):e.set_editor_property('texture',tex)
    unreal.MaterialEditingLibrary.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat,False)
    r.update(status='passed',material=mat.get_path_name(),texture=tex.get_path_name(),expressions=len(expressions),method='Repoint expressions then recompile Phase4E material to refresh cached referenced textures; no prior asset save')
except Exception:r.update(status='failed',error=traceback.format_exc())
save('material_dependency_cleanup.json',r)
