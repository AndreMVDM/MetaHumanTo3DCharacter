🟠 **Medium confidence**

# MetaHumanTo3DCharacter — Phase 4E Character Quality Refinement

Completed investigation, candidate generation, native comparison and reporting on 1 October 2026. Overall quality acceptance remains incomplete. This report is the final Phase 4E result; failed exploratory logs and intermediate candidate manifests remain for provenance.

Project: `E:\Repo\UE\Projects\MetaHumanTo3DCharacter`. UE 5.8 installed at `D:\Epic Games\UE_5.8`. All authored changes are isolated to Phase4E. Execution used Level 1 single-agent work with self-review; no fitting rerun, bone movement, conventional weight painting, commit, push or polished plugin UI.

## 1. Executive summary

Programmatic weighting materially repairs Lara's severe front-crotch fold and improves shirt/shoulder deformation while preserving the accepted skeleton and original surface. Native matched-camera views confirm the original trouser fold is stabilised. The selected candidate combines a pelvis/side-aware refinement with a local direct-distance shoulder bind. It remains a research candidate, not a fully accepted production character.

The final 34-pose suite gives 55.8% lower mean front-pants edge-log strain, 44.0% lower back/hip strain and 41.9% lower shoulder strain. Those numbers are screening measurements, not volume or visual-quality guarantees. Some worst reach frames have **more** shoulder triangles below half their reference area. Angular armpit detail remains. Finger support remains 9/10; natural thumb motion is unproven.

A separate sole-aware authoring contact bake reduces flat-floor penetration to **0.0000 cm idle, 0.1579 cm walk and 0.3376 cm run**, evaluated from UE at 120 Hz. No actor offset or root translation was introduced.

**Product decision: continue bounded quality research; do not begin the polished Assisted Rigging plugin/UI on the premise that deformation risk is solved.** This phase does not establish that traditional full manual weight painting is fundamentally required. It also does not establish a general automatic solution for arbitrary clothed humanoids.

## 2. Phase 4D starting point

The mandatory [Phase 4D report](../Phase4D/Phase4DGuidedLandmarkCorrection.md), especially completed appendix 29, and its actual accepted assets were read before authoring. Historical pending sections in that report were not treated as the final result. [Evidence index](phase4d_evidence_index.json) records the input paths and hashes; [immutable inventory](protected_before.json) records prior project files.

Retained: 186/186 anatomy checks, downstream_authorised=true, 23 accepted body roles, ten finger identities, one actual human landmark movement at the neck, no manual phalange placement, fresh 53-bone hierarchy, 180 cm Lara surface, IK mapping and native idle/walk/run/reach/finger clips. No semantic fitting or human-ledger editing occurred.

The saved Phase4D skin was freshly read through GeometryScript. Recorded and disk weights match numerically exactly; influence ordering alone differs at some vertices. Baseline contains 28,189 vertices, 49,508 triangles, one material slot, maximum five influences and no unweighted vertices. The working baseline reproduces geometry, UVs, reference transforms and weights. [Readback](baseline_asset_readback.json).

## 3. Exact baseline deformation reproduction

Source mesh: `/Game/MetaHumanTo3DCharacter/Phase4D/Character/SK_Lara`. Unrefined copy: `/Game/MetaHumanTo3DCharacter/Phase4E/Character/SK_Lara`. Comparison map: `/Game/MetaHumanTo3DCharacter/Phase4E/Maps/L_QualityComparison`.

Native JumpingJacks at normalised time 0.5 reproduces the inward front-trouser/crotch fold and shirt/armpit stress. Both meshes use the same Phase4E native animation and are placed at the same origin for each capture, with the other mesh hidden. Camera transforms, clip times and screenshot-file confirmation are retained in [native capture manifest](native_visual_capture.json). Front, side and review views are actual textured UE screenshots. The first nominal close views were wider than ideal; additional closer stress views were captured and labelled separately in [stress manifest](native_stress_visual_capture.json).

The original 244 body poses and 22 finger samples remain read-only input. Baseline contact reproduces approximately 2.60 cm idle, 4.52 cm walk and 3.14 cm run penetration. Native motion sampling and support fixtures are retained alongside new evidence.

## 4. Pants/crotch diagnosis

The skeleton-relative front-pants review envelope contains 802 vertices and 1,332 fully enclosed triangles. It is a review envelope, not a ground-truth trouser segmentation. **768/802 vertices carry over 10% root weight; 319/802 carry over 10% from each thigh simultaneously.** The mean influences are:

| Bone | Baseline mean | Saved refined mean |
| --- | ---: | ---: |
| root | 0.1943 | 0.0000 |
| pelvis | 0.2776 | 0.7453 |
| thigh_l | 0.1343 | 0.0087 |
| thigh_r | 0.2032 | 0.0554 |
| spine_01 | 0.1738 | 0.1738 |
| spine_02 | 0.0168 | 0.0168 |

Installed UE binding source builds parent-to-child bone fans. The grounded root-to-pelvis segment is long and competes geometrically with deforming anatomy. Approximately 19.4% stationary root influence in this envelope, coupled with competing pelvis/thigh motion, provides a measured explanation for distortion. A root-to-pelvis-only control reduces pants strain; adding a stable central pelvis envelope and soft side gating improves it further. This is stronger causal evidence than appearance alone.

The final mean pelvis weight rises to 74.5%, with continuous fades into thighs. It deliberately keeps the waistband/central crotch following the pelvis. It may be too rigid for other clothing; that is a generalisation risk. Cloth/body proximity and voxel leakage were considered, but no separate underlying body donor exists and neither was isolated as the dominant cause. No quantitative evidence establishes an unsuitable accepted pivot.

## 5. Shoulder diagnosis

The shoulder envelope contains 1,661 vertices. Baseline mean combined upperarm weight is 0.4753, clavicles 0.2624, spine_01–03 0.2133 and lowerarms 0.0308. Full distributions and quantiles are in [weight-field analysis](weight_field_analysis.json).

Neither simply increasing torso support nor globally smoothing gives the best multi-region result. A stiffer direct-distance bind reduces shoulder distortion but severely worsens the pants when applied globally. Blending it only over the shoulder/upper-shirt neighbourhood avoids that global regression. Saved means become approximately 0.5235 upperarms, 0.2747 clavicles and 0.1738 spine_01–03. The result is not explained by “more clavicle weight” alone; spatial distribution matters.

Native overhead/horizontal views show less chest/neck/necklace dragging and a more stable shirt outline. Armpit/upperarm faceting and local compression persist. LBS volume loss, coarse surface detail and overlapping clothing/accessory surfaces remain plausible contributing factors; this phase does not identify them as proven sole causes.

## 6. Weight-field analysis

[Heatmaps](baseline_weight_heatmaps.png) visualise actual root, pelvis, thigh, clavicle, upperarm and spine weights. [Before/after distributions](before_after_weights.json) and [adjacent weight-gradient diagnostics](weight_gradient_diagnostics.json) provide machine-readable review flags. Masks derive from accepted pivots, body axes and relative spans rather than lists of manually painted vertices.

Analysis-only positional seam welding at 0.00001 cm finds 102 connected components. The largest upper component has 11,550 vertices; a lower component has 7,424. These mix anatomical/clothing regions; one material slot does not supply shirt/trouser/boot/glove labels. Connectivity can identify some accessories but cannot reliably label all garments. Actual topology was never welded or changed. No semantic material names were invented.

## 7. UE skinning/refinement API investigation

The installed GeometryScript bone-weight functions, `SkinWeightBinding.cpp`, `SkinWeightModifier.h` and FloorConstraint operation implementation were inspected read-only. UE provides direct-distance and geodesic voxel binding, influence pruning/blending, weight transfer and inpainting options. The binder already measures parent/child bone-segment geometry; replacing “joint distance” with “bone distance” would not by itself be a new solution.

`USkinWeightModifier` is Python-accessible: set a skeletal mesh, set named per-vertex weights, normalise/prune and commit. This successfully wrote and reloaded isolated candidates. Saved quantisation changes the final input weight by at most 0.00002643; saved weights, not idealised input weights, drive final measurement.

Primary references: [Skeleton Editing](https://dev.epicgames.com/documentation/unreal-engine/skeleton-editing-in-unreal-engine), [UE 5.8 retarget operation stack](https://dev.epicgames.com/documentation/unreal-engine/retargeting-operation-stack-in-unreal-engine-5-8), [GeometryScript transfer options](https://dev.epicgames.com/documentation/en-us/unreal-engine/BlueprintAPI/Utilities/Struct/MakeGeometryScriptTransferBoneWe-), and [Epic cloth weight-transfer tutorial](https://dev.epicgames.com/community/learning/tutorials/Dl20/unreal-engine-panel-cloth-transfer-skin-weights-node). API availability was confirmed against installed source/runtime rather than assuming older tutorials matched 5.8.

Transfer/inpainting is available but was **not executed as a valid body-to-garment experiment**: Lara has no separately established correctly weighted underlying body. Transferring the same faulty field would not test the desired donor strategy. No Engine source was modified.

## 8. Candidate approaches tested

Six fresh UE bind controls were produced:

| Method | Resolution | Stiffness | Influences |
| --- | ---: | ---: | ---: |
| Direct distance | not applicable | 0.2 | 5 |
| Direct distance | not applicable | 0.8 | 4 |
| Geodesic voxel | 128 | 0.8 | 4 |
| Geodesic voxel | 256 | 0.2 | 5 |
| Geodesic voxel | 256 | 0.6 | 4 |
| Geodesic voxel | 128 | 0.2 | 8 |

Measured binder calls took 0.265–0.672 seconds on this mesh, excluding extraction, saving, analysis and pipeline overhead. [Binding evidence](ue_binding_experiments.json).

Initial screening compares baseline plus 13 alternatives: root-only redistribution, global graph smoothing, pelvis-only/shoulder-only/combined semantic envelopes, moderated strengths, local smoothing and six UE bind controls. Four local hybrid alternatives follow. [Initial comparison](candidate_comparison.json), [hybrids](hybrid_comparison.json). These exploratory score files predate correction of the synthetic 45° arm convention; **final_stress_comparison.json and final_deformation_summary.json are authoritative final results**.

Global direct binding was rejected because pants strain increases markedly. Global smoothing improves shoulder metrics but does not solve the pants. Higher voxel resolution alone is insufficient. Eight influences do not reliably improve finger support. The selected method is `hybrid_direct_08_4`; it is an explicit bounded candidate choice, not an unconstrained optimiser.

## 9. Pants refinement result

Native matched-camera JumpingJacks views show the severe original inward crotch fold materially repaired. The 0.5 reach sample drops from 16 to 0 triangles below half reference area and from 7 to 1 above twice area in the review envelope. Edge-log strain drops 0.124245 → 0.048346. Reference geometry remains exact.

Neutral/reference, idle/normal stance, wide stance, reach and walk comparisons were generated. Wide stance preserves a continuous crotch transition in the reviewed native view. Back/hips mean strain improves by 44.0% in the final stress suite and the sampled native backside does not show a gross new defect. No visible tearing was observed in these views. There is no exhaustive self-intersection, seam-coincidence, cloth simulation or enclosed-volume proof.

This is a **successful material pants repair on Lara**, with residual quality review still required. It is not a certification across unseen poses or garments.

## 10. Shoulder refinement result

Neutral/reference, 45° elevation from down, horizontal, overhead, elbows-bent and native reach poses were tested. Native paired horizontal/overhead images show better shirt/chest shape. Mean shoulder edge-log strain in the final stress suite falls 0.235414 → 0.136863.

The result remains **partial**. Across the 61 actual reach samples, the maximum count of shoulder triangles below half area rises **703 → 844**, while maximum over-twice-area count falls 409 → 110 and mean strain falls 0.333455 → 0.197961. An averaged score would conceal that compression regression. Angular armpit detail remains visibly reviewable. Full “no obvious catastrophic collapse across representative raised-arm motion” acceptance is not claimed.

No bone-position change was warranted: weights alone materially improve both primary regions. No proof was obtained that all reasonable weights fail at the current pivot.

## 11. Stress-pose framework

`Working/Phase4E/model.py` evaluates CPU linear blend skinning against the saved surface, reference inverse matrices and actual UE bone transforms. The suite has 34 poses: seven synthetic body poses, four samples from each of idle/walk/run/reach and eleven selected finger-fixture samples. The seven body poses are published as native `StressAnimations` as well.

The neutral pose is the accepted reference; it is not a newly authored arms-down rest. The 45° fixture lowers the horizontal reference arms by 45°. Wide stance and strong knee bend are diagnostics, not natural motion captures. All body roles also receive a separate 244-pose evaluation from UE-exported animation samples.

Measurements include triangle area ratios below 0.5/0.1 and above 2, edge ratios, RMS log edge strain, adjacent weight gradients, root/bilateral thigh influence, finite geometry and sole height. Degenerate reference faces/edges are excluded from relevant ratios. Counts refer only to triangles fully inside each review mask; comparisons use identical membership.

RMS log strain is sqrt(mean(log(deformed_edge_length/reference_edge_length)^2)). Lower is useful for locating distortion but can reward stiffness and is not visual truth. There is no robust full self-intersection detector or local thickness/volume acceptance. CPU figures expose geometry; actual UE textured images independently support the primary visual comparison.

## 12. Automated repair feasibility

A reusable sequence is technically feasible: bind → inspect semantic influence errors → replay stress poses → generate a small bounded set of local refinements → preserve normalisation/top-five influences → replay all tests → reject regressions → flag residual regions. This phase implements the core analysis/refinement operations as scripts, not a plugin.

The pelvis envelope, side gating, local bind blending and rejection loop are reusable concepts. They are not a validated universal clothing classifier. The current shoulder blend includes centimetre thresholds calibrated on the accepted 180 cm Lara mesh; those must become dimensionless limb/span parameters before broader reuse. Mesh axes and signed sides are accepted pipeline conventions. Arbitrary orientation/topology requires the same canonical frame, not Lara-specific vertex numbers.

One character is insufficient to claim a production automatic repair system. The evidence supports avoiding full manual painting for this pants defect. It does not yet support automatic acceptance of shoulders/hands or all clothed characters.

## 13. Feet/contact refinement

Weights alone do not resolve contact: measured idle/walk/run penetration remains approximately 2.61/4.59/3.17 cm. An authoring-only UE FloorConstraint retarget experiment, configured with four-point footprints derived from the soles, produces 1.59/2.20/3.23 cm. Run worsens, so that configuration was rejected as the final uniform correction. [Comparison](contact_comparison.json), [operation settings and native poses](contact_ue_experiment.json).

The selected correction is a post-bake authoring step: evaluate the actual skinned sole, raise only a penetrating foot target by its required clearance, solve two-bone leg IK with retained segment lengths/knee plane, keep foot/ball orientation and iterate up to five times. The static sole probes contain 192 left and 198 right vertices from the original bottom 2 cm of the surface; this is not exhaustive boot/whole-mesh collision measurement. Correction is bounded to 6 cm per iteration and does not translate the actor, root or pelvis. The original accepted reference skeleton is unchanged. It changes animation leg rotations, so it is separate from the weights-only quality comparison.

The first 30 Hz bake looked nearly clear at keys but dense midpoint evaluation found 0.55 cm walk and 0.95 cm run penetration. That result was retained in [30 Hz evidence](surface_contact_30fps_dense_validation.json). A second and final bounded 60 Hz bake reduces interpolation error. **Final saved weights + UE key/half-key evaluation at 120 Hz:**

| Clip | Original 4D penetration cm | Final penetration cm | Dense poses |
| --- | ---: | ---: | ---: |
| idle | 2.5967 | 0.0000 | 909 |
| walk | 4.5199 | 0.1579 | 225 |
| run | 3.1355 | 0.3376 | 229 |

The baseline and final sampling densities differ; baseline numbers reproduce the requested historical measurement, while final dense sampling is stricter. [Dense result](surface_contact_dense_validation.json), [bake](surface_contact_native_bake.json). Root displacement and unit-scale error are zero. Non-leg component translations differ by at most 0.000064 cm at matched keys. Walk's largest adjacent left-foot displacement is 7.895 → 8.080 cm at 60 Hz; endpoint continuity remains approximately 0.00011 cm. This is a diagnostic, not proof of planting. [Continuity](contact_continuity.json).

The primary demonstrated issue is animation/retarget contact on the actual sole surface, not proven bad foot pivots. No arbitrary offset was used. Speed Planting, contact curves, foot sliding, stride adaptation, terrain, collision-driven runtime IK and other motions remain untested. These flat-floor authoring results must not be advertised as a general locomotion system.

## 14. Fingers/thumb refinement

Accepted identity, correspondence, chain positions and independent animation are retained. The ten active-digit support screens on freshly saved body-refined weights remain 9/10. Right ring is approximately **1.2517 cm**, above the unchanged 1.2 cm threshold. [Final saved-weight validation](final_finger_validation.json).

A bounded accepted-track segment-distance weighting with proximal hand fade was tested and rejected: right-ring support worsened to approximately 1.278 cm. Six alternative UE bind controls were also tested; the best worst-digit value is 1.200153 cm (geodesic 256, stiffness 0.6, four influences), which still fails. No threshold rounding or acceptance relaxation was used. [Finger experiment](finger_weight_experiment.json), [bind controls](finger_binding_controls.json), [decision](finger_candidate_decision.json).

The right-ring sparse track group has 77 vertices. In the unchanged reference pose, joint-to-nearest-group distances are 1.319731, 0.918300 and 0.653601 cm. The proximal screen therefore already fails at rest; the group omits some palm support. This weakens a conclusion that the animation or pivot must be faulty, but does not prove a correct replacement support definition. [Rest evidence](right_ring_rest_support.json). Accepted joint positions were not changed.

A separate two-axis thumb diagnostic was added using the accepted thumb/index/hand axes: swing, hand-axis rotation and interphalangeal flexion, at 0/0.5/1 amplitude on both sides. Geometry is finite and chain support remains below 1.2 cm in that fixture. Synthetic axis/sign choices, unvalidated joint limits and absent grasp/collision/human assessment mean **natural thumb opposition remains unproven**. [Diagnostic](thumb_opposition_diagnostic.json), [image](thumb_opposition_diagnostic.png).

Semantic swaps were not introduced: hierarchy/identities and source fixture transforms are preserved. Full deformed-surface crossing/collision was not exhaustively retested. The requested material finger-support improvement acceptance is **not passed**.

## 15. Before/after visual comparison

Every native pair below uses matching camera and clip time recorded in its manifest. Images remain unaltered UE captures. CPU figures use the same orthographic review boxes per pair.

| View | Baseline | Refined |
| --- | --- | --- |
| Native JumpingJacks front | [Image](native_baseline_front.png) | [Image](native_refined_front.png) |
| Native side | [Image](native_baseline_side.png) | [Image](native_refined_side.png) |
| Pants review | [Image](native_baseline_pants_close.png) | [Image](native_refined_pants_close.png) |
| Wide stance pants | [Image](native_baseline_pants_wide.png) | [Image](native_refined_pants_wide.png) |
| Back/hips in reach | [Image](native_baseline_hips_back.png) | [Image](native_refined_hips_back.png) |
| Horizontal arms | [Image](native_baseline_shoulders_horizontal.png) | [Image](native_refined_shoulders_horizontal.png) |
| Overhead arms | [Image](native_baseline_shoulders_overhead.png) | [Image](native_refined_shoulders_overhead.png) |
| 45° arms | [Image](native_baseline_shoulders_45.png) | [Image](native_refined_shoulders_45.png) |
| Reference | [Image](native_baseline_neutral.png) | [Image](native_refined_neutral.png) |
| Worst original walk feet/front | [Image](native_baseline_feet_front.png) | [Image](native_refined_feet_front.png) |
| Feet/side | [Image](native_baseline_feet_side.png) | [Image](native_refined_feet_side.png) |

The foot pair intentionally uses original versus contact-corrected animation at the same time; body skin pairs use identical original motion. [Foot capture manifest](native_contact_visual_capture.json). CPU figures: [pants/front](pants_front_comparison.png), [pants/side](pants_side_comparison.png), [shoulders](shoulder_comparison.png), [whole body](body_comparison.png), [finger fixture](finger_stress_comparison.png). [Visual findings and limits](visual_review.json).

## 16. Quantitative deformation comparison

Final mean of per-pose RMS log edge strain over the 22 non-neutral/non-finger body tests (six synthetic body poses plus sixteen clip samples):

| Region | Baseline | Saved refined | Reduction |
| --- | ---: | ---: | ---: |
| front_pants | 0.122974 | 0.054406 | 55.8% |
| back_hips | 0.166027 | 0.092983 | 44.0% |
| shoulders | 0.235414 | 0.136863 | 41.9% |
| upper_torso | 0.201887 | 0.140081 | 30.6% |

The table is computed directly from those named tests, using saved candidate weights and the corrected 45° fixture, rather than the preliminary screen.

All 244 actual body samples give:

| Motion | Region | Mean strain baseline | Mean strain refined | Worst <0.5 area count |
| --- | --- | ---: | ---: | ---: |
| idle | front_pants | 0.096020 | 0.051579 | 2 → 2 |
| idle | shoulders | 0.176260 | 0.100886 | 112 → 12 |
| walk | front_pants | 0.146930 | 0.073123 | 37 → 7 |
| walk | shoulders | 0.180863 | 0.111149 | 116 → 79 |
| run | front_pants | 0.254262 | 0.107395 | 151 → 34 |
| run | shoulders | 0.280829 | 0.151820 | 167 → 151 |
| reach | front_pants | 0.157487 | 0.052619 | 100 → 9 |
| reach | shoulders | 0.333455 | 0.197961 | 703 → 844 |

Counts are not percentages and a lower mean can coexist with more collapsed faces. Full per-pose files are [baseline](final_baseline_244_pose_metrics.json), [refined](final_refined_244_pose_metrics.json) and [stress comparison](final_stress_comparison.json). No non-finite deformation was accepted. Reference surface equality is an independent invariant, not inferred from these scores.

## 17. Final refined skinning method

Final mesh: `/Game/MetaHumanTo3DCharacter/Phase4E/Character/Candidates/SK_Lara_Refined`.

1. Start from freshly read accepted geodesic weights and unchanged skeleton/reference/surface.
2. Reassign non-anatomical grounded root influence to pelvis.
3. Apply a smooth left/right anatomical limb gate; redistribute removed opposite-side lower-limb influence to pelvis and upper-limb influence to spine_03.
4. Keep the waistband/central crotch stable through a smooth pelvis envelope derived from pelvis/thigh span and height, fading towards each thigh.
5. Generate a separate UE direct-distance bind at stiffness 0.8, four influences; apply root exclusion/side gating to it.
6. Blend that field only near shoulders/upper shirt using smooth spatial fades; retain pelvis-refined baseline elsewhere.
7. Prune to five maximum influences, normalise, commit with SkinWeightModifier, save and read back.
8. Reject finger refinement controls; retain the selected body's existing finger field.

Saved final mesh has 20,172 five-influence, 3,660 four-influence, 3,763 three-influence and 594 two-influence vertices. No unweighted vertices; maximum normalisation error 0.00000004843. Geometry/topology/UV/reference equality is exact on fresh UE readback. [Publication](candidate_asset_publication.json), [fresh audit](final_dependency_closure.json).

Implementation: `Working/Phase4E/model.py`, `refine_hybrid.py`, `ue_publish.py`; actual final weights: `Working/Phase4E/saved_Refined_weights.json`. Contact-corrected clips are under `Character/SurfaceContactAnimations`; native unchanged-motion copies under `Character/NativeAnimations`. RootOnly/Semantic meshes remain diagnostic controls. Older `Character/Animations` duplicates and the authoring retargeter are not final runtime seeds.

## 18. Remaining required human intervention

A small Skin Review could ask the user to accept/reject flagged shoulder/hand regions, identify an ambiguous garment/accessory shell or choose a bounded torso-versus-limb stiffness preset. These are proposed interventions; this phase did not implement UI or demonstrate that these choices suffice.

No claim is made that hundreds of painted vertices are necessary. Equally, acceptable armpit/finger quality has not yet been delivered automatically. Human visual acceptance of shoulder compression, wrist/finger flexion and task-based thumb opposition remains required before calling Lara production-ready. A reviewer cannot fix unproven quality merely by dismissing a numerical flag.

## 19. Native animation playback

The baseline/refined Blueprint ran all five destination-native clips in SIE: 120 sampled component frames, 53 bone positions each and no foreign skeletal mesh actor. Final contact idle/walk/run clips additionally ran for 72 sampled component frames. [Original-motion playback](source_independent_playback.json), [contact playback](contact_native_playback.json). Actual native screenshots demonstrate rendering and stress poses as well.

Phase4E animation copies were rebuilt on the identical Phase4E skeleton from evaluated source keys at 30 Hz. Raw-track byte-copy API attempts returned empty track data and were abandoned without saving partial tracks. The failed [raw-copy experiment](exact_animation_preservation.json) is not an acceptance result. Fresh comparison at 121 times per clip measures:

| Clip | Maximum component position difference cm | Maximum rotation difference degrees |
| --- | ---: | ---: |
| MM_Idle | 0.00010001 | 0.000103 |
| MF_Walk_Fwd | 0.00005333 | 0.000117 |
| MM_Run_Fwd | 0.00006854 | 0.000124 |
| JumpingJacks | 0.00007758 | 0.015849 |
| MannyFingerIdentity | 0.00005311 | 0.000090 |

Durations match. These small evaluated differences support preserving the original motion for comparison; they do not establish byte-identical raw tracks. The largest rotation difference is 0.01585° in reach. `MannyFingerIdentity` is the retained name of a **Lara-native** fixture, not a Manny runtime asset. Contact animations deliberately differ in leg rotations. Native playback passed; standalone/cooked performance is not tested.

## 20. Dependency closure

Fresh commandlet reload and recursive hard/soft package closure pass. Seeds include comparison map/Blueprint, baseline/final meshes, skeleton, five native clips, three surface-contact clips and seven stress clips. Closure contains **22 /Game packages and 16 normal /Engine or /Script packages**. Zero foreign /Game, prior-phase, Manny/MetaHuman, authoring-rig or helper-plugin dependencies occur. [Edges, seeds and fresh readback](final_dependency_closure.json).

A stale cached material texture reference to Phase4D was found and removed by recompiling/saving only the Phase4E material. Fresh audit verifies closure after that repair. [Cleanup](material_dependency_cleanup.json). Retargeter copies retain authoring inputs deliberately, outside runtime seeds. No clean-project migration or cooked executable was performed; package closure is not a substitute for those tests.

## 21. Product implications

**Can Assisted Rigging produce acceptable deformation for a clothed unrigged humanoid without conventional full manual weight painting?** Promising for Lara's body/pants, **not yet established end-to-end**. All acceptance criteria are not passed, and one character cannot establish arbitrary clothing compatibility.

**Can the observed shoulder and front-pants/crotch defects be repaired programmatically with reusable methods?** Pants: material repair demonstrated. Shoulders: material improvement demonstrated, full repair incomplete. The algorithm structure is reusable; its parameter choices/clothing interpretation are not validated across characters.

**Is remaining risk low enough to build the actual plugin/native Assisted Rigging UI?** **No for polished productisation.** A bounded engineering prototype for quality testing could be justified as research, but this phase does not authorise or implement it. Unresolved finger support, thumb motion, shoulder compression and clothing generalisation remain material risks.

| Area | Confidence | Scope of conclusion |
| --- | --- | --- |
| Semantic Assisted Rigging | 🟢 **High confidence** | Accepted Lara anatomy/identity preserved; no refit needed for these repairs |
| Automatic/refined skinning | 🟠 **Medium confidence** | Measured/material body improvements; shoulder worst-case regression and one-character evidence |
| Clothing | 🟠 **Medium confidence** | Lara pants improved; no reliable general garment classifier/donor strategy |
| Feet/contact | 🟢 **High confidence** for measured flat-floor result; 🟠 **Medium confidence** for general use | Dense/native authoring verification; planting/terrain/stride untested |
| Fingers | 🟠 **Medium confidence** for identity/support diagnosis; 🔴 **Low confidence** for natural thumb quality | Semantic success retained; support repair rejected and natural motion unaccepted |
| Overall Mode A viability | 🟠 **Medium confidence** | Still plausible; product go remains withheld |

There is insufficient evidence to conclude the product fundamentally requires traditional manual rigging/painting. There is also insufficient evidence to claim that risk has been eliminated. Continuing an unlimited Lara tuning exercise would not answer the general product question.

## 22. Recommended next phase

Phase 4F should be a bounded **quality acceptance/generalisation gate**, keeping semantic architecture intact. First reproduce the flagged reach shoulder compression and hand support with a task-based thumb/grasp fixture, explicit proximal palm support definition and native reviewer acceptance. Test volume/collision locally where appropriate; do not redefine a failing screen just to pass it.

Then run the same dimensionless refinement rules on at least two materially different clothed unrigged humanoids, including separable garments and merged surfaces. For a genuine separate garment, evaluate UE weight transfer/inpainting from an established body donor. Record whether limited shell selection/stiffness presets suffice, time required and unsolved regions. Add foot-plant/sliding and clean-project/cooked playback checks.

Set a finite candidate/iteration budget and an explicit stop/go gate: materially acceptable primary regions, supported fingers/thumb task, preserved references, source-free runtime and limited review without conventional full painting. If those fail across representative inputs, revise Mode A scope or stop productisation. Do not reopen landmark fitting or build a polished UI to conceal unresolved deformation quality.

## 23. Protected-file audit

Final hash audit passes: **3,209 protected files; zero changed, zero missing, zero unexpected authored files outside Phase4E**. This includes prior Content assets, prior reports/evidence, human correction ledger, original ZIP and project configuration. [Before inventory](protected_before.json), [final audit](protected_file_audit.json).

Coverage includes Characters, Config, Content, Reference, Documentation, Working and the uproject, excluding Phase4E and execution/cache directories (Intermediate, Saved, DerivedDataCache, DDC, __pycache__). Engine source and external reference projects were read-only and never authored; the workspace inventory is not a hash audit of those external trees. No commit, push, branch/config change, fit rerun or prior asset save occurred.

Final self-review checked fresh disk invariants, package closure, actual saved weights, rejection evidence, sampling-density/interpolation caveats, metric regressions and report claims. Phase 4E investigation/deliverables are complete; overall deformation/product acceptance is explicitly incomplete.
