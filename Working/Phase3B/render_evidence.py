"""Static geometric evidence, CPU skin estimate; no Unreal render claim."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase3B';W=P/'Working/Phase3B'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
skin={r:json.loads((W/('skin_'+r+'.json')).read_text()) for r in ['UE5','Mixamo']}
data=json.loads((W/'visual_skin_samples.json').read_text())
def panel(vertices,rig,label,size=(340,450),scale=1.8):
    im=Image.new('RGB',size,'#f4f6f8');d=ImageDraw.Draw(im);v=np.asarray(vertices);tri=np.asarray(skin[rig]['triangles'])
    u=np.array([.894,.447,0]);dep=np.array([.447,-.894,.18]);depth=v@dep
    xy=np.c_[size[0]/2+(v@u)*scale,size[1]-40-v[:,2]*scale]
    face=v[tri];normal=np.cross(face[:,1]-face[:,0],face[:,2]-face[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12)
    light=np.array([.3,-.5,.8]);light/=np.linalg.norm(light);shade=.3+.7*np.abs(normal@light)
    for i in np.argsort(depth[tri].mean(axis=1)):
        s=shade[i];d.polygon([tuple(p) for p in xy[tri[i]]],fill=(int(80+90*s),int(88+90*s),int(100+90*s)))
    d.line([(12,size[1]-40),(size[0]-12,size[1]-40)],fill='#788696');d.text((12,8),label,fill='#192839',font=font)
    return im
refs=json.loads((O/'scaled_candidates.json').read_text());im=Image.new('RGB',(1700,960),'white');d=ImageDraw.Draw(im)
d.text((16,8),'Reference geometry: same pixel/cm scale; coordinated uniform scaling',fill='#192839',font=font)
for i,row in enumerate(refs):
    v=np.asarray(skin[row['rig']]['vertices_cm'])*row['factor'];im.paste(panel(v,row['rig'],row['rig']+' '+format(row['requested_height_cm'],'.3f')+' cm'),((i%5)*340,40+(i//5)*450))
im.save(O/'height_reference_matrix.png')
for rig in ['UE5','Mixamo']:
    im=Image.new('RGB',(1360,960),'white');d=ImageDraw.Draw(im)
    d.text((16,8),rig+' 180 cm run: CPU skin estimate from actual UE evaluated poses',fill='#192839',font=font)
    for j,state in enumerate(['FK','Full']):
        for i,fraction in enumerate([0.0,.25,.5,.75]):
            key='|'.join([rig,'Height180',state,'run',str(fraction)])
            im.paste(panel(data[key],rig,state+'  '+str(int(fraction*100))+'%'),(i*340,40+j*450))
    im.save(O/(rig.lower()+'_run_cycle.png'))
print('VISUAL_EVIDENCE_DONE')
