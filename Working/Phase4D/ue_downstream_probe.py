import unreal,json,sys
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase4D'
names=['SkeletonModifier','Transform','Quat','MathLibrary','Phase4DLibrary']
out={n:{'doc':getattr(unreal,n).__doc__,'methods':[x for x in dir(getattr(unreal,n)) if any(k in x for k in ['transform','rot_from','quat','skeleton_reference'])]} for n in names}
for cls,methods in [('SkeletonModifier',['add_bone','set_bones_transforms','get_bone_transform']),('Transform',['transform_location','inverse_transform_location','multiply']),('MathLibrary',['make_rot_from_xy']),('Phase4DLibrary',['sync_skeleton_reference'])]:
 for m in methods:
  out[cls][m]=getattr(getattr(unreal,cls),m).__doc__ if hasattr(getattr(unreal,cls),m) else None
(O/'downstream_api_probe.json').write_text(json.dumps(out,indent=2))
print('PHASE4D_DOWNSTREAM_API_PROBE_DONE')

