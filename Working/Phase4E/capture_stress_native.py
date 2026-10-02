"""Additional native paired stress and backside review from identical cameras."""
from pathlib import Path
p=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4E/capture_native.py')
src=p.read_text();start=src.index('shots=[]');end=src.index('stage=0;',start)
block="""shots=[]
for label in ['Baseline','Refined']:
    for view,clip,camera,rot in [('pants_wide','Stress_wide_stance',[0,90,98],[0,-90,0]),('hips_back','JumpingJacks',[0,-100,98],[0,90,0]),('shoulders_horizontal','Stress_arms_horizontal',[0,100,134],[0,-90,0]),('shoulders_overhead','Stress_arms_overhead',[0,100,134],[0,-90,0]),('shoulders_45','Stress_arms_45',[0,100,134],[0,-90,0]),('neutral','Stress_neutral',[0,240,100],[0,-90,0])]:
        shots.append({'label':label,'name':'native_'+label.lower()+'_'+view,'camera':camera,'rotation':rot,'clip':clip,'fraction':.5})
"""
src=src[:start]+block+src[end:];src=src.replace("B+'/Character/NativeAnimations/'+shot['clip']","B+'/Character/'+('StressAnimations/' if shot['clip'].startswith('Stress_') else 'NativeAnimations/')+shot['clip']");src=src.replace('native_visual_capture.json','native_stress_visual_capture.json')
exec(compile(src,str(p),'exec'),globals())
