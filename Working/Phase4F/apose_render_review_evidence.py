"""CPU source/proposal and connectivity views, labelled as diagnostics, not anatomy approval."""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F';O=P/'Documentation/Phase4F'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',12)
def render(character,axes,name,lo,hi,overlay=True,components=False,side=None):
    d=np.load(W/character/'normalised_geometry.npz');v=d['vertices'];t=d['triangles'];co=O/character;fit=json.loads((co/'current_proposal.json').read_text());tracks=json.loads((co/'finger_tracks.json').read_text())['sides']
    im=Image.new('RGB',(1200,900),'#f4f6f8');draw=ImageDraw.Draw(im);draw.text((18,12),character+' — '+name+' | CPU source-data projection; anatomy NOT accepted',font=font,fill='#152436')
    lo=np.array(lo);hi=np.array(hi);scale=min(1140/(hi[axes[0]]-lo[axes[0]]),780/(hi[axes[1]]-lo[axes[1]]));centre=(lo+hi)/2
    def xy(p):return (600+(p[axes[0]]-centre[axes[0]])*scale,465-(p[axes[1]]-centre[axes[1]])*scale)
    depth=next(a for a in range(3) if a not in axes)
    tv=v[t];ids=np.flatnonzero(np.all(tv.max(1)>=lo,axis=1)&np.all(tv.min(1)<=hi,axis=1));ids=ids[np.argsort(tv[ids,:,depth].mean(1))]
    normals=np.cross(tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-10);light=.5+.45*abs(normals@np.array([.25,.5,.83]))
    palette=np.array([[80,140,210],[204,123,74],[116,166,81],[176,102,181],[217,175,60],[68,177,175],[175,80,100]])
    for k in ids:
        colour=palette[int(d['weld_component'][t[k,0]])%len(palette)] if components else np.array([174,188,205])
        draw.polygon([xy(p) for p in tv[k]],fill=tuple((colour*light[k]).astype(int)))
    if overlay:
        rows={r['role']:r for r in fit['joints']}
        for r in rows.values():
            p=np.array(r['position_cm'])
            if r['parent_role']:draw.line([xy(rows[r['parent_role']]['position_cm']),xy(p)],fill='#8040b0',width=2)
            colour='#0c8650' if r['status']=='automatically_accepted' else '#cc6500';x,y=xy(p);draw.ellipse((x-4,y-4,x+4,y+4),fill=colour);draw.text((x+6,y-8),r['role'],fill='#101820',font=small)
    if side:
        for i,tr in enumerate(tracks[side]):
            pts=list(reversed(tr['ordered_surface_section_centres_cm']));draw.line([xy(p) for p in pts],fill='#bf1438',width=3)
            x,y=xy(pts[-1]);draw.text((x+4,y-14),'Track '+str(i+1),font=small,fill='#101820')
    if components:
        summary=json.loads((O/character/'geometry_summary.json').read_text())
        for s in summary['components']:
            if s['vertices']<500:continue
            p=(np.array(s['bounds_cm']).mean(0)@np.array(json.loads((O/character/'coordinate_frame.json').read_text())['rotation_columns_world'])-np.array(json.loads((O/character/'coordinate_frame.json').read_text())['origin_body_coordinates_cm']))*180/json.loads((O/character/'coordinate_frame.json').read_text())['source_height_cm']
            x,y=xy(p);draw.text((x,y),'C'+str(s['id'])+' / '+str(s['vertices'])+'v',font=small,fill='black')
    draw.text((18,865),'Colours/nearest-surface outlines are diagnostic evidence; no human review or garment body-donor acceptance is inferred.',font=small,fill='#26323f')
    path=co/(name+'.png');im.save(path);return path
for character in ['John','Jane']:
    co=O/character
    render(character,(0,2),'proposal_front',[-100,-40,0],[100,40,185])
    render(character,(1,2),'proposal_side',[-100,-40,0],[100,40,185])
    render(character,(0,2),'connectivity_front',[-100,-40,0],[100,40,185],False,True)
    for side in ['l','r']:
        ts=json.loads((co/'finger_tracks.json').read_text())['sides'][side];points=np.array([p for tr in ts for p in tr['ordered_surface_section_centres_cm']]);lo=points.min(0)-4;hi=points.max(0)+4
        render(character,(0,1),'hand_'+side+'_top',lo,hi,False,False,side)
        render(character,(0,2),'hand_'+side+'_front',lo,hi,False,False,side)
print('Source proposal/connectivity/finger review projections written')
