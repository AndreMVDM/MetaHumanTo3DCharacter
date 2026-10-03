# Rigged uniform-root unit correction — focused native result

The imported-unit retarget/playback blocker is resolved for neutral/reference, idle, walk and run. Each passed advancing native PIE playback at normal and quarter speed, first through live retargeting, then through destination-native sequences in a fresh main-project UE process. This is a focused scale/placement result, not full Benchmark 1 quality acceptance.

Correction version: **phase4f.rigged-unit-canonicalisation/1.0.0**. Installed engine: UE 5.8.3. No frozen anatomy, motion-quality or source-fixture policy was changed.

## Root cause and transform spaces

The FBX declares UnitScaleFactor 100 (metre source units). The imported mesh already measures 99.95117324217154 cm high. Its actor/component scale is 1, but the reference root carries scale 100; descendant translations remain in the pre-root representation. The original reference pelvis local Y is approximately -0.52123, which the rotated/scaled root maps to component Z 52.122979 cm. Root translation is already component centimetres and must not be multiplied again.

UE's IK retarget pose resolver computes component reference translations and strips scale to one. Its batch baker converts that scale-free component output to local animation keys. Those keys contain a pelvis translation around 52 cm and unit root scale. The original destination's forced REF_POSE root lock then restores the **entire reference root transform**, including its scale 100. It scales the newly baked centimetre translations again: native pelvis Z was approximately 5212.44 cm. This is a representation mismatch in the retarget/bake path; skin weights and source anatomy are not its cause.

Offline AnimPose evaluation with incorporate_root_motion_into_pose enabled sets bIgnoreRootLock. It therefore sees the baked unit root instead of the native reference-root reset, explaining the earlier scale-collapse versus native elevated-placement discrepancy.

Installed source supporting this diagnosis:

- IKRig/Private/Retargeter/IKRetargetProcessor.cpp: FResolvedRetargetPoseSet::AddOrUpdateRetargetPose strips local/component scale.
- IKRigEditor/Private/RetargetEditor/IKRetargetBatchOperation.cpp: scale-free source evaluation and local destination key generation.
- Engine/Public/Animation/AnimCompressionTypes.h: FRootMotionReset::ResetRootBoneForRootMotion replaces the root with RefPoseRootTransform for REF_POSE.
- AnimationBlueprintLibrary/Private/AnimPose.cpp: evaluation option sets bIgnoreRootLock.

| Transform stage | Original representation | Corrected derived representation |
| --- | --- | --- |
| FBX/import units | Metres converted to UE centimetres; unit factor stored in root | Original unchanged |
| Mesh vertices / weights | Already centimetres / complete original skin | Identical |
| Reference root scale | 100 | 1 |
| Root local translation / rotation | Already component-cm offset / FBX axis rotation | Unchanged |
| All non-root local translations | Pre-root units | Multiplied by detected uniform root factor |
| Component-space bind positions | Correct physical size and location | Preserved within native arithmetic error |
| Source/destination retarget space | Scale-free solver incompatible with original local units | Both solver and destination reference use centimetres |
| IK root settings | Ordinary in-place setup; no compensating subject offset | Same policy; no tuned height multiplier |
| AnimSequence / native root lock | Unit animation root conflicts with 100 reference root | Unit animation root agrees with unit reference root |
| Actor / component / floor | Scale 1 / scale 1 / floor Z 0 | Unchanged |

## Generic correction

For a single connected root with finite positive isotropic scale s, duplicate the destination mesh and its associated skeleton into an isolated derived namespace. Set reference root scale to one and multiply **every non-root local translation** by s. Keep root translation, rotations and descendant scales unchanged. Rebuild derived inverse binds and synchronise the cloned USkeleton reference pose. Preserve bone names, parents, geometry and weights.

The planner detects the factor from reference transforms, with no vendor, character, bone-name, component-ID or stature constant. Unit-root inputs need no derived conversion. Nonuniform, nonpositive, nonfinite or invalid/disconnected hierarchies are rejected rather than guessed. Native assertions certify the resulting representation before retargeting. This supported uniform-root case is suitable for automatic detection in a future Rigged Body Wizard; broader scale/shear representations require their own certified conversion.

Python source: [rigged_unit_canonicalisation.py](../../../../../../Working/Phase4F/rigged_unit_canonicalisation.py). A minimal editor-only RiggedUnitBridge in the run's UnitNativeHost exposes isolated skeleton attachment and reference synchronisation, which the installed Python API does not expose. The playback assets have no bridge dependency. No final plugin or UI integration was implemented.

## Native proof

| Task | Live normal / quarter speed | Fresh baked normal / quarter speed | Live pelvis Z (cm) |
| --- | --- | --- | --- |
| Neutral/reference | PASS / PASS | PASS / PASS | 52.23204 (retarget reference); own bind 52.12298 |
| Idle | PASS / PASS | PASS / PASS | 51.00177–51.19957 |
| Walk | PASS / PASS | PASS / PASS | 45.54569–50.34427 |
| Run | PASS / PASS | PASS / PASS | 44.55925–49.32268 |

Actual native game-world playback advanced. Hands/feet visibly change pose in walk/run captures and native transform samples. Root scale remains exactly one; no 100x or 0.01x size/placement error remains. Bind height remains 99.95117324217154 cm. Maximum component bind-position error is 0.00000451114 cm; maximum baked limb-length error is 0.0000118775 cm. Geometry/skin hash is exactly unchanged. The character's imported stature was preserved, not enlarged to a presumed adult height.

Native evidence: [live proof](native_live_proof.json), [fresh baked proof](native_baked_proof.json), [live captures](NativeLivePIE/), [baked captures](NativeBaked/), [canonicalisation invariants](canonicalisation.json).

Baked observations include the previous clip's pose during asynchronous clip-switch settling. Those raw samples are retained; they are not pure steady-state motion extrema. Native surface snapshots remain near the unchanged floor: sampled walk minimum Z reached -0.15098 cm, run -0.03686 cm, and idle approximately 0.104–0.146 cm. These are contact diagnostics/review triggers under the unchanged quality protocol, not certification of foot/contact quality. Flat native captures establish motion and placement but do not certify detailed deformation quality.

## Assets and reload

All derived assets are under:

    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/UnitCorrection

Character/SK_Canonical and Character/SKEL_Canonical retain the original 61-bone hierarchy and skin. Retarget/RTG_Canonical uses 22 exact named chain mappings plus the pelvis retarget-root binding (23 semantic bindings). Live authoring assets and Playback/L_BakedProof are isolated here.

Only the three motion bakes were generated after the live proof passed. Reference_Native is a destination's own reference-pose helper, not a replacement for any frozen common fixture.

| Destination animation under Animations/ | Duration (s) | Rate | Keys |
| --- | --- | --- | --- |
| Reference_Native | 1.0 | 60 Hz | Reference helper |
| MM_Idle | 7.566666603 | 30 Hz | 228 |
| MF_Walk_Fwd | 1.866666675 | 30 Hz | 57 |
| MM_Run_Fwd | 1.899999976 | 30 Hz | 58 |

The common idle/walk/run sources remain the registered Phase3B SourceAnimations/InPlace assets. Their baked root flags remain enable_root_motion=false, force_root_lock=true and REF_POSE; root locking was not disabled to hide the mismatch.

A fresh main-project editor process loaded the saved destination assets and played them through native SingleNode PIE. It contained no source actor, no live retarget node and no loaded authoring bridge. Dependency closure contains the derived character/skeleton/sequences plus ordinary engine/plugin packages, with no foreign Game packages, authoring packages or bridge references. See [native_bake.json](native_bake.json) and [native_baked_proof.json](native_baked_proof.json).

## Preservation, regression and stop boundary

[Preservation audit](preservation_audit.json): 27,129 protected files unchanged, zero missing. Original archive/FBX hashes remain preserved. Fresh original mesh inspection matches its pre-correction hierarchy/bind, geometry/skin, bone count and bounds hashes; original asset write times still precede this correction. John retains 29 approvals/218 events and Jane 29 approvals/205 events. Frozen policies and common sources remain preserved. Git's pre-existing tracked Jane changes remain unchanged; no Git mutation was performed.

[Regression controls](unit_plan_regressions.json): 9/9 pass. They cover arbitrary bone names and rotated/translated roots at factors 1, 0.01, 100 and 2.54, and rejection of nonuniform, negative, zero, nonfinite and cyclic inputs.

Changed/added scope: the generic Python correction; run-local native editor bridge/host; focused setup, live proof, bake, reload and audit scripts; derived UnitCorrection assets; and this evidence/report directory. UnitNativeHost/.gitignore excludes generated host output and its Content junction. The original Character assets were not changed.

Earlier failed API attempts and scale-invalid benchmark bakes are retained as diagnostic history. static_editor_control_non_authoritative.json does not prove live animation because its editor pose did not advance; native_live_proof.json supersedes it. Broad-suite/clean-project/cook attempts made before the course correction remain historical and were not resumed.

**No remaining unit-representation blocker in these four tests.** Full benchmark deformation/contact/finger quality, root-motion clips and package/cook acceptance remain outside this focused result. Work stops here: no full-suite rerun, further clean-project/cook work, UI integration, other subjects or validator expansion.
