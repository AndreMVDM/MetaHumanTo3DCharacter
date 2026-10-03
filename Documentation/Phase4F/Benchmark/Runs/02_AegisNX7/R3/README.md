🟢 **High confidence**

# Module R3 — Aegis NX-7 second rigged-character generalisation

## 1. Executive result

**GENERALISATION_PASS_WITH_GENERIC_FIX.** Aegis passed input validation, unchanged R1 unit handling, automatic R2 semantic/IK/retarget authoring, four destination-native animations and advancing source-free native playback. No subject-specific rig, retarget, stature, weight or material repair was used.

The authoritative first unchanged R2 run passed all authoring stages, then failed before PIE at its folder-based runtime ownership screen: Aegis's correctly retained original material and texture were outside the derived folder. This failure is preserved in [Initial/native_playback.json](Initial/native_playback.json) and [Initial/first_failure_context.json](Initial/first_failure_context.json). The diagnosis preceded the successor implementation: [initial_failure_diagnosis.json](initial_failure_diagnosis.json).

Generic correction: **phase4f.rigged-runtime-appearance-closure/1.0.0**. Runtime seeds plus appearance assets reached from actual mesh material slots are certified by package graph and native asset types, including Engine/plugin parents. Unknown, unbound and foreign character/animation/rig dependencies fail. UE script/transient graph containers remain traversed. Accepted R1/R2 files are unchanged. The successor changes one ownership assignment in memory; native motion/scale tests remain identical. Exact statement/hash evidence: [Final/playback_execution_identity.json](Final/playback_execution_identity.json).

R3 evidence version: phase4f.rigged-character-r3/1.0.0. Installed UE 5.8.3. This accepts the focused engineering route, not full deformation/contact/finger quality or packaging.

| Stage | Result |
| --- | --- |
| source_and_input_contract | PASS |
| input_validation | PASS |
| unit_classification | PASS |
| canonicalisation | PASS |
| semantic_mapping | PASS |
| ik_rig | PASS |
| manny_source | PASS |
| retarget_setup | PASS |
| animation_bake | PASS |
| authored_stature_preservation | PASS |
| appearance_UV_material_preservation | PASS |
| native_four_clip_playback_and_fresh_reload | PASS |
| typed_destination_runtime_closure | PASS |
| generic_ownership_regression_controls | PASS |
| Female_input_unit_semantics_replay | PASS |
| Female_fresh_native_regression | PASS |
| preservation | PASS |

## 2. Aegis source/input

Archive: `Characters/Aegis+NX-7.zip`, 6,172,882 bytes. SHA-256 `eb4967bb254d96009e34192609e4d32082ec932143db15f2b5c8578572d0f5fd`. Safe extraction retained one FBX and one supplied 4096×4096 JPEG, without rewriting them. FBX 7400 contains one geometry, one skin deformer, 61 clusters/bones, one material, one base-colour texture, one bind pose and no animation objects. Source control points: 26,120; all weighted; maximum influence count 5. Native triangulation/splits produce 26,230 vertices and 51,785 triangles.

Exact inventory and all source hashes: [archive_inventory.json](archive_inventory.json), [source_fbx.json](source_fbx.json). Normal import settings and native material/texture evidence: [import_inspection.json](import_inspection.json). The logging-only first inspection API failure is retained separately; it did not alter the source or implement a character repair.

## 3. v1 contract validation

**PASS.** One already-rigged/skinned humanoid Skeletal Mesh and one coherent connected 61-bone hierarchy rooted at `root`. Skeleton exists; parents resolve; reference transforms are finite/nonsingular. Zero invalid/unweighted native vertices; maximum weight-sum error 4.47034835815e-08. Integrated robot/armour geometry is part of this same weighted mesh. No assembly, new skinning or scope expansion was required. Evidence: [Initial/input_validation.json](Initial/input_validation.json).

## 4. Scale and stature representation

| Layer | Original | Final |
| --- | --- | --- |
| Source intrinsic / imported physical height | 179.912110 cm | 179.912110 cm |
| FBX UnitScaleFactor / OriginalUnitScaleFactor | 100 / 100 | Source unchanged; native unit representation handled |
| Root reference scale | 100 / 100 / 100 | 1 / 1 / 1 |
| Import uniform scale | 1 | 1; no reimport correction |
| Actor scale | 1 / 1 / 1 | 1 / 1 / 1 |
| Component relative/world scale | 1 / 1 / 1 | 1 / 1 / 1 |
| Effective reference world height | 179.912110 cm | 179.912110 cm |

Reported possible 1.8 factor: **baked_into_geometry_or_reference**, in the limited sense that the source already has approximately 1.799121 m intrinsic stature. No standalone 1.8 Model, import, actor or component multiplier exists. The archive supplies no external actor/component scene. A historical multiplication by exactly 1.8 cannot be established without its unscaled predecessor; current physical size is directly measured. Decision: **intrinsic_size_already_correct**; no extra stature conversion.

FBX axes: Up Y positive, Front Z positive, Coord X positive. Normal import uses scene conversion, no extra uniform scale, zero import rotation/translation and no scene-unit conversion toggle. Full numeric root translation/quaternion, child reference transforms, source Model scales and scene stack are preserved in [import_inspection.json](import_inspection.json) and [scale_transformation_ledger.json](scale_transformation_ledger.json). The uniform root 100 is a separate FBX/UE unit representation, not an intentional 1.8 stature layer. No doubling or loss of stature occurred.

## 5. Unit/root canonicalisation

**canonicalisation_required**, detected uniform factor 100. Existing `phase4f.rigged-unit-canonicalisation/1.0.0` applied unchanged to a private derived mesh/Skeleton. Root reference scale becomes 1; all non-root local translations receive the detected factor; root translation, rotations, names/parents, geometry and skin weights remain preserved. Physical bind size is invariant; maximum component bind-position error 1.01403698657e-05 cm, below the existing 0.001 cm allowance. Geometry/skin hash remains `4fcddf574e3b6e9bccae29ae988d4b2d78d0b17a7cecd9b340365f22ce5c7a49`. All six existing invariants passed: [Initial/canonicalisation.json](Initial/canonicalisation.json).

## 6. Semantic mapping

**23 automatic bindings: 22 chains plus pelvis**, including all ten fingers. UE automatic humanoid template resolution plus ancestry validation; no manual names/mappings. No unresolved requirement. Confidence is the exposed template match and structural validation; alternatives are not exposed by UE. Same binding structure as Female. Exact discovered names:

- Root: root
- Spine: spine_01 → spine_02 → spine_03
- Neck: neck_01
- Head: head
- LeftClavicle: clavicle_l
- LeftArm: upperarm_l → lowerarm_l → hand_l
- LeftLeg: thigh_l → calf_l → foot_l
- LeftFoot: ball_l
- LeftThumb: thumb_01_l → thumb_02_l → thumb_03_l
- LeftIndex: index_01_l → index_02_l → index_03_l
- LeftMiddle: middle_01_l → middle_02_l → middle_03_l
- LeftRing: ring_01_l → ring_02_l → ring_03_l
- LeftPinky: pinky_01_l → pinky_02_l → pinky_03_l
- RightClavicle: clavicle_r
- RightArm: upperarm_r → lowerarm_r → hand_r
- RightLeg: thigh_r → calf_r → foot_r
- RightFoot: ball_r
- RightThumb: thumb_01_r → thumb_02_r → thumb_03_r
- RightIndex: index_01_r → index_02_r → index_03_r
- RightMiddle: middle_01_r → middle_02_r → middle_03_r
- RightRing: ring_01_r → ring_02_r → ring_03_r
- RightPinky: pinky_01_r → pinky_02_r → pinky_03_r
- PelvisRetargetRoot: pelvis

Evidence: [Initial/semantic_mapping.json](Initial/semantic_mapping.json).

## 7. Destination IK Rig

**PASS.** Preview destination mesh; pelvis retarget/FBIK root; root motion bone `root`; all 22 required chains. Four generated hand/foot goals. The unchanged R2 route aligns leg goals/endpoints with the discovered Foot-chain start (ball convention), validates chain ancestry/goal bones/transforms and saves the rig. FBIK remains automatic, with stretch disabled. No manual edit. Native saved configuration: [Initial/ik_rig.json](Initial/ik_rig.json).

## 8. Manny → Aegis Retargeter

**PASS.** Same isolated Manny source-rig copy route; missing LeftFoot/RightFoot chains derived automatically from Manny semantics. Original Epic assets unchanged. All 22 stored mappings are exact semantic matches, plus pelvis binding; finite automatic target alignment; native FIKRetargetProcessor initialisation passed. Default pelvis/FK/IK operations retained; in-place root-motion operation disabled exactly as R2. No per-character offsets, multipliers or tuned pose. Evidence: [Initial/manny_source.json](Initial/manny_source.json), [Initial/retarget_setup.json](Initial/retarget_setup.json).

## 9. Destination animation bake

**PASS.** Same fixed R2 source set; newly baked destination Skeleton ownership, preserved durations, finite native key validation and unit root keys. Native root-lock behaviour is retained. The dependency correction reused these first-run saved assets; no re-bake was needed.

| Motion | Duration s | Rate | Keys | Native advance s |
| --- | ---: | ---: | ---: | ---: |
| neutral | 1.000000 | 60/1 | 61 | 1.007945 |
| idle | 7.566667 | 30/1 | 228 | 7.574651 |
| walk | 1.866667 | 30/1 | 57 | 3.736073 |
| run | 1.900000 | 30/1 | 58 | 3.804728 |

All exact final asset object paths:

    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial/Character/SK_Destination.SK_Destination
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial/Character/SKEL_Destination.SKEL_Destination
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial/Retarget/IK_Destination.IK_Destination
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial/Retarget/IK_MannySource.IK_MannySource
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial/Retarget/RTG_MannyToDestination.RTG_MannyToDestination
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial/Animations/Reference_Native.Reference_Native
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial/Animations/MM_Idle.MM_Idle
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial/Animations/MF_Walk_Fwd.MF_Walk_Fwd
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial/Animations/MM_Run_Fwd.MM_Run_Fwd
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7/R2_EndToEnd/Initial/Playback/L_DestinationProof

Evidence: [Initial/animation_bake.json](Initial/animation_bake.json), [result.json](result.json).

## 10. Native playback

**PASS** for reference, idle, walk and run, in a fresh main-project PIE world. Actual time advancement: one reference/idle cycle and two walk/run cycles. All 61 bone transforms finite; root, component and actor scales remain 1; unchanged limb-length tolerances pass. Distinct moving hands/feet are recorded. Neutral posed height matches 179.912 cm; no 100× elevation, 0.01× collapse or extra 1.8 multiplication.

| Motion | Pelvis Z cm | Max limb error cm | Native skinned snapshot Z cm |
| --- | ---: | ---: | ---: |
| neutral | 99.444 to 99.444 | 0.00000117 | -0.000 to 179.912 |
| idle | 97.285 to 97.654 | 0.00002583 | -1.029 to 176.402 |
| walk | 87.124 to 96.193 | 0.00000706 | -0.719 to 174.907 |
| run | 85.571 to 94.269 | 0.00000706 | 1.016 to 158.928 |

Final authoritative native evidence: [Final/native_playback.json](Final/native_playback.json). Eight native captures: [Final/NativePlayback](Final/NativePlayback/). Frontal reference/idle/walk/run frames were inspected; captures and transform telemetry jointly establish advancing animation, not still frames alone.

## 11. Appearance/deformation observations

One unchanged material slot `tripo_mat_1c5da8ca`, with its original imported MaterialInstanceConstant and supplied sRGB 4096×4096 texture. Normal UE import parent is `/InterchangeAssets/Materials/FBXLegacyPhongSurfaceMaterial`; this standard material dependency remains required. One UV set; exact source/destination triangle-UV hash `929680349476595f910f4a6304ed4e4286f232a3be28ef0796412215989788f1`. No artistic material or texture edit. White/dark/cyan robot appearance is visible in native captures.

No gross inversion/explosion or obvious tearing was seen in sampled frontal frames. This does not certify rigid armour behaviour, all-time intersections or hidden-side deformation. Idle/walk snapshots include roughly 1.03/0.72 cm mesh-bound penetration; run snapshot roughly 1.02 cm clearance. These are snapshot bounds, not certified stance/sole-contact metrics. No floor movement or contact repair. Independent finger motion/thumb naturalness and full quality suite were **NOT_RUN** under the fixed four-clip scope. Evidence: [appearance_audit.json](appearance_audit.json), [appearance_deformation_observations.json](appearance_deformation_observations.json).

## 12. Fresh reload

**PASS.** Authoring host closed; independent main project loaded saved destination mesh/Skeleton and all four native sequences from disk, with no authoring bridge loaded. Reference-root/height/Skeleton ownership verified before PIE. Final proof map was loaded from disk. Additional final native run used the exact final helper hash. All motion/reload checks passed.

## 13. Runtime independence

**PASS.** Recursive hard/soft/searchable/management package graph: 34 packages, zero foreign or authoring packages. One destination character, AnimSingleNodeInstance, zero source actors/live retarget nodes. No Manny/Female/John/Jane/donor mesh, source animation, IK Rig, retargeter, Copy Pose, live retarget or bridge is required for playback. Normal Engine, Interchange material-parent and original bound appearance packages are required; these are explicitly enumerated, not hidden by a broad folder allowance. Exact closure and typed certificate: [runtime_dependency_closure.json](runtime_dependency_closure.json).

## 14. Generalisation comparison

| Property | Female_Body_Rigged | Aegis NX-7 |
| --- | --- | --- |
| Surface | Body-only | Integrated textured robotic/armoured humanoid |
| Native bones | 61 | 61 |
| Native vertices / triangles | 27,699 / 52,540 | 26,230 / 51,785 |
| Physical reference height | 99.951173 cm | 179.912110 cm |
| Detected root factor | 100 | 100 |
| Extra stature conversion | None | None |
| Automatic bindings / fingers | 23 / 10 | 23 / 10 |
| Native fixed four clips | PASS | PASS |
| Final corrected ownership policy | PASS | PASS |

Female regression is isolated R3 evidence/map only: unchanged R2 input inspection, R1 classifier and R2 semantics replay **10/10**; fresh native saved-mesh/four-bake playback **4/4**. No accepted Female assets/evidence regenerated or overwritten. Synthetic ownership regression **20/20** covers valid bound appearance, unbound/same-folder content, unknown/missing/mixed classes, hidden foreign mesh/Skeleton/animation/rig/Blueprint, plugin-parent and transient-container edges. Evidence: [FemaleRegression/read_only_replay.json](FemaleRegression/read_only_replay.json), [FemaleFinal/native_playback.json](FemaleFinal/native_playback.json), [runtime_appearance_regression.json](runtime_appearance_regression.json), [generalisation_comparison.json](generalisation_comparison.json).

## 15. Product implications

R2 authoring generalised unchanged; its original folder-based closure gate did not. Aegis exposed a generic textured-input ownership defect, corrected by explicitly bound typed appearance ownership. Existing R1 already handles the measured root-unit representation. No new external-stature case was present or implemented. Robot/armour surface geometry did not prevent the one-mesh rigged/skinned humanoid path; supplied integrated appearance survived. This evidence gives no reason to alter v1 scope, and does not establish arbitrary rig-family support or finished skin/contact quality.

Manual character interventions: zero bone renames/reparents, manual mappings, tuned retarget offsets, stature multipliers, weight or material edits. Generic runtime policy work and instrumentation are engineering effort, not hidden subject repair. Elapsed wall time through result aggregation: 21.6 minutes; active time not measured. No UI, another subject, broad animation library or cook/package work.

## 16. Preservation

**PASS: 38,111 protected files; zero changed, zero missing.** Aegis ZIP/extracted FBX/JPEG/original imported character assets; accepted R1/R2 code/assets/evidence; Female/Manny; John/Jane; frozen protocols preserved. All current 29 John and 29 Jane confirmations verified, immutable events John 218/Jane 205 valid. Git HEAD/index/previous tracked status unchanged; existing Jane changes remain untouched. No staging/commit/push/config change. New work is confined to R3/Aegis authoring/evidence namespaces, with ordinary generated editor runtime/cache files excluded by existing project rules.

Audit: [preservation_audit.json](preservation_audit.json). Content/evidence/source hashes: [manifest.json](manifest.json). Original authoritative first failure and logging/inspection attempts are retained. Mandatory self-review checked input/scale provenance, exact AST change scope, final helper hash identity, four-clip source-free playback, Female regression and preservation. **Stopped at R3 classification.**
