"""Read the real FBX using the existing project parser. No source mutation."""
import sys,json,hashlib,struct,importlib.util,collections,math
from pathlib import Path
sys.dont_write_bytecode=True
W=Path(__file__).parent;R=W.parents[4];O=R/'Documentation/Phase4F/Benchmark/Runs/02_AegisNX7/R3'
spec=importlib.util.spec_from_file_location('existing_fbx_reader',R/'Documentation/Phase3/Evidence/collect_evidence.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
path=next((W/'Input').glob('*.fbx'));data=path.read_bytes();version=struct.unpack_from('<I',data,23)[0];nodes,_=m.nodes(data,27,len(data),version>=7500);roots={n['name']:n for n in nodes};objects=roots['Objects']['children'];byid={n['props'][0]:n for n in objects};connections=[c['props'] for c in m.child(roots['Connections'],'C')]
summary=m.fbx(path);bones={n['props'][0]:n for n in objects if n['name']=='Model' and n['props'][2] in ['LimbNode','Root']};names={i:str(n['props'][1]).split('\x00')[0] for i,n in bones.items()}
summary['bone_hierarchy']=[dict(id=i,name=names[i],parent=next((names[b] for kind,a,b,*rest in connections if kind=='OO' and a==i and b in bones),None),properties=m.properties(n)) for i,n in bones.items()]
clusters=[];weights=collections.defaultdict(list)
for n in objects:
    if n['name']!='Deformer' or n['props'][2]!='Cluster':continue
    fields={c['name']:c['props'][0] for c in n['children'] if c['props']};boneid=next((a for kind,a,b,*rest in connections if kind=='OO' and b==n['props'][0] and a in bones),None)
    skinid=next((b for kind,a,b,*rest in connections if kind=='OO' and a==n['props'][0] and byid.get(b,{}).get('name')=='Deformer'),None)
    geometryid=next((b for kind,a,b,*rest in connections if kind=='OO' and a==skinid and byid.get(b,{}).get('name')=='Geometry'),None)
    row=dict(id=n['props'][0],bone=names.get(boneid),skin_id=skinid,geometry_id=geometryid,fields=fields);clusters.append(row)
    for index,weight in zip(fields.get('Indexes',[]),fields.get('Weights',[])):weights[(geometryid,index)].append([names.get(boneid),weight])
summary['skin_clusters']=clusters;summary['source_skin_weights']=[dict(geometry_id=g,control_point=i,influences=ws) for (g,i),ws in sorted(weights.items())]
summary['weight_summary']=dict(cluster_count=len(clusters),weighted_control_points=len(weights),negative_or_nonfinite=sum(not math.isfinite(w) or w<0 for ws in weights.values() for _,w in ws),maximum_weight_sum_error=max((abs(sum(w for _,w in ws)-1) for ws in weights.values()),default=None),missing_cluster_bone_count=sum(c['bone'] is None for c in clusters),max_influences=max((len(ws) for ws in weights.values()),default=0))
summary['bind_pose_nodes']=[n for n in objects if n['name']=='Pose'];summary['source_sha256']=hashlib.sha256(data).hexdigest()
(O/'source_fbx.json').write_text(json.dumps(summary,indent=2));print('SOURCE',version,'bones',len(bones),'geometries',summary['geometries'],'weights',summary['weight_summary']);print('NAMES',list(names.values()))
