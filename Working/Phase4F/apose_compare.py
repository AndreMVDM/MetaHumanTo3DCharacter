"""Read-only control comparison; never initialises new proposals from controls."""
import sys
sys.dont_write_bytecode=True
import json,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F';O=P/'Documentation/Phase4F'
rows={}
for ch in ['Bill','John','Jill','Jane']:
    co=O/ch;gate=json.loads((co/'anatomical_validation.json').read_text());fit=json.loads((co/'current_proposal.json').read_text());tracks=json.loads((co/'finger_tracks.json').read_text())['sides'];checks={c['name']:c for c in gate['checks']}
    symmetry=checks['bilateral_body_consistency']['measured']
    positions={j['role']:np.array(j['position_cm']) for j in fit['joints']}
    arms={n:checks['surface_envelope_'+n] for n in ['upperarm_l','upperarm_r','lowerarm_l','lowerarm_r','hand_l','hand_r']}
    row={'source_pose':'A' if ch in ['John','Jane'] else 'T','anatomy_checks_passed':sum(c['pass'] for c in gate['checks']),'anatomy_checks_total':len(gate['checks']),
        'body_roles_requiring_review':len([j for j in fit['joints'] if j['status']=='ambiguous']),
        'shoulder_envelope_failures':sum(not arms['upperarm_'+s]['pass'] for s in ['l','r']),
        'elbow_envelope_failures':sum(not arms['lowerarm_'+s]['pass'] for s in ['l','r']),
        'wrist_envelope_failures':sum(not arms['hand_'+s]['pass'] for s in ['l','r']),
        'bilateral_mismatch_max_cm':max(r['difference_cm'] for r in symmetry),'bilateral_role_mismatch_cm':symmetry,
        'finger_tracks_detected':{s:len(t) for s,t in tracks.items()},'downstream_authorised':gate['downstream_authorised'],
        'arm_envelope_checks':arms,'donor_wrist_positions_cm':{s:positions['hand_'+s].tolist() for s in ['l','r']}}
    if ch in ['John','Jane']:
        pose=json.loads((co/'source_pose_validation.json').read_text());row['wrist_to_source_narrowing_proxy_cm']={s:float(np.linalg.norm(positions['hand_'+s]-pose['arms'][s]['wrist_surface_narrowing_cm'])) for s in ['l','r']}
        row['elbow_to_source_section_proxy_cm']={s:float(np.linalg.norm(positions['lowerarm_'+s]-pose['arms'][s]['elbow_surface_anchor_cm'])) for s in ['l','r']}
    rows[ch]=row
out={'comparison':rows,'method':'Identical retained 106-check starting anatomy gate; envelope tolerance +/-0.8 cm, mirrored-role max <6cm; no review approvals. New source surface anchors were measured before donor solve.',
    'interpretation_limits':'Different meshes/proportions/topology, source arm angles and Jane fore/aft asymmetry confound attribution. An envelope pass is a coarse numerical improvement, not anatomical truth or proven correction savings. Finger track count is neither identity nor surface-support acceptance.'}
(O/'APoseContinuation/pose_control_comparison.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
for ch,r in rows.items():print(ch,{k:v for k,v in r.items() if k not in ['arm_envelope_checks','bilateral_role_mismatch_cm','donor_wrist_positions_cm']})
