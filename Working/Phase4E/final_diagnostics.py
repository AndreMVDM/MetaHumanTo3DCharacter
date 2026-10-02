from model import *
from render import draw_mesh,font
from PIL import Image,ImageDraw
m=Model();w=m.dense(load(W/'saved_Refined_weights.json'));rows={}
for label,weights in [('baseline',m.weights),('refined',w)]:
    gradients=np.linalg.norm(weights[m.edges[:,1]]-weights[m.edges[:,0]],axis=1)/np.maximum(m.edgelen,1e-5)
    rows[label]={r:{'weight_gradient_per_cm_p50_p95_p99':np.quantile(gradients[np.all(mask[m.edges],axis=1)],[.5,.95,.99]).tolist()} for r,mask in m.regions.items()}
save('weight_gradient_diagnostics.json',{'method':'Euclidean norm of adjacent-vertex weight difference / reference edge length; descriptive review flag only','results':rows,'full_surface_self_intersection_and_volume':'Not measured; open multi-shell mesh is unsuitable for a global enclosed-volume acceptance'})
im=Image.new('RGB',(1600,900),'#f7f9fc');d=ImageDraw.Draw(im)
for i,s in enumerate([s for s in m.fingers if s['active_digit'] in ['thumb_r','index_l','ring_r','pinky_l']]):
    digit=s['active_digit'];side=digit.split('_')[1];hand=m.pos[m.bi['hand_'+side]];pose=m.from_sample(s)
    for j,(label,weights) in enumerate([('baseline',m.weights),('refined',w)]):
        rect=(i*400,j*450,400,450);draw_mesh(im,m,m.deform(weights,pose),rect,0,hand-np.array([19,19,19]),hand+np.array([19,19,19]));d.text((rect[0]+8,rect[1]+8),label+' | '+digit,font=font,fill='#172433')
im.save(O/'finger_stress_comparison.png')
save('visual_review.json',{'status':'reviewed_with_residuals','reviewer':'Level1 single-agent visual inspection and self-review','images':'Original UE viewport captures; matching per-pair cameras and clip times verified in capture manifests. CPU images are geometry diagnostics, not textured native rendering.','findings':{'pants_reach':'Severe inward front-crotch fold is visibly stabilised; native front/side and CPU multi-pose comparisons support material improvement. No obvious tearing seen in reviewed views. No exhaustive collision/volume proof.','pants_wide_back':'Wide stance retains crotch transition. Back/hips no gross new defect in sampled native back view; quantitative mean strain improves.','shoulders':'Shirt contour and chest/neck dragging improve in horizontal/overhead and reach. Angular armpit/upperarm detail remains; worst reach area-collapse counts regress. Full shoulder quality gate is not passed.','reference':'Fresh geometry/UV/reference readback exact, so weight edits cannot change rest surface; synthetic neutral is accepted reference, not an independently authored arms-down rest.','fingers':'Motion identity inherited and observed, support remains 9/10. Synthetic thumb opposition is finite but natural-motion quality not accepted.','feet':'Dense flat-floor contact improves substantially; native paired worst-baseline-walk views retained. Terrain, foot locking and sliding untested.'},'acceptance':{'reference':'passed','runtime':'subject_to_final_closure','pants_primary':'material_improvement_observed','shoulders':'partial','feet_flat_floor':'material_improvement_measured','fingers_material_support_improvement':'not_passed','overall_product_go':'not_passed'}})
print('Final diagnostics saved')
