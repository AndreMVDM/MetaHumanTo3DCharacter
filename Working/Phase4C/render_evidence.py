"""Orthographic renders of actual extracted surfaces/joints; no animation claim."""
import json,re,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4C';O=P/'Documentation/Phase4C'
d=json.loads((W/'donor_geometry_and_joints.json').read_text());src=np.load(W/'normalised_geometry.npz');v=src['vertices'];t=src['triangles']
m=d['meshes_lod0'][0];dv=np.array(m['vertices_cm']);dt=np.array([[f[0],f[i],f[i+1]] for f in m['faces'] for i in range(1,len(f)-1)])
j={x['name']:x for x in d['joints']};b=json.loads((P/'Documentation/Phase4B/automatic_fit_v2.json').read_text())['joints']
core=['root','pelvis','spine_01','spine_02','spine_03','spine_04','spine_05','neck_01','neck_02','head']+[n+'_'+s for s in ['l','r'] for n in ['clavicle','upperarm','lowerarm','hand','thigh','calf','foot','ball']]
digits=[n for n in j if re.match(r'^(thumb|index|middle|ring|pinky)_(0[123]|metacarpal)_[lr]$',n)]
digit_colours={'thumb':'#c33535','index':'#006eae','middle':'#13874a','ring':'#8a42bd','pinky':'#c46d00'}
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
attempt=json.loads((O/'analysis_summary.json').read_text())['selected_attempt'] if (O/'analysis_summary.json').exists() else 'body-only/full surface diagnostic'
def render(name,axis,box,donor=False,skeleton=True,old=False,source=True,hands=False):
    width,height=1250,1050;lo,hi=np.array(box[0]),np.array(box[1]);scale=min((width-280)/(hi[axis]-lo[axis]),(height-220)/(hi[2]-lo[2]));centre=(lo+hi)/2
    def xy(p):return [width/2+(p[axis]-centre[axis])*scale,height/2+20-(p[2]-centre[2])*scale]
    im=Image.new('RGB',(width,height),'#f7f9fc');draw=ImageDraw.Draw(im)
    def surface(verts,tris,colour,opacity=255):
        layer=Image.new('RGBA',im.size,(0,0,0,0));dr=ImageDraw.Draw(layer);tv=verts[tris];depth=1-axis
        keep=np.all(tv.max(1)>=lo,axis=1)&np.all(tv.min(1)<=hi,axis=1)
        ids=np.where(keep)[0];ids=ids[np.argsort(tv[ids,:,depth].mean(1))]
        normal=np.cross(tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-9)
        intensity=.65+.30*abs(normal@np.array([.35,.45,.82]))
        for i in ids:
            col=tuple(int(c*intensity[i]) for c in colour)+(opacity,);dr.polygon([tuple(xy(p)) for p in tv[i]],fill=col)
        im.paste(Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB'))
    if source:surface(v,t,(196,207,217))
    if donor:surface(dv,dt,(54,137,168),105 if source else 255)
    draw=ImageDraw.Draw(im)
    if old:
        bp={x['role']:np.array(x['position_cm']) for x in b}
        for row in b:
            if row['parent_role']:draw.line([tuple(xy(bp[row['role']])),tuple(xy(bp[row['parent_role']]))],fill='#b48a00',width=3)
    names=core+(digits if hands else [])
    if skeleton:
        for n in names:
            if n not in j:continue
            row=j[n];p=np.array(row['world_cm']);par=d['joints'][row['parent_index']]['name']
            # Collapse helper joints only for display; original hierarchy retained in JSON.
            pp=np.array(j[par]['world_cm']) if par in j else p
            colour=digit_colours.get(n.split('_')[0],'#d94740')
            visible=lambda q: lo[axis]<=q[axis]<=hi[axis] and lo[2]<=q[2]<=hi[2]
            if par in j and n!='root' and visible(p) and visible(pp):draw.line([tuple(xy(p)),tuple(xy(pp))],fill=colour,width=3)
            if np.all(p>=lo)&np.all(p<=hi):
                x,y=xy(p);draw.ellipse([x-5,y-5,x+5,y+5],fill=colour,outline='white',width=1)
                if (hands and n.startswith('hand_')) or (not hands and n in ['pelvis','head','neck_01','upperarm_l','lowerarm_l','hand_l','thigh_l','calf_l','foot_l','ball_l']):
                    draw.text((x+8,y-12),n,font=small,fill='#172433')
    if hands:
        draw.rectangle((20,124,330,345),fill='#f7f9fc')
        for i,(digit,colour) in enumerate(digit_colours.items()):draw.text((30,140+i*30),digit+' 01 / 02 / 03',font=font,fill=colour)
        draw.text((30,315),'Metacarpals included where exposed',font=small,fill='#172433')
    draw.rectangle((0,0,width,98),fill='#f7f9fc');draw.rectangle((0,height-76,width,height),fill='#f7f9fc')
    draw.text((24,15),name.replace('_',' ')+' | '+('front' if axis==0 else 'side'),font=font,fill='#172433')
    draw.text((24,44),'Grey: original Lara source surface | Cyan: temporary donor | Coloured points: donor joints',font=small,fill='#172433')
    draw.text((24,69),'Gold: Phase4B geometry proposal' if old else 'Lara: fresh ZIP geometry | Donor: public posed-DNA readback | Orthographic projection',font=small,fill='#172433')
    draw.text((24,height-63),'Attempt: '+attempt+' | Anatomy not accepted; no skinning or animation',font=small,fill='#172433')
    draw.text((24,height-36),'Centimetres, +X left / +Y forward / +Z up; same scale and origin for target and donor',font=small,fill='#172433')
    im.save(O/(name+'.png'))
full=[[-65,-30,0],[65,60,210]]
render('original_Lara_surface',0,full,skeleton=False)
render('temporary_donor_overlay',0,full,donor=True)
render('donor_semantic_skeleton',0,full,source=False,donor=True)
render('mapped_donor_front',0,full)
render('mapped_donor_side',1,full)
render('front_comparison',0,full,donor=True,old=True)
render('side_comparison',1,full,donor=True,old=True)
render('pelvis_hip_closeup',0,[[-22,-20,80],[22,25,120]],donor=True)
render('shoulder_elbow_closeup',0,[[-36,-20,108],[36,22,158]],donor=True)
render('knee_closeup',0,[[-25,-20,35],[25,25,75]],donor=True)
render('ankle_ball_foot_closeup',1,[[-30,-15,0],[30,35,30]],donor=True)
render('hand_finger_closeup',1,[[20,-4,78],[44,20,108]],donor=True,hands=True)
render('hand_finger_right_closeup',1,[[-44,-4,78],[-20,20,108]],donor=True,hands=True)
render('Phase4B_vs_Phase4C_overlay',0,full,old=True)
print('Rendered 14 actual-data debug views including both hands')
