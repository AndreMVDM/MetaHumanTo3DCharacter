🟠 **Medium confidence**

# Phase 4D — Guided Landmark Correction and MetaHuman Refinement

1 October 2026, Australia/Sydney. UE 5.8.3 / 58210709. Level 1 single-agent execution and self-review. This is a correction-tool investigation paused at genuine human anatomical judgement.

## 1. Executive summary

The correction scene and data pipeline are prepared; **practical assisted Mode A is not established**. The immutable Phase4C donor proposal is reused at 180 cm without another solve. The prototype offers native UE transform gizmos, semantic body selection, optional paired mirroring, explicit recorded placements, grouped anatomical review, and independent digit correspondence for both hands.

Real trial status: **awaiting_human_review**. Actual recorded human commands: **0**; actually moved landmarks: **0**. These are performed counts, not required effort. Required corrections and authoring time remain unknown. Current anatomy gate: **106 checks, 38 failures; downstream_authorised=False**.

## 2. Prior evidence recap

All eight requested reports were indexed/read for relevant findings, with Phase4B/4C JSON evidence inspected and hash-indexed in [existing_evidence_index.json](existing_evidence_index.json). Earlier retargeting proves destination-native animation for suitable rigs. Phase3B establishes coordinated physical-height authoring, unit transforms, explicit root/pelvis policy, matched endpoints/goals and native bake/playback. Phase4A's authored control demonstrates downstream feasibility, with deformation/contact limitations. It is evaluation evidence only.

Phase4B produced 23 body roles, six provisional candidates, 17 ambiguous roles and zero accepted named finger chains. Phase4C actually solved/exported posed DNA, exposed 342 joints and deterministically inverted the target transform; 19/23 body roles required review and 0/10 finger chains passed. Its 22-failure rejection, lack of downstream authorisation, and experimental-assisted classification remain intact. No prior result is overwritten.

## 3. Automatic starting proposal

[automatic_starting_proposal.json](automatic_starting_proposal.json) is byte-identical to Phase4C automatic_fit_v2.json (SHA-256 0324a9f4796865ff9ac350c7d8b03136d6ff54bbe4b532dce4b8af71325572fe). It is selected for explicit donor semantics and reproducibility, not because 4C outscored 4B anatomically. Target geometry arrays are byte-identical copied Phase4C arrays; 4B geometry tracks are secondary evidence. Neither 4A body nor finger coordinates initialise correction positions.

The physical profile is 180 cm; source frame stature is 99.748171 cm, uniform factor 1.8045443647800623. Canonical +X left / +Y forward / +Z up is left-handed; the source basis determinant -1 is never directly treated as a quaternion. Current data are independent of the temporary donor asset, but the prototype uses the retained extraction JSON as authoring provenance.

## 4. Correction-control design

There are 13 primary body candidates: pelvis; two shoulders, elbows, wrists, knees, ankles and balls. Six optional/advanced controls cover neck/head, hips and clavicle roots. This is a candidate set, **not 13 required corrections**. Root and spines are generated/provisional display points, not primary manual controls. [Control design](correction_control_design.json).

One pelvis edit can update five dependent points; shoulder edits can propagate to clavicles. Paired mirroring is opt-in and records one grouped command plus the affected landmark moves. It does not impose symmetry on Lara silently.

## 5. User interaction model

UE map: /Game/MetaHumanTo3DCharacter/Phase4D/Maps/L_GuidedCorrection. Open the accompanying Phase4D correction panel. Green means automatic provisional, amber unresolved, blue recorded movement, cyan reviewed without movement, purple procedural dependency. Selection uses real native UE actor gizmos. Front/side and body/hand view buttons reduce navigation. The primary trial does not require JSON editing or manual intermediate-bone placement.

Drag a selected control, observe live dependent preview, then **Record placement**. Preview is not recorded movement or approval. Review a point/group only after visually inspecting its final positions. Movement never accepts anatomy. Review records include the category, positions, proposal hash and immutable event evidence. Any subsequent dependent position change invalidates that approval. Use one intended placement then Record; exploratory/unrecorded mouse gestures are outside the operation metric.

The panel communicates through atomic local Phase4D command files, with session binding and processed-command retention. It needs no network, new engine plugin or project configuration change. The default Python installation lacked usable Tcl scripts; matching existing bundled Python/Tcl resources are used with a Phase4D-local Tcl/Tk copy. Launching from UE puts the panel on the editor's interactive desktop. This is a temporary external panel, not a final integrated UI.

The panel process/window was observed through native window inventory; [panel_layout_validation.json](panel_layout_validation.json) confirms that all controls construct and fit the requested window. Native capture/activation of this Tk window failed even after refreshed selection, reporting that the window no longer belonged to its listed app (both printed app identifiers were identical). Consequently its actual desktop appearance and real button-click path are not independently screenshot-verified. The UE viewport and handler mechanics were verified; this limitation remains explicit for the human trial. The already open panel uses the initial Start label; the saved updated panel uses Start / resume. A resumed measured trial retains the original start time and includes pauses between sessions.

## 6. Real correction trial status

**Awaiting actual user anatomical judgement.** Autonomous execution performed mechanics/preview tests only, explicitly labelled synthetic. It did not identify real digit identities, accept anatomical locations, or move points as hidden anatomical corrections. The real session has no fabricated review. The editor scene is prepared for the user. A real beginner usability trial has not occurred.

## 7. Actual correction list

[actual_correction_list.json](actual_correction_list.json) records immutable events. At this boundary it contains 0 events. Automatically accepted: root and three spines, provisionally under the inherited score policy. Reviewed without movement: 0. Actually moved: 0. Unresolved: 19 body roles and 10 finger chains. Role-review counts and user edit counts remain separate.

## 8. Correction propagation rules

[correction_propagation.json](correction_propagation.json) records the rules. Replay starts from the immutable proposal. Pelvis translates donor hip offsets and blends lower-spine positions; explicit hip overrides take precedence. Shoulder correction uses the inherited .48 clavicle propagation factor; this is a prototype coupling, not inferred anatomical proof. Elbow/wrist and hip/knee/ankle anchors define new aims and bend planes. Feet retain independently proposed ball anchors and recompute the ankle-to-ball direction. All proper axes and parent-frame local transforms are rebuilt.

Finger roots/tips warp an actual target track with an arc-length endpoint blend. Donor segment-length proportions generate intermediate points along that target path. A partial track remains explicitly uncertain. Directly placing all donor phalanges onto Lara is avoided.

## 9. Pelvis/torso result

The original pelvis and three spine candidates remain unchanged until real input. Five-point propagation works in synthetic and UE preview tests. Generated spines lose prior acceptance if moved; review of the final pelvis/hips/spine group is required. Internal pelvis/hip locations are not certified by clothed contours. Head/neck remain unresolved, with dedicated optional controls.

## 10. Arm result

Shoulder, elbow and wrist controls expose intuitive articulation roles; segment axes and pole plane are recomputed. No shoulder/elbow/wrist correction is anatomically accepted. The donor wrist displacement toward digit regions remains a correspondence hypothesis for review.

The inherited right clavicle side-sign failure persists because its root lies at +0.069 cm X. A central clavicle root is convention-sensitive; that sign does not prove a crossed right arm. Classify it as pivot convention if appropriate and keep unresolved where the numeric gate disagrees. **Do not move it merely to match 4A or clear a check.** The strict inherited criterion is retained.

## 11. Leg result

Hip/knee/ankle positions and knee pole directions remain unresolved. Pelvis-driven hips can be reviewed as a group first; expose optional hip correction only if the translated donor offsets are unsuitable. No hidden hip estimate from 4A is inserted. Descending heights, side signs, finite nonzero lengths, target envelopes and bend degeneracy remain checked.

## 12. Foot result

Ankle and ball/toe landmarks determine forward foot aim. Current numerical forward/ordering screens do not establish concealed ankle/metatarsal articulation or production floor contact. No foot correction, skinning or animated contact is accepted. Geometry/boot ambiguity can be retained instead of guessed.

## 13. Finger correspondence result

Both hands independently expose five actual 4B surface tracks. Use the panel to highlight a numbered track, choose its digit identity, then identify it. Duplicate use of one track for two digits is rejected. Root/tip controls and three procedural phalanges appear after assignment. Review each generated chain against its digit in front/side, including the palm attachment.

Hand buttons use close views across the X axis so the five tracks separate in the Y/Z plane. The initial general front-facing hand framing overlapped several tracks and was corrected during visual self-review. Highlighting selects the chosen track's six segments in UE; actual identity remains the user's decision. The [visual evidence manifest](visual_evidence.json) distinguishes UE captures from orthographic source-data projections.

No real identities are assigned yet. Synthetic tests generate ten separate chains and 30 phalanges from arbitrary test labels; **those labels are not anatomical evidence**. Initial section-track roots/tips are automatic previews, not human edits. The tracks are partial and may need extension toward palm/fingertip; acceptance is not presumed. Whether five identities per hand plus optional root/tip adjustments are sufficient remains unproven.

## 14. Anatomical validation

[anatomical_validation.json](anatomical_validation.json) includes every pass/fail and measured threshold. The 61 inherited body checks are retained, including strict side signs, hierarchy, grounding, stature, sections, limb ordering and unresolved roles. The review adapter now allows explicit position-bound review of unchanged ambiguous points; this enables reviewed-without-movement without relaxing numerical checks. No movement requirement substitutes for judgement.

Additional checks cover proper orthonormal axes, nondegenerate poles and explicit elbow/knee direction review; five unique digit identities per hand; chain review; side, surface support, segment lengths and sampled path collision screens. Current failures preserve unresolved anatomy and right clavicle sign disagreement. Bounding envelopes and nearest-vertex finger checks are coarse numerical screens; human judgement remains necessary. They do not certify medical joint centres, signed range limits, skin deformation or continuous collision.

The two Phase4C aggregate finger requirements are retained: noncollapsed distinct target paths with every collision screen passing, and 10/10 independently accepted semantic chains. Neither passes by absence of finger assignments.

## 15. Correction-count/time/distance metrics

[correction_metrics.json](correction_metrics.json): recorded human commands 0; placement commands 0; digit-identification commands 0; reviewed landmarks 0; moved landmarks 0; total/maximum recorded movement 0.000/0.000 cm. Timing is null until a real Start/Finish interval exists and includes pauses. Authoring time is not inferred.

The tool measures explicit panel operations and recorded placements; navigation commands are counted separately from corrections. Raw OS clicks and individual exploratory gizmo gestures are not instrumented and remain null. This limitation prevents an unjustified claim of exhaustive physical-interaction measurement. Product targets of roughly 10–12 body corrections and semantic hand matching are evaluation goals, never pass criteria.

## 16. Comparison with Phase4B

Current baseline mean difference from 4B is 5.297 cm. 4B retains its six provisional/17 unresolved body-role result; its geometry is used to visualise digit tracks and support gate sections. Review counts do not rank methods or predict actual correction effort.

## 17. Comparison with Phase4C

Current body positions differ by 0.000000 cm maximum from Phase4C: the original baseline is deliberately unchanged. This phase adds an actual correction interface, per-operation ledger, root/tip track generation and review-aware replay. It does not yet demonstrate a better anatomical outcome, fewer real corrections, or successful downstream conversion.

## 18. Comparison with Phase4A control

Post-proposal evaluation gives mean/max difference 5.243/12.524 cm. [phase_comparisons.json](phase_comparisons.json) records every role. Control coordinates are read only by final comparison, not core.py or ue_tool.py. 4A pivots are approximate and convention-sensitive, not anatomical ground truth or prescribed correction targets.

## 19. Lara skeleton construction

Not run: anatomy rejected and real review pending. There is no Phase4D Skeleton or Skeletal Mesh. Current generated joints/local transforms are proposal data and static markers only. A future accepted proposal must construct a fresh 4D Lara hierarchy, validate axes/rest pose/180 cm and preserve source appearance; donor runtime assets are excluded.

## 20. Skinning/deformation results

Not run. Unweighted vertices, influence count, normalisation and sensitive-region deformation are null/unmeasured. After acceptance, reuse 4A's UE geodesic/smooth binding (voxel 128, stiffness .2, maximum five influences) and record any required weight edits. Earlier skin feasibility is not this phase's result.

## 21. IK/retarget results

Not run. Later use the established Manny source rig and fresh target rig; inspect characterisation, explicit body/digit chains, matched hand/ball goals, one intended FBIK solver, regenerated pose and independent grounded root/pelvis policy. No inherited scale workaround or unchecked auto-characterisation is accepted.

## 22. Baked animation results

Not run. Idle, walk, run and upper-body/arm motion remain required. No destination-native 4D Animation Sequence exists. No success is inferred from marker appearance or script tests.

## 23. Manny-removed playback

Not run; no accepted baked character exists. Earlier source-free playback proofs remain earlier-phase evidence.

## 24. Final dependency closure

No runtime package exists. Static debug assets are entirely in 4D, with existing Engine primitives. Duplicated texture/material references are repointed within 4D. The tool consumes prior extraction/track files as read-only authoring evidence. Runtime asset closure and no-Manny/no-MetaHuman/no-fitting playback must be measured only after real acceptance, skinning and baking.

## 25. Beginner-workflow assessment

The interaction concept is plausible: intuitive point names, native gizmos, fixed views, optional groups/mirroring and digit matching avoid exposing every intermediate bone. It remains a two-window technical prototype and requires explicit Record/review actions. Internal clothed articulations, pivot conventions, partial tracks and front/side depth judgement may still demand substantial expertise. A beginner trial and the 10–12-edit target have not been measured. Do not build the final Authoring Master UI yet.

## 26. Mode A classification and final decisions

Body: **experimental assisted**. Fingers: **experimental assisted, correspondence trial pending**. Overall: **experimental assisted**. No reliable small correction set has produced an accepted Lara rig here.

Can Lara pass with a small intuitive set? **Unknown until real correction input and the same gate pass.** How many actual interactions are required? **Unknown; zero performed so far is not zero required.** Can semantic digit identification/root-tip replace manual phalanges? **Mechanically supported by the prototype, anatomically unproven.** Is Mode A practical assisted? **No evidence yet; retain experimental assisted.** Lara-only mechanics do not establish arbitrary humanoid support.

## 27. Recommended next step and exact user trial

1. In the open panel click **Start measured trial**. Keep UE out of Play mode and disable viewport translation snapping for small placements.
2. Begin with pelvis. Select **Pelvis centre → Select in UE**. Inspect pelvis view/front/side. If needed, drag its gizmo and click **Record placement**; inspect generated hips/lower spine. Choose the pelvis/hips/lower-spine group and accept only if every listed point is appropriate; otherwise keep unresolved and use optional hips as needed.
3. Review left/right shoulder pivots, elbows, wrists, knees, ankles and balls in front/side. Move only genuinely misplaced points, Record each placement, then accept or keep unresolved. Mirroring is optional, requires inspection of both sides, and is recorded as a group. Review shoulder/clavicle groups and neck/head separately; do not reposition convention-sensitive pivots merely because of 4A differences.
4. Choose **left hand** view. For each numbered track, use **Highlight selected track**, choose the actual digit and **Identify track**. Select root/tip only where the initial track extent is wrong; reposition with the gizmo and Record. Accept a digit chain only after its identity, root/tip and generated intermediate positions follow the correct finger. Repeat independently for the right hand. Leave ambiguity unresolved rather than assigning a guessed digit.
5. Click **Save trial**, then **Finish measured trial**. Tell the agent the real inputs are ready. No JSON editing is required.

No minimum number of moves can honestly be prescribed in advance. The minimum initial action is genuine review; acceptance without movement is supported. Review groups reduce approval operations without treating uninspected points as approved.

To reopen on this machine, run Working/Phase4D/ue_tool.py in the local UE Python console, then Working/Phase4D/ue_launch_panel.py in that same console. LaunchPanel.ps1 is an alternative when running on an interactive desktop. After real input, rerun only Phase4D validation/report generation:

    python -X utf8 Working/Phase4D/finalise.py
    python -X utf8 Working/Phase4D/render_evidence.py

Do not rebuild/reset the session or alter gate criteria to force acceptance. This refresh does not build a rig; continue through conditional downstream construction only when anatomy genuinely passes.

## 28. Protected-file audit and verification

[protected_file_audit.json](protected_file_audit.json): 2515 prior authored files, 0 changed, 0 missing, 0 unexpected new authored files outside Phase4D. Original archive/source entries remain byte-identical. Normal UE Saved/Intermediate/DDC and build outputs are excluded explicitly. Engine/reference projects were not write targets; no exhaustive external-engine hash baseline exists.

Mechanics validation: 29 synthetic checks passed=True, including immutability, dependency invalidation, explicit override priority, unknown/stale/nonfinite/zero-segment rejection, digit uniqueness, root-tip propagation, synthetic metrics exclusion and 53-joint local-transform reconstruction. UE mechanics passed=True; its evidence separately labels preview/selection tests, with no human approvals. [ue_scene.json](ue_scene.json) records observed height/triangles/UV sets and zero skeletal assets. Visuals use real source arrays and UE viewport captures; post-correction/accepted skeleton/skinned/animation evidence remains pending.

[source_surface_preservation.json](source_surface_preservation.json) verifies exact ordered triangle topology and per-corner position/UV hashes against the prior normalised mesh: 49,508 triangles, one UV set and 180 cm. Original texture/material source bytes remain protected; only duplicated Phase4D material references are repointed. The earlier UE callback reload defect was corrected by removing its obsolete Phase4D callback; subsequent preview/status and source readback succeeded. A redundant sandbox-desktop helper was stopped; the visible editor-desktop panel is retained.

Self-review corrected metric/provenance distinctions, added unchanged-position review support and approval invalidation, ensured local transform reconstruction, and retained the right-clavicle failure. Working state: no Git repository; no commit or push. This is ready at the human-review boundary, not a completed accepted-rig claim.

A short-lived Windows reader lock was observed during heartbeat replacement. Atomic publication now uses unique temporary files and bounded retry; a regression check reproduces two denied replacements before successful publication. Permanent failures still surface as explicit errors. The final ready status and real trial ledger are verified separately.

![Automatic proposal](pre_correction_front.png)

![Target left-hand tracks](left_hand_tracks.png)


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

The sole move was neck_01 from [0.7336481809616089, -9.163066864013672, 150.45700073242188] cm to [0.7336483209043365, -0.7638249224990512, 150.02043073097894] cm. Delta XYZ=[1.3994272762829496e-07, 8.399241941514621, -0.4365700014429308] cm; Euclidean distance **8.410580156 cm**, predominantly +Y forward, with a −0.437 cm vertical change. All other body positions and finger endpoints remained accepted without movement. Generated axes/local transforms were recomputed; this is not additional human landmark movement.

The ledger contains **159** real panel commands: {'start': 1, 'select': 28, 'view': 46, 'review': 34, 'move': 1, 'assign': 13, 'preview_track': 34, 'save': 1, 'finish': 1}. The user's observed 157 commands precede the preserved Save event 158 and Finish event 159. There are 13 digit-assignment commands, including reassignment, yielding ten final identities; 34 review commands yield 32 distinct current approvals; 108 commands are navigation/selection/track-preview. These are command counts, not raw mouse gestures. Elapsed Start-to-Finish time is **12179.218627 seconds (3 h 22 min 59.219 s)**, including pauses; active authoring time and novice usability were not measured. One placement does not imply one-click completion.

| Track | Left hand | Right hand |
| --- | --- | --- |
| 1 | Index | Middle |
| 2 | Middle | Index |
| 3 | Ring | Ring |
| 4 | Pinky | Pinky |
| 5 | Thumb | Thumb |

Three phalange pivots per accepted track were sampled procedurally from retained donor length proportions along the actual Lara target path. The donor JSON is authoring provenance; the donor is not the final skeleton or a runtime dependency. No hidden Phase4A manual coordinate was used. Evidence: [metrics](correction_metrics.json), [human reviews](human_review.json), [actual events](actual_correction_list.json), [ledger preservation](human_ledger_preservation.json).

### 29.2 Gate failures, diagnoses and legitimate corrections

The initial refresh produced 186 checks, 183 passes and three failures. Each was investigated before downstream work:

| Initial failure | Classification | Evidence and minimal correction |
| --- | --- | --- |
| left_right_not_crossed | Pivot/skeleton convention mismatch | Thoracic parent X=0.690281570 cm; right clavicle global X=+0.067035258 cm but relative X=−0.623246312 cm; left relative X=+0.763563216 cm. Clavicle roots are judged relative to their thoracic parent. All other limb articulations retain strict global left-positive/right-negative signs. |
| finger_review_thumb_l | Correction replay/propagation bug causing provenance invalidation | UE Python 3.11 and offline Python 3.14 generated a third-thumb Y difference of 1.7763568394002505e−15 cm. Exact hash matching discarded a real human approval. The original in-editor state was recovered and independently matched to all 159 event files. |
| finger_chains_anatomically_resolved | Same replay bug, aggregate consequence | The lost thumb approval reduced the complete set. No extra anatomical review was invented. |

Replay now retains the exact reviewed finger coordinates only when the review signature is current, all other regenerated fields match, and recomputation differs by at most 1e−10 cm. This guard handles arithmetic replay; the human review hash remains exact. Real endpoint, track or dependent body changes still invalidate approval. Generated local transform replay differs only at floating-point round-off and is measured separately. [Thirteen regression checks](finalisation_regression.json) pass, including wrong-side clavicle and crossed-wrist rejection. No numerical anatomy thresholds were relaxed, checks removed, or failures renamed. The clavicle reference origin change is explicit in gate_policy_correction.

Final result: **186 checks, 186 passes, 0 failures, downstream_authorised=true**. Structural/geometric checks pass; automatic_anatomical_passed=false because this is human-assisted acceptance. There is no remaining numerical convention disagreement under the documented clavicle convention. Numerical envelope/path screens and human judgement still do not certify internal anatomy or animated deformation. [Full gate](anatomical_validation.json).

### 29.3 Fresh skeleton and original-surface UE skinning

Created /Game/MetaHumanTo3DCharacter/Phase4D/Character/SKEL_Lara and SK_Lara, with intermediate SK_Lara_Authoring. The connected hierarchy has 53 bones: grounded root, pelvis, three spines, neck/head, two clavicles, arms/hands, legs/feet/balls, and 30 finger phalanges. All parents, accepted component pivots, local transforms and proper axes were checked. Maximum component position construction error is 5.79733460242e-07 cm; maximum axis error is 1.44822257924e-08; all reference scales are unit. Skeleton/skin/gate evidence share final proposal SHA256 083ec2ea0c8ec4b7666dfb43a53a066d14d2d008186f6f2f062bb63e132fb49e.

Binding used UE GeometryScript **GEODESIC_VOXEL, voxel resolution 128, stiffness 0.2, max five influences**. There are 28,189 vertices, 49,508 triangles, exactly five positive influences per vertex, zero invalid/unweighted vertices and normalised weights. Fresh disk reload verifies identical ordered vertices/triangles and per-corner UV hash, original 180.0 cm physical geometry and original Phase4D material/texture. Saved and pre-save weight maps have maximum numerical delta 0.0; a raw Python list/tuple representation mismatch is not a weight alteration. No weight-paint edits were made.

Native reference-pose appearance was inspected beside the source static mesh. Live component/reference position maximum error is 1.36166760688e-13 cm. The Phase4D material's SkeletalMesh usage flag was persisted after UE auto-enabled it; texture/shader graph remained intact. [Skeleton](skeleton_construction.json), [binding](skinning_results.json), [material usage](material_usage_correction.json), [native reference capture](native_visual_capture.json).

![Original static source, left; final skeletal reference pose, right](native_reference_pose.png)

### 29.4 IK, Manny mapping and baked clips

Fresh assets are /Game/MetaHumanTo3DCharacter/Phase4D/Character/IK_Lara and RTG_Manny_Lara. UE automatic characterisation and automatic FBIK succeeded, then the actual result was inspected. One enabled FBIK solver starts at pelvis, with 20 iterations, 10 subiterations and allow_stretch=false. Retarget root is pelvis; root-motion bone is root. Hand goals terminate at hand_l/r and foot goals at ball_l/r, with actual solver goal bindings checked. The automatically generated target legs ended at foot; both were extended to ball and their goals matched. An explicit Root chain and LeftFoot/RightFoot ball chains complete the setup.

The original /Game/Characters/Mannequins/Rigs/IK_Mannequin remains unchanged. A fresh Phase4D/Authoring/IK_MannySource copy adds two explicit ball chains; its existing leg chains already ended at ball. All **22 essential mappings** pass exactly: Root, Spine, Neck, Head, left/right Clavicle, Arm, Leg, Foot and ten named fingers, each mapped to the same semantic source chain. Target retarget pose was reset and aligned with UE auto_align_all_bones. Root Motion, Speed Planting and Stride Warping operations were removed for the diagnostic in-place bake; no Copy Pose or live donor runtime is used. This choice does not solve world-space locomotion/contact.

| Role | Exact destination-native asset | Duration s | Evaluated poses |
| --- | --- | ---: | ---: |
| idle | /Game/MetaHumanTo3DCharacter/Phase4D/Character/Animations/MM_Idle.MM_Idle | 7.566667 | 61 |
| walk | /Game/MetaHumanTo3DCharacter/Phase4D/Character/Animations/MF_Walk_Fwd.MF_Walk_Fwd | 1.866667 | 61 |
| run | /Game/MetaHumanTo3DCharacter/Phase4D/Character/Animations/MM_Run_Fwd.MM_Run_Fwd | 1.900000 | 61 |
| reach | /Game/MetaHumanTo3DCharacter/Phase4D/Character/Animations/JumpingJacks.JumpingJacks | 9.466666 | 61 |

All four clips reference SKEL_Lara. All 244 sampled poses are finite with unit bone scales; grounded root displacement is zero. Actual live pose variation was observed for every clip, not inferred from asset creation. Pelvis ranges, limb lengths and bend magnitudes are retained in [native motion summary](native_motion_summary.json); positive segment lengths and finite transforms do not prove every anatomical bend sign. [IK/mapping/goal evidence](ik_retarget_results.json), [batch bake](animation_bake_results.json).

### 29.5 Deformation and foot/contact evaluation

CPU linear-blend deformation uses the actual UE binding weights and all 244 evaluated baked poses. Original nondegenerate triangle area below 10% or above 5× is a **diagnostic flag**, not a new anatomy gate or an automatic quality verdict. Per-region screens cover points within 5 cm of the listed pivots. Native material captures and front/side CPU projections were inspected for shoulders, elbows, wrists, pelvis/hips, knees, ankles, fingers and clothing transitions. Reference surface is retained; animated shoulder/shirt transitions show thinning/jagged distortion, wrists/fingers carry local flags, and boots penetrate the plane. No gross digit identity swap or reversed limb is evident in the representative views; exhaustive continuous collision/bend-sign acceptance is not claimed.

| Clip | Max collapsed triangles | Max stretched triangles | Left minimum-sole Z range cm | Right minimum-sole Z range cm |
| --- | ---: | ---: | --- | --- |
| idle | 14 | 7 | -1.551 to -1.335 | -2.597 to -2.401 |
| walk | 18 | 23 | -4.520 to 5.269 | -4.371 to 6.078 |
| run | 39 | 128 | -3.136 to 46.687 | -3.109 to 39.128 |
| reach | 44 | 258 | -4.032 to 16.334 | -3.772 to 18.674 |

These maxima can occur at different samples. Run/reach flags affect a small portion of the 49,508-triangle surface; the count alone does not quantify visual severity. Native shoulder/clothing shape and stance penetration independently prevent quality acceptance. Root stays at Z=0; all bone scale errors are zero. Positive sole height during running/jumping can be intended airborne motion and is not automatically called hover.

| Region | Max collapsed, any clip | Max stretched, any clip |
| --- | ---: | ---: |
| shoulders | 0 | 0 |
| elbows | 0 | 0 |
| wrists | 5 | 6 |
| pelvis_hips | 0 | 0 |
| knees | 1 | 0 |
| ankles | 1 | 0 |
| fingers | 12 | 12 |

Heel/rear-sole and toe/front-sole minima, ankle and ball positions, ankle-to-ball pitch and original-surface trajectories are recorded at every sample. Heel/toe groups use the rear/front 20% of the original sole Y coordinates; they are geometric proxies. The maximum measured stance-surface penetration is **4.520 cm** in walk; idle right sole stays approximately 2.40–2.60 cm below ground. Foot-contact quality is not accepted.

| Clip | Side | Near-ground intervals | Max apparent slide cm/s | Ankle-to-ball pitch range deg |
| --- | --- | ---: | --- | --- |
| idle | l | 60 | 0.282 | -27.81 to -27.47 |
| idle | r | 0 | no qualifying intervals | -26.91 to -26.50 |
| walk | l | 15 | 545.255 | -87.96 to 3.57 |
| walk | r | 20 | 487.136 | -86.65 to 1.19 |
| run | l | 3 | 503.595 | -88.73 to -11.51 |
| run | r | 1 | 412.945 | -87.55 to 2.26 |
| reach | l | 16 | 115.026 | -52.09 to -25.75 |
| reach | r | 3 | 1.059 | -56.09 to -21.25 |

Near-ground means both sampled minimum-sole heights lie within ±2 cm. Apparent sliding is measured in component space on a stationary in-place actor, with no world locomotion and no authoritative planted-contact labels. The high walking/running values are not a complete planted-foot controller assessment. Near −89° toe pitch can occur on lifted feet; these angles need phase-aware interpretation. Penetration is directly measured. Speed Planting/world movement/contact refinement and shoulder/finger skinning remain future quality work, with no hidden fixes in this trial. [Per-sample contact/deformation](deformation_contact_results.json), [visual review](deformation_visual_review.json).

![Native raised-arm shoulders and clothing, with run instance at left](native_shoulders_reach.png)

![Actual weighted animated feet and grounded reference; red line is Z=0](animated_feet_side.png)

### 29.6 All ten fingers under real animation

A new authoring-only Manny finger fixture holds the remaining skeleton at an idle baseline while rotating each of ten named three-phalange chains independently about local Z by a 45° sine peak, one digit per one-second slot. This is diagnostic animation, not a human correction or a claim of natural flexion. The same Phase4D retargeter baked /Game/MetaHumanTo3DCharacter/Phase4D/Character/Animations/MannyFingerIdentity onto SKEL_Lara. It has 22 evaluated baseline/peak/boundary poses and was also exercised during native source-free playback.

| Digit | Peak local angular change deg | Largest other digit change deg | Peak phalange nearest same-digit surface support cm | ≤1.2 cm diagnostic |
| --- | ---: | ---: | ---: | --- |
| thumb_l | 51.693 | 0.000000 | 0.644 | passes |
| index_l | 62.364 | 0.000000 | 0.656 | passes |
| middle_l | 45.998 | 0.000000 | 0.791 | passes |
| ring_l | 53.952 | 0.000000 | 0.955 | passes |
| pinky_l | 46.647 | 0.000000 | 0.435 | passes |
| thumb_r | 52.105 | 0.000000 | 0.842 | passes |
| index_r | 58.744 | 0.000000 | 0.660 | passes |
| middle_r | 46.666 | 0.000000 | 1.081 | passes |
| ring_r | 54.214 | 0.000000 | 1.252 | fails |
| pinky_r | 45.210 | 0.000000 | 0.257 | passes |

**10/10 semantic independent-motion checks pass** and all sampled 3D same-hand chain separation screens exceed 0.25 cm. Identity stays Index/Middle/Ring/Pinky/Thumb, including both thumbs; the human correspondence avoided all manual phalange placement. Surface groups use the accepted actual target tracks and original vertices, not donor geometry. Same-chain mean weight is approximately 0.71–0.86. Nine of ten peak surface-support screens pass; **right ring is 1.252 cm and fails**. The ≤1.2 cm and >0.25 cm screens are explicit diagnostics, not inherited anatomy thresholds. Sparse nearest-surface support is not full volumetric containment; projected paths can overlap while remaining separated in 3D.

Natural thumb opposition/curl, exhaustive ROM, full finger-volume containment and continuous collapse/collision-free behaviour are not proved by this fixture. Body clips also flag finger-local triangle collapse/stretch. Finger deformation is therefore not accepted, despite successful semantic correspondence and independent motion. No finger anatomical corrections or weight edits were added. [Fixture bake](finger_animation_bake.json), [all ten results](finger_animation_validation.json).

![Actual baked independent digit peaks](animated_finger_validation.png)

### 29.7 Source-free native playback and dependency closure

Saved /Game/MetaHumanTo3DCharacter/Phase4D/Character/BP_LaraNativePlayback has four Lara SkeletalMeshComponents, directly playing idle/walk/run/JumpingJacks in AnimSingleNode mode. Map: /Game/MetaHumanTo3DCharacter/Phase4D/Maps/L_LaraNativePlayback. The final scene was created with **no Manny or donor component**, satisfying the disabled/removed-source condition from the start. No source actor was briefly destroyed as a fabricated demonstration.

Actual SIE recorded **125 time samples × four components = 500 component frames** over all four clips plus the finger fixture, with all 53 component/world bone transforms captured, zero errors and zero foreign runtime skeletal meshes. All five sequences showed nonzero live pose variation. Direct native AnimSingleNodeInstance was verified. A source authoring rig remains in the project for rebaking but is absent from playback dependencies. No fitting, cloud service or inference runs during playback. The interactive saved test scene is left open with its four native clips playing.

Fresh UE commandlet reload and recursive hard/soft dependency audit pass. Runtime seeds include the map, Blueprint, final Skeleton/Skeletal Mesh and all five Lara-native sequences. Closure contains **12 /Game packages and 16 normal /Engine or /Script dependencies**. There are zero foreign /Game, MetaHuman/donor, prior-phase, live Manny, retarget authoring or helper-plugin references. The accidental Skeleton preview-mesh reference was saved; reference transforms were checked unchanged. Remaining authoring-preview packages: [].

The original material, texture and static Lara reference are intentional dependencies of the visual test map. This is a verified package closure, **not** a clean-project migration or cooked executable test. [Native playback](source_independent_playback.json), [motion observed](native_motion_summary.json), [closure edges and fresh readback](final_dependency_closure.json), [safe preview cleanup](preview_dependency_cleanup.json).

### 29.8 Product conclusion and preservation

| Scope | Classification | Measured basis |
| --- | --- | --- |
| Landmark/correspondence stage on this Lara | Practical assisted | One moved neck; 21 body + ten finger reviews accepted unchanged; generated phalanges; no manual intermediate placement. Expert review, 159 commands and elapsed time still apply. |
| Body as an animated character | Experimental assisted | Native build/bake/playback succeeds; stance penetration and shoulder/clothing quality remain unacceptable. |
| Fingers as animated/skinned digits | Experimental assisted | Ten identities and independent motions succeed; right-ring support fails a screen and natural thumb/full-range quality remains unproven. |
| Overall Mode A | Experimental assisted | Completed downstream measurements do not yet support a fully working character-quality claim. |

Can automatic Lara be converted into an anatomically accepted Manny-compatible native character using a small number of intuitive landmark corrections? **Anatomical acceptance and the mechanical native pipeline: yes, with one real neck movement plus explicit body/digit review. A fully working, acceptably deforming/contacting character: not yet demonstrated.** Auto-skin, retarget, bake and native source-free playback succeeded. The remaining blockers concern deformation/contact and finger surface quality, not missing semantic mappings or runtime Manny/MetaHuman dependency. A single expert-reviewed mesh does not establish broad automation or novice intuitiveness.

Protected audit: **2515 prior authored files, zero changed, zero missing and zero unexpected authored files outside Phase4D**. Original Lara ZIP SHA256 remains 45fa309b7b9114ff71618feac8d0951dd55596d091d4f03e2434b6cc1384f959. Phase2/3/3B/4A/4B/4C project evidence/assets, original source and project configuration remain byte-identical within that audit. All 159 human event files retain their input hashes; exact recorded body/finger positions and approvals match the recovered editor snapshot. New authored work is confined to Phase4D. No Engine-source/reference-project mutation, Git staging, commit or push was performed; an exhaustive external Engine hash baseline was not available.

The helper build used Phase4D-only native outputs after the installed UBT action runner failed; failed build/API/capture attempts remain in Working/Phase4D. Closing the warning window closed the editor, so the saved scene was reopened; an initial sandbox shader-cache failure and a command-line Python option that exits after execution were resolved for interactive reopening. Native material usage is saved and the reopened map check reports zero errors/warnings. None of these recovery steps added human events. [Protected audit](protected_file_audit.json), [ledger audit](human_ledger_preservation.json), [final classification](experiment_result.json).

Reproducible evidence refresh (does not author human reviews or rebuild assets):

    python -X utf8 Working/Phase4D/finalisation_regression.py
    python -X utf8 Working/Phase4D/finalise.py
    python -X utf8 Working/Phase4D/render_evidence.py
    python -X utf8 Working/Phase4D/complete_trial_report.py

The report writer is guarded against duplicate appendices; refresh updates only section 29 and checks that the historical prefix matches the preserved reconstruction. Current machine-readable anatomy is distinct from character_quality_accepted=false. Full build/retarget scripts, exact paths, data and logs remain Phase4D-scoped for review. Level 1 single-agent execution and mandatory self-review were used.
