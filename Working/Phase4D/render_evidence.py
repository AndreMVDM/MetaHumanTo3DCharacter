"""Actual-source projections; baseline and completed human trial labelled separately."""
import sys, numpy as np
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import core
W=core.W;O=core.O
src=np.load(W/'normalised_geometry.npz');v=src['vertices'];t=src['triangles'];fit=core.read(O/'current_proposal.json');base=core.read(O/'automatic_starting_proposal.json');state=core.read(W/'session.json')
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
colours={'automatically_accepted':'#159947','ambiguous':'#d88016','manually_corrected':'#1263de','dependency_recomputed':'#9845d6'}
views=[('original_automatic_proposal',0,[-60,-25,0],[60,35,190],False,False),('pre_correction_front',0,[-60,-25,0],[60,35,190],False,False),('pre_correction_side',1,[-60,-25,0],[60,35,190],False,False),('pelvis_hips',0,[-25,-20,85],[25,25,123],False,False),('shoulders_elbows_wrists',0,[-43,-20,88],[43,25,155],False,False),('knees',0,[-26,-18,35],[26,26,78],False,False),('ankles_feet_balls',1,[-30,-15,0],[30,28,30],False,False),('left_hand_tracks',1,[23,-3,78],[42,20,108],True,False),('right_hand_tracks',1,[-43,-3,78],[-23,20,108],True,False),('automatic_current_overlay',0,[-60,-25,0],[60,35,190],False,True),('correction_control_design',0,[-60,-25,0],[60,35,190],False,False)]
views.extend([('accepted_front',0,[-60,-25,0],[60,35,190],False,False),('accepted_side',1,[-60,-25,0],[60,35,190],False,False)])
manifest=[]
for name,axis,lower,upper,hands,overlay in views:
    lo=np.array(lower);hi=np.array(upper);size=(1180,1050);scale=min((size[0]-250)/(hi[axis]-lo[axis]),(size[1]-205)/(hi[2]-lo[2]));centre=(lo+hi)/2
    def xy(p):return (size[0]/2+(p[axis]-centre[axis])*scale,size[1]/2+20-(p[2]-centre[2])*scale)
    im=Image.new('RGB',size,'#f7f9fc');draw=ImageDraw.Draw(im);tv=v[t];ids=np.where(np.all(tv.max(1)>=lo,axis=1)&np.all(tv.min(1)<=hi,axis=1))[0];ids=ids[np.argsort(tv[ids,:,1-axis].mean(1))]
    normals=np.cross(tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-9);light=.65+.3*abs(normals@np.array([.35,.45,.82]))
    for i in ids:draw.polygon([xy(p) for p in tv[i]],fill=tuple(int(c*light[i]) for c in [198,208,219]))
    def joints(rows,baseline=False):
        by={r['role']:r for r in rows}
        for n,r in by.items():
            p=np.array(r['position_cm']);colour='#687e91' if baseline else colours[r['status']]
            if n in state['approvals'] and not baseline and r['status'] not in ['manually_corrected','dependency_recomputed']:colour='#009daa'
            if r['parent_role']:
                pp=np.array(by[r['parent_role']]['position_cm'])
                if lo[2]<=p[2]<=hi[2] and lo[2]<=pp[2]<=hi[2]:draw.line([xy(p),xy(pp)],fill=colour,width=3)
            if np.all(p>=lo) and np.all(p<=hi):
                x,y=xy(p);draw.ellipse([x-4,y-4,x+4,y+4],fill=colour,outline='white')
                if not hands and n not in ['root','spine_01','spine_02','spine_03']:draw.text((x+6,y-10),core.LABELS.get(n,n),font=small,fill='#172433')
    if overlay:joints(base['joints'],True)
    historical=name in ['original_automatic_proposal','pre_correction_front','pre_correction_side']
    joints(base['joints'] if historical else fit['joints'],historical)
    if hands:
        side='l' if name.startswith('left') else 'r'
        palette=['#d94b69','#2279c9','#159947','#9945c8','#b07808']
        for track,colour in zip(state['tracks'][side],palette):
            points=track['ordered_surface_section_centres_cm'];draw.line([xy(p) for p in points],fill=colour,width=4);x,y=xy(points[0]);draw.text((x+7,y+3),'Track '+track['candidate_id'].split('_')[2],font=small,fill=colour)
        for key,f in state['fingers'].items():
            if f['side']==side:draw.line([xy(p) for p in f['path_cm']],fill='#9845d6',width=3)
    draw.rectangle([0,0,size[0],95],fill='#f7f9fc');draw.rectangle([0,size[1]-72,size[0],size[1]],fill='#f7f9fc');draw.text((22,12),name.replace('_',' ')+' | Phase4D',font=font,fill='#172433');draw.text((22,40),'Grey: original Lara surface | Green: automatic | Amber: review | Blue: moved | Purple: dependent',font=small,fill='#172433');draw.text((22,65),'Orthographic numerical projection; target height 180cm. Baseline before human review.' if historical else 'Orthographic numerical projection; completed human trial. Cyan: accepted without movement.',font=small,fill='#172433');draw.text((22,size[1]-60),'Historical automatic proposal; no human corrections shown.' if historical else 'Accepted landmark proposal; original surface is unskinned. Native playback is separate evidence.',font=small,fill='#172433');draw.text((22,size[1]-33),'Single neck movement; all ten digit assignments use recorded human correspondence.' if not historical else 'Preserved baseline for comparison with the actual final human-reviewed proposal.',font=small,fill='#172433');path=O/(name+'.png');im.save(path);manifest.append({'file':path.name,'kind':'actual-source numerical debug projection','post_correction':not historical,'baseline':historical})
manifest.extend({'file':p.name,'kind':'actual UE static proposal viewport capture','post_correction':False} for p in sorted(O.glob('ue_pre_*.png')))
core.save(O/'visual_evidence.json',{'available':manifest,'separate_downstream_evidence':['native_playback.png','animated_finger_validation.png','deformation_contact_results.json'],'pending':[],'no_synthetic_corrections_presented_as_real':True})
print('Rendered',len(manifest),'actual-data views')
