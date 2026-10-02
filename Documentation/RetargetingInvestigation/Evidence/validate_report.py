import json,re,pathlib
E=pathlib.Path(__file__).parent;D=E.parent
def read(n):return json.loads((E/n).read_text(encoding='utf-8-sig'))
report=(D/'InvestigationReport.md').read_text(encoding='utf-8');checks={}
checks['twelve_deliverable_sections']=re.findall(r'^## (\d+)\.',report,re.M)==[str(x) for x in range(1,13)]
missing_links=[]
for label,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',report):
    if not target.startswith('https:') and not (D/target).exists():missing_links.append(target)
checks['local_evidence_links_exist']=not missing_links
inventory=read('inventory.json'); known={a['package']+'.'+a['asset_name'] for a in inventory}
known.add(read('detail.json')['abp']['path'])
scene=read('scene.json');known.add(scene['world'])
unknown=[]
for p in re.findall(r'`(/Game/[^`\s]+)`',report):
    if ':PersistentLevel.' in p or ':Echo_Cloth_Scarf' in p:continue
    if p.endswith('_C'):p=p[:-2]
    if p not in known:unknown.append(p)
checks['explicit_asset_paths_verified']=not unknown
bone=read('bone_summary.json');checks['bone_mapping_counts']=(bone['source_count'],bone['target_count'],bone['matched_count'])==(89,134,80) and not bone['parent_mismatches']
graph=read('ABP_CopyPoseFromMesh.t3d.connected.json');checks['main_graph_copy_pose_to_root']=len(graph)==2 and graph[0]['class'].endswith('.AnimGraphNode_CopyPoseFromMesh') and graph[1]['class'].endswith('.AnimGraphNode_Root')
cdo=(E/'ABP_CopyPoseFromMesh_CDO.t3d').read_text(encoding='utf-8-sig');checks['compiled_copy_pose_flags']=all(x in cdo for x in ['bUseAttachedParent=True','bCopyCurves=True','bCopyCustomAttributes=False','bUseMeshPose=True'])
assets=read('assets.json');morphs={p.rsplit(':',1)[-1] for p in assets['/Game/Characters/Echo/Meshes/Echo']['properties']['morph_targets']}
post=(E/'Echo_PostProcess_AnimBP.t3d').read_text(encoding='utf-8-sig');driven=set(re.findall(r'DrivenName="([^"]+)"',post))
checks['corrective_curve_morph_mapping_counts']=len(morphs)==181 and len(driven)==65 and len(driven&morphs)==56
runtime=read('runtime.json');comparison=read('runtime_comparison.json');checks['runtime_body_pose_matches']=len(comparison)==2 and all(s['bones'][b]['max_absolute_component_difference']==0 for s in comparison for b in ['root','pelvis','spine_03','head','hand_l','foot_l'])
source=[next(c for c in s['components'] if c['name']=='Source_SkeletalMesh')['pose'] for s in runtime]
checks['runtime_source_pose_advances']=source[0]['pelvis']!=source[1]['pelvis']
checks['twist_rotations_differ']=all(s['bones']['lowerarm_twist_01_l']['rotation_distance_degrees']>1 for s in comparison)
final=read('final_queries.json');checks['no_dirty_reference_packages']=all(not final[k] for k in ['dirty_maps','dirty_content','dirty_maps_after_queries','dirty_content_after_queries'])
preservation=read('preservation.json');checks['reference_file_preservation']=preservation['BaselineFileCount']==preservation['CurrentFileCount']==673 and not preservation['Changes'] and not preservation['Added']
support=read('support.json');checks['supplemental_asset_count']=len(support['rigs'])==6 and len(support['retargeters'])==9
supplement=(D/'SupplementalIKConfiguration.md').read_text(encoding='utf-8');bot=supplement.split('## IK Retargeter `/Game/ExampleContent/AnimationRetargeting/AnimBlueprints/RTG_Mannequin_StackOBot`')[1].split('## IK Retargeter ')[0]
checks['bot_mapping_table_unambiguous']='| Spine | Spine |' in bot and '| Spine | None |' not in bot and '| Neck | None |' in bot
result={'checks':checks,'unknown_paths':unknown,'missing_links':missing_links,'driven_curves_without_morph_targets':sorted(driven-morphs),'all_passed':all(checks.values())}
(E/'report_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if not result['all_passed']:raise SystemExit(1)
