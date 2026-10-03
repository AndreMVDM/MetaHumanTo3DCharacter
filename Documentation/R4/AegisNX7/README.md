# Module R4 — Aegis NX-7 animation library and playable jump review

🟢 **High confidence**

**PASS — technical R4 acceptance.** Aegis owns 89 destination-native mannequin body sequences. Fresh native representative playback and all nine interactive control phases pass. Unreal Editor process 48184 remains open on the final review level, with PIE stopped and ready to press Play. Human judgement of motion/deformation quality remains Andre's review.

## Discovery and classification

The project and the installed UE 5.8 mannequin template were inspected through the native asset registry and loaded animation data. The installed source root is:

    D:\Epic Games\UE_5.8\Templates\TemplateResources\High\Characters\Content\Mannequins

Its 102 candidate packages were copied byte-for-byte into isolated R4 source content; original and staged hashes remain identical. The inventory also includes existing project mannequin sequences and helpers. Source ownership is the native shared mannequin Skeleton:

    /Game/Characters/Mannequins/Meshes/SK_Mannequin.SK_Mannequin

Manny/Quinn variants with different evaluated motion are retained. One exact evaluated-frame/metadata duplicate MM_Idle is excluded; no equivalence is inferred merely from a masculine/feminine name. Assets with curves/notifies are conservatively excluded from cross-path fingerprint deduplication because their complete payload equivalence was not independently established.

| Classification | Count | Treatment |
| --- | ---: | --- |
| BAKE_DEFAULT | 89 | All baked and validated |
| BAKE_OPTIONAL | 18 | Additive support poses; explicit base-pose recipes needed before standalone use |
| EXCLUDE_NOT_BODY_ANIMATION | 9 | Native classes other than body AnimSequence |
| EXCLUDE_DUPLICATE_OR_HELPER | 12 | Eleven benchmark helpers and one exact duplicate |
| EXCLUDE_UNSUPPORTED | 0 | None |
| Total | 128 | Every candidate has a reason |

Default categories: **56 Locomotion, 13 Jump, 20 Actions**. No default crouch or turn-in-place sequence was discovered; none was fabricated or added to the review controller. Optional additives were not counted as successful default bakes.

Exact object paths, native classes, Skeletons, rates, durations, frame/key counts, additive/root flags, retarget sources, curves, notifies, markers, classifications and reasons are recorded in [source_inventory.json](source_inventory.json). [installed_source_provenance.json](installed_source_provenance.json) retains original installed paths/packages and hashes.

## Destination library and reusable backend

Authoritative library:

    /Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/Animations/LibraryV1/

Subfolders are Locomotion, Jump and Actions. Original basenames are retained; collisions receive a deterministic eight-character source-path SHA-256 suffix. [animation_library_manifest.json](animation_library_manifest.json), version `phase4f.animation-library/1.0.0`, provides every source → destination binding and validation certificate.

**89 attempted, 89 succeeded, 0 failed.** The destination Skeleton is the accepted Aegis SKEL_Destination from R2. No mesh, Skeleton, bind pose, weights or materials were repaired.

`Working/R4/animation_library.py` contains the generic native discovery/metadata/fingerprint/validation utilities. `Working/R4/AegisNX7/profile.json` binds the accepted destination mesh/Skeleton, source mesh, accepted retargeter and isolated output namespace. The profile-driven bake orchestration can consume another accepted destination without changing the generic library layer. Future wizard packs can select manifest categories; missing packs should remain unavailable, and optional additive packs require explicit implementation. No wizard UI was built.

Earlier uncertified bake/review attempts are retained as diagnostic evidence outside LibraryV1 and the final ReviewV2 map. They are not the authoritative runtime library.

## Root-motion correction and metadata

The accepted in-place retarget configuration is preserved. An isolated retargeter copy handles clips with enabled extraction **or an actual non-constant authored source root trajectory**. Original per-sequence root flags remain unchanged.

The dormant source Root Motion operation was bound to **pelvis**, rather than the source hierarchy root. Enabling it transferred pelvis height/bob into the destination root. The exact settings readback ruled out the earlier ground-snapping hypothesis: CopyHeightFromSource was already set.

The generic correction detects the unique parentless source mesh bone and uses that bone as the source root. It retains source height and the accepted scale settings. The original accepted retargeter is unchanged. Installed RootMotionGeneratorOp/PelvisMotionOp source establishes source root displacement multiplied by the target/source reference pelvis-height ratio; the measured ratio here is **1.0369859393655365**. Every frame is checked against this independently source-bound expected trajectory within 0.001 cm arithmetic tolerance. Long authored root trajectories are therefore supported without accepting arbitrary placement explosions. Non-root translation/body-size checks remain bounded.

Native batch baking retained root flags, curve names, notify classes/names/counts, sync marker names/times and metadata classes in all 89 sequences, including after reload. Notify trigger times/durations are not exposed by the installed Python struct API, and full curve values were not separately audited; native batch duplication is the preservation mechanism for those payloads. Transform-curve handling follows the installed UE batch baker.

Source Sequencer editing links were copied by native duplication. Five derived sequences carried AnimSequenceLevelSequenceLink user data; four pointed to source LevelSequences, while the wall-jump link was also detached. These links are editor-only in installed UE source and are inappropriate editing relationships for independent destination bakes. Only this typed user data was removed from derived R4 sequences; source assets, gameplay metadata and animation data were untouched. [editor_link_detachment.json](editor_link_detachment.json) records the detachment. The final strict dependency graph contains no source LevelSequence either.

## Validation and native playback

Authoring checks cover native raw finite/unit-root keys, all-frame native evaluated transforms, independent source-root trajectory certificates and representative world poses. Python's reflected internal track arrays are empty in this UE version; they were not treated as proof of raw keys.

Fresh main-project reload checks all **89/89** sequences, their destination ownership, finite all-frame evaluation, duration, canonical root scale, trajectory, representative poses, metadata and saved hashes. The authoring bridge is absent from the fresh playback process. See [fresh_validation.json](fresh_validation.json).

Eight representatives pass actual fresh native single-node playback at normal rate:

| Role | Sequence |
| --- | --- |
| Idle | MM_Idle |
| Walk | MF_Unarmed_Walk_Fwd |
| Run/jog | MF_Unarmed_Jog_Fwd |
| Jump | MM_Jump |
| Air/fall | MM_Fall_Loop |
| Land | MM_Land |
| Strafe | MF_Unarmed_Walk_Right |
| Action | MM_Attack_01 |

Each advances through a complete cycle with finite native transforms, unit actor/component/root scale, preserved limb lengths and no elevated actor. There is one destination actor, no source actor and no live retarget. [native_library.json](native_library.json) retains telemetry and screenshots. This is technical playback evidence, not aesthetic certification; contact, armour intersections and weighting quality were not repaired.

## Final playable review

Loaded final level:

    /Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/ReviewV2/L_AegisMovementReview

Character, AnimBP and GameMode are copies of the accepted movement-review setup. Ground speed selection, camera-relative movement, 300 cm/s walk, 600 cm/s run, camera and orientation remain intact. Native Character Jump/StopJumping handles Space; jump velocity is 420 cm/s. Actor/component/root scales remain one and reference stature remains **179.91210982641414 cm**.

Destination jump assets:

    /Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/Animations/LibraryV1/Jump/MM_Jump.MM_Jump
    /Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/Animations/LibraryV1/Jump/MM_Fall_Loop.MM_Fall_Loop
    /Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/Animations/LibraryV1/Jump/MM_Land.MM_Land

Rising IsFalling plus duration guard selects jump; descending air selects fall. The airborne → grounded edge selects non-looping land for its duration, then resumes locomotion. Air sequence children reset on activation. The original three proven destination-native ground sequences remain in use.

The first review attempt exposed that GetBasicTypeByName('double') falls back to integer in installed UE. The clean ReviewV2 successor uses the installed `real` type (double subcategory), so fractional timers work. Failed attempts are preserved; no accepted review baseline was changed.

All nine native input phases pass: idle, W, Shift+W, S, A, D, mouse yaw, mouse pitch, Space. Space produces **85.55556239353024 cm** observed capsule rise. Native sequence-player times independently show jump player advancement during ascent, fall during descent, land advancing to clip completion and idle resuming. The first short injected Space press was missed across input frames; the final normal held press follows the actual native PlayerController input route without directly moving or jumping the pawn. See [native_verification.json](native_verification.json).

**Press Play. WASD moves, mouse looks, Shift runs, Space jumps.** PIE is stopped, possession is automatic, the viewport is positioned for review, and Editor PID 48184 is still running. The final level is ready for Andre's subjective review.

## Runtime independence

Strict recursive dependency inspection covers all 89 sequences, the final review level/Character/AnimBP/GameMode, destination mesh/Skeleton and their typed appearance dependencies. It passes with no Manny/Quinn mesh, source Skeleton/actor, live retargeter, IK rig, Copy Pose/Retarget Pose node, source editor LevelSequence or authoring bridge in playback closure. Authoring retargeters and source copies remain outside runtime closure for future baking.

## Preservation and final self-review

Fourteen independent acceptance checks pass in [final_acceptance.json](final_acceptance.json), including source/staged/destination hashes, all defaults baked/reloaded, metadata/root policy, native playback, jump flow, closure, preservation and the running ready review process.

The audit covers **38,279 protected files**. **38,278 have unchanged hashes; no file is missing.** The sole differing file is the pre-existing running review editor's runtime log, `Working/HumanReview/AegisMovement/interactive_editor_009.log`. Its original 297,783-byte prefix matches the baseline SHA-256 exactly; only a runtime append occurred. The raw strict audit retains FAIL for that hash difference rather than concealing it. [runtime_log_append_audit.json](runtime_log_append_audit.json) and the final aggregate distinguish this append from authored/evidence changes.

Accepted R1/R2/R3 assets and evidence, original Aegis inputs/appearance, Female benchmark, John/Jane review evidence, frozen protocols and project mannequin sources are unchanged. Installed mannequin sources are independently rehashed. Git HEAD, index and pre-existing tracked status are unchanged; no staging, commit or push occurred. The unrelated original editor was untouched; only agent-owned prior review windows were replaced by the final R4 window.

**Stop boundary reached.** No other character, skin/geometry/rig repair, sophisticated gameplay, wizard UI, cook/package or downstream scope was started.
