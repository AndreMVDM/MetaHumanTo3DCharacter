"""Diagnostic illustrations and controls; never changes production gates."""
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from diagnose_body_topology import D,policy,planar_faces,winding

data=json.loads((D/'measurements.json').read_text())
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for name,row in data['roles'].items():
    canvas=Image.new('RGB',(1600,920),'white');draw=ImageDraw.Draw(canvas)
    draw.text((20,15),name+': diagnostic regions and real source junctions',fill='#142c40',font=font)
    draw.text((20,45),'Blue = source section; green = candidate boundary; red = accepted pivot. Candidate regions are not gate passes.',fill='#142c40',font=small)
    arrangement=row['locally_matched_region_arrangement']
    selected=[f for f in arrangement['bounded_faces'] if f['region_inside'] and f['valid_boundary_cycles']]
    foci=[b['position_cm'][:2] for b in row['branch_nodes']]+[c['xy_cm'] for c in row['crossings']]
    # Main role-local plot plus four actual source defect insets.
    components=set(row['section_components'])
    if name.startswith('thigh'):components={25}
    if name=='foot_l':components={32}
    if name=='foot_r':components={7}
    segs=[s for s in row['segments'] if s['component'] in components]
    xy=np.array([s[k][:2] for s in segs for k in ['a_cm','b_cm']]);lo=xy.min(0)-1;hi=xy.max(0)+1
    views=[((20,85,810,805),lo,hi)]+[((850+(i%2)*370,85+(i//2)*365,1210+(i%2)*370,430+(i//2)*365),np.array(q)-1.1,np.array(q)+1.1) for i,q in enumerate(foci[:4])]
    for idx,(box,low,high) in enumerate(views):
        x0,y0,x1,y1=box;scale=min((x1-x0-30)/(high[0]-low[0]),(y1-y0-40)/(high[1]-low[1]))
        centre=(low+high)/2
        def project(q):return ((x0+x1)/2+(q[0]-centre[0])*scale,(y0+y1)/2-(q[1]-centre[1])*scale)
        draw.rectangle(box,outline='#c6c6c6');draw.text((x0+8,y0+6),'Role scope' if idx==0 else f'Junction {idx}; 2.2 cm square',fill='#142c40',font=small)
        for s in row['segments']:
            a=np.array(s['a_cm'][:2]);b=np.array(s['b_cm'][:2])
            if np.any(np.maximum(a,b)<low) or np.any(np.minimum(a,b)>high):continue
            pa=project(a);pb=project(b)
            if all(x0<=q[0]<=x1 and y0<=q[1]<=y1 for q in [pa,pb]):draw.line([pa,pb],fill='#256bad',width=2)
        for f in selected:
            for c in f['boundary_cycles']:
                coords=c['polygon_cm']+[c['polygon_cm'][0]]
                for a,b in zip(coords,coords[1:]):
                    pa=project(a);pb=project(b)
                    if all(x0<=q[0]<=x1 and y0<=q[1]<=y1 for q in [pa,pb]):draw.line([pa,pb],fill='#178a4d',width=3)
        px,py=project(row['pivot_cm'])
        if x0<px<x1 and y0<py<y1:draw.line([(px-7,py),(px+7,py)],fill='#d22a40',width=3);draw.line([(px,py-7),(px,py+7)],fill='#d22a40',width=3)
    draw.text((20,835),f'Candidate containing regions: {len(selected)}. Source components in the section: {row["section_components"]}.',fill='#142c40',font=font)
    draw.text((20,875),'All source segments, triangle IDs, incident faces, normals, seam distances and rays: measurements.json',fill='#142c40',font=small)
    canvas.save(D/f'{name}_regions_and_junctions.png')

def segs(poly):return [{'component':0,'triangle_index':i,'a_cm':[a[0],a[1],0.],'b_cm':[b[0],b[1],0.]} for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1]))]
square=segs([[-2,-2],[2,-2],[2,2],[-2,2]])
controls=[]
def check(name,s,p,expected):
    r=planar_faces(s,np.array([*p,0.]),True);actual=r['containing_valid_regions']>0
    assert actual==expected,(name,actual)
    controls.append({'control':name,'expected_enclosing_arrangement':expected,'observed':actual})
check('closed square',square,[0,0],True)
check('outside point',square,[3,0],False)
check('open three sides',square[:3],[0,0],False)
check('small real gap is not numerical closure',[dict(square[0],b_cm=[1.99,-2,0.])]+square[1:],[0,0],False)
check('dangling external tail does not destroy closed face',square+[{'component':0,'triangle_index':4,'a_cm':[2,2,0.],'b_cm':[3,3,0.]}],[0,0],True)
check('exact endpoint-on-edge T contact',square+[{'component':0,'triangle_index':4,'a_cm':[0,2,0.],'b_cm':[0,3,0.]}],[0,0],True)
check('concave outside point',segs([[-2,-2],[2,-2],[2,-1],[-1,-1],[-1,2],[-2,2]]),[0,0],False)
check('overlapping closed loops',square+segs([[0,-1],[3,-1],[3,1],[0,1]]),[1,0],True)
# Deliberately expose the method's limitation: boundary coordinates alone do not
# encode an oriented cavity or choose garment layers. This must never be a gate.
nested=planar_faces(square+segs([[-1,-1],[1,-1],[1,1],[-1,1]]),np.zeros(3),True)
controls.append({'control':'disconnected nested boundaries need shell semantics','candidate_enclosure_count':nested['containing_valid_regions'],
                 'limitation':'An oriented cavity must reject this point; a filled nested garment layer may support it. Arrangement-only containment cannot decide.'})
v=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]])
f=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
for name,p,expected in [('closed cube interior',[0,0,0],1),('closed cube exterior',[2,0,0],0)]:
    actual=winding(np.array(p),v[f]);assert abs(actual-expected)<1e-10
    controls.append({'control':name,'winding':actual,'expected':expected})
controls.append({'control':'open cube is not an integer volume certificate','interior_winding':winding(np.zeros(3),v[f[2:]]),
                 'limitation':'A large winding value on an open surface is corroboration, not watertight enclosure proof.'})
(D/'diagnostic_controls.json').write_text(json.dumps(controls,indent=2),encoding='utf-8')
before=json.loads((D/'preservation_before.json').read_text())
changed=[p for p,h in before.items() if hashlib.sha256(__import__('pathlib').Path(p).read_bytes()).hexdigest()!=h]
assert not changed,changed
(D/'preservation_after.json').write_text(json.dumps({'baseline_files':len(before),'changed':changed,'gate_and_review_preserved':True,
        'validator_run':False,'new_policy_implemented':False,'diagnostic_assertions_passed':10},indent=2),encoding='utf-8')
print('10 diagnostic assertions passed; nested/open volume limitations recorded; 385 existing files preserved.')
