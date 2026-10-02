import json,math,collections
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase4A';W=P/'Working/Phase4A'
def load(p):return json.loads(p.read_text())
def save(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False))
assisted=load(O/'assisted_candidates.json');trials=load(O/'medial_trials.json');analysis=[];skin=[]
canvas=Image.new('RGB',(1300,850),'white');draw=ImageDraw.Draw(canvas)
def panel(i,count,title,points,lines=None):
    width=1300/count;cx=width*(i+.5);factor=3.7;xy=lambda p:(cx+p[0]*factor,790-p[2]*factor)
    draw.text((width*i+15,15),title,fill='black')
    for z in range(0,181,20):draw.line([(width*i+10,790-z*factor),(width*(i+1)-10,790-z*factor)],fill='#e5e5e5')
    for p in points:draw.point(xy(p),fill='#999999' if lines is not None else '#222222')
    for a,b in lines or []:draw.line([xy(a),xy(b)],fill='#2563eb',width=2)
    draw.line([(width*i+10,790),(width*(i+1)-10,790)],fill='#dc2626',width=2)
v=np.array(load(W/'Unrigged_assisted_skin.json')['geometry']['vertices'])
for i,row in enumerate([trials[0],trials[1],assisted[0]]):
    bones=row['snapshot']['bones'];parents=row['parents'];ps={n:np.array(b['component']['translation']) for n,b in bones.items()}
    panel(i,3,'Actual UE skeleton: '+('Medial '+str(row['max_spheres']) if 'max_spheres' in row else 'MANUAL landmarks'),v,[(ps[n],ps[p]) for n,p in parents.items() if p in ps])
canvas.save(O/'skeleton_comparison.png')
landmarks={n:np.array(x) for n,p,x in assisted[0]['authored_landmarks_cm'] if not any(f in n for f in ['thumb','index','middle','ring','pinky'])}
for row in trials+assisted:
    bones=row['snapshot']['bones'];parents=row['parents'];ps={n:np.array(b['component']['translation']) for n,b in bones.items()};children=collections.Counter(p for p in parents.values() if p in ps);lengths={n:float(np.linalg.norm(ps[n]-ps[p])) for n,p in parents.items() if p in ps};arr=np.array(list(ps.values()))
    result={'case':row['case'],'type':'automatic_medial' if 'max_spheres' in row else 'assisted_manual_landmarks','parameter':row.get('max_spheres'),'bone_count':len(ps),'root':{n:ps[n].tolist() for n,p in parents.items() if p not in ps},'max_children':max(children.values()),'branch_points_with_more_than_3_children':{n:c for n,c in children.items() if c>3},'bone_lengths_cm':lengths,'unit_scale':all(abs(s-1)<.0001 for b in bones.values() for s in b['local']['scale']),'nearest_to_manual_landmark_proxy':{n:{'bone':list(ps)[int(np.argmin(np.linalg.norm(arr-x,axis=1)))],'distance_cm':float(np.linalg.norm(arr-x,axis=1).min())} for n,x in landmarks.items()},'anatomical_proxy_limit':'Manual landmarks are approximate geometry-based comparison points, not anatomical ground truth. Nearest distance alone cannot establish a connected humanoid hierarchy.'}
    if 'max_spheres' in row:
        mirrored=arr.copy();mirrored[:,0]*=-1;result['mirror_nearest_mean_max_cm']=[float(np.mean([np.linalg.norm(arr-x,axis=1).min() for x in mirrored])),float(np.max([np.linalg.norm(arr-x,axis=1).min() for x in mirrored]))];result['accepted_humanoid']=False;result['reason']='Non-semantic branched medial tree, asymmetric joint correspondence, no validated connected pelvis/spine/limb/finger chains; installed automatic characterisation and FBIK both fail.'
        data=load(W/(row['case']+'_Medial'+str(row['max_spheres'])+'_skin.json'));ws=data['weights'];vv=np.array(data['geometry']['vertices'])
    else:
        data=load(W/(row['case']+'_assisted_skin.json'));ws=data['weights'];vv=np.array(data['geometry']['vertices']);result['accepted_humanoid']=False;result['reason']='Diagnostic semantic hierarchy succeeds; hand/finger locations approximate, sole hover and deformation flags prevent quality acceptance.'
    hist=collections.Counter(sum(w>0 for b,w in pairs) for pairs in ws);sums=np.array([sum(w for b,w in pairs) for pairs in ws]);names=list(bones);bx=np.array([ps[n][0] for n in names]);cross=[]
    for i,pairs in enumerate(ws):
        if abs(vv[i,0])>8 and vv[i,2]<95:
            wrong=sum(w for b,w in pairs if bx[b]*vv[i,0]<-1)
            if wrong>.25:cross.append(i)
    skin.append({'case':row['case'],'type':result['type'],'parameter':row.get('max_spheres'),'vertices':len(ws),'positive_influence_histogram':dict(hist),'max_positive_influences':max(hist),'zero_weight_vertices':int((sums==0).sum()),'weight_sum_range':sums.min().item() and [float(sums.min()),float(sums.max())],'opposite_side_influence_gt25pct_lower_body_vertices':len(cross),'bleed_screen_limit':'Screen outside 8cm centre band below95cm, using signed reference bone X; not a semantic clothing/limb segmentation.'});analysis.append(result)
save('skeleton_analysis.json',analysis);save('skin_weight_analysis.json',{'statistics':skin,'deformation_evidence':'deformation_metrics.json','accepted_quality':False,'limitations':'Weight coverage and stable transforms do not prove deformation acceptance. Hands/fingers and clothing need dedicated anatomical fitting and local weight review.'})
visual=load(W/'visual_skin_samples.json');canvas=Image.new('RGB',(1300,850),'white');draw=ImageDraw.Draw(canvas)
for i,role in enumerate(['idle','walk','run','reach']):panel(i,4,'CPU LBS: '+role+' @50%',np.array(visual['Unrigged|'+role+'|0.5']))
canvas.save(O/'deformation_contact_sheet.png')
print('QUALITY_ANALYSIS',len(analysis),skin)
