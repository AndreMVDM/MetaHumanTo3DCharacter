import json,numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
from geometry_tools import body_frame,sections
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B'
d=np.load(W/'source_geometry.npz');v,frame=body_frame(d['vertices']);t=d['triangles'];np.savez(W/'normalised_geometry.npz',vertices=v,triangles=t)
(O/'coordinate_frame.json').write_text(json.dumps(frame,indent=2))
rows=[]
for z in np.arange(3,178,2):
    cs=sections(v,t,z);rows.append({'height_cm':float(z),'contours':[{k:q[k] for k in q if k!='points'} for q in cs]})
(O/'cross_sections.json').write_text(json.dumps(rows,indent=2))
im=Image.new('RGB',(1250,1020),'#f7f8fa');draw=ImageDraw.Draw(im)
for side,(horizontal,label) in enumerate([(0,'Front: left X / up Z'),(1,'Side: forward Y / up Z')]):
    for p in v:draw.point((310+side*620+p[horizontal]*5,960-p[2]*5),fill='#444b55')
    draw.text((side*620+30,25),label,fill='black')
    for row in rows[::5]:
        for c in row['contours']:
            p=c['centre'];draw.ellipse((308+side*620+p[horizontal]*5,958-p[2]*5,312+side*620+p[horizontal]*5,962-p[2]*5),fill='#dc2626')
im.save(O/'raw_geometry_sections.png')
print('FRAME',frame)
for row in rows[::4]:print(row['height_cm'],[(np.round(c['centre'],1).tolist(),np.round(np.array(c['max'])-c['min'],1).tolist(),c['closed']) for c in row['contours']])
