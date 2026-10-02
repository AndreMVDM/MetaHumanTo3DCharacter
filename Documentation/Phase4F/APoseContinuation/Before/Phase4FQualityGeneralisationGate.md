🟠 **Medium confidence**

# MetaHumanTo3DCharacter — Phase 4F Quality Acceptance & Generalisation Gate

1 October 2026, Australia/Sydney. **INTERIM — stopped at the genuine human-review boundary.** Level 1 single-agent execution and self-review. This is not a completed generalisation decision.

## 1. Executive summary

**Hold Phase 5 pending evidence. Assisted Rigging generalisation is not yet established.** All three inputs were freshly inventoried and both new characters received character-local automatic donor proposals. Both solves succeeded, but both anatomical gates reject them. Source T-pose arms and donor lowered-arm landmarks disagree substantially; successful donor extraction is not successful target anatomy.

Native technical review scenes and position-bound correction recording are prepared for Bill and Jill. Each has 19 unresolved body roles and ten unnamed finger chains. Five actual surface tracks per hand were detected on each new mesh. Actual human review/correction counts remain zero; required burden is unknown. No new skeleton, weights, retarget or animation was built before anatomy passed.

The downstream quality, runtime and clean-project tasks remain blocked by anatomy. The definitive GO/HOLD/NO-GO gate remains open. HOLD here is an administrative recommendation to withhold Phase 5, not the brief's technical HOLD finding that architecture already generalises with only one or two quality issues. No fabricated anatomy or premature NO-GO is substituted for unperformed work. [Machine state](phase_status.json).

## 2. Prior evidence recap

Read [Phase4D](../Phase4D/Phase4DGuidedLandmarkCorrection.md), including completed appendix 29, and [Phase4E](../Phase4E/Phase4ECharacterQualityRefinement.md), plus relevant 3B/4A/4B/4C architecture sections and machine evidence before new proposal work. Hash-indexed sources: [evidence index](prior_evidence_index.json).

Mode B remains the validated automatic rigged workflow. Lara's semantic Assisted Rigging anatomy passed 186/186 checks: 23 body roles, ten accepted finger chains, one actual neck movement, no manual intermediate phalange placements. The 53-bone skeleton, GEODESIC_VOXEL binding, IK, retarget, bake and source-free playback work. Phase4E materially repairs pants/crotch, partially improves shoulders, and measures approximately 0.16/0.34 cm walk/run penetration after authoring correction. Finger support remains 9/10 and natural thumb opposition unproven. Overall Mode A remains experimental assisted.

## 3. Phase 4F policy/budget

[Frozen evaluation policy](evaluation_policy.json) was saved before optimisation: at most three semantic/landmark passes per new character and four skin variants per quality region including baseline. No conventional vertex-by-vertex painting, prior-character coordinate initialisation or final hardcoded vertex-ID masks. Only diagnostic segmentation is permitted. All three use a controlled 180 cm physical profile while retaining individual relative proportions; intended generated real-world stature is not assumed.

[Budget consumed](budget_consumption.json): Bill 2 proposal attempts (first frame-rejected/aborted, second successfully extracted), Jill 1, Lara 0. Skin candidates: zero for all. Remaining semantic limits: Bill 1, Jill 2; not an obligation to spend them. No unlimited fitting research or polished plugin/UI was begun. Existing donor/review architecture is reused; correction remains the authorised next route.

Baseline skin after anatomy acceptance: GEODESIC_VOXEL, resolution 128, stiffness 0.2, five influences. Evaluate root redistribution, character-relative pelvis envelope, left/right gating, local shoulder bind blending and explicit reject-regression comparison. Convert distances to ratios of height/span/segment length and record exceptional per-character values. Do not silently adopt Lara's centimetre settings. Contact authoring is bounded to five iterations, relative lift limit 0.033333 × height, 60 Hz bake with 120 Hz interpolation checks; actor/root/pelvis offsets are excluded.

## 4. Input inventories

[Archive inventory and hashes](input_inventory.json); [Lara geometry](lara_geometry_summary.json), [Bill geometry](bill_geometry_summary.json), [Jill geometry](jill_geometry_summary.json). Each ZIP has one binary FBX mesh, one material, one texture/video reference; no FBX deformers, skeleton nodes, skin clusters or Blender armature/vertex groups/armature modifiers. Mesh components are not distinct named objects/materials.

| Character | Source vertices | Polygons | Triangles | Raw components | Positional-seam components | Observed clothing |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Lara | 27,725 | 28,636 | 49,508 | 102 | 102 | partially separable |
| Bill | 25,728 | 26,505 | 49,374 | 31 | 31 | separable garment shells |
| Jill | 27,014 | 29,132 | 52,392 | 14 | 14 | merged/integrated surface |

Positional seam welding at 0.00001 cm is analysis-only; no source topology was welded. UV loops, layers, bounds, hashes, material/image links, texture dimensions, mesh matrices and component bounds are recorded per character. Vertex and UV values are finite. Original archives/extracted entries were not authored. Textured source renders: [Lara](lara_source_front.png), [Bill](bill_source_front.png), [Jill](jill_source_front.png); side/back images sit beside these.

FBXs declare UpAxis +Y, FrontAxis +Z, CoordAxis +X and UnitScaleFactor 100. Blender imports into RH +Z-up world centimetres; canonical UE left/forward/up conversion has determinant −1, with inverse round-trip error approximately 1.6e−14 cm. Facing is checked against textured features. Bill's toe-extension heuristic initially chose his back as forward; direct face/belt-buckle views rejected it before the accepted starting proposal. The first imported wrong-frame static mesh remains diagnostic only. No anatomical approval follows from frame orientation.

UE target readback has 25,728/27,014 vertices and height 180.0 cm for Bill/Jill, but 49,363/52,385 triangles versus Blender 49,374/52,392. Import triangulation/degenerate-face removal is recorded, not called exact original topology preservation. [Bill source/UE comparison](Bill/source_ue_comparison.json), [Jill comparison](Jill/source_ue_comparison.json). Near-zero tangent/binormal warnings remain in execution logs. Any eventual native skin must preserve its original UE static surface/UV baseline and disclose DCC-to-UE import differences.

## 5. Lara benchmark

Use prior accepted 4D/4E assets as read-only benchmark. No Lara fit, landmark movement, binding candidate or animation rerun occurred. Source inventory is new; prior skin values remain labelled inherited. Phase4E's 34-pose and 244-body-sample results, 120 Hz contact measurements, original native captures and closure evidence remain authoritative within their scope. Lara is not promoted to full quality acceptance by including it in this test set.

## 6. Bill anatomy/Assisted Rigging

Automatic character-local combined donor solve: 48.141 s; 342 exposed joints; public Python and native extraction agree exactly. No Lara positions or tracks initialise Bill. [Execution](automatic_proposal_execution.json), [body proposal](Bill/automatic_starting_proposal.json), [gate](Bill/anatomical_validation.json), [front overlay](Bill/proposal_front.png), [side](Bill/proposal_side.png).

Gate: **65/106 pass, 41 fail; downstream_authorised=false**. Hard failures include bilateral body consistency, left elbow envelope, both wrist envelopes and incomplete accepted finger correspondence. Maximum mirrored body difference is 6.1449 cm versus the retained <6 cm screen. Human-review failures remain separately listed. Wrists are around Z=96 cm, far from the actual horizontally extended source hands. No guessed automatic movement was inserted. Four root/spine roles are only provisional policy outputs; 19 articulation roles require independent judgement.

## 7. Jill anatomy/Assisted Rigging

Automatic character-local combined donor solve: 44.485 s; 342 joints; public extraction APIs agree exactly. [Body proposal](Jill/automatic_starting_proposal.json), [gate](Jill/anatomical_validation.json), [front overlay](Jill/proposal_front.png), [side](Jill/proposal_side.png).

Gate: **62/106 pass, 44 fail; downstream_authorised=false**. Both shoulders, elbows and wrists fail surface-envelope screens; bilateral mismatch reaches 20.6221 cm. Donor hand/elbow layout does not match the T-pose mesh. Four root/spine roles remain provisional, 19 require review, and ten digit identities/chains are unresolved. Long hair is separate in part, but does not certify neck/head/shoulder pivot locations. No semantic fitting research was reopened to force these through.

## 8. Correction effort comparison

Lara's actual prior ledger: 159 commands, one 8.4106 cm neck placement, 13 digit identification commands, 34 review commands, 32 distinct currently reviewed roles/chains, 31 accepted without movement and 108 navigation commands. Elapsed Start-to-Finish 12,179.219 seconds includes pauses; active time and beginner usability are not established.

Bill/Jill: zero actual review commands, zero moved landmarks, zero digit-identity interactions, zero manual phalange placements, zero accepted-without-movement, null measured session time. Those are performed counts, not required effort. Current unresolved counts: 19 body + ten finger chains each. [Bill effort](Bill/correction_metrics.json), [Jill effort](Jill/correction_metrics.json). Real immutable event ledgers are empty. Synthetic tests never populate real review sessions.

## 9. Clothing structure analysis

Lara: Large upper body/clothing and lower pants/boots components plus many accessories. Not an established isolated trouser/body-donor pair.

Bill: Distinct trouser-region, shirt-region, belt and boot shells supported by connected components, spatial extents and source texture views. Not separate named mesh objects/material slots; no proven complete underlying body donor. Largest trouser-region shell is 4,892 vertices; shirt-region shell 3,085; belt-region 1,685; major boot shells 2,033 and 1,692. [Connectivity projection](Bill/connectivity_front.png). Geometry makes shell-specific weighting/inpainting/stiffness comparison meaningful after anatomy, but no transfer result exists. A complete valid underlying weighted donor body has not been established; transferring a faulty field to itself would not demonstrate garment transfer.

Jill: One dominant connected surface spans both arms, torso and trousers/legs; boots, head and hair-related pieces remain separate. Primary garments cannot be selected as complete distinct connected shirt/trouser shells. Dominant surface has 14,602 vertices; head/hair/boots add separate components. [Connectivity projection](Jill/connectivity_front.png). Integrated cloth refinement must use character-relative anatomical/spatial envelopes or a separately validated classifier; complete garment-shell selection cannot be assumed. Classification covers principal clothing, not every hair/accessory shell.

## 10. Initial skinning comparison

**Blocked by anatomy for both new characters.** Zero native Skeleton/SkeletalMesh/IK/retarget/animation candidates were built. No geodesic quality measurements or garment transfer were performed. Lara's inherited binding/refinement remains a control, not proof of new-character generalisation. The initial binding contract and bounded candidate budget are frozen above.

## 11. Shoulder results

Lara inherited mean strain improves 0.235414 → 0.136863, but worst reach triangles below half area regress 703 → 844; angular armpit detail persists. Shoulder acceptance remains withheld. Bill/Jill deformation, armpit, deltoid, clavicle/chest/back, local thickness/volume loss, stretch and worst-frame visuals are unmeasured. Review poses must include 45°, horizontal, overhead and full reach sequence; means cannot hide a worst case.

## 12. Pelvis/pants results

Lara inherited pants mean strain improves 55.8%; primary front-crotch fold is visibly stabilised in native reviewed poses. Full collision/volume certification is absent. Bill trousers shell comparison and Jill integrated weighting are unperformed until anatomy passes. Waistband/crotch/thigh cross-influence/front/back tests and absence of conventional painting remain mandatory.

## 13. Fingers/thumb results

Each new hand has five actual unnamed section-component tracks. T-pose slicing uses X along the outward arm rather than Lara's A-pose Z; adjacent tracking/branch logic is retained and all paths come from that character's mesh. [Bill tracks](Bill/finger_tracks.json), [Jill tracks](Jill/finger_tracks.json). Both hands have top/front source-data closeups. Naming/order is deliberately not automatically accepted. Root/tip tracks may be partial.

The technical review utility retains independent digit assignment, root/tip corrections and procedural three-phalange generation using each character's own donor segment proportions. No Lara finger coordinates or manual phalange positions are reused. Ten independent-motion, support, crossing/collision and thumb opposition/flex tests remain unperformed. Lara's identity motion is 10/10, support 9/10, natural thumb task unproven; no claim of universal finger usability.

## 14. Foot/contact results

Lara prior dense idle/walk/run maximum penetration: 0.0000/0.1579/0.3376 cm with unchanged root displacement and unit scales. Surface probes and authoring correction limits remain explicit. Hover must be phase-aware; airborne run/jump is not automatically a hover defect. Bill/Jill penetration, slide proxy and ankle-ball orientation are not measured. Generalised contact authoring, planting, terrain and world stride are not proven.

## 15. Stress-suite results

Frozen same suite: neutral/reference; arms 45°; horizontal; overhead; bent elbows; wide stance; strong knee bend/crouch; idle; walk; run; reach/JumpingJacks; independent fingers; thumb opposition/flex. Lara's prior suite covers body/finger stress plus separate synthetic thumb diagnostics, with existing quality limits. No new Phase4F same-suite runs occurred on any character. Both new meshes are unweighted, so comparing source T-pose geometry to animated Lara would be invalid.

## 16. Refinement generalisation analysis

Rules are reusable hypotheses, not established multi-character results. Clothing connectivity differs materially, and the initial donor-to-source pose match fails on both T-pose inputs. Guided movement can represent all affected points, but actual correction burden and successful anatomy remain unmeasured. This is a concrete semantic proposal limitation, not yet evidence that the skinning/refinement architecture requires manual painting. No hardcoded vertex mask or hidden Lara parameter fit was introduced.

## 17. Native playback

Lara's prior destination-native playback passed, with no runtime Manny/MetaHuman/fitting requirement. New maps are static authoring review scenes, not native character playback. The temporary donors and DNA are authoring-only. Bill/Jill destination-native playback remains blocked. A MetaHuman authoring asset is not an accepted fresh Bill/Jill native skeleton.

## 18. Clean-project/cooked validation

Not performed for any Phase4F runtime package because neither new character has an accepted runtime package. Lara prior closure is not a clean-project proof. After acceptance, copy/migrate runtime seeds into a Phase4F-local clean host; verify fresh load, motion and no authoring dependencies, then cook/package smoke test if practical. Do not treat package closure or an authoring map reload as cooked/runtime validation.

## 19. Runtime dependency closure

No new accepted runtime seed set exists. Lara inherited Phase4E recursive closure passes with 22 /Game and 16 normal /Engine or /Script packages and zero foreign/prior/authoring-helper references. New review maps deliberately reference authoring static source/markers. Donor closure is irrelevant to the required final runtime closure. No cloud/external inference call is in this authoring workflow; disconnected execution was not tested.

## 20. Product generalisation matrix

| Metric | Lara | Bill | Jill |
| --- | --- | --- | --- |
| Input topology type | 1 mesh / 27,725 source vertices | 1 mesh / 25,728 source vertices | 1 mesh / 27,014 source vertices |
| Clothing classification | partially separable | separable garment shells | merged/integrated surface |
| Body roles requiring human review | 19 initially; 22 body roles actually reviewed | 19 | 19 |
| Actual moved landmarks | 1 neck; 8.4106 cm | 0 performed; required unknown | 0 performed; required unknown |
| Actual human reviews | 32 distinct roles/chains; 34 review commands | 0 | 0 |
| Accepted without movement | 31 current roles/chains | 0 | 0 |
| Finger mapping interactions | 13 identification commands; ten final identities | 0; ten identities pending | 0; ten identities pending |
| Manual phalange placements | 0 | 0 performed | 0 performed |
| Measured review session time | 12,179.219 s incl. pauses | not started | not started |
| Anatomy gate | 186/186 passed in Phase4D | 65/106; blocked | 62/106; blocked |
| Skeleton built | 53-bone native skeleton (prior) | no; anatomy blocked | no; anatomy blocked |
| Shoulder accepted | no; partial improvement / worst reach regression | not tested | not tested |
| Pelvis/pants accepted | material pants repair on reviewed poses; limited acceptance | not tested | not tested |
| Fingers accepted | identity/motion 10/10; support 9/10; quality incomplete | identity/review pending | identity/review pending |
| Thumb accepted | natural opposition unproven | not tested | not tested |
| Foot/contact accepted | 0/0.158/0.338 cm idle/walk/run flat-floor penetration; planting untested | not tested | not tested |
| Conventional manual painting required | none used; full acceptable quality not established | unknown; none used | unknown; none used |
| Source-free playback | passed in prior native scene/closure | not built/tested | not built/tested |
| Clean-project playback | not performed | not performed | not performed |
| Overall result | experimental assisted | awaiting human anatomy review | awaiting human anatomy review |

Machine table: [product_generalisation_matrix.json](product_generalisation_matrix.json). Unperformed items remain unperformed; no averages hide the two new anatomy failures.

## 21. GO/HOLD/NO-GO decision

**Phase 5: HOLD pending human review and the blocked tests. Definitive Phase4F decision: incomplete.** Neither new character currently passes anatomy. The brief's GO cannot be justified. The technical HOLD condition (architecture working across characters with only limited remaining quality issues) is also not proven. NO-GO/manual-painting/scope reduction cannot honestly be inferred from skinning tasks that have not run. The user explicitly authorised stopping at a genuine anatomical review boundary, which is reached here.

This report must be updated after real input and bounded quality testing. If corrected proposals still fail within the remaining semantic budget or burden approaches manual rigging, assess NO-GO/scope reduction explicitly. If anatomy and skinning generalise but a limited quality issue remains, use technical HOLD. Only the supplied multi-character quality/runtime/effort conditions can support GO.

## 22. Phase 5 recommendation or scope revision

Do not begin Phase 5 architecture/UI now. Complete actual Bill/Jill review using [exact native review instructions](HumanReviewInstructions.md), rerun the retained gates, and build fresh character-local native assets only after the full gate passes. The console/native gizmo tool is a technical research utility, not a demonstrated beginner workflow. It retains immutable movements, explicit review, digit matching and timing without the external Phase4D Tk panel.

Answers at this boundary:

- Does Assisted Rigging generalise beyond Lara? **Not established; proposals exist but both new anatomies are rejected pending review.**
- Do skinning/refinement rules generalise across proportions/clothing? **Unknown; downstream tests blocked.**
- Can acceptable results be achieved without conventional manual painting? **Lara pants materially improve without painting; complete quality and multi-character feasibility are unproven.**
- Is correction burden small enough for beginners? **Unknown; actual new trials have not started and Lara's elapsed expert trial includes more than three hours with pauses.**
- Are all primary regions acceptable enough for productisation? **No demonstrated acceptance; Lara shoulders/finger support/thumb remain incomplete and new characters are untested.**
- Proceed to Phase 5? **No at this boundary; withhold until the definitive gate is supported.**

## 23. Protected-file audit

Captured 3,431 prior authored files before Phase4F work. [Baseline](protected_before.json), [audit](protected_file_audit.json). The already-running Phase4E editor appended to its protected execution log; it was normally shut down and the exact baseline prefix was restored only after its SHA256 matched. Full append evidence is retained inside Phase4F. [Repair evidence](live_log_preservation_repair.json). New interactive editor logs are Phase4F-scoped. Final audit status must be read from its JSON, not inferred from this report writer.

All original ZIPs, Phase4D human ledger, prior assets/reports/evidence and project configuration are preserved byte-for-byte in the final audit. Engine/PCH/library inputs and external references were read-only; no exhaustive external-tree hash claim. Normal Saved/Intermediate/DDC caches are excluded explicitly. The initial Blender invocation loaded existing user add-ons and encountered blocked external extension-cache writes; later invocations used --factory-startup. No Engine/source/reference edit, staging, commit, push or config change. Workspace is not a Git repository.

New authored work stays in Documentation/Phase4F, Working/Phase4F and /Game/MetaHumanTo3DCharacter/Phase4F. The isolated DNA reader binary retains the existing Phase4CTools module/class names for compatibility but is compiled and loaded from Phase4F; it does not imply a production plugin. A prior PCH is read-only, and scope checks read only Phase4F DNA. Failed frame/API/cache attempts remain as labelled diagnostic logs. The interactive launcher explicitly scopes LocalDataCachePath and ShaderWorkingDir to Phase4F after default locations were blocked; no project or Engine configuration was edited for this recovery.

[Self-review](self_review.json): 23 focused checks pass, including zero synthetic human metrics, movement/endpoint approval invalidation, duplicate-track rejection and unchanged real sessions. [Fresh native review readback](native_review_fresh_readback.json) passes for both saved maps: 22 controls each with zero position error, unit source scale, 180 cm height and character-local texture references. These are static authoring checks. No final anatomical, deformation, beginner or cooked acceptance is manufactured.
