from pathlib import Path
import json
p=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4E/capture_native.py');src=p.read_text();data=json.loads((p.parents[2]/'Documentation/Phase4E/contact_comparison.json').read_text());walk=next(x for x in data['results']['Phase4D'] if x['role']=='walk');worst=min(walk['samples'],key=lambda r:min(r['left_min_z'],r['right_min_z']));fraction=worst['time_s']/1.8666666746139526
start=src.index('shots=[]');end=src.index('stage=0;',start)
block="shots=[]\nfor label in ['Baseline','Refined']:\n    for view,camera,rot in [('feet_front',[0,70,15],[0,-90,0]),('feet_side',[80,0,15],[0,180,0])]:\n        shots.append({'label':label,'name':'native_'+label.lower()+'_'+view,'camera':camera,'rotation':rot,'clip':'MF_Walk_Fwd','fraction':"+str(fraction)+"})\n"
src=src[:start]+block+src[end:];src=src.replace("B+'/Character/NativeAnimations/'+shot['clip']","B+'/Character/'+('SurfaceContactAnimations/' if shot['label']=='Refined' else 'NativeAnimations/')+shot['clip']");src=src.replace('native_visual_capture.json','native_contact_visual_capture.json');exec(compile(src,str(p),'exec'),globals())
