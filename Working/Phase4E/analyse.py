from model import *
m=Model();v=m.v;w=m.weights
components=[]
for c in np.unique(m.components):
    ix=np.flatnonzero(m.components==c)
    components.append({'id':int(c),'vertices':len(ix),'bounds':[v[ix].min(0).tolist(),v[ix].max(0).tolist()]})
components.sort(key=lambda x:-x['vertices'])
fields={}
for n,mask in m.regions.items():
    region=w[mask];mean=region.mean(0)
    fields[n]={'vertices':int(mask.sum()),'mean_weights':{m.names[b]:float(mean[b]) for b in np.argsort(-mean) if mean[b]>1e-5},'weight_quantiles':{m.names[b]:np.quantile(region[:,b],[0,.1,.5,.9,1]).tolist() for b in np.argsort(-mean)[:10]},'root_weight_over_10pct':int((region[:,m.bi['root']]>.1).sum()),'bilateral_thigh_over_10pct':int(((region[:,m.bi['thigh_l']]>.1)&(region[:,m.bi['thigh_r']]>.1)).sum())}
save('weight_field_analysis.json',{'source':'fresh saved UE Phase4D readback','regions':'Skeleton-relative geometric review envelopes; not clothing labels','fields':fields,'connectivity':{'weld_tolerance_cm':1e-5,'components':components,'material_slots':1,'body_under_clothes_available':False},'root_explanation':'Installed binder considers parent-to-child bone fans. Grounded root-to-pelvis is a long binding segment, not a deforming anatomical region.'})
save('stress_pose_suite.json',{'method':'Accepted reference transforms swung about current pivots; no bone relocation; synthetic poses are diagnostics, not natural motion proof','poses':{n:pose.tolist() for n,pose in m.poses.items()},'native_samples':244,'finger_samples':len(m.fingers),'units':'centimetres','measurements':['triangle area ratio','edge log strain','weight distribution','sole minimum Z'],'thresholds_are_review_screens':True})
baseline={n:m.measure(w,pose) for n,pose in m.poses.items()};save('baseline_deformation.json',baseline)
print('Components',len(components),components[:8]);print('Pose count',len(m.poses));print('Front weights',fields['front_pants']['mean_weights']);print('Baseline reach',baseline['reach_0.5']['front_pants'])
