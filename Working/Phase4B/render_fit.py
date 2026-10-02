import json,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B';d=np.load(W/'normalised_geometry.npz');v=d['vertices'];fit=json.loads((O/'automatic_fit_v2.json').read_text());j={r['role']:r for r in fit['joints']};font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
colours={'automatically_accepted':'#15935f','ambiguous':'#d58b00','manually_corrected':'#2563eb','rejected':'#c93e45'}
def render(name,axis,bounds,width=1000,height=1100,labels=True,edges=True,fingers=False):
    lo,hi=np.array(bounds[0]),np.array(bounds[1]);factor=min((width-160)/(hi[axis]-lo[axis]),(height-150)/(hi[2]-lo[2]));centre=(lo+hi)/2
    def xy(p):return (width/2+(p[axis]-centre[axis])*factor,height-85-(p[2]-lo[2])*factor)
    im=Image.new('RGB',(width,height),'#f7f8fa');draw=ImageDraw.Draw(im)
    ids=np.all(v>=lo,axis=1)&np.all(v<=hi,axis=1)
    for p in v[ids]:draw.point(xy(p),fill='#a0a7af')
    for r in j.values():
        if edges and r['parent_role'] and all(np.all(np.array(p)>=lo) and np.all(np.array(p)<=hi) for p in [r['position_cm'],j[r['parent_role']]['position_cm']]):
            a=j[r['parent_role']]['position_cm'];b=r['position_cm'];draw.line([xy(a),xy(b)],fill='#668196',width=3)
    labelrows=[]
    for r in j.values():
        p=np.array(r['position_cm']);x,y=xy(p)
        if not np.all(p>=lo) or not np.all(p<=hi):continue
        draw.ellipse((x-5,y-5,x+5,y+5),fill=colours[r['status']],outline='white',width=1)
        if labels:labelrows.append((x,y,r['role']))
    for sign in [-1,1]:
        last=65
        for x,y,n in sorted([r for r in labelrows if (r[0]<width/2)==(sign<0)],key=lambda r:r[1]):
            ly=max(y-9,last);last=ly+20;lx=18 if sign<0 else width-148
            draw.line([(x,y),(lx+135 if sign<0 else lx-3,ly+9)],fill='#8c99a5',width=1);draw.text((lx,ly),n,font=font,fill='#23313d')
    if fingers:
        branches=json.loads((O/'finger_branch_prototype.json').read_text())['sides']['l']
        for branch in branches:
            pts=branch['connected_joint_proposal_cm'];draw.line([xy(p) for p in pts],fill='#d58b00',width=3)
            for p in pts:
                x,y=xy(p);draw.ellipse((x-4,y-4,x+4,y+4),fill='#d58b00')
    draw.text((25,20),name.replace('_',' '),font=font,fill='#23313d')
    draw.text((25,48),'Green: accepted proposal   Amber: ambiguous; overall proposal REJECTED',font=font,fill='#23313d')
    draw.text((25,height-35),'Geometry-derived Phase4B proposal; no Phase4A joint input; centimetre coordinates',font=font,fill='#23313d')
    im.save(O/(name+'.png'))
render('fitted_skeleton_front',0,[[-43,-30,0],[43,30,180]])
render('fitted_skeleton_side',1,[[-43,-30,0],[43,30,180]])
render('automatic_major_landmarks',0,[[-43,-30,0],[43,30,180]],edges=False)
render('hand_finger_evidence',1,[[25,-9,75],[40,19,110]],900,850,fingers=True)
render('foot_ankle_ball',1,[[10,-9,0],[30,25,28]],900,850)
print('FIT_IMAGES_DONE')
