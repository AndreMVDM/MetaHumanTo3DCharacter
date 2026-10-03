"""Finalise editor independence of already validated R4-derived sequences only."""
import unreal,json,sys,traceback
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');sys.path.insert(0,str(R/'Working/R4'));import animation_library as lib
O=R/'Documentation/R4/AegisNX7';M=json.loads((O/'animation_library_manifest.json').read_text());D=dict(status='RUNNING',removed=[])
try:
    for row in M['entries']:
        if row.get('bake_result')!='PASS':continue
        anim=unreal.load_asset(row['destination_path']);removed=lib.detach_source_editor_links(anim)
        row['detached_source_editor_links']=removed
        if removed:
            lib.require(unreal.EditorAssetLibrary.save_loaded_asset(anim,False),'save detached derived asset');D['removed'].append(dict(path=anim.get_path_name(),links=removed))
    D['status']='PASS';(O/'animation_library_manifest.json').write_text(json.dumps(M,indent=2)+'\n')
except Exception:D.update(status='FAIL',error=traceback.format_exc())
(O/'editor_link_detachment.json').write_text(json.dumps(D,indent=2)+'\n');print('R4_EDITOR_LINKS',D)
