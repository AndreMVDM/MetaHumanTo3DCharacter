"""Identical-camera CPU LBS geometry views and actual weight-field heatmaps."""
from model import *
from PIL import Image,ImageDraw,ImageFont
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
def draw_mesh(im,m,out,rect,axis,lo,hi,field=None):
    draw=ImageDraw.Draw(im);x,y,w,h=rect;lo=np.array(lo);hi=np.array(hi);scale=min((w-30)/(hi[axis]-lo[axis]),(h-65)/(hi[2]-lo[2]));centre=(hi+lo)/2
    points=np.c_[x+w/2+(out[:,axis]-centre[axis])*scale,y+h/2+20-(out[:,2]-centre[2])*scale]
    tv=out[m.tri];mask=np.all(tv.max(1)>=lo,axis=1)&np.all(tv.min(1)<=hi,axis=1);ix=np.flatnonzero(mask);ix=ix[np.argsort(tv[ix,:,1-axis].mean(1))]
    normals=np.cross(tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-9);light=.55+.4*abs(normals@np.array([.25,.5,.83]))
    if field is not None:
        f=field[m.tri].mean(1);colour=np.stack([40+215*f,65+55*(1-f),205-165*f],axis=1)
    else:colour=np.tile([174,189,208],(len(m.tri),1))
    for t in ix:draw.polygon([tuple(p) for p in points[m.tri[t]]],fill=tuple((colour[t]*light[t]).astype(int)))
    if lo[2]<=0<=hi[2]:
        zz=y+h/2+20+centre[2]*scale;draw.line([(x,zz),(x+w,zz)],fill='#c01b35',width=2)
def compare(m,candidates,file,poses,region='body',axis=0):
    box={'body':([-100,-100,-15],[100,100,205]),'pants':([-30,-40,70],[30,40,120]),'shoulders':([-45,-45,110],[45,45,158]),'feet':([-40,-35,-8],[40,35,45])}[region]
    cw=430;rh=420;im=Image.new('RGB',(cw*len(candidates),55+rh*len(poses)),'#f7f9fc');d=ImageDraw.Draw(im)
    d.text((15,10),'Phase4E | original triangles | actual weights + diagnostic/UE poses | CPU LBS',font=font,fill='#172433')
    for col,(name,w) in enumerate(candidates.items()):
        for row,n in enumerate(poses):
            rect=(col*cw,55+row*rh,cw,rh);draw_mesh(im,m,m.deform(w,m.poses[n]),rect,axis,*box);d.text((rect[0]+10,rect[1]+5),name+' | '+n,font=font,fill='#172433')
    im.save(O/file)
if __name__=='__main__':
    m=Model();ws={'baseline':m.weights}
    selected=W/'selected_weights.json'
    if selected.exists():ws['refined']=m.dense(load(selected))
    compare(m,ws,'pants_front_comparison.png',['neutral','idle_0','wide_stance','reach_0.5','walk_0.5'],'pants',0)
    compare(m,ws,'pants_side_comparison.png',['neutral','wide_stance','reach_0.5','walk_0.5'],'pants',1)
    compare(m,ws,'shoulder_comparison.png',['neutral','arms_horizontal','arms_overhead','reach_0.5'],'shoulders',0)
    compare(m,ws,'body_comparison.png',['neutral','wide_stance','knee_bend','reach_0.5'],'body',0)
    im=Image.new('RGB',(1680,900),'#f7f9fc');d=ImageDraw.Draw(im)
    for i,n in enumerate(['root','pelvis','thigh_l','thigh_r','clavicle_l','upperarm_l','spine_03','clavicle_r']):
        rect=(i%4*420,i//4*450,420,450);box=([-30,-40,75],[30,40,118]) if i<4 else ([-35,-35,115],[35,35,155]);draw_mesh(im,m,m.v,rect,0,*box,m.weights[:,m.bi[n]]);d.text((rect[0]+10,rect[1]+5),n+' | blue=0 red=1',font=font,fill='#172433')
    im.save(O/'baseline_weight_heatmaps.png');print('Rendered geometry and weight comparisons')
