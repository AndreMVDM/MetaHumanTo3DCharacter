"""Accepted chains only: two-axis opposition diagnostic, not a natural-motion acceptance."""
from model import *
from render import draw_mesh,font
from PIL import Image,ImageDraw
m=Model();w=m.dense(load(W/'saved_Refined_weights.json'));fit=load(P/'Documentation/Phase4D/current_proposal.json');chains=fit['finger_chains'];rows=[];poses={}
for side in ['l','r']:
    n='thumb_01_'+side;root=m.pos[m.bi[n]];axis=m.pos[m.bi['thumb_02_'+side]]-root;axis/=np.linalg.norm(axis)
    target=m.pos[m.bi['index_01_'+side]]-root;cross=np.cross(axis,target);cross/=np.linalg.norm(cross)
    hand=m.ref[m.bi['hand_'+side],:3,2];hand/=np.linalg.norm(hand)
    for fraction in [0,.5,1]:
        pose=m.ref.copy();m.rotate_branch(pose,n,rotation(cross,math.radians(30*fraction)));m.rotate_branch(pose,n,rotation(hand,math.radians(20*fraction)))
        for j in [2,3]:m.rotate_branch(pose,'thumb_0'+str(j)+'_'+side,rotation(cross,math.radians(20*fraction)))
        poses[side+'_'+str(fraction)]=pose;out=m.deform(w,pose);d=np.linalg.norm(m.v[:,None,:]-np.array(chains['thumb_'+side]['path_cm'])[None,:,:],axis=2).min(1);ix=np.flatnonzero(d<.9);ids=[m.bi['thumb_0'+str(j)+'_'+side] for j in [1,2,3]];support=np.linalg.norm(pose[ids,:3,3,None]-out[ix].T[None,:,:],axis=1).min(1).max()
        rows.append({'side':side,'fraction':fraction,'support_cm':float(support),'thumb_tip_bone_displacement_cm':float(np.linalg.norm(pose[ids[-1],:3,3]-m.pos[ids[-1]])),'finite':bool(np.isfinite(out).all())})
im=Image.new('RGB',(1200,850),'#f7f9fc');d=ImageDraw.Draw(im)
for s,side in enumerate(['l','r']):
    hand=m.pos[m.bi['hand_'+side]];lo=hand-np.array([18,18,18]);hi=hand+np.array([18,18,18])
    for j,f in enumerate([0,.5,1]):
        draw_mesh(im,m,m.deform(w,poses[side+'_'+str(f)]),(j*400,s*425,400,425),0,lo,hi);d.text((j*400+8,s*425+8),side+' thumb | opposition diagnostic '+str(f),font=font,fill='#172433')
im.save(O/'thumb_opposition_diagnostic.png')
save('thumb_opposition_diagnostic.json',{'status':'diagnostic_only','method':'Accepted thumb chain; 30 degree swing towards index base plus 20 degree hand-axis rotation and 20 degree interphalangeal flexion','bone_positions_and_identity_unchanged':True,'samples':rows,'acceptance':'Natural thumb opposition remains unproven: angles/sign/axis are synthetic, no validated task motion, anatomical joint limits, collision or human acceptance.'})
# The Phase4D sparse right-ring support group fails even at rest; report, do not relax its threshold.
digits=list(chains);dist=np.stack([np.linalg.norm(m.v[:,None,:]-np.array(chains[k]['path_cm'])[None,:,:],axis=2).min(1) for k in digits],axis=1);nearest=dist.argmin(1);ix=np.flatnonzero((nearest==digits.index('ring_r'))&(dist[:,digits.index('ring_r')]<.9));ids=[m.bi['ring_0'+str(j)+'_r'] for j in [1,2,3]]
save('right_ring_rest_support.json',{'group_vertices':len(ix),'joint_nearest_group_distances_cm':np.linalg.norm(m.pos[ids,None,:]-m.v[ix][None,:,:],axis=2).min(1).tolist(),'screen_threshold_cm':1.2,'interpretation':'The sparse track group omits proximal palm support. A screen failure alone does not prove pivot misplacement; the unchanged reference surface already fails this group at the root.'})
