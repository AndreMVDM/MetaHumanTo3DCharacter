🟢 **High confidence**

# Module R2 — End-to-End Rigged Character Acceptance

**PASS — 38/38 required criteria, plus the native reference helper.** `Female_Body_Rigged`, an already-rigged and already-skinned Tripo humanoid, was automatically validated, unit-canonicalised, mapped to Manny semantics, configured for UE IK retargeting, baked to destination-native idle/walk/run animations and played independently in Unreal Engine without a live Manny/source/retarget dependency.

Module version: `phase4f.rigged-character-r2/1.0.0`. Engine: installed UE 5.8.3. Prerequisite consumed unchanged: `phase4f.rigged-unit-canonicalisation/1.0.0` and its [authoritative R1 result](../UnitCorrection/README.md).

This accepts the focused automatic engineering pipeline for this one benchmark. It does not accept full deformation/contact/finger quality, unknown rig families, cook/package deployment or a polished wizard. No other benchmark character was processed.

## 1. Executive result and stage matrix

| Required stage | Result | Evidence |
| --- | --- | --- |
| Input rig/skin/hierarchy validation | PASS | [input_validation.json](input_validation.json) |
| Unit classification | PASS | [unit_classification.json](unit_classification.json) |
| Unchanged R1 canonicalisation and invariants | PASS | [canonicalisation.json](canonicalisation.json) |
| Humanoid semantics, including ten fingers | PASS | [semantic_mapping.json](semantic_mapping.json) |
| Destination IK Rig | PASS | [ik_rig.json](ik_rig.json) |
| Manny source configuration | PASS | [manny_source.json](manny_source.json) |
| Stored mapping, finite alignment, native processor initialisation | PASS | [retarget_setup.json](retarget_setup.json) |
| Reference helper and three destination bakes | PASS | [animation_bake.json](animation_bake.json) |
| Advancing destination-only native playback | PASS | [native_playback.json](native_playback.json) |
| Fresh main-project asset/map reload | PASS | [native_playback.json](native_playback.json) |
| Recursive runtime dependency closure | PASS | [native_playback.json](native_playback.json) |
| Preservation | PASS | [preservation_audit.json](preservation_audit.json) |

The final authoring invocation completed all automatic stages without intermediate asset repair. The native verification ran in a separate main-project process, with the authoring process already closed. Machine-readable acceptance enumerates the user's 38 conditions in [result.json](result.json).

## 2. Input validation

Input mesh:

    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/Character/SK_FemaleBodyRigged.SK_FemaleBodyRigged

Associated Skeleton:

    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/Character/SK_FemaleBodyRigged_Skeleton.SK_FemaleBodyRigged_Skeleton

The native mesh contains 61 bones, 27,699 source vertices and 52,540 triangulated faces. Skin weights exist and are complete: zero invalid/unweighted vertices; maximum weight-sum error approximately 0.0000000456. The actual mesh bone indices resolve to a single connected hierarchy; native parents resolve to valid bones; transforms are finite and nonsingular. UE's transient automatic humanoid analysis resolves all required chains before derived retarget assets are created. Validity comes from the loaded assets and geometry/weight APIs, not filenames.

Unsupported inputs fail at their stage with explicit reasons, including missing mesh/Skeleton, invalid hierarchy/reference transforms/weights, unsupported scale representation and insufficient humanoid chains. Disconnected surface islands and material slots are not rejected merely for being present; they remain part of the existing skinned mesh. No skin repair was performed.

## 3. Canonicalisation

Detector result: `canonicalisation_required`, finite positive isotropic root factor **100**. Route: **generated canonical derived asset** using unchanged R1 `plan`/`derive`. No compensation was introduced into actor or retarget settings. The original-canonical route is also explicitly represented in the implementation, but this benchmark exercised the derived route.

Final mesh and Skeleton:

    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/Final/Character/SK_Destination.SK_Destination
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/Final/Character/SKEL_Destination.SKEL_Destination

Root reference scale is one. Names and hierarchy are identical; geometry/weights hash is exactly identical (`10b18d452db7724db6b47ab12823bf9512aa66401792ba8246a948bb0fc77594`). Bind height remains **99.95117324217154 cm**. Component bind-position error remains within the established R1 0.001 cm verification tolerance (approximately 0.00000452 cm observed). Root translation and rotations were preserved; all non-root local reference translations were converted by the detected factor. Derived inverse binds and Skeleton reference pose were synchronised. No landmark or skin-weight change occurred.

## 4. Semantic analysis

**23 semantic bindings: 22 named chains plus the pelvis retarget-root binding.** Root, Spine, Neck, Head, bilateral Clavicle/Arm/Leg/Foot and bilateral Thumb/Index/Middle/Ring/Pinky chains are resolved. Hands and feet are recorded through the discovered chain endpoints/paths, including the foot-to-ball anatomy in each leg. All ten three-bone finger chains exist and map.

Every assignment records its discovered destination bones, resolution method, requirement, confidence and validation result. Resolution uses UE auto-characterisation and validates actual bone existence and ancestry. No benchmark bone names are supplied by the configuration. UE exposes a template match rather than a probability or alternative-candidate list; no missing or conflicting required assignment was exposed on this input. This is not proof of automatic semantic resolution for arbitrary unknown naming schemes.

## 5. Destination IK Rig

    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/Final/Retarget/IK_Destination.IK_Destination

Preview mesh: SK_Destination. Retarget root: pelvis. Root-motion bone: root. **22 chains**, including Root, three torso/head chains, eight bilateral major-body chains and ten finger chains. UE automatic FBIK is configured. LeftHandIK/RightHandIK goals bind to the discovered hands; LeftFootIK/RightFootIK bind to the discovered ball bones. Leg chain ends match those ball goals, following the proven common source convention. Endpoints/ancestry and finite goal transforms were validated before save.

## 6. Manny source and IK Retargeter

Original source assets remain unchanged:

    /Game/Characters/Mannequins/Meshes/SKM_Manny_Simple
    /Game/Characters/Mannequins/Rigs/IK_Mannequin

The original source rig lacks LeftFoot/RightFoot chains required by the destination. R2 makes an isolated source rig copy and adds just those two chains, using endpoints discovered from UE's source auto-characterisation:

    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/Final/Retarget/IK_MannySource.IK_MannySource

Retargeter:

    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/Final/Retarget/RTG_MannyToDestination.RTG_MannyToDestination

Source rig: IK_MannySource; target rig: IK_Destination. Both retarget roots are pelvis. **All 22 stored chain mappings match exactly**, including all ten digits; automatic target chain alignment produces finite pose offsets. The installed native FIKRetargetProcessor initialises successfully before baking.

Enabled operations: Pelvis Motion, FK Chains, Run IK Rig and Remap Curves. Root Motion is disabled for these registered in-place clips. Pelvis translation offsets are zero; horizontal/vertical multipliers remain one. No character-specific height, root/pelvis offset, 0.01 or 100 retarget compensation was added. Existing REF_POSE root locking remains enabled in the baked motions.

## 7. Animation bake

All sequences belong to SKEL_Destination. Native key validation inspects every stored bone key for finite transforms, unit root scale and gross local-translation explosion. Source durations are retained.

| Sequence | Duration (s) | Rate | Keys |
| --- | --- | --- | --- |
| Reference_Native | 1.0 | 60 Hz | 61 |
| MM_Idle | 7.566666603 | 30 Hz | 228 |
| MF_Walk_Fwd | 1.866666675 | 30 Hz | 57 |
| MM_Run_Fwd | 1.899999976 | 30 Hz | 58 |

Exact destination paths:

    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/Final/Animations/Reference_Native.Reference_Native
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/Final/Animations/MM_Idle.MM_Idle
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/Final/Animations/MF_Walk_Fwd.MF_Walk_Fwd
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/Final/Animations/MM_Run_Fwd.MM_Run_Fwd

Registered motion sources are the unchanged Phase3B SourceAnimations/InPlace/MM_Idle, MF_Walk_Fwd and MM_Run_Fwd assets. Reference_Native is this destination's own reference helper, not a replacement common fixture.

## 8. Native playback

Saved destination-only proof map:

    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/Final/Playback/L_DestinationProof

One native SkeletalMeshActor uses AnimSingleNodeInstance and the destination sequences. There is no live retarget/Copy Pose animation blueprint. Actor and component scale remain one at the origin; the fixed floor is Z=0. All observed native bone transforms and sampled posed surfaces are finite. Maximum observed limb-length error is below **0.000012 cm**. Reference surface height is approximately **99.95119 cm**, matching the unchanged bind size within native arithmetic tolerance.

| Task | Native result | Observed animation advance (s) | Settled pelvis Z (cm) | Representative settled motion |
| --- | --- | --- | --- | --- |
| Neutral | PASS | 1.00414 | 52.12298 | Reference stable |
| Idle | PASS | 7.57192 | 51.00193–51.19959 | Left hand excursion 2.103 cm |
| Walk | PASS | 3.73674 | 45.56256–50.33011 | Left hand 35.082 cm; left ball 64.331 cm |
| Run | PASS | 3.80165 | 44.56214–49.30547 | Left hand 23.476 cm; right ball 51.098 cm |

These native observations cover a full idle and two walk/run cycles. Motion summaries exclude the first 0.25 seconds of native animation advancement after a clip switch, so a transition from the previous clip cannot masquerade as that clip's motion. Raw observations are retained. Root scale stays one; no elevated-placement, 100x multiplication or 0.01x collapse remains. [Native captures](NativePlayback/) show advancing walk/run poses near the floor; detailed deformation/contact quality was not classified from them.

## 9. Fresh reload

The authoring commandlet closed before verification. A fresh main-project editor loaded the saved destination mesh, Skeleton and sequences and reloaded the saved proof map before native PIE. The final strengthened playback process opened that destination-only map directly. Its script did not load the source IK Rig or retargeter for authoring inspection. No authoring bridge or correction host was loaded. All four tasks passed from disk.

## 10. Runtime independence

Runtime playback requires no Manny mesh/actor/source component, live IK Retargeter, Retarget Pose From Mesh, Copy Pose, donor or authoring bridge. The authoring bridge is used only to create/synchronise derived Skeleton assets and validate retarget initialisation/raw keys. Native destination playback runs in the unmodified main project where that bridge is absent.

The result is an independent native animated SkeletalMeshActor and destination animation assets. Player movement/controllers, a production AnimBP and polished UI are not claimed by this module.

## 11. Dependency closure

Recursive hard/soft package and management dependency inspection starts from the saved proof map, final mesh/Skeleton and all four sequences. The final closure contains **26 packages**, with zero foreign Game packages and zero authoring packages. Intentional dependencies are the R2 destination assets, normal Engine/Script packages and standard ACL compression assets/plugin references. Authoring IK assets may remain for rebaking but are outside runtime seed closure. No source FBX, John/Jane, other character or previous UnitCorrection helper is required.

## 12. Preservation and self-review

**38,035 protected files unchanged; zero missing/changed.** Original mesh/Skeleton binaries, archive/FBX, geometry/weights, R1 source/assets/evidence, Manny/common sources, John/Jane and frozen protocols are protected by the before/after hashes. John retains 29 valid approvals and 218 immutable events; Jane retains 29 valid approvals and 205 immutable events. Freeze/dependency and human-signature audits passed without re-running anatomy/fitting/review.

Git HEAD, index hash and the nine pre-existing tracked Jane changes remain unchanged. No staging, commit, push, branch change or Git configuration mutation was performed. New code/assets/evidence remain in the R2-specific folders; generated host/cache state is ignored, including the authoring host's Content junction.

[Self-review](self_review.json) passed seven independent evidence checks. Implementation findings corrected: use supported controller endpoint accessors; distinguish actual mesh bones from absent shared-Skeleton bones; exclude clip-switch settling from motion acceptance; keep authoring inspection out of independent playback; tie acceptance to current destination asset lineage; allow explicitly validated original destination mesh/Skeleton seeds for an already-canonical route. Two development failures and the first native observations are preserved as audit history. Their derived candidate is not the final runtime seed.

No intermediate character repair occurred: no bone rename/reparent, manual mapping assignment, skin edit, landmark movement, source-fixture change or retarget offset tuning.

## 13. Wizard Product Implications

| Conceptual wizard stage | Engineering readiness from R2 |
| --- | --- |
| Select Character | Loaded SkeletalMesh input contract ready; selection UI not built |
| Validate Character | Rig/skin/hierarchy/finite-reference checks and stage failures ready |
| Detect Units | Unchanged R1 classifier ready for supported representation |
| Canonicalise | Automatic derived route ready; unsupported representations rejected |
| Analyse Skeleton | Proven UE template/ancestry path ready; unknown rigs/ambiguous naming need further engineering and validation |
| Configure Manny Mapping | Required semantics and actual chain-map verification ready on the demonstrated route |
| Generate Retarget Assets | Automatic isolated IK/FBIK/source-copy/retarget alignment and native initialisation ready |
| Bake Animations | Fixed destination-native idle/walk/run generation and key validation ready |
| Verify Character | Fresh native advancement, scale/placement and runtime seed closure checks ready |
| Finish | Machine-readable stage result, provenance and preservation audit ready |

The proven core is suitable for later wizard integration. Packaging the editor bridge into the eventual plugin, transactional cancellation/rerun/output ownership, friendly failure UX and wider rig/material provenance validation still need product engineering. This single benchmark does not demonstrate every clothed/armoured/robotic/stylised input, nor weaken the declared already-rigged/skinned one-mesh v1 scope.

Separate clothing/accessory assembly, unrigged auto-skinning, skin repair, cloth/hair/facial systems, quadrupeds and deformation optimisation remain deliberately outside this v1 path. Polished UI, full visual-quality certification, full Manny-library conversion and package/cook work remain outside R2.

## Execution and changed files

The engineering runner is [run.ps1](../../../../../../Working/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2/run.ps1). It executes native authoring, launches fresh main-project native playback, then aggregates acceptance and preservation. Existing asset namespaces are refused rather than overwritten; a reproducibility run must select a fresh output namespace and preserve this accepted evidence. The configured final run completed end-to-end, followed only by the stricter native self-review verification.

    Working/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2/
        config.json, run.ps1, author.py, playback.py, finalise.py
        AuthoringHost/ (isolated editor-only bridge, generated outputs ignored)
    Content/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2_EndToEnd/
        Final/Character, Final/Retarget, Final/Animations, Final/Playback
        Character/ (preserved failed development candidate; not runtime)
    Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/R2_EndToEnd/
        stage evidence, baseline, native captures, audits, result and this report

**No remaining R2 blocker. Work stops at this accepted module boundary.** No second character, broader quality/validator work, UI or cook/package work was started.
