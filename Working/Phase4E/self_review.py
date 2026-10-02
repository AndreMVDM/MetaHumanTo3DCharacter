from model import *
import re
p=O/'Phase4ECharacterQualityRefinement.md';s=p.read_text(encoding='utf-8');sections=[x for x in s.splitlines() if x.startswith('## ')];assert len(sections)==23
assert [int(x.split('.')[0][3:]) for x in sections]==list(range(1,24))
links=re.findall(r'\]\(([^)]+)\)',s);missing=[x for x in links if not x.startswith('http') and not (O/x).exists()];assert not missing
required=['baseline_asset_readback.json','candidate_asset_publication.json','surface_contact_native_bake.json','native_visual_capture.json','native_stress_visual_capture.json','native_contact_visual_capture.json','source_independent_playback.json','contact_native_playback.json','final_dependency_closure.json','protected_file_audit.json']
assert all(load(O/n)['status']=='passed' for n in required)
f=load(O/'final_finger_validation.json');assert f['support_pass_count']==9 and f['digit_count']==10
m=Model();stress=load(O/'final_stress_comparison.json');assert len(m.poses)==34 and len(stress['refined'])==34;assert all(p['global']['finite'] for p in stress['refined'].values())
visual=load(O/'visual_review.json');visual['acceptance']['runtime']='passed_package_closure_and_native_playback';save('visual_review.json',visual)
save('self_review.json',{'status':'passed','workflow':'Level1 single-agent self-review','report_sections':23,'missing_evidence_links':missing,'required_verified_artifacts':required,'skeleton_geometry_uv_and_weights':'fresh UE reload verified','metric_claims':'final saved-weight 34-pose and 244-native-pose data; averages and reach area-collapse regression both reported','contact_claims':'60 Hz final bake,120 Hz dense evaluation,static sole probes,no actor/root offset; interpolation and planting limits disclosed','finger_claims':'9/10 final support; rejected alternatives; natural thumb unproven; no relaxed threshold','product_decision':'no polished plugin/UI go; no evidence full conventional painting is fundamentally required','failed_experiments':'Raw-track API and intermediate save/capture failures retained, not asserted as successful; final acceptance uses passed manifests','limits':'Self-review is not independent artistic approval or cooked/clean-project testing'})
print('Self-review passed: 23 sections, linked evidence present, final acceptance claims consistent')
