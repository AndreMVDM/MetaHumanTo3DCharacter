🟠 **Medium confidence**

# Phase 4F — exact human anatomical review instructions

Bill and Jill are not anatomically accepted. Their automatic donor arms are lowered while the actual source arms are in T-pose. Review and, where necessary, correct the real source articulation positions. Do not approve points merely because they have semantic bone names or generated axes.

This is a technical native UE gizmo/console utility, not the final beginner-facing UI. No external Tk panel is required. The agent has not started a measured trial, moved a landmark, assigned a digit or accepted any anatomy.

## Open the prepared review

The Phase4F editor opens Bill's review. In the bottom command-entry dropdown choose **Python**. If the Python names are not already available, enter this once:

    import ue_review; rigreview = ue_review.rigreview

To reopen the prepared editor, run the scoped launcher from the project directory in PowerShell:

    & .\Working\Phase4F\launch_review.ps1

It keeps editor logs, derived data and shader working files inside Phase4F. Wait for Bill's review map to finish opening before starting a measured trial.

If reopening in another editor, first load the utility, then open the saved map:

    import sys; sys.dont_write_bytecode = True; sys.path.insert(0, 'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4F'); import ue_review; rigreview = ue_review.rigreview; rigreview.open('Bill')

Maps:

- `/Game/MetaHumanTo3DCharacter/Phase4F/Bill/Maps/L_BillReview`
- `/Game/MetaHumanTo3DCharacter/Phase4F/Jill/Maps/L_JillReview`

Keep the editor out of Play/Simulate. Disable translation snapping if it impedes small placements. Canonical physical units are centimetres; source and controls have unit actor scale. Amber markers require anatomical review; green root/spine policy points are provisional. Purple lines are generated connections, not editable intermediate bones. The translucent mesh is the correction surface; the textured source is alongside it.

Press `G` while the viewport has focus if editor light icons obscure the review surface. Static control spheres remain visible; toggle `G` back if you need editor overlays.

## Start a real measured trial

Enter:

    rigreview.start()

Timing includes pauses until `finish()`. Only commands issued after this real start count as human navigation. OS mouse clicks and exploratory drags are not exhaustively measured. Do not start the trial simply to test tool mechanics.

## Body review and placements

Select a role using the Outliner (`F4 CONTROL <role>`) or the following command, then use the normal UE translation gizmo:

    rigreview.select('hand_l')

Inspect front and side, with focused views when useful:

    rigreview.view('front')
    rigreview.view('side')
    rigreview.view('arms')
    rigreview.view('pelvis')
    rigreview.view('feet')

Bill/Jill elbows and wrists plainly need source-pose review first. `upperarm_l/r` are shoulder pivots, `lowerarm_l/r` elbows and `hand_l/r` wrists. Use the actual T-pose arm, not the hanging donor lines. Do not invent an exact correction distance in advance.

After dragging the **directly selected** control to its intended position, record the placement:

    rigreview.record()

Recording is not acceptance. Shoulder edits recompute clavicle dependents; pelvis edits recompute hips/lower-spine dependencies. Inspect those dependent points again. Explicit overrides are supported. There is no automatic mirrored correction.

To restore unrecorded gizmo positions:

    rigreview.discard()

Only after personally inspecting the final point/group and relevant bend plane in front/side, record your judgement. For example, **only if the selected wrist is actually acceptable**:

    rigreview.accept('hand_l')

If uncertain, keep it unresolved and state the category:

    rigreview.unresolved('hand_l', 'wrist_palm_correspondence_uncertain')

The 19 initially unresolved roles are pelvis, neck/head, both clavicles, shoulders, elbows, wrists, hips, knees, ankles and balls. Root and spines are provisional, but moved/generated spine points require fresh review. Optional explicit review groups are:

- `Pelvis / hips / lower spine`
- `Left shoulder / clavicle`
- `Right shoulder / clavicle`
- `Neck / head`

For a group, use its exact name in `accept()` only after every member has been reviewed. You can instead pass an explicit list of inspected roles. Accept elbow/knee roles only after assessing their bend plane/direction. Movement invalidates affected position-bound approvals; it never clears a gate automatically.

Do not alter a correct source T-pose point merely to satisfy an inherited descending-height or pole screen. If a screen conflicts with a sound reviewed pose, leave the discrepancy recorded and return it for diagnosis. Gates are not relaxed or hidden by this utility.

## Finger identity and generated phalanges

Each side has five **unnamed** actual source-surface tracks. Numbers do not imply thumb/index/middle/ring/pinky ordering. Identify each hand independently.

Highlight a track and inspect both top/front:

    rigreview.track('l', 1)
    rigreview.view('hand_l_top')
    rigreview.view('hand_l_front')

After you identify that highlighted track's actual digit, assign the identity. This example is an API example, **not a proposed identity for track 1**:

    rigreview.identify('l', 'index', 1)

Valid identities are `thumb`, `index`, `middle`, `ring`, `pinky`; sides are `l` and `r`; numbers 1–5. One track cannot be used by two digits. A mistaken assignment can be reassigned; it invalidates acceptance. Use the full source geometry and the labelled hand closeups in `Documentation/Phase4F/Bill/` or `Jill/` as additional evidence.

Inspect the generated root/tip and three procedural phalanges. Their length proportions come from that character's own solved donor; they are still proposals. If endpoints are inadequate, select `index_l:root` or `index_l:tip`, drag in UE, then `record()`. Do not manually place intermediate phalanges; report the procedural chain limitation if endpoints cannot resolve it.

Accept a named chain only after its identity, palm attachment, root/tip and generated phalanges follow the intended finger in multiple views:

    rigreview.accept('index_l')

Repeat all five digits on each side. Natural motion, thumb opposition, support and collision acceptance happen later under the shared stress suite; anatomical acceptance alone does not prove deformation quality.

## Finish Bill, then review Jill

Inspect current effort/unresolved state:

    rigreview.status()

Once your actual review is complete, record its measured end and save the Phase4F map:

    rigreview.finish()

Then open Jill and start a separate measured trial:

    rigreview.open('Jill')
    rigreview.start()

Repeat the same review process. Use `save()` to preserve an in-progress trial without claiming completion. `start()` resumes a finished trial and retains its original start timestamp; elapsed time still includes pauses.

The utility writes only character-local Phase4F session/proposal/review/metrics/event files. Real human events are immutable. Moving a point later invalidates affected approvals and requires new review. Do not edit approval JSON or reuse Phase4D human events.

## Return boundary

Tell the agent when both real reviews are ready, or report any role/track you cannot resolve. The agent then reruns `Working/Phase4F/Bill/validate.py` and `Working/Phase4F/Jill/validate.py`. Fresh skeletons are authorised only if the complete anatomy gate passes; zero remaining numerical flags alone is insufficient without the required real approvals.

No conventional weight painting, skinning optimisation, retargeting, animation or Phase5 UI work is required from you at this review boundary.


## John/Jane current primary review

This section supersedes the primary-subject directions above. Bill/Jill instructions remain historical T-pose-control instructions; do not review them to unlock the current generalisation path. John and Jane require real review. No measured trial has started.

Open the current interactive review (John is the startup map):

    & .\Working\Phase4F\apose_launch_review.ps1

Use **Python** in the bottom console dropdown. Bind the current utility once if needed:

    import apose_ue_review; rigreview = apose_ue_review.rigreview

If module search paths are absent:

    import sys; sys.dont_write_bytecode=True; sys.path.insert(0,'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4F'); import apose_ue_review; rigreview=apose_ue_review.rigreview; rigreview.open('John')

Maps: /Game/MetaHumanTo3DCharacter/Phase4F/John/Maps/L_JohnReview and /Game/MetaHumanTo3DCharacter/Phase4F/Jane/Maps/L_JaneReview. Stay out of Play/Simulate. Normal translation gizmos act on F4 CONTROL actors; disable snapping for small edits. Amber requires review; green root/spines are provisional; purple lines are procedural. The ghost is the review surface and textured source is alongside. Press G in the viewport to hide light icons if needed.

Start only when beginning your real anatomical review:

    rigreview.start()

For each character review all these 19 roles against its actual A-pose, in front AND side:

- pelvis; neck_01; head;
- clavicle_l, upperarm_l, lowerarm_l, hand_l;
- clavicle_r, upperarm_r, lowerarm_r, hand_r;
- thigh_l, calf_l, foot_l, ball_l;
- thigh_r, calf_r, foot_r, ball_r.

upperarm is shoulder, lowerarm elbow, hand wrist; thigh hip, calf knee, foot ankle, ball metatarsal/forefoot. Assess elbow/knee bend direction as well as point position. Source asymmetry is not automatically an error. Body arms are now correctly aligned by coarse envelopes: do not perform the old T-pose-control arm relocation.

John priorities: inspect both clavicles and generated spine_03 in depth; neck/head, wrists, hips and hidden boot articulations still require judgement. Jane priorities: inspect pelvis/upper-spine lateral bias, clavicle roots and real fore/aft arm asymmetry. Jane left clavicle is on the wrong side relative to donor spine_03 under the retained convention; bilateral max17.777cm and the source sole-count screen also fail. Do not move a sound source point just to force symmetry or satisfy a screen. The sole count cannot be cleared with a human placement. Report convention/sampling conflicts for diagnosis.

Select and inspect:

    rigreview.select('hand_l')
    rigreview.view('front')
    rigreview.view('side')

Other views: arms, pelvis, feet, hand_l_top, hand_l_front, hand_r_top, hand_r_front. Drag only if the selected point actually needs correction, then record:

    rigreview.record()

After personally inspecting the final point, accept it (example only, not an approval recommendation):

    rigreview.accept('hand_l')

Keep uncertainty explicit:

    rigreview.unresolved('clavicle_l','pivot_convention_or_surface_ambiguity')

Record and accept are separate. No automatic mirroring. Pelvis/shoulder movements update dependent hips/spines/clavicles and invalidate affected approvals. Review moved/generated spines as necessary. Existing exact named groups remain available: Pelvis / hips / lower spine; Left shoulder / clavicle; Right shoulder / clavicle; Neck / head. Accept a group only after reviewing every member. discard() restores unrecorded drags; save() preserves progress.

Each character has five independent **unnamed** tracks on each side, numbered1–5 within that hand. Track numbers do not inherit Lara/Bill/Jill identities. John tracks follow relaxed partly curled fingers; Jane tracks have asymmetry. Use the per-hand top/front images in Documentation/Phase4F/John or Jane as additional views.

Highlight each actual track and identify it yourself:

    rigreview.track('l',1)
    rigreview.view('hand_l_top')
    rigreview.view('hand_l_front')

Only after identification, assign its actual identity. This is an API example, not the identity of track1:

    rigreview.identify('l','index',1)

Identities: thumb,index,middle,ring,pinky. Review each side independently. Duplicate track assignments are rejected. Inspect each generated chain's palm attachment, root/tip and all three procedural phalanges. If needed, select index_l:root or index_l:tip (substitute actual digit), move its gizmo and record(). Intermediate phalanges stay procedural; report a chain limitation rather than manually placing all joints. After actual identity/root/tip/chain review:

    rigreview.accept('index_l')

Repeat all five on each side; natural motion/thumb opposition is tested downstream, not certified by this acceptance.

Check progress and finish the real trial:

    rigreview.status()
    rigreview.finish()

Then independently review Jane:

    rigreview.open('Jane')
    rigreview.start()

Timing is Start-to-Finish and includes pauses. save() can preserve an unfinished trial. Moving anything after approval invalidates relevant position-bound evidence; never edit approval JSON or borrow Phase4D events.

Return when both reviews are ready, or report roles/tracks you cannot resolve. The agent will rerun Working/Phase4F/John/validate.py and Jane/validate.py, diagnose surviving geometry/convention flags without fabricating reviews, and proceed downstream only after the full gate passes. No manual weight painting or external Tk panel is required at this boundary.

## Guided John/Jane review panel

A Phase4F-local browser wrapper now calls the same `apose_ue_review` methods. It provides guided anatomy steps with Select & view, Accept & continue, Adjust and Unsure, plus the explicit body/finger controls. It does not alter criteria or automatically name digits, approve anatomy or start a trial.

At panel delivery John is already in progress, with pelvis genuinely accepted without movement. Preserve that state; do not press Start again. Jane has not started. The existing console examples above remain a reference, not instructions to repeat already completed actions.

Open `http://127.0.0.1:8746/`, or run `Working\Phase4F\ReviewPanel\Launch.ps1`. A fresh UE attachment uses `from ReviewPanel import bridge; bridge.attach()` after the existing review has been opened. [Launch and validation record](ReviewPanel/README.md).

Upload [ChatGPTPlannerReviewManual.md](ChatGPTPlannerReviewManual.md) to the ChatGPT project's source files for the planner guiding the real review. The manual explains the full sequential procedure, current-state checks, finger identity, immutable evidence, pending placements and the separate anatomy-validation boundary.
