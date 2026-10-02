"""Geometry-only proposal. Phase4A control is deliberately inaccessible in this module."""
import json,math,hashlib
from pathlib import Path
import numpy as np
from geometry_tools import sections
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B'
d=np.load(W/'normalised_geometry.npz');V=d['vertices'];T=d['triangles'];H=float(np.ptp(V[:,2]));cache={}
def section(z):
    z=float(z)
    if z not in cache:cache[z]=sections(V,T,z)
    return cache[z]
def group(z,role,side=0):
    cs=section(z);ps=np.array([p for c in cs for p in c['points']])
    if role=='torso':
        eligible=[c for c in cs if abs(c['centre'][0])<H*.08 and (c['max'][0]-c['min'][0])>H*.055 and c['centre'][1]>-H*.05]
        if not eligible:eligible=[c for c in cs if abs(c['centre'][0])<H*.10 and c['centre'][1]>-H*.05]
        # Include front/back surfaces of split torso shells rather than picking a breast/front shell alone.
        ps=np.array([p for c in eligible for p in c['points']])
    elif role=='arm':
        # Split the cross section at geometric empty gaps, allowing disconnected clothing fragments.
        xs=np.sort(np.unique(ps[:,0]));gaps=np.diff(xs);ix=np.argsort(gaps)[::-1]
        bounds=[]
        for i in ix:
            mid=(xs[i]+xs[i+1])/2
            if gaps[i]>1.0 and abs(mid)>H*.055:bounds.append(mid)
            if len([b for b in bounds if b<0]) and len([b for b in bounds if b>0]):break
        b=max([b for b in bounds if b<0],default=-H*.13) if side<0 else min([b for b in bounds if b>0],default=H*.13)
        ps=ps[ps[:,0]<b] if side<0 else ps[ps[:,0]>b]
        if not len(ps):raise ValueError('No isolated arm section')
    elif role=='leg':
        eligible=[c for c in cs if side*c['centre'][0]>H*.025 and (c['max'][0]-c['min'][0])>H*.025]
        c=max(eligible,key=lambda c:(c['max'][0]-c['min'][0])*(c['max'][1]-c['min'][1]));ps=np.array(c['points'])
    lo=ps.min(0);hi=ps.max(0);centre=(lo+hi)/2
    return centre,{'section_z_cm':z,'region':role,'side':side,'points':len(ps),'bounds_cm':[lo.tolist(),hi.tolist()],'width_cm':float(hi[0]-lo[0]),'depth_cm':float(hi[1]-lo[1]),'closed_contour_fraction':float(np.mean([c['closed'] for c in cs]))}
def curve(role,side,lo,hi):
    rows=[]
    for z in np.arange(lo,hi+.1,1):
        try:p,e=group(z,role,side);rows.append((p,e))
        except (ValueError,IndexError):continue
    return rows
def piecewise(rows,lo,hi):
    p=np.array([r[0] for r in rows]);z=p[:,2];out=[]
    for k in range(3,len(rows)-3):
        if not lo<=z[k]<=hi:continue
        residual=0
        for ids in [np.arange(k+1),np.arange(k,len(rows))]:
            a=np.c_[z[ids],np.ones(len(ids))];fit=a@np.linalg.lstsq(a,p[ids,:2],rcond=None)[0];residual+=float(((fit-p[ids,:2])**2).sum())
        u=p[k]-p[0];v=p[-1]-p[k];angle=math.degrees(math.acos(float(np.clip(u@v/(np.linalg.norm(u)*np.linalg.norm(v)),-1,1))))
        out.append({'position_cm':p[k].tolist(),'residual_cm2':residual,'bend_deg':angle,'evidence':rows[k][1]})
    return sorted(out,key=lambda r:r['residual_cm2'])
joints=[];features={};curves={}
def add(name,parent,p,evidence,score=.85,flags=None,candidates=None):
    flags=flags or [];parts={'surface_support':min(1.0,evidence.get('points',30)/30),'role_specificity':score,'hierarchy_prior':1.0};s=.3*parts['surface_support']+.6*parts['role_specificity']+.1
    joints.append({'role':name,'parent_role':parent,'position_cm':np.array(p).tolist(),'side':'left' if name.endswith('_l') else 'right' if name.endswith('_r') else 'centre','evidence_sources':[evidence,'Canonical connected biped hierarchy; region/height search windows are priors, positions come from target sections'],'confidence_score':s,'confidence_components':parts,'ambiguity_flags':flags,'competing_candidates':candidates or [],'status':'ambiguous' if flags or s<.80 else 'automatically_accepted','manual_correction':None})
add('root',None,[0,0,0],{'method':'ground frame origin','points':json.loads((O/'coordinate_frame.json').read_text())['ground_plane_points']},1)
# Crotch is the first stable transition from two large leg contours to one central pelvic contour.
merged=[]
for z in np.arange(H*.40,H*.58,1):
    cs=[c for c in section(z) if c['count']>=25 and c['max'][0]-c['min'][0]>H*.05]
    merged.append((z,any(c['min'][0]<-1 and c['max'][0]>1 for c in cs)))
crotch=next(z for i,(z,ok) in enumerate(merged[:-2]) if ok and merged[i+1][1] and merged[i+2][1])
torso=curve('torso',0,crotch+3,H*.75)
waist=min([r for r in torso if H*.55<r[0][2]<H*.68],key=lambda r:r[1]['width_cm'])
pelvis_z=(crotch+waist[0][2])/2;pelvis,pe=group(pelvis_z,'torso');pelvis[0]=0
features.update({'crotch_merge_z_cm':float(crotch),'waist_min_width':waist[1],'pelvis_region_midpoint_z_cm':float(pelvis_z)})
add('pelvis','root',pelvis,pe,.66,['internal_pelvis_articulation_not_visible'])
# Upper torso/neck boundary is geometric shoulder-width collapse, not a fixed coordinate.
neck_curve=curve('torso',0,H*.77,H*.88);neck=min(neck_curve,key=lambda r:r[1]['width_cm']);neckp=neck[0].copy();neckp[0]=0
shoulder_z=max(z for z in np.arange(H*.72,H*.82,1) if group(z,'torso')[1]['width_cm']>H*.18)-3
for i,z in enumerate(np.linspace(pelvis_z,shoulder_z-2,4)[1:],1):
    p,e=group(z,'torso');p[0]=0;add(f'spine_{i:02}','pelvis' if i==1 else f'spine_{i-1:02}',p,e,.84)
add('neck_01','spine_03',neckp,neck[1],.77,['hair_and_neck_surface_overlap'])
headz=(neckp[2]+H)/2;p,e=group(headz,'torso');p[0]=0;add('head','neck_01',p,e,.84)
for side,s in [('l',1),('r',-1)]:
    arm=curve('arm',s,H*.51,H*.735);leg=curve('leg',s,H*.12,crotch-2);curves['arm_'+side]=[{'position_cm':p.tolist(),'evidence':e} for p,e in arm];curves['leg_'+side]=[{'position_cm':p.tolist(),'evidence':e} for p,e in leg]
    # The wrist is the narrow neck between palm and lower arm. Restrict to lower-arm/palm transition.
    wristrows=curve('arm',s,H*.51,H*.59);wrist=min(wristrows,key=lambda r:r[1]['width_cm']*r[1]['depth_cm']);wp=wrist[0]
    elbow_candidates=piecewise(arm,max(wp[2]+8,H*.60),H*.71);elbow=elbow_candidates[0];ep=np.array(elbow['position_cm'])
    shoulder=arm[-1][0].copy();shoulder[2]=shoulder_z
    # Extrapolate isolated upper-arm centreline to shoulder region, then project into shoulder cross section.
    pp=np.array([r[0] for r in arm[-8:]]);a=np.c_[pp[:,2],np.ones(len(pp))];shoulder[:2]=np.array([shoulder_z,1])@np.linalg.lstsq(a,pp[:,:2],rcond=None)[0]
    shoulder_section=section(shoulder_z);sp=np.array([p for c in shoulder_section for p in c['points']]);sp=sp[s*sp[:,0]>H*.055];bounds=[sp.min(0),sp.max(0)];shoulder[:2]=np.clip(shoulder[:2],bounds[0][:2]+1,bounds[1][:2]-1)
    clav=shoulder.copy();clav[0]*=.48;clav[2]+=1
    add('clavicle_'+side,'spine_03',clav,{'method':'upper torso to fitted shoulder branch','points':len(sp)},.68,['shoulder_girdle_internal_landmark'])
    add('upperarm_'+side,'clavicle_'+side,shoulder,{'method':'upper-arm section extrapolation and shoulder volume projection','points':len(sp),'bounds_cm':[b.tolist() for b in bounds]},.68,['hair_clothing_obscures_shoulder_articulation'])
    add('lowerarm_'+side,'upperarm_'+side,ep,elbow['evidence'],.69,['piecewise_bend_may_follow_surface_not_elbow'],elbow_candidates[:5])
    add('hand_'+side,'lowerarm_'+side,wp,wrist[1],.89)
    knee_candidates=piecewise(leg,H*.25,H*.39);knee=knee_candidates[0];kp=np.array(knee['position_cm'])
    # Hip joint proposal is extrapolated from the upper thigh within the pelvic articulation volume.
    pp=np.array([r[0] for r in leg[-7:]]);a=np.c_[pp[:,2],np.ones(len(pp))];hipz=pelvis_z-2;hip=np.r_[np.array([hipz,1])@np.linalg.lstsq(a,pp[:,:2],rcond=None)[0],hipz]
    anklecurve=curve('leg',s,H*.045,H*.13);ankle=min(anklecurve,key=lambda r:r[1]['width_cm']*r[1]['depth_cm']);ap=ankle[0]
    shoe=V[(s*V[:,0]>H*.055)&(V[:,2]<ap[2])];front=np.quantile(shoe[:,1],.98);heel=np.quantile(shoe[:,1],.02)
    # Ball is a forefoot cross-section maximum width, chosen forward of the ankle. Shoe hides real metatarsals.
    ball_candidates=[]
    for y in np.linspace(ap[1]+.25*(front-ap[1]),ap[1]+.88*(front-ap[1]),18):
        band=shoe[abs(shoe[:,1]-y)<.7]
        if len(band)<8:continue
        ball_candidates.append({'position_cm':[float(np.median(band[:,0])),float(y),float((band[:,2].min()+band[:,2].max())/2)],'width_cm':float(np.ptp(band[:,0])),'points':len(band)})
    ball=max(ball_candidates,key=lambda q:q['width_cm']);bp=np.array(ball['position_cm'])
    add('thigh_'+side,'pelvis',hip,{'method':'upper thigh curve extrapolation into pelvis','points':len(pp),'upper_thigh_z_cm':pp[:,2].tolist()},.64,['internal_hip_articulation_extrapolated'])
    add('calf_'+side,'thigh_'+side,kp,knee['evidence'],.72,['knee_pad_and_leg_bend_compete'],knee_candidates[:5])
    add('foot_'+side,'calf_'+side,ap,ankle[1],.84)
    add('ball_'+side,'foot_'+side,bp,{'method':'forefoot width maximum','points':ball['points'],'shoe_forward_cm':float(front-ap[1]),'shoe_heel_cm':float(heel-ap[1])},.70,['shoe_hides_metatarsal_articulation'],ball_candidates)
    # Investigate digit branches without fabricating five named chains from palm percentages.
    digit_rows=[]
    for z in np.arange(H*.42,wp[2]-2,1):
        cs=[c for c in section(z) if s*c['centre'][0]>H*.14 and c['max'][0]-c['min'][0]<3 and c['max'][1]-c['min'][1]<4]
        digit_rows.append({'z_cm':float(z),'candidate_count':len(cs),'candidates':[{k:v for k,v in c.items() if k!='points'} for c in cs]})
    features['fingers_'+side]={'slice_branch_evidence':digit_rows,'accepted_chains':[],'decision':'Separated digit surfaces exist, but thumb identity/order/root correspondence is unresolved. No named chains accepted.'}
result={'method':'Fixed semantic hierarchy + actual target cross-sections, limb curves, split-line bends and width features; no Phase4A manual data','input_geometry_sha256':hashlib.sha256((W/'normalised_geometry.npz').read_bytes()).hexdigest(),'height_cm':H,'joints':joints,'features':features,'confidence_model':{'type':'documented deterministic support score, not probability','formula':'.30*min(section_points/30,1)+.60*role_specificity+.10*hierarchy_prior','automatic_threshold':.80,'flags_override_score':True,'role_specificity':'Prototype authored feature-reliability categories; not statistically calibrated','correction_schema':'corrections.json: role, position_cm or candidate_index, provenance, reason. Refit dependent spine/clavicle/limb joints then rerun all gates.'},'manual_corrections_applied':0,'unresolved_fingers':['thumb','index','middle','ring','pinky']}
(O/'automatic_fit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');(W/'limb_curves.json').write_text(json.dumps(curves,indent=2))
print('AUTOMATIC_FIT',len(joints),[(r['role'],np.round(r['position_cm'],2).tolist(),r['status']) for r in joints])
