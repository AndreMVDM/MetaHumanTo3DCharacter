import json,hashlib,collections,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[2];O=P/'Documentation/Phase4A';W=P/'Working/Phase4A'
def load(n,root=O):return json.loads((root/n).read_text())
def save(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
original=load('protected_before.json');changed=[];missing=[]
for n,before in original.items():
    f=P/n
    if not f.exists():missing.append(n);continue
    if f.stat().st_size!=before['bytes'] or hashlib.sha256(f.read_bytes()).hexdigest()!=before['sha256']:changed.append(n)
save('protected_validation.json',{'baseline_files':len(original),'changed':changed,'missing':missing,'all_unchanged':not changed and not missing,'scope':'Source archives, protected project Content, Config, reference packages and earlier documentation selected before execution. Engine source was read only; no engine before/after baseline was captured.'})
assert not changed and not missing
reload=load('disk_reload_validation_ball_forward.json');assert all(not r.get('error') and r['uv_equal_to_bound_dynamic_mesh'] and r['geometry_equal_to_bound_dynamic_mesh'] and all(m['material'] for m in r['materials']) for r in reload)
source=next(e for r in load('zip_inventory.json') if r['case']=='Unrigged' for e in r['entries'] if e['name'].endswith('.jpg'))
jpeg=W/'Inputs/Unrigged'/source['name'];assert hashlib.sha256(jpeg.read_bytes()).hexdigest()==source['sha256']
save('material_uv_validation.json',{'accepted_preservation':True,'source_jpeg_sha256':source['sha256'],'source_jpeg_unchanged':True,'source_uv_import':load('uv_import_validation.json'),'disk_reload':reload,'height_uv_unchanged':all(r['uv_identical'] for r in load('height_ordering_results.json')),'original_material_assignments':load('material_assignment_final.json'),'live_texture_reference':load('material_render_probe.json'),'before_after_images':[str(W/'texture_front_unlit.png'),str(W/'texture_before_after_unlit.png'),str(W/'native_playback_ball_forward.png')],'repair':'Restored source JPEG to original imported material DiffuseColor/BaseColor connection, and original imported materials to generated material slots. No source pixel authoring or UV editing. Mixamo archive has no source UVs or textures; its neutral imported material is preserved.','limit':'Appearance/UV preservation demonstrated for this source diffuse texture; cross-renderer shader equivalence and all lighting models are not certified.'})
analysis=load('skeleton_analysis.json');analysis=[r for r in analysis if r.get('profile')!='BallForward'];skin=load('skin_weight_analysis.json');skin['statistics']=[r for r in skin['statistics'] if r.get('profile')!='BallForward']
for r in load('assisted_candidates_ball_forward.json'):
    bones=r['snapshot']['bones'];ps={n:np.array(b['component']['translation']) for n,b in bones.items()};parents=r['parents'];lengths={n:float(np.linalg.norm(ps[n]-ps[p])) for n,p in parents.items() if p in ps}
    analysis.append({'case':r['case'],'type':'assisted_manual_landmarks','profile':'BallForward','bone_count':len(bones),'root':{n:ps[n].tolist() for n,p in parents.items() if p not in ps},'bone_lengths_cm':lengths,'unit_scale':all(abs(v-1)<.0001 for b in bones.values() for v in b['local']['scale']),'landmark_coordinates':r['authored_landmarks_cm'],'accepted_humanoid':False,'reason':'Semantic authoring and downstream bake pass; manual approximate fingers, deformation screening flags and mixed floor contact prevent production acceptance.'})
    d=load(r['case']+'_assisted_ball_forward_skin.json',W);sums=[sum(w for b,w in ws) for ws in d['weights']];hist=collections.Counter(len(ws) for ws in d['weights'])
    skin['statistics'].append({'case':r['case'],'type':'assisted_manual_landmarks','profile':'BallForward','vertices':len(sums),'positive_influence_histogram':dict(hist),'max_positive_influences':max(hist),'zero_weight_vertices':sum(v==0 for v in sums),'weight_sum_range':[min(sums),max(sums)]})
skin['corrected_deformation_evidence']='deformation_metrics_ball_forward.json';save('skeleton_analysis.json',analysis);save('skin_weight_analysis.json',skin)
visual=load('visual_skin_samples_ball_forward.json',W);canvas=Image.new('RGB',(1400,850),'white');draw=ImageDraw.Draw(canvas)
for i,role in enumerate(['idle','walk','run','reach']):
    cx=350*(i+.5);draw.text((350*i+15,15),'Assisted BallForward CPU LBS: '+role+' @50%',fill='black')
    for z in range(0,181,20):draw.line([(350*i+5,800-4*z),(350*(i+1)-5,800-4*z)],fill='#eeeeee')
    for v in visual['Unrigged|'+role+'|0.5']:draw.point((cx+4*v[0],800-4*v[2]),fill='#303030')
    draw.line([(350*i+5,800),(350*(i+1)-5,800)],fill='#dc2626',width=2)
canvas.save(O/'deformation_contact_sheet_ball_forward.png')
for n in ['foot_comparison.json','runtime_samples.json']:
    d=load(n);d['latest_corrected_evidence']=n.replace('.json','_ball_forward.json');d['profile']='Original assisted toe landmark, retained for failure comparison';save(n,d)
deps=load('bake_dependencies_ball_forward.json');live=load('independence_live_ball_forward.json');assert len(live['samples'])==100 and not live['errors'] and live['manny_destroyed'] and not any(s['manny_components_remaining'] for s in live['samples'])
assert all(not r['foreign_game_packages'] and not r['native_plugin_dependencies'] for r in deps)
save('migration_manifest.json',{'status':'Dependency readiness verified; no clean-project migration or packaged/cooked executable test performed','profile':'Assisted180BallForward diagnostic only','cases':[{'case':r['case'],'game_packages':[p for p in r['closure'] if p.startswith('/Game/')],'engine_script_packages':[p for p in r['closure'] if not p.startswith('/Game/')],'preview_reference_note':'SK_Lara_Authoring is in the current hard/soft closure via Skeleton preview metadata; include it, or explicitly clear and re-audit that editor preview reference before a minimal migration.'} for r in deps],'not_created':['PhysicsAsset','destination AnimBP','playable Character pawn'],'authoring_not_runtime_dependencies':['Manny','source IK Rig','IK Retargeter','Phase4ATools native helper'],'diagnostic_map_excluded':True})
metrics=load('deformation_metrics_ball_forward.json')['summary'];delta=max(abs(x['Phase4A_assisted_min_sole_z_cm']['Unrigged'][s]-x['Phase4A_assisted_min_sole_z_cm']['MixamoRecovered'][s]) for x in load('foot_comparison_ball_forward.json')['comparison'] for s in ['l','r'])
save('phase4a_result.json',{'engine_version':'5.8.3-58210709+++UE5+Release-5.8','investigation_complete':True,'production_rig_accepted':False,'automatic_humanoid_rig_accepted':False,'engine_generated_medial_rigs':4,'assisted_controls':4,'source_geometry_converges':True,'corrected_foot_minima_between_cases_max_difference_cm':delta,'automatic_weight_generation_works':True,'deformation_quality_accepted':False,'textures_uv_preserved':True,'foot_issue_overall_improved':False,'corrected_native_playback_frames':len(live['samples']),'diagnostic_native_bake_works':True,'corrected_baked_pose_samples':400,'original_baked_pose_samples':400,'supported_modes':{'A':'Experimental assisted unrigged workflow; not primary fully automatic','B':'Primary validated UE-compatible rigged input contract','C':'Experimental geometry recovery followed by assisted workflow'},'deformation_summary':metrics,'report':str(O/'Phase4AAutoRigInvestigation.md')})
print('FINAL_EVIDENCE_DONE',len(original),'protected unchanged; convergence foot delta',delta)
