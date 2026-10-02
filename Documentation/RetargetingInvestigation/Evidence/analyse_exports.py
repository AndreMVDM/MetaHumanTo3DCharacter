import pathlib, re, json, csv
OUT=pathlib.Path(__file__).parent
def nodes(filename):
    stack=[]; records={}; classes={}
    for line in (OUT/filename).read_text(encoding='utf-8-sig').splitlines():
        if line.strip().startswith('Begin Object'):
            localname=re.search(r'Name="([^"]+)"',line).group(1)
            exportpath=re.search(r'ExportPath="([^"]+)"',line)
            name=exportpath.group(1).split(':')[-1].rstrip("'") if exportpath else localname
            cls=re.search(r'Class=([^ ]+)',line)
            if cls: classes[name]=cls.group(1)
            rec=records.setdefault(name,{'name':name,'class':classes.get(name,''),'lines':[]})
            if cls:rec['class']=cls.group(1)
            stack.append(rec)
        elif line.strip()=='End Object':stack.pop()
        elif stack:stack[-1]['lines'].append(line.strip())
    result={}
    for name,r in records.items():
        if 'Node' not in r['class']:continue
        pins=[]
        for l in r['lines']:
            if l.startswith('CustomProperties Pin '):
                def field(n):
                    m=re.search(n+r'="([^"]*)"',l);return m.group(1) if m else None
                linked=re.search(r'LinkedTo=\(([^)]*)\)',l)
                pins.append({'name':field('PinName'),'direction':field('Direction') or 'input','category':field('PinCategory'),'subcategoryobject':field('PinSubCategoryObject'),'default':field('DefaultValue'),'default_object':field('DefaultObject'),'links':re.findall(r'(\w+) [A-F0-9]{32}',linked.group(1)) if linked else []})
        prefix=name.rsplit('.',1)[0]+'.' if '.' in name else ''
        for p in pins:p['links']=[prefix+link for link in p['links']]
        result[name]={'class':r['class'],'settings':[l for l in r['lines'] if not l.startswith(('CustomProperties','ShowPin','NodePos','NodeGuid','Binding','bComment','NodeWidth','NodeHeight','bCanToggle'))],'pins':pins}
    return result
allnodes={}
for f in ['ABP_CopyPoseFromMesh.t3d','BP_CopyPoseFromMesh.t3d','Echo_PostProcess_AnimBP.t3d','ABP_StackOBot_Retargeting.t3d','Echo_Twist_CtrlRig.t3d','Echo_Helpers_CtrlRig.t3d']:
    allnodes[f]=nodes(f)
(OUT/'graphs.json').write_text(json.dumps(allnodes,indent=2),encoding='utf-8')
for f in ['ABP_CopyPoseFromMesh.t3d','Echo_PostProcess_AnimBP.t3d']:
    graph=allnodes[f]; root=next(n for n,r in graph.items() if r['class'].endswith('.AnimGraphNode_Root'))
    chain=[];seen=set()
    def walk(n):
        if n in seen:return
        seen.add(n)
        for p in graph[n]['pins']:
            if p['direction']=='input' and 'PoseLink' in str(p['subcategoryobject']):
                for link in p['links']:
                    if link in graph:walk(link)
        chain.append(n)
    walk(root)
    print(f, ' -> '.join(chain))
    (OUT/(f+'.connected.json')).write_text(json.dumps([{'name':n,**graph[n]} for n in chain],indent=2),encoding='utf-8')
detail=json.loads((OUT/'detail.json').read_text())
source=next(c for c in detail['components'] if c['name']=='Source_SkeletalMesh')['bones']
target=next(c for c in detail['components'] if c['name']=='Target_SkeletalMesh')['bones']
sm={b['name']:b for b in source}; tm={b['name']:b for b in target}
rows=[{'target_bone':b['name'],'target_parent':b['parent'],'source_bone':b['name'] if b['name'] in sm else '', 'source_parent':sm.get(b['name'],{}).get('parent','')} for b in target]
with (OUT/'bone_mapping.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'source_count':len(source),'target_count':len(target),'matched_count':len(sm.keys()&tm.keys()),'target_only':sorted(tm.keys()-sm.keys()),'source_only':sorted(sm.keys()-tm.keys()),'parent_mismatches':[r for r in rows if r['source_bone'] and r['source_parent']!=r['target_parent']]}
(OUT/'bone_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8'); print(json.dumps(summary,indent=2))
