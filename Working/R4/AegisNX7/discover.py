"""Read-only native source inventory. No animation asset writes."""
import sys,json,traceback
from pathlib import Path
R=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');sys.path.insert(0,str(R/'Working/R4'));sys.dont_write_bytecode=True
import animation_library as lib
import unreal
C=json.loads((Path(__file__).parent/'profile.json').read_text());O=R/C['evidence_directory'];O.mkdir(parents=True,exist_ok=True)
result=dict(version=lib.VERSION,status='RUNNING',assets=[],skeleton_relationships=[],source_assets_modified=False)
try:
    reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True)
    source=unreal.load_asset(C['source_mesh']);sk=source.skeleton;compatible={sk.get_path_name()}|{x.get_path_name() for x in sk.compatible_skeletons}
    result['source_skeleton']=sk.get_path_name();result['compatible_skeletons']=sorted(compatible)
    all_assets=reg.get_all_assets();seen=set();fingerprints={}
    for ad in sorted(all_assets,key=lambda x:str(x.package_name)):
        p=str(ad.package_name);cls=str(ad.asset_class_path.asset_name);in_root=any(p.startswith(x+'/') for x in C['discovery_roots'])
        skeleton_tag=str(ad.get_tag_value('Skeleton') or '')
        candidate=in_root or (cls=='AnimSequence' and any(x in skeleton_tag for x in compatible))
        if not candidate:continue
        name=str(ad.asset_name);row=dict(source_path=p+'.'+name,name=name,asset_class=cls,source_identity='Quinn' if name.startswith('MF_') else 'Manny' if name.startswith('MM_') else 'shared_or_unspecified',category=lib.category(name))
        if cls!='AnimSequence':row.update(classification='EXCLUDE_NOT_BODY_ANIMATION',reason='Native asset class is '+cls)
        else:
            a=ad.get_asset()
            row.update(lib.metadata(a));row['motion_fingerprint']=lib.motion_fingerprint(a)
            if row['skeleton'] not in compatible:row.update(classification='EXCLUDE_UNSUPPORTED',reason='Skeleton is not declared compatible with the accepted source Skeleton')
            elif not row['tracks'] or not any(x in row['tracks'] for x in ['pelvis','spine_01','thigh_l','upperarm_l']):row.update(classification='EXCLUDE_NOT_BODY_ANIMATION',reason='No mannequin body skeletal tracks')
            elif a.get_editor_property('additive_anim_type')!=unreal.AdditiveAnimationType.AAT_NONE:row.update(classification='BAKE_OPTIONAL',reason='Additive sequence requires its base-pose recipe; excluded from standalone default playback')
            elif row['motion_fingerprint'] in fingerprints:row.update(classification='EXCLUDE_DUPLICATE_OR_HELPER',reason='Exact raw motion/metadata duplicate',equivalent_source=fingerprints[row['motion_fingerprint']])
            elif '/SourceReadiness/' in p or '/Benchmark/' in p or '/Phase4' in p:row.update(classification='EXCLUDE_DUPLICATE_OR_HELPER',reason='Preregistered benchmark fixture/helper; not shipping mannequin library')
            elif any(str(ref.asset_class_path.asset_name)=='PoseAsset' for rp in reg.get_referencers(ad.package_name,unreal.AssetRegistryDependencyOptions(include_hard_package_references=True,include_soft_package_references=True)) for ref in reg.get_assets_by_package_name(rp)):row.update(classification='EXCLUDE_DUPLICATE_OR_HELPER',reason='Native PoseAsset support sequence, not independent body action')
            else:row.update(classification='BAKE_DEFAULT',reason='Native non-additive body sequence on accepted source Skeleton');fingerprints[row['motion_fingerprint']]=row['source_path']
        result['assets'].append(row)
    for ad in all_assets:
        if str(ad.asset_class_path.asset_name)=='SkeletalMesh' and any(str(ad.package_name).startswith(x+'/') for x in C['discovery_roots']):
            mesh=ad.get_asset();result['skeleton_relationships'].append(dict(mesh=mesh.get_path_name(),skeleton=mesh.skeleton.get_path_name()))
    result['totals']={c:sum(x['classification']==c for x in result['assets']) for c in ['BAKE_DEFAULT','BAKE_OPTIONAL','EXCLUDE_UNSUPPORTED','EXCLUDE_NOT_BODY_ANIMATION','EXCLUDE_DUPLICATE_OR_HELPER']};result['status']='PASS'
except Exception:result.update(status='FAIL',error=traceback.format_exc())
(O/'source_inventory.json').write_text(json.dumps(result,indent=2)+'\n');print('R4_DISCOVERY',result['status'],result.get('totals'),result.get('error',''))
