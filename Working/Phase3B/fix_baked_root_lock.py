import sys
sys.path.insert(0,r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B')
from common import *
fixed=[]
for row in json.loads((O/'scaled_candidates.json').read_text()):
    if row['rig']!='Mixamo':continue
    base=row['snapshot']['mesh'].split('.')[0].rsplit('/',1)[0]
    for path in unreal.EditorAssetLibrary.list_assets(base+'/Tests',recursive=True,include_folder=False):
        asset=unreal.load_asset(path)
        if isinstance(asset,unreal.AnimSequence):
            asset.set_editor_property('force_root_lock',False)
            assert unreal.EditorAssetLibrary.save_loaded_asset(asset)
            fixed.append(asset.get_path_name())
save('baked_root_lock_correction.json',{'reason':'Hips is the Mixamo root and pelvis. Manny ForceRootLock inherited during bake freezes Hips at reference, erasing valid pelvis animation at runtime. Clear destination ForceRootLock for these already in-place outputs.','corrected_assets':fixed})
exec((P/'Working/Phase3B/inspect_final.py').read_text(),globals())
