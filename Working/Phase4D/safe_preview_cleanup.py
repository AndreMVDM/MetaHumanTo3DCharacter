"""Phase4D-only native preview cleanup; exact reference-pose equality is required."""
import sys,json,traceback,runpy
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));from ue_common_d import *
row={'status':'running','intent':'Replace accidental Skeleton authoring-mesh preview with final Lara mesh; keep all reference transforms unchanged'}
try:
 mesh=unreal.load_asset('/Game/MetaHumanTo3DCharacter/Phase4D/Character/SK_Lara');sk=mesh.skeleton;before=mesh_snapshot(mesh)['bones'];assert unreal.Phase4DLibrary.set_skeleton_preview_mesh(mesh);after=mesh_snapshot(mesh)['bones'];assert before==after,'Reference transform change forbidden'
 assert unreal.EditorAssetLibrary.save_loaded_asset(sk,only_if_is_dirty=False)
 row.update(status='saved',asset=sk.get_path_name(),preview=mesh.get_path_name(),reference_transforms_identical=True,native_guard='Both mesh and skeleton must belong to Phase4D namespace')
except Exception:row.update(status='failed',error=traceback.format_exc())
save('preview_dependency_cleanup.json',row)
if row['status']=='saved':runpy.run_path(str(W/'audit_native_assets.py'),run_name='__main__')
print('PHASE4D_SAFE_PREVIEW_CLEANUP',row['status'])
