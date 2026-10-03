🟢 **High confidence** — this contract is implemented and verified for phase4f.rigged-playable-locomotion/1.0.0.

# Rigged Character Wizard playable-generation contract

## Authoritative backend entry

Use `E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/PlayableCharacter/generate.py` in the installed UE Python authoring environment. Supply `-PlayableProfile=<absolute JSON profile path>`.

The registry at `Working/PlayableCharacter/default_template.json` selects the versioned implementation and checks its hash. The Python callable is `LocomotionV1.generator.generate(config)`. This step generates playable scaffolding only; it does not perform import, fitting, retargeting, skeleton creation, skinning or animation baking.

Historical per-character review builders are preserved reproduction artefacts. Future wizard code must use the registered entry rather than duplicate those historical builders or manually repair generated AnimBPs.

## Required profile fields

| Field | Meaning |
| --- | --- |
| output_namespace | Fresh, empty /Game package namespace. Existing outputs are never overwritten. |
| destination_mesh | Accepted destination SkeletalMesh object path. |
| animations | Exact destination-native AnimSequence paths keyed Idle, Walk, Run, Jump, Fall, Land. All must bind to the destination Skeleton. |
| scaffold | Read-only legacy six-clip scaffold paths keyed character, anim_blueprint, game_mode, level. The supported topology/guards are validated before mutation. |
| evidence_directory | Absolute directory for the generation receipt. |
| locomotion | Optional overrides of the four settings below; omitted settings use established defaults. |

The checked fixture profile is `Working/PlayableCharacter/LocomotionV1/fresh_profile.json`. Its subject/scaffold paths are test inputs; the implementation has no subject-path constants. The scaffold must use the validated unfixed legacy graph format. Fixed copies and already-generated v1 outputs are rejected as scaffold inputs to prevent nesting stale thresholds. The generator does not modify the scaffold.

## Configurable settings and rule

| Setting | Default | Native destination |
| --- | ---: | --- |
| IdleSpeedThreshold | 5 cm/s | AnimBP variable shared by ground selection and landing guard |
| WalkSpeed | 300 cm/s | Character variable / ordinary movement and Shift release |
| RunSpeed | 600 cm/s | Character variable / Shift press |
| LandingBlendDuration | 0.1 s | AnimBP variable / landing-ground and air-ground blend pins |

Settings must be finite, with 0 <= IdleSpeedThreshold < WalkSpeed < RunSpeed and nonnegative blend duration. Run selection uses the WalkSpeed/RunSpeed midpoint, retaining 450 cm/s at defaults. Configuration is applied at generation time; changing those settings later requires coherent regeneration/configuration of both generated classes, not only editing a movement component value.

Continuous horizontal speed is the native owning-pawn velocity length in XY. Landing is selected only while LandTime>0, not airborne and horizontal speed <= IdleSpeedThreshold. Above that same threshold, grounded selection immediately chooses Walk or Run. Stationary recovery remains interruptible if movement begins.

Jump/Fall flow, existing ground blends, CharacterMovement acceleration/braking/friction and input routes are retained. Destination Jump/Land durations supply their timer guards. The generator cannot opt into a full stationary-land hold at moving speed. It never stops velocity to conceal sliding.

## Output and provenance

Outputs use generic package names BP_PlayableCharacter, ABP_PlayableLocomotion, BP_PlayableGameMode and L_PlayableReview under the requested namespace. All six animation bindings come from the profile. No live retarget/source dependency is intended.

The generation receipt records version, implementation/profile hashes, input scaffold, destination mesh, configured clips/settings, output paths, and whether the policy was installed during generation. Both native Blueprint classes and asset metadata carry LocomotionTemplateVersion. Failed generation is not a consumable character result; preserve the failure receipt and use a new namespace for a repaired attempt.

## Reusable regression gate

`Working/PlayableCharacter/LocomotionV1/native_regression.py` runs normal native PIE through PlayerController InputKey, without directly moving the pawn or setting velocity. Configure a named entry in regression_profiles.json and pass `-LocomotionCase=<entry>`.

The profile supplies exact output package paths, settings and speed_variable. Use HorizontalSpeed for generated v1 outputs; historical corrected reviews use their existing Speed telemetry. Set expected_version for generated output to verify its native version field.

Required cases: stationary land-to-idle, continuing walk touchdown, continuing run touchdown, released-forward touchdown and repeated running jumps. The harness additionally covers held forward, idle, WASD, Shift, Space and camera axes. Record touchdown horizontal speed, first grounded branch, transition time/distance, native sequence times and bone poses. Moving touchdown must select correct locomotion immediately, preserve intended held-input speed and avoid teleport/non-finite/scale/placement failures. Stationary landing must still be observed.

Fresh native reload and dependency closure must independently verify configured bindings, no live source/retarget dependency and runtime independence. Preserve prior accepted assets and library hashes. The regression receipt proves branch timing; it does not claim a zero-duration pose blend or fabricate human approval.

No polished wizard UI or downstream capability is added by this contract.
