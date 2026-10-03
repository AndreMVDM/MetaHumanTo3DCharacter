# Accepted Rigged Humanoid Backend — 2026-10-03

Rigged Humanoid Backend accepted. Next phase is productisation / native UE wizard development.

This checkpoint records Andre's accepted handoff of 3 October 2026. Historical reports retain their original technical results and then-pending human-review wording; this later checkpoint records the supplied overall movement/character acceptance without rewriting that evidence. No new runtime testing or implementation is claimed by this source-control task.

## Accepted v1 scope

One already-rigged, already-skinned humanoid Skeletal Mesh with one coherent humanoid skeleton. Human, clothed, armoured, robotic/android, fantasy and stylised forms are supported when integrated geometry is already in the same weighted Skeletal Mesh. Disconnected geometry islands and multiple material slots are allowed.

Unrigged inputs, automatic skinning, skin-weight repair, separate accessory assembly, cloth/hair systems, facial rigging and non-humanoid rigs are outside v1.

## Accepted backend

| Version | Accepted capability | Authoritative evidence |
| --- | --- | --- |
| `phase4f.rigged-unit-canonicalisation/1.0.0` | Supported finite positive isotropic reference-root scale canonicalisation; preserved geometry, weights, hierarchy, rotations and root translation; synchronised inverse binds and Skeleton reference pose | [R1](../Phase4F/Benchmark/Runs/01_FemaleBodyRigged/UnitCorrection/README.md) |
| `phase4f.rigged-character-r2/1.0.0` | Validation, automatic unit classification, 23 Manny semantic bindings including ten finger chains, destination IK Rig/FBIK, source-rig copy, retargeter, native bake and playback | [R2](../Phase4F/Benchmark/Runs/01_FemaleBodyRigged/R2_EndToEnd/README.md) |
| `phase4f.rigged-character-r3/1.0.0` | Aegis NX-7 generalisation: GENERALISATION_PASS_WITH_GENERIC_FIX | [R3](../Phase4F/Benchmark/Runs/02_AegisNX7/R3/README.md) |
| `phase4f.rigged-runtime-appearance-closure/1.0.0` | Typed, bound material/texture dependencies certified while unrelated character, animation and rig dependencies are rejected | [R3 closure correction](../Phase4F/Benchmark/Runs/02_AegisNX7/R3/README.md) |
| `phase4f.animation-library/1.0.0` | Profile/manifest-driven library bake and authored-root trajectory handling | [R4](../R4/AegisNX7/README.md) |
| `phase4f.rigged-playable-locomotion/1.0.0` | Reusable Character/AnimBP/camera/input generation with corrected moving touchdown | [Generator](../PlayableCharacter/LocomotionV1/README.md), [wizard contract](../PlayableCharacter/LocomotionV1/wizard_contract.md) |

No compensating 0.01/100 scale hacks are part of the accepted representation. For extracted or nonconstant authored root trajectories, transfer binds to the unique parentless source mesh bone, rather than pelvis; ordinary in-place configuration remains unchanged.

## Proven characters and animations

- Female_Body_Rigged: complete final workflow and user-accepted movement/character behaviour; [final technical evidence](../FinalAcceptance/FemaleBodyRigged/README.md).
- Aegis NX-7: integrated robotic/armoured humanoid; intrinsic stature approximately 179.912 cm with no external 1.8 multiplier.
- Each character has 89/89 destination-native default mannequin body animation bakes: 56 Locomotion, 13 Jump and 20 Actions. Eighteen optional candidates and 21 exclusions are outside the default library.
- Native Idle / Walk / Run / Jump / Fall / Land, WASD, mouse camera, Shift run and Space jump are established.
- Runtime playback needs no Manny/Quinn actor or component, live IK Retargeter, Retarget Pose From Mesh, Copy Pose or authoring bridge. Source/retarget assets remain authoring inputs for future rebaking.

## Accepted landing rule

Stationary touchdown within the idle-speed range may play Land, then return to Idle. Moving touchdown immediately selects the appropriate Walk/Run state through the existing approximately 0.1 s blend. CharacterMovement remains authoritative; velocity is not zeroed, movement speeds are unchanged and locomotion is not redesigned around root motion.

The generic entry is `Working/PlayableCharacter/generate.py`. Its registry selects the versioned implementation and verifies its hash. Fresh generation inherited the correction with no manual output edits and no rebake. Fresh generated, Female and Aegis native regressions each passed 14/14 cases. Observed moving-touchdown branch-selection delay/distance were 0 s / 0 cm; stationary recovery remains approximately 0.87 s. Both 89-animation libraries remained unchanged. [Fix evidence](../ReviewFixes/RunJumpLand/README.md).

## Repository checkpoint boundary

The checkpoint includes accepted backend source, versioned generator, evidence, intended authored UE assets and the two original rigged character archives under the existing ignore and Git LFS policy. Historical authoring/review assets remain identified by their original reports; the fixed review copies and default generator define corrected touchdown behaviour.

Pre-existing tracked Jane edits, Jane research/review additions, unused character inputs, earlier broad benchmark/source-readiness investigations and live editor logs are left local and untouched. Unreal build/cache directories remain excluded. This checkpoint does not start wizard implementation, reopen unrigged research or claim cook/package certification.
