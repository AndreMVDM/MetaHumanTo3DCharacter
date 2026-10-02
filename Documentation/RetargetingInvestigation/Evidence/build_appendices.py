import json,re,csv,pathlib,math
E=pathlib.Path(__file__).parent; D=E.parent
def read(n):return json.loads((E/n).read_text(encoding='utf-8-sig'))
def clean(s):return re.sub(r' \(0x[0-9A-Fa-f]+\)', '',str(s))
def mapping_blocks(raw):
    result=[];offset=0
    while True:
        i=raw.find('ChainMap=',offset)
        if i<0:return result
        start=raw.find('(',i);depth=0;quoted=False
        for j in range(start,len(raw)):
            ch=raw[j]
            if ch=='"':quoted=not quoted
            if quoted:continue
            if ch=='(':depth+=1
            elif ch==')':
                depth-=1
                if depth==0:
                    result.append(raw[start:j+1]);offset=j+1;break
assets=read('assets.json'); support=read('support.json'); scene=read('scene.json'); final=read('final_queries.json')
copy_abp=read('detail.json')['abp']
assets[copy_abp['path'].split('.')[0]]={'path':copy_abp['path'],'class':'/Script/Engine.AnimBlueprint'}
with (D/'ReferenceClosure.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['package','object_path','asset_class','note'])
    for a in read('inventory.json'):w.writerow([a['package'],a['package']+'.'+a['asset_name'],a['class'],'Broad registry closure; includes inactive authoring, rendering and neighbouring exhibit dependencies'])
with (D/'AssetInventory.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['package','object_path','asset_class','note'])
    for p,a in sorted(assets.items()):w.writerow([p,a['path'],a['class'],'Broad dependency closure; presence does not establish runtime execution'])
lines=['🟢 **High confidence**','','# Supplemental IK configuration evidence','','These assets belong to other demonstrations in the same map. None participates in the authoritative Manny → Echo Copy Pose path. Values are read from the current UE 5.8 assets; authoring history and the original auto-map command cannot be recovered from a final mapping.','','## Scene assignments','','| Actor | Component | Skeletal mesh | Animation mode | Animation Blueprint or sequence |','|---|---|---|---|---|']
for a in scene['actors']:
    if not a['class'].startswith('/Game/ExampleContent/AnimationRetargeting/Blueprints/'):continue
    for c in a['components']:
        if c['class']!='/Script/Engine.SkeletalMeshComponent':continue
        p=c['properties']; data=p.get('animation_data',''); m=re.search(r"AnimSequence'([^']+)'",data)
        if not p.get('skeletal_mesh_asset'):continue
        lines.append(f"| {a['label']} | {c['name']} | `{p.get('skeletal_mesh_asset')}` | {p.get('animation_mode')} | `{p.get('anim_class') or (m.group(1) if m else 'None')}` |")
for p,r in support['rigs'].items():
    name=p.split('/')[-1]; raw=(E/(name+'.t3d')).read_text(encoding='utf-8-sig')
    line=next((x for x in raw.splitlines() if x.strip().startswith('RetargetDefinition=')), '')
    chains=re.findall(r'ChainName="([^"]+)",StartBone=\(BoneName="([^"]+)"\),EndBone=\(BoneName="([^"]+)"\)(?:,IKGoalName="([^"]+)")?',line)
    excluded=re.search(r'ExcludedBones=\(([^)]*)\)',raw)
    lines+=['',f'## IK Rig `{p}`','',f"Preview mesh: `{r['get_skeletal_mesh']}`. Retarget pelvis/root: `{r['get_retarget_root']}`. Root-motion bone: `{r['get_root_motion_bone']}`. Solver exclusions: {excluded.group(1) if excluded else 'none serialised'}. These exclusions apply to solving, not removal of bones from the mesh.",'','| Chain | Start | End | IK goal |','|---|---|---|---|']
    for c in chains:lines.append('| '+' | '.join('`'+x+'`' if x else 'None' for x in c)+' |')
    lines+=['','Solvers:']
    for s in r['solvers']:lines+=['',f"- `{s['controller']}`, enabled={s['enabled']}, start=`{s['start']}`, end=`{s['end']}`.",f"  Settings: {clean(s['settings'])}"]
    if not r['solvers']:lines.append('- None.')
    for x in raw.splitlines():
        if x.strip().startswith('SolverStack('):lines+=['','Serialised per-bone/per-goal solver overrides:', '', '    '+x.strip()]
for p,r in support['retargeters'].items():
    name=p.split('/')[-1]; raw=(E/(name+'.t3d')).read_text(encoding='utf-8-sig')
    lines+=['',f'## IK Retargeter `{p}`','']
    for side,vals in r.items():
        if side=='ops':continue
        lines+=[f"{side}: rig `{vals.get('get_ik_rig')}`, preview `{vals.get('get_preview_mesh')}`, current pose `{vals.get('get_current_retarget_pose_name')}`."]
    lines+=['','| Order | Operation | Enabled | Controller |','|---|---|---|---|']
    for o in r['ops']:lines.append(f"| {o['index']} | {o['name']} | {o['enabled']} | `{o['controller']}` |")
    maps=[]
    for target,source in re.findall(r'\(TargetChainName="([^"]+)"(?:,SourceChainName="([^"]+)")?\)','\n'.join(mapping_blocks(raw))):
        pair=(target,source or 'None')
        if pair not in maps:maps.append(pair)
    lines+=['','Actual chain mappings (None means unmapped):','','| Target | Source |','|---|---|']
    for t,s in maps:lines.append(f'| {t} | {s} |')
    lines+=['','Operation settings from controller getters (including inherited defaults):','']
    for o in r['ops']:
        lines+=[f"- **{o['name']}**: {clean(o['settings'])}"]
    lines+=['','Explicit asset overrides and poses (quaternions are local bone rotation offsets; these are not mesh transforms):','']
    for x in raw.splitlines():
        if x.strip().startswith(('TargetMeshOffset=','SourceMeshOffset=','TargetRetargetPoses=','SourceRetargetPoses=','CurrentRetargetPose=','RetargetOps(')):
            lines+=['    '+x.strip(),'']
    if p in final['ops']:
        lines+=['','Expanded per-chain settings are in `Evidence/final_queries.json`; inspect these before treating an enabled operation as effective.']
(D/'SupplementalIKConfiguration.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
runtime=read('runtime.json'); comparisons=[]
def nums(s):return [float(x) for x in re.findall(r'(?:x|y|z|w): (-?\d+\.\d+)',s)]
for frame in runtime:
    s=next(c for c in frame['components'] if c['name']=='Source_SkeletalMesh');t=next(c for c in frame['components'] if c['name']=='Target_SkeletalMesh')
    differences={}
    for b in s['pose']:
        if b not in t['pose']:continue
        x=nums(s['pose'][b]);y=nums(t['pose'][b])
        qdot=sum(a*z for a,z in zip(x[:4],y[:4]))/math.sqrt(sum(a*a for a in x[:4])*sum(a*a for a in y[:4]))
        differences[b]={'max_absolute_component_difference':max(abs(a-z) for a,z in zip(x,y)),'translation_distance_cm':math.sqrt(sum((a-z)**2 for a,z in zip(x[4:7],y[4:7]))),'rotation_distance_degrees':math.degrees(2*math.acos(min(1,abs(qdot))))}
    comparisons.append({'sample_monotonic_time':frame['time'],'bones':differences})
(E/'runtime_comparison.json').write_text(json.dumps(comparisons,indent=2),encoding='utf-8')
print('Inventory rows:',len(assets),'IK rigs:',len(support['rigs']),'Retargeters:',len(support['retargeters']),'Runtime samples:',len(runtime))
print(json.dumps(comparisons,indent=2))
