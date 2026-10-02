"""Actual UE-pose-driven CPU surface renders, with original triangles and weights."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4D';O=P/'Documentation/Phase4D';z=np.load(W/'animated_surface_samples.npz');tri=z['triangles'];font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
def panel(draw,verts,rect,axis,lo,hi):
 x,y,w,h=rect;lo=np.array(lo);hi=np.array(hi);scale=min((w-25)/(hi[axis]-lo[axis]),(h-60)/(hi[2]-lo[2]));centre=(hi+lo)/2
 def xy(p):return (x+w/2+(p[axis]-centre[axis])*scale,y+h/2+15-(p[2]-centre[2])*scale)
 tv=verts[tri];ix=np.where(np.all(tv.max(1)>=lo,axis=1)&np.all(tv.min(1)<=hi,axis=1))[0];ix=ix[np.argsort(tv[ix,:,1-axis].mean(1))]
 normals=np.cross(tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-9);light=.6+.38*abs(normals@np.array([.25,.5,.83]))
 for i in ix:draw.polygon([xy(p) for p in tv[i]],fill=tuple(int(c*light[i]) for c in [174,189,208]))
 if lo[2]<=0<=hi[2]:draw.line([xy([lo[0],lo[1],0]),xy([hi[0],hi[1],0])],fill='#c01b35',width=2)
roles=['idle','walk','run','reach'];files=[]
for name,axis,lo,hi in [('animated_body_front',0,[-80,-80,-10],[80,80,205]),('animated_body_side',1,[-80,-80,-10],[80,80,205]),('animated_feet_side',1,[-80,-40,-10],[80,40,65])]:
 size=(1650,1740);im=Image.new('RGB',size,'#f7f9fc');draw=ImageDraw.Draw(im)
 draw.text((15,10),'Phase4D | actual baked poses + original UE bound weights | CPU LBS, no material/cloth',font=font,fill='#172433')
 for row,role in enumerate(roles):
  for col,key in enumerate(['reference']+[role+'_'+str(f) for f in [0.,.25,.5,.75]]):
   rect=(col*330,55+row*415,330,410);panel(draw,z[key],rect,axis,lo,hi);draw.text((rect[0]+8,rect[1]+4),role+' | '+key.split('_')[-1],font=font,fill='#172433')
 im.save(O/(name+'.png'));files.append(name+'.png')
print('Rendered deformation views:',files)
