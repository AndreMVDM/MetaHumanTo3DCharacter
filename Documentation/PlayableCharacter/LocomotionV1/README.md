🟢 **High confidence** — PASS, verified through fresh generation, native playback, reload and preservation audits.

# Generic playable locomotion promotion

Version: **phase4f.rigged-playable-locomotion/1.0.0**.

## Reusable layer and default entry

The previous path was Python authoring plus copied Blueprint scaffolding:

- `E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/HumanReview/AegisMovement/build.py` authored basic controls and grounded selection.
- `Working/R4/AegisNX7/build_review.py` extended copies with jump/fall/land.
- `Working/FinalAcceptance/RiggedCharacters/FemaleBodyRigged/build_review.py` duplicated that six-clip scaffold and rebound destination assets.

The unfixed source scaffold used for this fresh generation was the four review packages under:

`/Game/MetaHumanTo3DCharacter/RiggedCharacters/AegisNX7/R4/ReviewV2/`

It was consumed read-only through the fixture profile. The isolated fixed Female/Aegis copies were **not** used as generation templates.

The new default front door is:

`E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/PlayableCharacter/generate.py`

It routes through `Working/PlayableCharacter/default_template.json` to:

`Working/PlayableCharacter/LocomotionV1/generate.py` → `generator.py:generate(config)`.

The registry pins the executed implementation hash. The implementation contains no Female/Aegis/John/Jane, Skeleton-name or per-character asset-path constants. Destination bindings and the read-only legacy scaffold are supplied in a profile. Historical builders remain unchanged for reproduction; they are not the future wizard entry point.

## Old versus new

Old: `Landing = LandTime>0 AND NOT Airborne`, holding the entire stationary landing clip even at running speed.

New: add `HorizontalSpeed<=IdleSpeedThreshold`. Moving touchdown selects grounded locomotion immediately through the existing 0.1 s blend. Stationary touchdown retains destination Land duration and returns to Idle. Jump/fall flow and CharacterMovement remain authoritative.

Defaults remain **IdleSpeedThreshold=5, WalkSpeed=300, RunSpeed=600, LandingBlendDuration=0.1**. Run selection remains at their midpoint, 450 cm/s. Ground blends remain 0.15 s. Jump and landing timing guards bind to the configured destination clip durations.

The generated template uses continuous VSizeXY for both grounded and landing comparisons, avoiding truncation at configurable boundaries. The historical integer Speed telemetry is retained separately. No accepted AnimBP was changed. No velocity-zeroing, movement-speed tuning, root-motion redesign or animation editing was introduced.

## Fresh-generation proof

The final fresh output is under:

`/Game/MetaHumanTo3DCharacter/PlayableCharacter/LocomotionV1Regression/FreshGenerated04/`

- `BP_PlayableCharacter`
- `ABP_PlayableLocomotion`
- `BP_PlayableGameMode`
- `L_PlayableReview`

Generation automatically installed the rule and all six configured destination-native players. **Post-generation manual edits: 0. Rebakes: 0.** The native Blueprint classes and metadata record the version. [Generation receipt](generation.json) records source/profile/implementation provenance.

## Native regression measurements

| Fresh generated case | Touchdown speed cm/s | First grounded branch | Time to locomotion | Distance before locomotion |
| --- | ---: | --- | ---: | ---: |
| Stationary | 0 | Land → Idle | 0.869575 s | 0 cm |
| Walking, forward held | 300 | Walk | 0 s | 0 cm |
| Running, forward held | 600 | Run | 0 s | 0 cm |
| Repeated running jumps, both touchdowns | 600 | Run | 0 s | 0 cm |
| Release forward before landing | 532.726 | Run, then normal deceleration to Idle | 0 s | 0 cm |

Zero values mean correct selection in the first observed touchdown sample; the 0.1 s pose blend still applies. Native sequence time and bone variation confirm advancing locomotion, beyond bool selection alone.

Fresh generated output: **14/14 native cases PASS**. Accepted corrected Female review: **14/14 PASS**. Accepted corrected Aegis review: **14/14 PASS**. Coverage includes stationary/walking/running/repeated/released-input jumps, held forward, idle, WASD, Shift, Space, both mouse axes, jump/fall/land, possession, finite poses, no horizontal teleport, no forced stop, unit scales and stature/placement preservation.

Existing-review regression consumed the accepted corrected review copies read-only. Archived pre-fix review assets retain historical behaviour and were not silently upgraded.

## Reload, runtime and safeguards

Fresh reload passed native destination mesh/Skeleton/AnimBP bindings, six exact configured sequences, configurable defaults, version fields and landing-guard structure. Runtime closure contains 31 packages and adds only the four generated review packages to the accepted destination closure. No live Manny/Quinn, retarget, authoring or foreign-subject dependency is present.

Three rejection controls passed before asset creation: already-corrected scaffold with a potentially stale threshold, wrong-Skeleton animation, and missing required role. The default front door also correctly rejected an existing output namespace. These deliberate FAIL receipts are negative controls, not integration failures.

Two failed variable-pin build attempts and an intermediate successful generation are retained as isolated diagnostic evidence. The final authoritative generation is FreshGenerated04; no partial attempt is registered as a default template or runtime output.

## Preservation and wizard implication

**46,132 protected files: zero changed, zero missing.** Both 89-animation libraries are individually hash-checked unchanged. Accepted R1–R4 assets/evidence, original sources, prior fix assets, John/Jane evidence and frozen protocols are preserved. Two pre-existing runtime logs appended with original prefixes intact. Git HEAD, index and pre-existing tracked status are unchanged; nothing was staged, committed or pushed.

Future wizard-generated playable scaffolding must call the registered default generator. Every successful output from that path receives the corrected landing rule automatically; there is no opt-out to old moving-landing behaviour. The polished wizard itself is not implemented here.

[Wizard contract](wizard_contract.md), [40-check integration result](integration_result.json), [fresh native/structural checks](fresh_validation.json), [template hashes](template_provenance.json), and [preservation audit](preservation_audit.json) contain the detailed evidence. Work stops at this promotion boundary.
