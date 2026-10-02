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
