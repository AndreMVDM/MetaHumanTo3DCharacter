# Final hands-on acceptance — Female_Body_Rigged

🟢 **High confidence**

**FINAL_ACCEPTANCE_READY — technical PASS.** The user corrected the requested input from an unavailable rigged Jane to `Characters/Female_Body_Rigged.zip`. This report is the authoritative continuation; early Jane input-discovery HOLD evidence remains preserved as historical evidence. Historical unrigged Jane was not processed or substituted.

All **89/89** accepted R4 default animations were freshly baked to a new Female destination Skeleton. Complete fresh reload, eight representative native playback tasks and nine native interactive control tasks pass. No shared R1/R2/R3/R4 implementation changed, no manual bone mapping, subject-specific rig/skin/retarget repair or aesthetic tuning was introduced. This repeats the previously accepted Female source with the full R4 library; it is not a claim about a new third character.

**Editor process 38556 is open on the final Female review level, PIE stopped, ready to press Play.** Human visual acceptance remains Andre's decision.

## Input and units

Confirmed source archive:

    E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Characters\Female_Body_Rigged.zip

The archive's single FBX hash exactly matches the existing imported source:

    E:\Repo\UE\Projects\MetaHumanTo3DCharacter\Working\Phase4F\BenchmarkRuns\01_FemaleBodyRigged\Input\tripo_convert_cacfc500-a133-4b70-abe0-51d9c097585a.fbx
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/Character/SK_FemaleBodyRigged.SK_FemaleBodyRigged
    /Game/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/Character/SK_FemaleBodyRigged_Skeleton.SK_FemaleBodyRigged_Skeleton

No reimport was needed. Current native inspection revalidated **61 bones, 27,699 source vertices, 52,540 triangles**, one connected hierarchy, finite nonsingular reference transforms, complete weights and **zero invalid/unweighted vertices**. Maximum native weight-sum error is 4.563480615615845e-08.

Unchanged `phase4f.rigged-unit-canonicalisation/1.0.0` classified the uniform reference-root factor 100 as canonicalisation_required. A private destination mesh/Skeleton was generated; root reference scale is one. Names, hierarchy, geometry/skin hash, physical height and component bind positions pass all six existing invariants. Maximum bind-position error is **0.000004511139116 cm**, below the unchanged 0.001 cm allowance.

**Physical reference stature remains 99.95117324217154 cm.** No height normalisation or retarget compensation was added. Camera and capsule use this measured height; actor/component scales remain one. Walk/run remain 300/600 cm/s and CharacterMovement jump remains 420 cm/s. The floor remains Z=0. The review camera/capsule adaptation is presentation/collision sizing, not mesh/rig/stature modification.

The source slot `tripo_mat_cacfc500` already binds `/Engine/EngineMaterials/WorldGridMaterial`. The original binding is retained, so default/grid shading is expected. No material/texture repair or appearance replacement was performed.

## Stage matrix and comparison

| Area | Aegis R4 | Confirmed Female final test |
| --- | --- | --- |
| Rigged/skinned v1 input contract | PASS | PASS |
| Unit/root handling | PASS | PASS — unchanged R1, root 100 → 1 |
| Physical reference height | 179.912 cm | 99.951 cm, preserved |
| Automatic semantic bindings | 23 | 23 |
| Finger chains | 10 | 10 |
| Native retarget processor initialisation | PASS | PASS |
| Default library expected | 89 | Same authoritative 89 |
| Default library attempted/baked | 89/89 | 89/89, zero failures |
| Fresh complete library reload | PASS | PASS |
| Representative native playback | PASS | PASS — eight roles |
| Idle/walk/run | PASS | PASS |
| Jump/fall/land/ground return | PASS | PASS |
| WASD | PASS | PASS |
| Shift run | PASS | PASS |
| Mouse look | PASS | PASS |
| Space / actual CharacterMovement jump | PASS | PASS |
| Destination-only runtime | PASS | PASS |
| Subject-specific repair | None | None |
| Human visual acceptance | Andre's review | Pending Andre's review |

The unchanged R2 authoring algorithm was executed with only its profile/evidence binding changed, certified by normalised AST identity. It automatically resolved **22 chains plus pelvis**, including all ten fingers, validated ancestry, created FBIK/hand/ball goals, generated the isolated Manny source-rig foot-chain configuration, saved exact mappings and initialised native FIKRetargetProcessor. Exact discovered bone names/configuration are in [R2/semantic_mapping.json](R2/semantic_mapping.json), [R2/ik_rig.json](R2/ik_rig.json) and [R2/retarget_setup.json](R2/retarget_setup.json).

## Library and native validation

The accepted R4 manifest was reused without rediscovery or reclassification: **56 Locomotion, 13 Jump, 20 Actions**. The 18 optional additive/support sequences remain optional; 21 exclusions remain excluded. Every default source path, category, root flags and deterministic naming policy are retained. No Aegis destination animation was copied as a Female animation.

The accepted R4 bake, fresh-validation and native representative playback scripts were consumed byte-for-byte unchanged with a new profile. Root operation selection uses extraction flags or an actual nonconstant source-root trajectory, with the unique parentless source root. Independent source-bound trajectory certification remains unchanged; the measured target/source reference pelvis-height ratio here is **0.5435320971563735**, rather than Aegis's ratio. This is generic measured proportional retargeting, not a 0.01/100 unit workaround.

All 89 sequences pass authoring-time native finite/unit-root checks, source-bound root certificates, all-frame evaluation and body-size checks. A fresh main-project process, without the authoring bridge, loaded all 89 from disk and repeated ownership, duration, finite pose, root, metadata and saved-hash validation. There is no scale collapse, 100× elevation or invalid-root acceptance.

Metadata follows the accepted R4 policy: root flags, curve names, notify classes/names/counts, sync marker names/times and metadata classes match. Typed source Sequencer editing links are detached only from derived outputs. Exact notify trigger times/durations and full curve values retain R4's documented Python API audit limitations; native duplication preserves their payload. No source asset was edited.

Eight normal-rate native destination-only representatives pass: **MM_Idle, MF_Unarmed_Walk_Fwd, MF_Unarmed_Jog_Fwd, MM_Jump, MM_Fall_Loop, MM_Land, MF_Unarmed_Walk_Right, MM_Attack_01**. Each completes an observed cycle, with finite bones, unit actor/component/root scale, preserved limb lengths and no elevated actor/source/live-retarget. [native_library.json](native_library.json) and captures retain evidence.

## Playable review and observations

The accepted R4 review design was copied into isolated Female assets. All six sequence-player bindings and the AnimBP target Skeleton/Character mesh were replaced by Female destination assets before final save. No Aegis destination mesh/Skeleton/animation remains in runtime closure. Fractional timers retain the proven real/double Blueprint type.

All nine actual PlayerController input tasks pass: Idle, W, Shift+W, S, A, D, mouse yaw, mouse pitch and Space. Native observations show rising jump, descending fall, landing playback to completion and grounded locomotion return. Sequence players independently advance in each active phase. Observed capsule rise is **85.55556239353021 cm**. No direct pawn movement or direct Jump call was used by the verification harness.

The supplied body/default material remains visible. Sampled frontal playback shows no gross mesh explosion or obvious material loss. All-time contact, fingers/thumb naturalness, hidden-side intersections and aesthetic deformation are not certified by these technical tests; no shoulder, skin, foot/contact or animation repair was attempted. Watch the preserved approximately one-metre stature and default/grid material during personal review.

Two review-authoring API binding errors (unexposed preview property and a required transform setter argument) are preserved in attempt evidence. They were corrected only in the new consumer script; they did not change any shared algorithm, policy, source character or retarget tuning. Final technical classification remains FINAL_ACCEPTANCE_READY, without a new generic backend fix.

## Exact final asset paths

    Mesh: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/R2_EndToEnd/Character/SK_Destination.SK_Destination
    Skeleton: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/R2_EndToEnd/Character/SKEL_Destination.SKEL_Destination
    Destination IK Rig: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/R2_EndToEnd/Retarget/IK_Destination.IK_Destination
    Manny source-rig copy: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/R2_EndToEnd/Retarget/IK_MannySource.IK_MannySource
    Retargeter: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/R2_EndToEnd/Retarget/RTG_MannyToDestination.RTG_MannyToDestination
    Library: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/Animations/LibraryV1/
    Jump: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/Animations/LibraryV1/Jump/MM_Jump.MM_Jump
    Fall: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/Animations/LibraryV1/Jump/MM_Fall_Loop.MM_Fall_Loop
    Land: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/Animations/LibraryV1/Jump/MM_Land.MM_Land
    Character: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/ReviewV1/BP_FemaleBodyMovementReviewCharacter.BP_FemaleBodyMovementReviewCharacter
    AnimBP: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/ReviewV1/ABP_FemaleBodyMovementReview.ABP_FemaleBodyMovementReview
    GameMode: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/ReviewV1/BP_FemaleBodyMovementReviewGameMode.BP_FemaleBodyMovementReviewGameMode
    Level: /Game/MetaHumanTo3DCharacter/RiggedCharacters/FemaleBodyRigged/FinalAcceptance/ReviewV1/L_FemaleBodyMovementReview

## Runtime, preservation and effort

Strict recursive runtime closure passes for all animations and the final review. No Manny/Quinn mesh/source Skeleton, source IK/live retargeter, Copy Pose/Retarget Pose node, Aegis, historical John/Jane/donor asset or authoring bridge is required. Only the Female destination/runtime seeds, original material and normal Engine/Script/plugin dependencies remain. Authoring assets stay outside playback closure. See [fresh_validation.json](fresh_validation.json).

The baseline includes **43,082 protected files**. No authored asset, source, human evidence, frozen protocol or accepted R1/R2/R3/R4 result changed or disappeared. UE automatically changed three and rotated four generated authoring-host `Saved` files (SDK log metadata and uncontrolled-changelist state). One previous agent-owned R4 editor runtime log received a verified append. The raw strict hash audit retains these differences; [preservation_classification.json](preservation_classification.json) separates generated/runtime activity from immutable authored evidence. No diagnostic evidence was deliberately deleted. Git HEAD/index and all pre-existing tracked changes remain identical; nothing was staged, committed or pushed.

Twenty-one independent final checks pass in [final_acceptance.json](final_acceptance.json). [animation_library_manifest.json](animation_library_manifest.json) records every source → Female destination mapping. [input_selection.json](input_selection.json) records the user's source correction and archive/FBX identity.

User intervention: one input-selection correction. Manual bone mapping, rig/weight repairs, retarget tuning, landmark moves and human-review changes: **zero**. Native verification inputs are automation evidence, not human aesthetic approval. Active human time was not measured.

## Human handoff and stop

**Press Play.** Possession is automatic. **WASD** moves; **mouse** looks; **Shift** runs; **Space** jumps. The camera follows the measured-size character. Floor Z=0, saved final map loaded, PIE stopped, useful editor view, Editor PID 38556 remains open. The previous agent-owned Aegis review window was replaced; the unrelated original editor was untouched.

Technical result: **FINAL_ACCEPTANCE_READY**. Personal visual acceptance is pending. No wizard UI, other character, unrigged route, skin/deformation/contact repair, foot IK, cook/package or further system was started. Stop boundary reached.
