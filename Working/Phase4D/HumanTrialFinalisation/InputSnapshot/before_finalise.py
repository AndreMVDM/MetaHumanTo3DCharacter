"""Refresh evidence/report after actual input; never author skeletal assets."""
import sys, json, re, hashlib
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import core
from preflight import protected
P=core.P;W=core.W;O=core.O
def finish():
    state=core.rebuild(core.read(W/'session.json'));core.export(state)
    from validate import validate
    gate=validate();metrics=core.metrics(state)
    before=core.read(O/'protected_before.json')['files'];after=protected();changed=[p for p in before if p in after and before[p]['sha256']!=after[p]['sha256']];missing=[p for p in before if p not in after];added=[p for p in after if p not in before]
    audit={'protected_file_count':len(before),'changed':changed,'missing':missing,'new_authored_files_outside_phase4d':added,'passed':not(changed or missing or added),'archive_sha256':core.file_sha(P/'Characters/Lara_UnRigged_Textured.zip'),'scope':'All prior authored project Characters/Config/Content/Reference/Documentation/Working and descriptor; execution/build caches excluded','external_engine_limit':'Engine and reference projects were not write targets; no exhaustive external engine pre-run hash baseline','git':'Directory does not resolve as a Git repository; no staging/commit/push/branch/configuration operation attempted'};core.save(O/'protected_file_audit.json',audit)
    automatic=core.read(O/'automatic_starting_proposal.json');points={r['role']:r['position_cm'] for r in state['joints']}
    comparisons=[]
    for phase,filename,key in [('Phase4B','automatic_fit_v2.json','position_cm'),('Phase4C','automatic_fit_v2.json','position_cm'),('Phase4A','../Phase4B/manual_control_comparison_v2.json','control_in_inferred_frame_cm')]:
        data=core.read(P/'Documentation'/phase/filename);rows=data['joints'];distances=[{'role':r['role'],'difference_cm':core.norm(core.sub(points[r['role']],r[key]))} for r in rows];comparisons.append({'comparison':'current Phase4D vs '+phase,'evaluation_only':True,'initialisation_used':False,'mean_difference_cm':sum(r['difference_cm'] for r in distances)/len(distances),'max_difference_cm':max(r['difference_cm'] for r in distances),'joints':distances,'limit':'4A is approximate manual control, not ground truth; 4B/4C were rejected proposals'})
    core.save(O/'phase_comparisons.json',{'comparisons':comparisons,'proposal_bytes_sha256':core.file_sha(O/'current_proposal.json'),'control_used_for_initialisation':False})
    controls={'primary_body':{n:l for n,l in core.LABELS.items() if n not in ['neck_01','head','thigh_l','thigh_r','clavicle_l','clavicle_r']},'optional_review_controls':{n:core.LABELS[n] for n in ['neck_01','head','thigh_l','thigh_r','clavicle_l','clavicle_r']},'generated_body_points':['root','spine_01','spine_02','spine_03'],'finger_model':'five target tracks per hand -> user digit identity -> optional root/tip -> three donor-proportioned samples along corrected target track','groups':core.GROUPS,'visual_states':{'green':'automatic provisional','amber':'review required','blue':'recorded manual placement','cyan':'reviewed without movement','purple':'procedural dependent/generated'},'candidate_count_limit':'13 primary body controls, 6 optional; no assertion that 13 edits or any fixed count is required','prototype':'UE StaticMeshActor gizmos plus local button panel, no polished final UI'};core.save(O/'correction_control_design.json',controls)
    core.save(O/'correction_propagation.json',{'pelvis':'retain original donor hip offsets; shift hips by delta; blend 3 spine points by .75/.5/.25; explicit hip overrides win','shoulder':'clavicle root delta .48 * shoulder delta, preserving inherited correction-framework rule; convention remains reviewed','arms_legs':'recompute segment aims, local transforms and elbow/knee bend planes from corrected shoulder/elbow/wrist and hip/knee/ankle','feet':'corrected ankle and independent ball define new aim; forward/ground/side/envelope checks retained; ball is not invented from hidden 4A coordinates','fingers':'arc-length path through actual 4B track centres; root/tip offsets blended; donor segment length ratios sample three target phalanges; no direct donor phalange projection','override':'replay all explicit placements from immutable baseline, canonical role order; independent overrides win','approval_invalidation':'any position/chain signature change requires fresh explicit review','limits':'coarse contour tracks may be partial; root/tip extension can leave actual geometry and must fail validation'})
    blocked={'status':'not_run_anatomy_gate_rejected' if not gate['passed'] else 'anatomy_passed_next_stage_pending','measured_results':None,'assets':[],'reason':'Human correction input and anatomical acceptance required first'}
    for name in ['skeleton_construction','skinning_results','ik_retarget_results','animation_bake_results','source_independent_playback','final_dependency_closure']:core.save(O/(name+'.json'),blocked)
    scene=core.read(O/'ue_scene.json') if (O/'ue_scene.json').exists() else {};checks=core.read(O/'mechanics_validation.json');uechecks=core.read(O/'ue_mechanics_validation.json') if (O/'ue_mechanics_validation.json').exists() else {'passed':False}
    report=f'''🟠 **Medium confidence**

# Phase 4D — Guided Landmark Correction and MetaHuman Refinement

1 October 2026, Australia/Sydney. UE 5.8.3 / 58210709. Level 1 single-agent execution and self-review. This is a correction-tool investigation paused at genuine human anatomical judgement.

## 1. Executive summary

The correction scene and data pipeline are prepared; **practical assisted Mode A is not established**. The immutable Phase4C donor proposal is reused at 180 cm without another solve. The prototype offers native UE transform gizmos, semantic body selection, optional paired mirroring, explicit recorded placements, grouped anatomical review, and independent digit correspondence for both hands.

Real trial status: **{metrics['trial_status']}**. Actual recorded human commands: **{metrics['recorded_user_commands']}**; actually moved landmarks: **{metrics['landmarks_actually_moved']}**. These are performed counts, not required effort. Required corrections and authoring time remain unknown. Current anatomy gate: **{len(gate['checks'])} checks, {len(gate['failed'])} failures; downstream_authorised={gate['downstream_authorised']}**.

## 2. Prior evidence recap

All eight requested reports were indexed/read for relevant findings, with Phase4B/4C JSON evidence inspected and hash-indexed in [existing_evidence_index.json](existing_evidence_index.json). Earlier retargeting proves destination-native animation for suitable rigs. Phase3B establishes coordinated physical-height authoring, unit transforms, explicit root/pelvis policy, matched endpoints/goals and native bake/playback. Phase4A's authored control demonstrates downstream feasibility, with deformation/contact limitations. It is evaluation evidence only.

Phase4B produced 23 body roles, six provisional candidates, 17 ambiguous roles and zero accepted named finger chains. Phase4C actually solved/exported posed DNA, exposed 342 joints and deterministically inverted the target transform; 19/23 body roles required review and 0/10 finger chains passed. Its 22-failure rejection, lack of downstream authorisation, and experimental-assisted classification remain intact. No prior result is overwritten.

## 3. Automatic starting proposal

[automatic_starting_proposal.json](automatic_starting_proposal.json) is byte-identical to Phase4C automatic_fit_v2.json (SHA-256 {core.file_sha(O/'automatic_starting_proposal.json')}). It is selected for explicit donor semantics and reproducibility, not because 4C outscored 4B anatomically. Target geometry arrays are byte-identical copied Phase4C arrays; 4B geometry tracks are secondary evidence. Neither 4A body nor finger coordinates initialise correction positions.

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

[actual_correction_list.json](actual_correction_list.json) records immutable events. At this boundary it contains {len(state['events'])} events. Automatically accepted: root and three spines, provisionally under the inherited score policy. Reviewed without movement: {len(metrics['reviewed_without_movement'])}. Actually moved: {metrics['landmarks_actually_moved']}. Unresolved: {len(metrics['unresolved_body_roles'])} body roles and {len(metrics['unresolved_finger_chains'])} finger chains. Role-review counts and user edit counts remain separate.

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

[correction_metrics.json](correction_metrics.json): recorded human commands {metrics['recorded_user_commands']}; placement commands {metrics['placement_commands']}; digit-identification commands {metrics['digit_identification_commands']}; reviewed landmarks {metrics['landmarks_reviewed']}; moved landmarks {metrics['landmarks_actually_moved']}; total/maximum recorded movement {metrics['total_moved_distance_cm']:.3f}/{metrics['maximum_individual_move_cm']:.3f} cm. Timing is null until a real Start/Finish interval exists and includes pauses. Authoring time is not inferred.

The tool measures explicit panel operations and recorded placements; navigation commands are counted separately from corrections. Raw OS clicks and individual exploratory gizmo gestures are not instrumented and remain null. This limitation prevents an unjustified claim of exhaustive physical-interaction measurement. Product targets of roughly 10–12 body corrections and semantic hand matching are evaluation goals, never pass criteria.

## 16. Comparison with Phase4B

Current baseline mean difference from 4B is {comparisons[0]['mean_difference_cm']:.3f} cm. 4B retains its six provisional/17 unresolved body-role result; its geometry is used to visualise digit tracks and support gate sections. Review counts do not rank methods or predict actual correction effort.

## 17. Comparison with Phase4C

Current body positions differ by {comparisons[1]['max_difference_cm']:.6f} cm maximum from Phase4C: the original baseline is deliberately unchanged. This phase adds an actual correction interface, per-operation ledger, root/tip track generation and review-aware replay. It does not yet demonstrate a better anatomical outcome, fewer real corrections, or successful downstream conversion.

## 18. Comparison with Phase4A control

Post-proposal evaluation gives mean/max difference {comparisons[2]['mean_difference_cm']:.3f}/{comparisons[2]['max_difference_cm']:.3f} cm. [phase_comparisons.json](phase_comparisons.json) records every role. Control coordinates are read only by final comparison, not core.py or ue_tool.py. 4A pivots are approximate and convention-sensitive, not anatomical ground truth or prescribed correction targets.

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

[protected_file_audit.json](protected_file_audit.json): {len(before)} prior authored files, {len(changed)} changed, {len(missing)} missing, {len(added)} unexpected new authored files outside Phase4D. Original archive/source entries remain byte-identical. Normal UE Saved/Intermediate/DDC and build outputs are excluded explicitly. Engine/reference projects were not write targets; no exhaustive external-engine hash baseline exists.

Mechanics validation: {len(checks['tests'])} synthetic checks passed={checks['passed']}, including immutability, dependency invalidation, explicit override priority, unknown/stale/nonfinite/zero-segment rejection, digit uniqueness, root-tip propagation, synthetic metrics exclusion and 53-joint local-transform reconstruction. UE mechanics passed={uechecks.get('passed')}; its evidence separately labels preview/selection tests, with no human approvals. [ue_scene.json](ue_scene.json) records observed height/triangles/UV sets and zero skeletal assets. Visuals use real source arrays and UE viewport captures; post-correction/accepted skeleton/skinned/animation evidence remains pending.

[source_surface_preservation.json](source_surface_preservation.json) verifies exact ordered triangle topology and per-corner position/UV hashes against the prior normalised mesh: 49,508 triangles, one UV set and 180 cm. Original texture/material source bytes remain protected; only duplicated Phase4D material references are repointed. The earlier UE callback reload defect was corrected by removing its obsolete Phase4D callback; subsequent preview/status and source readback succeeded. A redundant sandbox-desktop helper was stopped; the visible editor-desktop panel is retained.

Self-review corrected metric/provenance distinctions, added unchanged-position review support and approval invalidation, ensured local transform reconstruction, and retained the right-clavicle failure. Working state: no Git repository; no commit or push. This is ready at the human-review boundary, not a completed accepted-rig claim.

A short-lived Windows reader lock was observed during heartbeat replacement. Atomic publication now uses unique temporary files and bounded retry; a regression check reproduces two denied replacements before successful publication. Permanent failures still surface as explicit errors. The final ready status and real trial ledger are verified separately.

![Automatic proposal](pre_correction_front.png)

![Target left-hand tracks](left_hand_tracks.png)
'''
    (O/'Phase4DGuidedLandmarkCorrection.md').write_text(report,encoding='utf-8')
    result=core.read(O/'experiment_result.json');result['protected_file_audit_passed']=audit['passed'];result['review_ready']=bool(scene) and uechecks.get('passed',False);core.save(O/'experiment_result.json',result)
    return audit
if __name__=='__main__':print('Final audit',finish())
