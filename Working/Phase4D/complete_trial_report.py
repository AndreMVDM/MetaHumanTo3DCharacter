"""Append the measured human/downstream outcome and publish consistent final evidence."""
import sys,collections,copy,hashlib,json
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));import core
P=core.P;W=core.W;O=core.O
load=lambda n:core.read(O/(n+'.json'))
state=core.read(W/'session.json');snap=core.read(W/'HumanTrialFinalisation/InputSnapshot/session_from_editor.json');metrics=load('correction_metrics');gate=load('anatomical_validation');audit=load('protected_file_audit');skin=load('skinning_results');skeleton=load('skeleton_construction');ik=load('ik_retarget_results');bake=load('animation_bake_results');finger=load('finger_animation_validation');live=load('source_independent_playback');closure=load('final_dependency_closure');native=load('native_visual_capture')
assert gate['downstream_authorised'] and not gate['failed'] and len(gate['checks'])==186
assert all(d['status']=='passed' for d in [skeleton,skin,ik,bake,live,closure,native])
assert audit['passed'] and metrics['landmarks_actually_moved']==1 and len(state['events'])==159
for key in ['events','fingers','approvals','joints','generated_joint_schema']:assert state[key]==snap[key],key
manifest=core.read(W/'HumanTrialFinalisation/InputSnapshot/event_manifest.json')['files'];bad=[p for p,h in manifest.items() if core.file_sha(P/p)!=h];assert not bad
assert len(list((W/'InteractionEvidence').glob('event_*.json')))==len(manifest)==159
ledger_audit={'passed':True,'original_events':159,'changed_event_files':bad,'new_human_event_files':[],'exact_editor_snapshot_fields_preserved':['events','fingers','approvals','joints','generated_joint_schema'],'editor_snapshot_sha256':core.file_sha(W/'HumanTrialFinalisation/InputSnapshot/session_from_editor.json'),'starting_proposal_sha256':core.file_sha(O/'automatic_starting_proposal.json'),'final_proposal_sha256':core.file_sha(O/'current_proposal.json'),'trial_elapsed_seconds':metrics['elapsed_trial_seconds'],'not_active_authoring_time':True}
core.save(O/'human_ledger_preservation.json',ledger_audit)
deformation=load('deformation_contact_results')
review={'status':'evaluated_not_accepted','reviewed_images':['native_reference_pose.png','native_representative_poses.png','native_shoulders_reach.png','native_walk_feet.png','animated_body_front.png','animated_body_side.png','animated_feet_side.png','animated_finger_validation.png'],'reference_pose':'Original material and reference silhouette retained; fresh disk geometry/UV equality and live reference transforms verified','shoulders_clothing':'Raised-arm native image shows jagged/thinned shoulder and shirt transitions; no production-quality acceptance','elbows':'Expected gross arm articulation in sampled poses; fine crease quality not certified','wrists':'Run/reach area screens flag local collapse/stretch; gloves and finger attachment require refinement','pelvis_hips':'Gross connected silhouette retained; apparel is ordinary auto-bound surface, with no separate cloth or rigid accessory treatment','knees':'Gross bend direction retained in representative native/CPU poses; reach flags one nearby collapsed triangle','ankles_feet':'Boot shape deforms, stance soles penetrate Z=0; lifted feet and toe pitch are assessed per sampled clip, not labelled as planting failures merely because airborne','fingers':'Independent identity and sampled 3D separation pass; right-ring support exceeds the explicit screen and natural thumb opposition is unproven','unexpected_limb_crossing_or_inversion':'No gross identity swap or reversed limb observed in representative images; nonzero segment lengths and complete finite poses measured separately. Not continuous collision or exhaustive bend-sign certification','weight_edits':[],'quality_accepted':False}
core.save(O/'deformation_visual_review.json',review)
deformation.update(status='evaluated_not_accepted',visual_review_artifact='deformation_visual_review.json',quality_accepted=False);core.save(O/'deformation_contact_results.json',deformation)
skin['deformation_acceptance']='evaluated_not_accepted; see deformation/contact and finger evidence';core.save(O/'skinning_results.json',skin)
assets=sorted(set(a for d in [skeleton,skin,ik,bake,load('finger_animation_bake'),load('playback_scene')] for a in d.get('assets',[])))
experiment=load('experiment_result');experiment.update(anatomy_passed=True,failed_gate_count=0,downstream_authorised=True,downstream_assets_created=assets,body_classification='experimental assisted',finger_classification='experimental assisted',overall_mode_a='experimental assisted',classification_basis={'landmark_correction_stage':'practical assisted on this Lara asset: one moved neck, 31 unchanged accepted reviews, no manual phalange placement','body':'Native construction/bake/playback works mechanically; penetration and observed shoulder/clothing distortion prevent practical character-quality acceptance','fingers':'Ten semantic independent chains work; right-ring support screen fails and natural thumb opposition/full range remain unproven','overall':'Reassessed from completed measured trial and downstream failures, not retained from the historical pending-trial label'},downstream_status='complete_evaluation_not_accepted_rig',downstream_mechanical_proof_passed=True,character_quality_accepted=False,human_trial_complete=True,human_ledger_preserved=True,generalisation='unproven; single expert-reviewed asset, no novice or diverse-mesh trial',reference_pose_verified=True,foot_contact_accepted=False,finger_semantic_motion_passed=True,finger_deformation_accepted=False,protected_file_audit_passed=True,review_ready=True)
core.save(O/'experiment_result.json',experiment)
visual=load('visual_evidence');visual['available'].extend({'file':n,'kind':'Actual UE native viewport capture','post_correction':True} for n in review['reviewed_images'] if n.startswith('native_'));visual['available'].extend({'file':n,'kind':'Actual UE baked poses driving CPU LBS','post_correction':True} for n in review['reviewed_images'] if n.startswith('animated_'));visual['available']=list({r['file']:r for r in visual['available']}.values());visual['pending']=[];visual['quality_acceptance']=False;core.save(O/'visual_evidence.json',visual)
motion=load('native_motion_summary');recovery=load('historical_report_recovery');readback=closure['measured_results']['fresh_disk_readback'];initial=core.read(W/'HumanTrialFinalisation/InputSnapshot/initial_finaliser_anatomical_validation.json')
movement=next(e['details']['moves'][0] for e in state['events'] if e['kind']=='move');delta=core.sub(movement['to_cm'],movement['from_cm']);counts=collections.Counter(e['kind'] for e in state['events']);rows=[]
for s in deformation['summary']:
 left=s['feet']['l'];right=s['feet']['r'];rows.append(f"| {s['role']} | {s['max_collapsed_triangles']} | {s['max_stretched_triangles']} | {left['sole_height_range_cm'][0]:.3f} to {left['sole_height_range_cm'][1]:.3f} | {right['sole_height_range_cm'][0]:.3f} to {right['sole_height_range_cm'][1]:.3f} |")
fingerrows=[]
for f in finger['results']:
 own=f['local_rotation_degrees'][f['digit']];others=max(v for n,v in f['local_rotation_degrees'].items() if n!=f['digit']);support=f['phalange_surface_support_cm'];fingerrows.append(f"| {f['digit']} | {own:.3f} | {others:.6f} | {support:.3f} | {'passes' if support<=1.2 else 'fails'} |")
regionrows=[]
for region in deformation['summary'][0]['regions']:
 regionrows.append(f"| {region} | {max(s['regions'][region]['max_collapsed'] for s in deformation['summary'])} | {max(s['regions'][region]['max_stretched'] for s in deformation['summary'])} |")
cliprows=[f"| {role} | {c['path']} | {c['duration_s']:.6f} | {c['samples']} |" for role,c in bake['measured_results']['clips'].items()]
slide_rows=[]
for s in deformation['summary']:
 for side,foot in s['feet'].items():
  speed=foot['near_ground_surface_slide_speed_cm_s_max'];pitch=foot['toe_pitch_range_deg'];slide_rows.append(f"| {s['role']} | {side} | {foot['near_ground_interval_count']} | {f'{speed:.3f}' if speed is not None else 'no qualifying intervals'} | {pitch[0]:.2f} to {pitch[1]:.2f} |")
game=[p for p in closure['measured_results']['closure'] if p.startswith('/Game/')]
append=f'''

## 29. Completed human trial and downstream evaluation — 1 October 2026

The corrected Lara proposal passes **186/186 anatomical checks, zero failures, downstream_authorised=true**. A fresh 53-bone Lara skeleton, original-surface skeletal mesh, IK Rig, Manny retargeter and destination-native animations were built and played without a live source. **The character-quality result is not accepted**: stance penetration, shoulder/clothing deformation and unresolved animated finger-surface quality remain. Mode A is experimental assisted after measured reassessment.

Sections 1–28 describe the earlier prototype/human-review boundary. Their pending statements and zero-event metrics are historical and are superseded by this appendix. The first finaliser refresh during this task rewrote that historical report before a byte snapshot was taken, and initially lost one derived approval during replay. The original report template and immutable automatic starting proposal were used to reconstruct the historical prose and zero-event metrics. The mixed first-refresh report is retained in Working/Phase4D/HumanTrialFinalisation/InputSnapshot. [Historical recovery provenance](historical_report_recovery.json) explicitly records that the original pre-refresh report bytes/hash were unavailable; byte-exact preservation of that particular report is not claimed. Subsequent refreshes preserve the report and measured downstream records. The immutable human events were never rewritten.

### 29.1 Human review, movement and time

| Measurement | Before human trial | Completed trial |
| --- | ---: | ---: |
| Unresolved body roles | 19 | 0 |
| Unresolved finger chains | 10 | 0 |
| Accepted body roles | 4 automatic/provisional | 23/23, including automatic grounded root |
| Human-accepted body roles | 0 | 22, including all three generated spines |
| Accepted finger chains | 0 | 10/10 |
| Actual moved landmarks | 0 | 1: neck_01 |
| Accepted review without movement | 0 | 31: 21 body + 10 digit chains |
| Manual phalange placements | 0 | 0 |

There are 32 distinct currently accepted human reviews. The three spine roles overlap the four automatic roles; these counts must not be added to claim 26 body roles. Grounded root was not a human-reviewed point. Category labels are retained verbatim from the events; an acceptance category does not fabricate a placement.

The sole move was neck_01 from {movement['from_cm']} cm to {movement['to_cm']} cm. Delta XYZ={delta} cm; Euclidean distance **{movement['distance_cm']:.9f} cm**, predominantly +Y forward, with a −0.437 cm vertical change. All other body positions and finger endpoints remained accepted without movement. Generated axes/local transforms were recomputed; this is not additional human landmark movement.

The ledger contains **159** real panel commands: {dict(counts)}. The user's observed 157 commands precede the preserved Save event 158 and Finish event 159. There are 13 digit-assignment commands, including reassignment, yielding ten final identities; 34 review commands yield 32 distinct current approvals; 108 commands are navigation/selection/track-preview. These are command counts, not raw mouse gestures. Elapsed Start-to-Finish time is **{metrics['elapsed_trial_seconds']:.6f} seconds (3 h 22 min 59.219 s)**, including pauses; active authoring time and novice usability were not measured. One placement does not imply one-click completion.

| Track | Left hand | Right hand |
| --- | --- | --- |
| 1 | Index | Middle |
| 2 | Middle | Index |
| 3 | Ring | Ring |
| 4 | Pinky | Pinky |
| 5 | Thumb | Thumb |

Three phalange pivots per accepted track were sampled procedurally from retained donor length proportions along the actual Lara target path. The donor JSON is authoring provenance; the donor is not the final skeleton or a runtime dependency. No hidden Phase4A manual coordinate was used. Evidence: [metrics](correction_metrics.json), [human reviews](human_review.json), [actual events](actual_correction_list.json), [ledger preservation](human_ledger_preservation.json).

### 29.2 Gate failures, diagnoses and legitimate corrections

The initial refresh produced {len(initial['checks'])} checks, {sum(c['pass'] for c in initial['checks'])} passes and three failures. Each was investigated before downstream work:

| Initial failure | Classification | Evidence and minimal correction |
| --- | --- | --- |
| left_right_not_crossed | Pivot/skeleton convention mismatch | Thoracic parent X=0.690281570 cm; right clavicle global X=+0.067035258 cm but relative X=−0.623246312 cm; left relative X=+0.763563216 cm. Clavicle roots are judged relative to their thoracic parent. All other limb articulations retain strict global left-positive/right-negative signs. |
| finger_review_thumb_l | Correction replay/propagation bug causing provenance invalidation | UE Python 3.11 and offline Python 3.14 generated a third-thumb Y difference of 1.7763568394002505e−15 cm. Exact hash matching discarded a real human approval. The original in-editor state was recovered and independently matched to all 159 event files. |
| finger_chains_anatomically_resolved | Same replay bug, aggregate consequence | The lost thumb approval reduced the complete set. No extra anatomical review was invented. |

Replay now retains the exact reviewed finger coordinates only when the review signature is current, all other regenerated fields match, and recomputation differs by at most 1e−10 cm. This guard handles arithmetic replay; the human review hash remains exact. Real endpoint, track or dependent body changes still invalidate approval. Generated local transform replay differs only at floating-point round-off and is measured separately. [Thirteen regression checks](finalisation_regression.json) pass, including wrong-side clavicle and crossed-wrist rejection. No numerical anatomy thresholds were relaxed, checks removed, or failures renamed. The clavicle reference origin change is explicit in gate_policy_correction.

Final result: **186 checks, 186 passes, 0 failures, downstream_authorised=true**. Structural/geometric checks pass; automatic_anatomical_passed=false because this is human-assisted acceptance. There is no remaining numerical convention disagreement under the documented clavicle convention. Numerical envelope/path screens and human judgement still do not certify internal anatomy or animated deformation. [Full gate](anatomical_validation.json).

### 29.3 Fresh skeleton and original-surface UE skinning

Created /Game/MetaHumanTo3DCharacter/Phase4D/Character/SKEL_Lara and SK_Lara, with intermediate SK_Lara_Authoring. The connected hierarchy has 53 bones: grounded root, pelvis, three spines, neck/head, two clavicles, arms/hands, legs/feet/balls, and 30 finger phalanges. All parents, accepted component pivots, local transforms and proper axes were checked. Maximum component position construction error is {max(skeleton['measured_results']['position_errors_cm'].values()):.12g} cm; maximum axis error is {max(skeleton['measured_results']['axis_errors'].values()):.12g}; all reference scales are unit. Skeleton/skin/gate evidence share final proposal SHA256 {ledger_audit['final_proposal_sha256']}.

Binding used UE GeometryScript **GEODESIC_VOXEL, voxel resolution 128, stiffness 0.2, max five influences**. There are 28,189 vertices, 49,508 triangles, exactly five positive influences per vertex, zero invalid/unweighted vertices and normalised weights. Fresh disk reload verifies identical ordered vertices/triangles and per-corner UV hash, original 180.0 cm physical geometry and original Phase4D material/texture. Saved and pre-save weight maps have maximum numerical delta {readback['maximum_saved_weight_delta']}; a raw Python list/tuple representation mismatch is not a weight alteration. No weight-paint edits were made.

Native reference-pose appearance was inspected beside the source static mesh. Live component/reference position maximum error is {native['reference_component_position_error_cm_max']:.12g} cm. The Phase4D material's SkeletalMesh usage flag was persisted after UE auto-enabled it; texture/shader graph remained intact. [Skeleton](skeleton_construction.json), [binding](skinning_results.json), [material usage](material_usage_correction.json), [native reference capture](native_visual_capture.json).

![Original static source, left; final skeletal reference pose, right](native_reference_pose.png)

### 29.4 IK, Manny mapping and baked clips

Fresh assets are /Game/MetaHumanTo3DCharacter/Phase4D/Character/IK_Lara and RTG_Manny_Lara. UE automatic characterisation and automatic FBIK succeeded, then the actual result was inspected. One enabled FBIK solver starts at pelvis, with 20 iterations, 10 subiterations and allow_stretch=false. Retarget root is pelvis; root-motion bone is root. Hand goals terminate at hand_l/r and foot goals at ball_l/r, with actual solver goal bindings checked. The automatically generated target legs ended at foot; both were extended to ball and their goals matched. An explicit Root chain and LeftFoot/RightFoot ball chains complete the setup.

The original /Game/Characters/Mannequins/Rigs/IK_Mannequin remains unchanged. A fresh Phase4D/Authoring/IK_MannySource copy adds two explicit ball chains; its existing leg chains already ended at ball. All **22 essential mappings** pass exactly: Root, Spine, Neck, Head, left/right Clavicle, Arm, Leg, Foot and ten named fingers, each mapped to the same semantic source chain. Target retarget pose was reset and aligned with UE auto_align_all_bones. Root Motion, Speed Planting and Stride Warping operations were removed for the diagnostic in-place bake; no Copy Pose or live donor runtime is used. This choice does not solve world-space locomotion/contact.

| Role | Exact destination-native asset | Duration s | Evaluated poses |
| --- | --- | ---: | ---: |
{chr(10).join(cliprows)}

All four clips reference SKEL_Lara. All 244 sampled poses are finite with unit bone scales; grounded root displacement is zero. Actual live pose variation was observed for every clip, not inferred from asset creation. Pelvis ranges, limb lengths and bend magnitudes are retained in [native motion summary](native_motion_summary.json); positive segment lengths and finite transforms do not prove every anatomical bend sign. [IK/mapping/goal evidence](ik_retarget_results.json), [batch bake](animation_bake_results.json).

### 29.5 Deformation and foot/contact evaluation

CPU linear-blend deformation uses the actual UE binding weights and all 244 evaluated baked poses. Original nondegenerate triangle area below 10% or above 5× is a **diagnostic flag**, not a new anatomy gate or an automatic quality verdict. Per-region screens cover points within 5 cm of the listed pivots. Native material captures and front/side CPU projections were inspected for shoulders, elbows, wrists, pelvis/hips, knees, ankles, fingers and clothing transitions. Reference surface is retained; animated shoulder/shirt transitions show thinning/jagged distortion, wrists/fingers carry local flags, and boots penetrate the plane. No gross digit identity swap or reversed limb is evident in the representative views; exhaustive continuous collision/bend-sign acceptance is not claimed.

| Clip | Max collapsed triangles | Max stretched triangles | Left minimum-sole Z range cm | Right minimum-sole Z range cm |
| --- | ---: | ---: | --- | --- |
{chr(10).join(rows)}

These maxima can occur at different samples. Run/reach flags affect a small portion of the 49,508-triangle surface; the count alone does not quantify visual severity. Native shoulder/clothing shape and stance penetration independently prevent quality acceptance. Root stays at Z=0; all bone scale errors are zero. Positive sole height during running/jumping can be intended airborne motion and is not automatically called hover.

| Region | Max collapsed, any clip | Max stretched, any clip |
| --- | ---: | ---: |
{chr(10).join(regionrows)}

Heel/rear-sole and toe/front-sole minima, ankle and ball positions, ankle-to-ball pitch and original-surface trajectories are recorded at every sample. Heel/toe groups use the rear/front 20% of the original sole Y coordinates; they are geometric proxies. The maximum measured stance-surface penetration is **4.520 cm** in walk; idle right sole stays approximately 2.40–2.60 cm below ground. Foot-contact quality is not accepted.

| Clip | Side | Near-ground intervals | Max apparent slide cm/s | Ankle-to-ball pitch range deg |
| --- | --- | ---: | --- | --- |
{chr(10).join(slide_rows)}

Near-ground means both sampled minimum-sole heights lie within ±2 cm. Apparent sliding is measured in component space on a stationary in-place actor, with no world locomotion and no authoritative planted-contact labels. The high walking/running values are not a complete planted-foot controller assessment. Near −89° toe pitch can occur on lifted feet; these angles need phase-aware interpretation. Penetration is directly measured. Speed Planting/world movement/contact refinement and shoulder/finger skinning remain future quality work, with no hidden fixes in this trial. [Per-sample contact/deformation](deformation_contact_results.json), [visual review](deformation_visual_review.json).

![Native raised-arm shoulders and clothing, with run instance at left](native_shoulders_reach.png)

![Actual weighted animated feet and grounded reference; red line is Z=0](animated_feet_side.png)

### 29.6 All ten fingers under real animation

A new authoring-only Manny finger fixture holds the remaining skeleton at an idle baseline while rotating each of ten named three-phalange chains independently about local Z by a 45° sine peak, one digit per one-second slot. This is diagnostic animation, not a human correction or a claim of natural flexion. The same Phase4D retargeter baked /Game/MetaHumanTo3DCharacter/Phase4D/Character/Animations/MannyFingerIdentity onto SKEL_Lara. It has 22 evaluated baseline/peak/boundary poses and was also exercised during native source-free playback.

| Digit | Peak local angular change deg | Largest other digit change deg | Peak phalange nearest same-digit surface support cm | ≤1.2 cm diagnostic |
| --- | ---: | ---: | ---: | --- |
{chr(10).join(fingerrows)}

**10/10 semantic independent-motion checks pass** and all sampled 3D same-hand chain separation screens exceed 0.25 cm. Identity stays Index/Middle/Ring/Pinky/Thumb, including both thumbs; the human correspondence avoided all manual phalange placement. Surface groups use the accepted actual target tracks and original vertices, not donor geometry. Same-chain mean weight is approximately 0.71–0.86. Nine of ten peak surface-support screens pass; **right ring is 1.252 cm and fails**. The ≤1.2 cm and >0.25 cm screens are explicit diagnostics, not inherited anatomy thresholds. Sparse nearest-surface support is not full volumetric containment; projected paths can overlap while remaining separated in 3D.

Natural thumb opposition/curl, exhaustive ROM, full finger-volume containment and continuous collapse/collision-free behaviour are not proved by this fixture. Body clips also flag finger-local triangle collapse/stretch. Finger deformation is therefore not accepted, despite successful semantic correspondence and independent motion. No finger anatomical corrections or weight edits were added. [Fixture bake](finger_animation_bake.json), [all ten results](finger_animation_validation.json).

![Actual baked independent digit peaks](animated_finger_validation.png)

### 29.7 Source-free native playback and dependency closure

Saved /Game/MetaHumanTo3DCharacter/Phase4D/Character/BP_LaraNativePlayback has four Lara SkeletalMeshComponents, directly playing idle/walk/run/JumpingJacks in AnimSingleNode mode. Map: /Game/MetaHumanTo3DCharacter/Phase4D/Maps/L_LaraNativePlayback. The final scene was created with **no Manny or donor component**, satisfying the disabled/removed-source condition from the start. No source actor was briefly destroyed as a fabricated demonstration.

Actual SIE recorded **125 time samples × four components = 500 component frames** over all four clips plus the finger fixture, with all 53 component/world bone transforms captured, zero errors and zero foreign runtime skeletal meshes. All five sequences showed nonzero live pose variation. Direct native AnimSingleNodeInstance was verified. A source authoring rig remains in the project for rebaking but is absent from playback dependencies. No fitting, cloud service or inference runs during playback. The interactive saved test scene is left open with its four native clips playing.

Fresh UE commandlet reload and recursive hard/soft dependency audit pass. Runtime seeds include the map, Blueprint, final Skeleton/Skeletal Mesh and all five Lara-native sequences. Closure contains **{len(game)} /Game packages and {len(closure['measured_results']['closure'])-len(game)} normal /Engine or /Script dependencies**. There are zero foreign /Game, MetaHuman/donor, prior-phase, live Manny, retarget authoring or helper-plugin references. The accidental Skeleton preview-mesh reference was {load('preview_dependency_cleanup')['status']}; reference transforms were checked unchanged. Remaining authoring-preview packages: {closure['measured_results']['authoring_preview_packages']}.

The original material, texture and static Lara reference are intentional dependencies of the visual test map. This is a verified package closure, **not** a clean-project migration or cooked executable test. [Native playback](source_independent_playback.json), [motion observed](native_motion_summary.json), [closure edges and fresh readback](final_dependency_closure.json), [safe preview cleanup](preview_dependency_cleanup.json).

### 29.8 Product conclusion and preservation

| Scope | Classification | Measured basis |
| --- | --- | --- |
| Landmark/correspondence stage on this Lara | Practical assisted | One moved neck; 21 body + ten finger reviews accepted unchanged; generated phalanges; no manual intermediate placement. Expert review, 159 commands and elapsed time still apply. |
| Body as an animated character | Experimental assisted | Native build/bake/playback succeeds; stance penetration and shoulder/clothing quality remain unacceptable. |
| Fingers as animated/skinned digits | Experimental assisted | Ten identities and independent motions succeed; right-ring support fails a screen and natural thumb/full-range quality remains unproven. |
| Overall Mode A | Experimental assisted | Completed downstream measurements do not yet support a fully working character-quality claim. |

Can automatic Lara be converted into an anatomically accepted Manny-compatible native character using a small number of intuitive landmark corrections? **Anatomical acceptance and the mechanical native pipeline: yes, with one real neck movement plus explicit body/digit review. A fully working, acceptably deforming/contacting character: not yet demonstrated.** Auto-skin, retarget, bake and native source-free playback succeeded. The remaining blockers concern deformation/contact and finger surface quality, not missing semantic mappings or runtime Manny/MetaHuman dependency. A single expert-reviewed mesh does not establish broad automation or novice intuitiveness.

Protected audit: **{audit['protected_file_count']} prior authored files, zero changed, zero missing and zero unexpected authored files outside Phase4D**. Original Lara ZIP SHA256 remains {audit['archive_sha256']}. Phase2/3/3B/4A/4B/4C project evidence/assets, original source and project configuration remain byte-identical within that audit. All 159 human event files retain their input hashes; exact recorded body/finger positions and approvals match the recovered editor snapshot. New authored work is confined to Phase4D. No Engine-source/reference-project mutation, Git staging, commit or push was performed; an exhaustive external Engine hash baseline was not available.

The helper build used Phase4D-only native outputs after the installed UBT action runner failed; failed build/API/capture attempts remain in Working/Phase4D. Closing the warning window closed the editor, so the saved scene was reopened; an initial sandbox shader-cache failure and a command-line Python option that exits after execution were resolved for interactive reopening. Native material usage is saved and the reopened map check reports zero errors/warnings. None of these recovery steps added human events. [Protected audit](protected_file_audit.json), [ledger audit](human_ledger_preservation.json), [final classification](experiment_result.json).

Reproducible evidence refresh (does not author human reviews or rebuild assets):

    python -X utf8 Working/Phase4D/finalisation_regression.py
    python -X utf8 Working/Phase4D/finalise.py
    python -X utf8 Working/Phase4D/render_evidence.py
    python -X utf8 Working/Phase4D/complete_trial_report.py

The report writer is guarded against duplicate appendices; refresh updates only section 29 and checks that the historical prefix matches the preserved reconstruction. Current machine-readable anatomy is distinct from character_quality_accepted=false. Full build/retarget scripts, exact paths, data and logs remain Phase4D-scoped for review. Level 1 single-agent execution and mandatory self-review were used.
'''
report=O/'Phase4DGuidedLandmarkCorrection.md';old=report.read_text(encoding='utf-8')
if '## 29. Completed human trial' not in old:
 assert hashlib.sha256(report.read_bytes()).hexdigest()==recovery['reconstructed_sha256'],'Historical report changed before append'
 report.write_text(old+append,encoding='utf-8')
else:
 historical=old.split('\n\n## 29. Completed human trial',1)[0]
 assert historical==(W/'HumanTrialFinalisation/InputSnapshot/reconstructed_pretrial_report.md').read_text(encoding='utf-8'),'Historical prefix changed'
 report.write_text(historical+append,encoding='utf-8')
core.save(O/'human_trial_finalisation.json',{'status':'completed_evaluation_not_accepted_rig','anatomical_checks':186,'anatomical_passes':186,'anatomical_failures':0,'downstream_authorised':True,'human_metrics':metrics,'human_ledger_audit':ledger_audit,'mechanical_native_pipeline_passed':True,'character_quality_accepted':False,'classifications':{k:experiment[k] for k in ['body_classification','finger_classification','overall_mode_a']},'report':str(report),'assets_created':assets,'report_sha256':core.file_sha(report),'original_historical_report_byte_exact_preservation_claimed':False,'preservation_audit':audit,'self_review':'Level1; anatomy policy, replay provenance, source-free pose variation, fresh asset readback, visual quality and report/machine-data consistency checked'})
print('Completed report:',report,'; quality accepted=False; protected files and human ledger unchanged')
