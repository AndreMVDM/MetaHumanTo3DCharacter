from model import *
m=Model();native=load(O/'native_contact_frame_export.json');baked=load(O/'surface_contact_native_bake.json');out=[]
for role in ['idle','walk','run']:
    a=[s for s in native['samples'] if s['role']==role];b=[s for s in baked['samples'] if s['role']==role and s['frame_fraction'].is_integer()];assert len(a)==len(b)
    pa=np.array([m.from_sample(s) for s in a]);pb=np.array([m.from_sample(s) for s in b]);legs=[m.bi[n+'_'+side] for side in ['l','r'] for n in ['thigh','calf','foot','ball']];body=[i for i in range(len(m.names)) if i not in legs];lengths=[]
    for side in ['l','r']:
        for x,y in [('thigh','calf'),('calf','foot')]:
            ia=m.bi[x+'_'+side];ib=m.bi[y+'_'+side];lengths.append(float(np.max(abs(np.linalg.norm(pb[:,ia,:3,3]-pb[:,ib,:3,3],axis=1)-np.linalg.norm(pa[:,ia,:3,3]-pa[:,ib,:3,3],axis=1)))))
    out.append({'role':role,'key_frames':len(a),'non_leg_component_translation_error_cm':float(np.max(np.linalg.norm(pa[:,body,:3,3]-pb[:,body,:3,3],axis=2))),'leg_length_preservation_error_cm':max(lengths),'feet':{side:{label:{'max_adjacent_key_displacement_cm':float(np.linalg.norm(np.diff(p[:,m.bi['foot_'+side],:3,3],axis=0),axis=1).max()),'end_to_start_displacement_cm':float(np.linalg.norm(p[-1,m.bi['foot_'+side],:3,3]-p[0,m.bi['foot_'+side],:3,3]))} for label,p in [('before',pa),('after',pb)]} for side in ['l','r']}})
save('contact_continuity.json',{'status':'measured','results':out,'limits':'Key displacement and loop endpoint diagnostics only; no planted foot/speed curves, sliding or terrain acceptance'})
print(out)
