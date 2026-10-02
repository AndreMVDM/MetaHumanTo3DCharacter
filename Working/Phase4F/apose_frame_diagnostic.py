"""Check whether a simple global yaw explains Jane's asymmetry; no frame edits."""
import sys
sys.dont_write_bytecode=True
import numpy as np,json
from pathlib import Path
P=Path(__file__).resolve().parents[2];sys.path.insert(0,str(P/'Working/Phase4B'))
from geometry_tools import nearest_distances
for ch in ['John','Jane']:
    v=np.load(P/'Working/Phase4F'/ch/'normalised_geometry.npz')['vertices'];regions={
        'lower_legs':v[(v[:,2]>25)&(v[:,2]<70)],
        'arms_hands':v[(v[:,2]>75)&(v[:,2]<135)&(abs(v[:,0])>35)]}
    out={}
    for region,pts in regions.items():
        sample=pts[::max(1,len(pts)//400)];results=[]
        for angle in np.linspace(-25,25,51):
            a=np.r_[np.cos(np.radians(angle)),np.sin(np.radians(angle)),0]
            offset=(np.min(pts@a)+np.max(pts@a))/2
            mirrored=sample-2*(sample@a-offset)[:,None]*a;dist=nearest_distances(mirrored,pts)
            results.append({'yaw_plane_normal_deg':float(angle),'offset_cm':float(offset),'mean_nearest_cm':float(dist.mean()),'p95_nearest_cm':float(np.quantile(dist,.95))})
        out[region]={'best':min(results,key=lambda r:r['mean_nearest_cm']),'zero_yaw':results[25],'candidates':results}
    result={'character':ch,'regional_reflection_planes':out,'frame_changed':False,'semantic_solve_repeated':False,
        'limit':'Nearest-vertex reflection of selected surface regions is a diagnostic, not a symmetry-ground-truth or anatomy acceptance. Different regional yaw optima do not support silently rotating one limb or pose-normalising the source.'}
    (P/'Documentation/Phase4F'/ch/'frame_asymmetry_diagnostic.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(ch,{k:r['best'] for k,r in out.items()})
