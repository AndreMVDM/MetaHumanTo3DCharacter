🟢 **High confidence**

# Phase 4F John/Jane anatomy review — ChatGPT planner manual

This manual is intended to be uploaded to the project's ChatGPT source files. It describes the review panel and the planner's role while Andre performs the real anatomical review. It is a prototype of the eventual beginner-facing Assisted Rigging wizard, not approval to build the final product or proceed downstream.

Project: `E:\Repo\UE\Projects\MetaHumanTo3DCharacter`.

## Authority and scope

Read this manual alongside `Documentation\Phase4F\HumanReviewInstructions.md` and `Documentation\Phase4F\Phase4FQualityGeneralisationGate.md`. Those documents retain the gate and project authority. The live review object and its persisted character-local evidence are authoritative for current review progress. Older comparison tables, `experiment_result.json` and gate snapshots may predate human review; do not treat their old interaction counts as current.

These paths identify project artefacts; uploading this manual does not grant ChatGPT filesystem or editor access. If the authority files or current progress are unavailable in the ChatGPT project, request their relevant contents or panel screenshots from Andre before claiming to have checked them.

Primary subjects are John and Jane, the fresh A-pose characters. Bill/Jill remain T-pose diagnostic controls. Lara remains the historical benchmark. Do not modify or reuse their human evidence.

The existing backend is `Working\Phase4F\apose_ue_review.py`, with `apose_ue_review.rigreview`. The panel invokes its existing methods. It does not replace the correction engine, alter criteria or generate downstream assets.

## Verified checkpoint at panel delivery

| Item | John | Jane |
| --- | --- | --- |
| Trial | In progress | Awaiting human review |
| Human body approvals | Pelvis only | None |
| Reviewed without movement | Pelvis | None |
| Placement commands | 0 | 0 |
| Review commands | 1 | 0 |
| Digit identification commands | 0 | 0 |
| Moved landmarks | 0 | 0 |
| Unresolved body roles | 18 | 19 |
| Unresolved finger chains | 10 | 10 |

John's existing session ID is `806685f8-75ef-4cc9-8134-cb203e56e766`. Its seven genuine events include one start and pelvis acceptance at event 7. This checkpoint is historical after further user work. Re-check the panel before proposing the next action.

**Do not press Start again for an in-progress John trial. Do not reset, initialise, overwrite, discard or reapprove his accepted pelvis merely to demonstrate the panel.** At delivery, John is selected, the neck control is selected for continuation, and no gizmo change is pending. Navigation validation added no real events.

The retained anatomy snapshots are John 66/106 and Jane 65/106. These are pre-review gate results, not live completion percentages. An approval updates review evidence; it does not automatically rerun or pass those gates.

## Planner's job

Guide one anatomy decision at a time. Explain the point in simple language, identify the next panel action, inspect the views Andre supplies, and ask for his judgement. Use the panel's current progress to choose the next unresolved item. Keep technical controls available as a fallback while presenting the guided sequence as the main path.

Do not silently perform anatomical acceptance, identity assignment, placement, Start or Finish on Andre's behalf. A recommendation or plausible-looking screenshot is not a genuine approval event. Only an explicit human decision followed by the corresponding backend action creates review evidence.

If ChatGPT has no access to the live editor or panel, say so and give Andre the next button to use. Do not claim to have selected, moved, saved, accepted or validated something unless an actual tool result confirms it. Request screenshots or progress text when needed; do not invent unseen anatomy or counts.

Distinguish:

- An observed position or visible silhouette.
- A recommendation with its uncertainty.
- Andre's judgement.
- A recorded placement or approval confirmed by refreshed progress.
- The separately executed full anatomy gate.

## Launch and reconnect

The panel address is `http://127.0.0.1:8746/`. It runs locally beside Unreal Editor. The current delivery already has the panel attached; opening the address is sufficient while that editor and host remain running.

To start/reopen its browser host from PowerShell:

    & 'E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase4F\ReviewPanel\Launch.ps1'

The launcher uses the installed `python` command, starts the host hidden if needed, and opens the browser. It does not start or change a review trial.

If Unreal has restarted, load the project and the existing review utility. Do not replace a live instance or pending gizmo changes. In a fresh Unreal Python console only:

    import sys; sys.path.insert(0, 'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4F')
    import apose_ue_review; rigreview = apose_ue_review.rigreview
    rigreview.open('John')
    from ReviewPanel import bridge; bridge.attach()

For an already loaded and open review, only the last line is needed. Attachment reuses the existing live object and does not call Start, Save, export or acceptance. Do not reload `apose_ue_review` to attach the panel. Loading a character rebuilds its display from the persisted session through the existing backend; it does not start a new trial.

Use Status / refresh. The panel should show Connected to Unreal Editor, the correct character, and the current trial state. A paused/disconnected heartbeat disables commands. Restore the editor/bridge, refresh, and inspect the state before retrying an unacknowledged action. The host must use the exact loopback address above.

## Guided sequence

| Stage | Points / chains | Useful views |
| --- | --- | --- |
| Pelvis / hips | Pelvis centre; independent hip points are revisited with each leg | Pelvis, front, side |
| Spine / neck / head | Three retained spine points, neck base, head pivot | Side, front |
| Left arm | Shoulder pivot, clavicle root, elbow, wrist | Arms, front, side |
| Right arm | Shoulder pivot, clavicle root, elbow, wrist | Arms, front, side |
| Left leg | Hip, knee, ankle, ball/toe | Front, side, feet |
| Right leg | Hip, knee, ankle, ball/toe | Front, side, feet |
| Left fingers | Thumb, index, middle, ring, pinky | Hand top, hand front |
| Right fingers | Thumb, index, middle, ring, pinky | Hand top, hand front |
| Review summary | Accepted, unresolved, moved and identity counts | Revisit any uncertain item |
| Anatomy validation | Existing full criteria and matching current evidence | Existing validation workflow |

On initial connection or character switch the guide resumes at the first unresolved item, skipping existing human approvals and automatically accepted starting roles. Spine roles remain accessible for optional explicit review. Accepted roles remain accessible through Review step without being made unresolved.

Choosing a role step, Previous step or Next step invokes selection and its useful camera view. Select & view step does the same for the displayed step. Initial page load only reflects state; it does not add navigation events. For an unidentified finger, the step opens a hand view; there is no named endpoint to select yet.

Accept & continue accepts exactly the displayed role/chain, then selects and views the next step after success. Previous/Next only navigate. They never accept the role being left. If advance fails, the completed acceptance remains valid; refresh and navigate again, rather than repeating acceptance.

## Body decision loop

1. Confirm the character, trial state and displayed point. Use Select & view step.
2. Inspect the front and side views, plus the regional view when helpful. Identify the control by its selection/gizmo; do not mistake a procedural line for a movable landmark.
3. Explain what appears sound or uncertain. A clothed surface can conceal the true joint centre. There is no universal numeric offset to apply to these subjects.
4. Ask Andre to choose Accept, Adjust or Unsure.
5. Confirm the refreshed progress and continue one role at a time.

| Choice | Panel action | Evidence meaning |
| --- | --- | --- |
| Accept | Accept & continue, or Accept current role | Explicit anatomy approval for current positions; movement is unnecessary if the point is sound |
| Adjust | Adjust selects/views the point; Andre moves its native UE gizmo; then Record placement | Recorded proposal movement, not acceptance; inspect again before Accept |
| Unsure | Unsure, or Mark current role unresolved | Explicit unresolved judgement; the gate remains blocked for that item |

Record immediately after a deliberate move, with its directly moved control still selected. The backend records only selected pending controls and redraws from the recorded proposal. Avoid several unrelated unrecorded drags; unselected exploratory changes may be lost when the backend redraws. Do not press Unsure or switch character while a placement is pending. If an unwanted exploratory change must be discarded, obtain Andre's explicit decision and use the existing console workflow; the panel has no automatic discard operation.

Moving the pelvis can propagate changes to hips/lower spine. Moving a shoulder can update its clavicle. The backend invalidates approvals whose position signatures no longer match, including affected dependencies. Revisit newly unresolved roles. Do not edit approval JSON to restore an invalidated approval.

The guide's pelvis stage does not implicitly approve the hips. Each hip still appears in its leg stage, and the optional Pelvis / hips / lower spine group includes all listed members. Group acceptance is explicit and applies to all those points. Use it only after Andre has reviewed every member; otherwise use individual decisions.

Do not move good anatomy just to satisfy a retained numeric screen. Source asymmetry is not automatically an error. Where surface evidence is inadequate, use Unsure and document the remaining question.

## Finger decision loop

For each named finger in the guided order:

1. Confirm the hand selector matches the guided left/right hand. Choose a surface track 1–5 to inspect.
2. Use Highlight track, Hand top view and Hand front view. The highlight previews geometry; it does not name a digit.
3. Andre identifies the actual digit from the mesh. Choose thumb/index/middle/ring/pinky in Digit identity after inspection, then Identify track. Track 1 is not implicitly thumb; no numbering-to-identity mapping is authorised.
4. Check the displayed assignment. The backend requires distinct tracks for distinct digits. If an assignment is questionable, stop and resolve it explicitly; do not overwrite it merely to force the intended ordering.
5. Choose Root or Tip, then Select root / tip. Inspect where the chain begins near the palm and where the distal endpoint lies. Partial section tracks and clothing/mesh occlusion can make endpoints uncertain.
6. If needed, move one endpoint's native gizmo, Record placement, and inspect again. Intermediate phalanges remain procedural and are not individual manual placements in this prototype.
7. For the displayed guided finger, use Accept & continue to accept that named chain and advance. Accept named chain is a separate explicit control for the identity dropdown; it accepts that dropdown's digit/hand and does not advance the guide. Check the two targets match before using it.

Root/tip selection and named-chain acceptance are unavailable until that identity exists. Adjust on an unidentified guided finger is disabled. No action guesses which track should become a finger. Identity reassignment or endpoint movement can invalidate chain approval through the existing signatures.

## Session controls and progress

- Open John / Open Jane restores that subject's existing persisted review; it never starts a trial. Pending gizmo changes block a character switch. Opening the already active character is a safe no-op and does not discard pending changes.
- Start explicitly begins a waiting trial or resumes a finished trial under the backend's existing timing semantics. It is disabled while a trial is in progress. Never restart an in-progress trial for the panel.
- Save exports the current backend state and saves the current level. It does not record an unrecorded drag or approve anatomy. Pending changes must be recorded first.
- Finish explicitly ends the timed trial and saves; unresolved anatomy may still remain. Finish is not an anatomy pass.
- Status / refresh reads the live progress. Regular polling also updates it without adding an event.

The progress column shows human body approvals separately from automatic starting roles, unresolved body roles, unresolved named finger chains, placement commands, review commands, digit identification commands, and actually moved landmark count. Reviewed without movement explicitly includes sound points accepted without a drag. Placement commands and moved landmarks are different metrics.

Normal human Select/View/Highlight actions during an active trial retain the backend's navigation-event behaviour. Those actions before Start do not create trial events. Agent validation used a separate navigation-only channel with event recording suppressed temporarily and restored; those checks are never presented as human review evidence.

The command transport binds each action to the current editor attachment, character, session and revision. Stale or expired commands are rejected. A claimed action is never automatically replayed after an interruption. Read any error, refresh and inspect the evidence before deciding whether another explicit command is needed.

## Summary, validation and stop conditions

Before proposing Finish, inspect unresolved lists, identities, pending gizmo changes, and any approvals invalidated by later moves. Finish only when Andre wants to end the timed trial. Saving and finishing are separate from acceptance.

The Anatomy validation step is informational in this prototype. It shows review readiness and explains the existing gate boundary; it does not execute validation. Zero unresolved roles/chains is necessary review progress, not proof that all full anatomy criteria pass.

To continue into validation, use the established Phase4F workflow against each character's current proposal and current human evidence. If the planner lacks the execution tools or authoritative validator, prepare a scoped request for the implementation agent and wait for its actual result. Do not regenerate proposals, rerun old preparation writers, or reuse the earlier zero-event self-review script: they predate this real John review.

Stop downstream work until the full anatomy gate passes with matching current evidence. No skeleton/skinning/IK/retarget/bake work is authorised by this manual, a panel count, Finish, or a partial gate score. Retain failed checks and uncertainties; do not relax criteria, suppress failures or force a GO/HOLD/NO-GO verdict from unperformed tests.

## Evidence and planner continuation record

Current state and immutable events:

- `Working\Phase4F\John\session.json` and `Working\Phase4F\Jane\session.json`.
- Each subject's `Working\Phase4F\<Character>\InteractionEvidence\event_*.json`.
- `Documentation\Phase4F\<Character>\human_review.json`.
- `Documentation\Phase4F\<Character>\correction_metrics.json`, `current_proposal.json` and `actual_correction_list.json`.
- The separately generated `anatomical_validation.json` and `experiment_result.json`; check freshness before relying on them.

Do not write these files directly to create placements, assignments or approvals. Use the backend through the panel.

At a pause, report only observed facts: character, trial state, last genuine decision, next unresolved role, pending placement status, approval invalidations, unresolved questions, and whether full validation has actually run. If evidence is unavailable, mark the corresponding claim unverified. Use Andre's confidence indicator and one copyable outer Markdown block for planner reports.

Suggested first prompt to the planner:

    Read ChatGPTPlannerReviewManual.md and the Phase4F review/gate instructions. Guide the anatomy review with me one step at a time. Verify the panel's current state first. Preserve my in-progress John trial and existing pelvis approval. Recommend the next view and decision, but do not accept, move or identify anatomy without my explicit judgement. Do not proceed downstream until the full existing anatomy gate passes.

## Prototype limitations

This is a local browser wrapper, not a finished native UE plugin. Initial bridge attachment requires one Python-console action after an editor restart. Placement still uses the UE gizmo. Camera views are the backend's existing presets, not a newly tuned per-role framing system. Finger identities and anatomy decisions remain human work. A Save/Finish or other explicit backend call can fail after part of its work has succeeded; refresh and inspect state before retrying. The panel retains the backend's timing, provenance, procedural phalanges and invalidation model.

Light is the first-use theme; Light/Dark selection persists locally. The guided step metadata, backend dispatch and transport are separate so later wizard wording/layout can evolve without changing evidence or gate logic.
