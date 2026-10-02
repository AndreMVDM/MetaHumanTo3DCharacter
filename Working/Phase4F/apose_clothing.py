"""Classify observed principal clothing with connected-component evidence."""
import sys
sys.dont_write_bytecode=True
import json,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F';O=P/'Documentation/Phase4F'
for ch in ['John','Jane']:
    co=O/ch;summary=json.loads((co/'geometry_summary.json').read_text());frame=json.loads((co/'coordinate_frame.json').read_text())
    d=np.load(W/ch/'normalised_geometry.npz');v=d['vertices'];labels=d['weld_component'];rows=[]
    for c in summary['components']:
        pts=v[labels==c['id']]
        rows.append({'id':c['id'],'vertices':len(pts),'triangles':c['triangles'],'canonical_bounds_cm':[pts.min(0).tolist(),pts.max(0).tolist()]})
    if ch=='John':
        classification='separable principal garment shells; mixed skin/accessory components'
        evidence='Component 25 (3420 vertices) spans both trouser legs, Z18.5–104.6; component 34 (2963) occupies shirt/torso Z101–153.4. Belt component 24 (1146), Z95.7–106, is separate. Arm/hand and boot pieces are distinct. This supports shell-aware tests after anatomy, not a proven complete underlying body donor.'
        tagged={'trouser_region':25,'shirt_region':34,'belt_region':24}
    else:
        classification='mixed: integrated central top/pelvis/upper-leg surface plus separable sleeve/boot/hand pieces'
        evidence='Dominant component 20 (9161 vertices) spans torso, pelvis and upper legs, Z51.7–146.5. Principal top and trousers cannot be isolated as separate complete shells. Sleeve pieces (including component 7, 1769), hands (0/25, 996/1000) and boots/shanks are distinct. Integrated anatomical-envelope refinement is appropriate for central clothing; separable pieces must not be described as fully merged.'
        tagged={'integrated_central_clothing':20,'right_upper_sleeve_region':7,'right_hand':0,'left_hand':25}
    result={'character':ch,'classification':classification,'connectivity_evidence':evidence,'diagnostic_component_labels':tagged,
        'components_canonical':rows,'raw_connected_components':summary['raw_connected_components'],'position_welded_components':summary['position_welded_components'],
        'weld_tolerance_cm':1e-5,'source_topology_modified':False,'complete_underlying_body_donor_verified':False,
        'basis':'Source front/side/back texture views plus independent raw and positional-seam connected components and spatial extents. Component IDs are inventory diagnostics, not final vertex-hardcoded weighting masks.',
        'weight_transfer_executed':False,'reason':'Anatomy must pass before binding; no established underlying weighted body exists yet.'}
    (co/'clothing_classification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    summary['clothing_classification']=classification;(co/'geometry_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(ch,classification)
