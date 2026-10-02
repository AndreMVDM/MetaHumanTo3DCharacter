"""Pre-donor A-pose surface-axis measurements; no internal joint acceptance."""
import sys
sys.dont_write_bytecode=True
import numpy as np, json
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F';O=P/'Documentation/Phase4F'
sys.path.insert(0,str(P/'Working/Phase4B'))
from geometry_tools import sections
for ch in ['John','Jane']:
    d=np.load(W/ch/'normalised_geometry.npz');v=d['vertices'];t=d['triangles'];H=np.ptp(v[:,2]);arms={}
    for side,sign in [('l',1),('r',-1)]:
        curve=[]
        for z in np.arange(.50*H,.77*H,1):
            cs=[c for c in sections(v,t,z) if sign*c['centre'][0]>.10*H and c['count']>=15 and c['max'][0]-c['min'][0]<.17*H]
            if not cs:continue
            # Largest lateral closed section; clothing overlays retained in evidence.
            c=max(cs,key=lambda c:c['count'])
            curve.append({'position_cm':c['centre'],'width_cm':c['max'][0]-c['min'][0],'depth_cm':c['max'][1]-c['min'][1],'section_count':len(cs)})
        wrist=min([r for r in curve if r['position_cm'][2]<.60*H],key=lambda r:r['width_cm']*r['depth_cm'])
        # Clothing overlap makes tiny proximal section slopes unreliable. Use
        # explicit long-span section anchors; retain every sampled section.
        shoulder=np.array(min(curve,key=lambda r:abs(r['position_cm'][2]-.715*H))['position_cm'])
        elbow=np.array(min(curve,key=lambda r:abs(r['position_cm'][2]-.635*H))['position_cm'])
        wp=np.array(wrist['position_cm'])
        upper=shoulder-elbow;upper/=np.linalg.norm(upper)
        lower=elbow-wp;lower/=np.linalg.norm(lower)
        chord=shoulder-wp
        angle=float(np.degrees(np.arctan2(abs(chord[2]),abs(chord[0]))))
        bend=float(np.degrees(np.arccos(np.clip(upper@lower,-1,1))))
        arms[side]={'arm_chord_below_horizontal_deg':angle,'upper_arm_surface_axis_up':upper.tolist(),'forearm_surface_axis_up':lower.tolist(),'elbow_surface_axis_change_deg':bend,'wrist_surface_narrowing_cm':wrist['position_cm'],'proximal_surface_anchor_cm':shoulder.tolist(),'elbow_surface_anchor_cm':elbow.tolist(),'curve':curve}
    left=np.array([r['position_cm'] for r in arms['l']['curve']]);right=np.array([r['position_cm'] for r in arms['r']['curve']]);common=min(len(left),len(right));right=right.copy();right[:,0]*=-1
    # Match by same Z sample, never by unrelated point indices.
    pairs=[np.linalg.norm(a-b) for a in left for b in right if abs(a[2]-b[2])<.1]
    feet=[]
    for sign in [1,-1]:
        pts=v[(sign*v[:,0]>.035*H)&(v[:,2]<.07*H)]
        feet.append(np.median(pts,axis=0))
    result={'character':ch,'measurement_before_semantic_solve':True,'height_cm':float(H),'arms':arms,
        'bilateral_arm_angle_difference_deg':abs(arms['l']['arm_chord_below_horizontal_deg']-arms['r']['arm_chord_below_horizontal_deg']),
        'mirrored_arm_curve_mean_max_cm':[float(np.mean(pairs)),float(max(pairs))],
        'foot_centre_lateral_separation_cm':float(abs(feet[0][0]-feet[1][0])),
        'visual_pose':'Lowered bilateral arms, slight elbow bend, separated legs: neutral A-pose variant. John relaxed curled digits; Jane more splayed digits.',
        'palms_facing':'Thumbs medial; textured front/side show hands approximately inward/forward, with relaxed flex. Exact palm normal and wrist articulation remain review tasks.',
        'source_axes':'FBX +Y up, +Z forward; Blender +Z up, observed -Y facing; canonical +X anatomical left,+Y forward,+Z up, determinant -1.',
        'contract_assessment':'Within broad neutral A-pose intent on directly inspected front/side renders and surface-axis measurements; no pose conversion performed.',
        'limitations':'Clothed surface centreline slopes, wrist narrowing and foot centres are reproducible pose proxies, not certified internal joint centres. No strict numeric A-pose angle contract existed; no threshold invented as product acceptance.'}
    (O/ch/'source_pose_validation.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    frame=json.loads((O/ch/'coordinate_frame.json').read_text());frame['facing_validation']='Source front/side render directly inspected: face and belt/front clothing towards Blender -Y. Verified before donor solve.'
    (O/ch/'coordinate_frame.json').write_text(json.dumps(frame,indent=2),encoding='utf-8')
    print(ch,{s:{k:q for k,q in r.items() if k!='curve'} for s,r in arms.items()},'symmetry',result['mirrored_arm_curve_mean_max_cm'],'feet',result['foot_centre_lateral_separation_cm'])
