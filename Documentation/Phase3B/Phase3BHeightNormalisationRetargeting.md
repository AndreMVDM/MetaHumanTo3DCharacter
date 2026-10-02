🟢 **High confidence**

# Phase 3B — Generic Height Normalisation and Stable Retargeting

Experiment date: 30 September–1 October 2026, Australia/Sydney. Installed Unreal Engine 5.8.3, Blender 5.2.0. Level 1 execution with self-review. This is an asset-authoring proof of concept with explicit animation-quality limits.

## 1. Executive summary

Generic uniform height authoring is proven for both Lara rigs at their original approximately 99.951 cm stature and user-selected 160, 175, 180 and 200 cm. All ten imported assets have unit local/component bone scales, unchanged hierarchy, finite reference transforms and height error below 0.00001409 cm against a 0.1 cm acceptance tolerance. Geometry, rest skeleton and bind relationship were scaled together before import; actor/component scale remains 1.

UE5's catastrophic IK behaviour is resolved in the clean candidates. The original representation is reproducibly unstable at the **Run IK Rig/FBIK stage**: either original solver sends the approximately 1 m target's pelvis roughly 48–55 m upward while FK remains near 0.5 m. Both independently tested solvers fail, so duplicate solver count is not the sole cause. The exact engine-internal arithmetic defect remains bounded rather than claimed fixed; no engine code was changed.

Mixamo foot behaviour is improved and explained. Align leg endpoints **and** goals to ToeBase, leave the Root chain unmapped where Hips is also pelvis, and clear inherited destination ForceRootLock for in-place clips. Run soles pass the experiment's 1%-of-height penetration proxy. Walk and some reach samples retain approximately 2.3 cm penetration at 180 cm; world-speed foot sliding and fine hand contact are not qualified.

The recommended route is coordinated DCC scaling into centimetre coordinates followed by an explicitly selected legacy FBX import at uniform scale 1. All ten targets produced destination-native validation clips. Fifty final full-IK clips have no foreign /Game package dependencies. Both 180 cm targets continued native playback after the live Manny component was destroyed. This establishes in-place bake independence; Mixamo ground-root extraction remains a separate future task.

## 2. Baseline Phase 2 import representation

Both original FBXs declare UnitScaleFactor 100: their coordinates are in metres. Physical bounds are approximately 99.951 cm, which is a legitimate stature. Both Phase 2 root reference scales are approximately (100,100,100), including the previously stable Mixamo target. UE5 has a separate root → pelvis; Mixamo has Hips as both root and retarget pelvis. UE5 has 61 bones, Mixamo 65. Actor and character component scales in the Phase 2 comparison are 1.

Stored import data identifies **InterchangeAssetImportData** and InterchangeGenericAssetsPipeline. Uniform offset scale is 1, offsets are zero, independent Skeleton creation is configured, Use T0 As Ref Pose is false, and skeleton-reference updating is false. The translator-settings object is absent, so the exact translator is not asserted. Nested stored pipeline settings and every reference transform are preserved in [baseline_import.json](baseline_import.json). Original unit/model/cluster metadata is in [fbx_units_and_bind_data.json](fbx_units_and_bind_data.json).

Phase 2 UE5 contains two Full Body IK solvers; its retargeter disables Run IK Rig and scales pelvis horizontal/vertical motion by 0.01. Mixamo has one solver. Chain definitions, goals, solver settings, operation stacks and all target pose offsets are in the baseline snapshot. Original Phase 2 documentation records UE5 bind-pose fallback and cluster/pose transform warnings. No original asset was resaved.

## 3. Clean import candidate methodology

The OriginalHeight candidates were first authored at factor 1. Blender imported each original FBX without automatic bone orientation changes. Mesh and armature were detached from parent transforms while preserving world space, transformed together into centimetres, and had location/rotation/scale baked coherently. The armature modifier continued to reference the same armature. Export used unit scale 0.01, FBX_SCALE_ALL, global scale 1, no added leaf bones and no animation export.

An explicit FbxFactory and FbxImportUI selected the legacy path. Settings: skeletal mesh import; scene and scene-unit conversion enabled; import uniform scale 1; zero translation/rotation; no supplied Skeleton; Use T0 As Ref Pose false; Update Skeleton Reference Pose false; import materials; no texture import; no Physics Asset creation. New meshes and Skeletons were explicitly saved separately. Root scale became 1 while original intended stature stayed approximately 100 cm.

New assets live only under /Game/MetaHumanTo3DCharacter/Phase3B/{UE5|Mixamo}/{OriginalHeight|Height160|Height175|Height180|Height200}. Deliberately invalid Raw controls and foot/root-motion variants have separate Phase3B subfolders. A control named RawInterchange actually still used FbxFactory and produced legacy import data: it is a repeated legacy control with a changed Interchange cvar, **not evidence of a second importer route**.

Legacy import recreated the bind pose for all four deliberately taller UE5 exports after a relative-matrix warning. It reported successful recreation and valid bind poses; Mixamo and UE5 OriginalHeight reported valid bind poses directly. This warning is retained, not silently classified as clean. All assets subsequently passed reference and deformation checks. See [import_warnings.json](import_warnings.json) and Working/Phase3B/build_final.log. No UV set and smoothing-group warnings originate in these untextured source meshes; FBX evidence confirms absent source UV layers. Detailed texture/material appearance is therefore outside the supplied assets' evidence.

## 4. Height measurement method

Measure a neutral, unscaled source pose in DCC world coordinates. Ground is the minimum Z of vertices with combined foot/toe weights ≥0.5 and Z below 12 cm. Crown is the maximum Z of head-weighted vertices ≥0.5 above the head joint within a central 12 × 16 cm region centred on that joint. These semantic regions are selected before scaling. Anatomical stature estimate = crown minus ground. Raw mesh bounds and head-joint height are recorded separately.

For these two meshes the semantic estimate and raw bounds agree, at approximately 99.951 cm. Hair is part of an unlabelled head surface, so this is a repeatable **head-weighted crown estimate**, not an independently segmented skull measurement. A future utility must allow an explicit crown/sole landmark override and flag accessories or ambiguous segmentation. Target cm values in this experiment refer to this stated estimate.

[height_measurements.json](height_measurements.json) records source estimate, raw bounds, ground, crown, head joint, scale factor, requested output, imported bounds and error. Static stature is checked in the reference pose; an animated arm above the head is allowed to increase the animated bounds.

## 5. Generic target-height implementation

ScaleFactor = TargetHeightCm / MeasuredCharacterHeightCm. No Manny or MetaHuman height enters this formula. Working/Phase3B/normalise_dcc.py accepts --heights followed by arbitrary numeric values, uses an OriginalHeight factor of 1, and validates finite inputs. The prototype's intentional guard range is 20–300 cm; the proven sample range is approximately 100–200 cm. Labels support fractional values through decimal-to-p naming.

Example DCC invocation, with the absolute project script path:

    & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python 'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase3B/normalise_dcc.py' -- --heights 160 175 180 200

The script applies the same uniform factor to all mesh vertices, skeleton rest positions and mesh/rest transforms. It compares every vertex and rest bone against the expected uniformly scaled source, verifies hierarchy and weights, and evaluates the reference-pose armature modifier before export. Scaling a parent and child together initially doubled the transform; the corrected implementation detaches them first and asserts the expected result.

## 6. Height-normalised asset results

All ten candidates pass requested-height tolerance, finite transforms, unit scales and imported hierarchy comparison. The largest imported height error is 0.00001409 cm. Maximum DCC coordinate comparison error is below 0.00002 cm; maximum evaluated reference deformation difference is below 0.000065 cm. These are floating-point checks on geometry/rest authoring, not promises of exact UE GPU vertex reproduction.

Both original meshes contain **two unweighted vertices**, indices 6502 and 19938. Silently preserving zero weights would let the importer assign them to root, potentially producing stray head-surface vertices during animation. Phase3B copies influences from the nearest weighted surface neighbour only for these undefined vertices; distances are approximately 0.263 and 0.146 cm. Every existing source influence remains unchanged, and scaling changes no influences. All outputs have zero unweighted vertices and at most six influences. This explicit repair is an exception to literal all-vertex weight identity; hashes and assigned influences are in [dcc_candidates.json](dcc_candidates.json).

The proportionality proof is stronger than selected ratios: every coordinate follows the same uniform factor, and hierarchy remains unchanged. Therefore shoulder width, arm/leg ratios, torso/head proportions and hand/foot proportions remain the source character's. No body reshaping or rig replacement occurred.

![Same pixel/cm scale, reference geometry](height_reference_matrix.png)

## 7. Root/reference-scale findings

Original unit metadata, deliberate stature and local root scale are separate variables. Raw original-height legacy imports also retain root scale 100; changing importer selection alone did not repair the source representation. Coordinated DCC authoring changes FBX UnitScaleFactor to approximately 1, produces unit imported local/component scales and preserves approximately 100 cm stature at factor 1. Deliberate stature changes are then 1.60078, 1.75085, 1.80088 and 2.00098 times the measured source, approximately.

Root, pelvis and all accumulated transforms are in [root_reference_transforms.json](root_reference_transforms.json) and scaled_candidates.json. Mixamo's root sits at pelvis height by design; UE5's distinct root sits near ground. The validation does not incorrectly demand that every skeleton root be on the floor.

Root scale 100 is a warning requiring a representation check, not a universal statement that the character is 100× too tall. Both Phase 2 rigs have that scale but only UE5 reproduces the catastrophic FBIK behaviour. The failing combination is bounded to the raw UE5 representation plus the tested generated FBIK setup and Phase 2 pelvis correction.

## 8. IK Rig regeneration

Each final mesh receives a candidate-specific fresh IK Rig after stature is established. Auto characterisation and auto FBIK are run, pelvis/retarget-root roles are set, Root is added where absent, and the root-motion bone is set explicitly. UE5 legs end at ball_l/ball_r; Mixamo legs end at LeftToeBase/RightToeBase. Their leg goals are moved to those same endpoints to correspond to Manny's ball goals.

All ten final rigs have exactly **one** Full Body IK solver. Generation clears previous Phase3B solvers first, making this step idempotent. Installed source IKRigAutoFBIK.cpp line 63 unconditionally adds a solver; repeating the generator without clearing can accumulate solvers. The clean two-solver control remained numerically stable in its bake tests, but duplicate solvers are unnecessary and excluded from accepted configurations.

[ik_rig_results.json](ik_rig_results.json) contains generated and final chains, reference goal transforms, all solver/goal/bone settings, and chain endpoint distances against each final skeleton. [reference_validation.json](reference_validation.json) confirms parent relationships and goal bounds. Engine name sanitisation strips Mixamo's namespace; comparison accounts for that consistently.

## 9. IK Retargeter regeneration

Source is /Game/Characters/Mannequins/Rigs/IK_Mannequin. Each target uses its own fresh post-height rig and target preview mesh. Default operations are created, shared chain names mapped exactly, every mapping validated, and a target retarget pose generated. Root Motion and optional speed/stride planting operations are disabled for the accepted in-place experiment; Pelvis Motion, FK Chains and Run IK Rig remain active in the full configuration.

For Mixamo only, Root mapping is deliberately empty: source root-to-target Hips FK would overwrite the preceding pelvis-motion output because Hips is both root and pelvis. Extra target foot chains without exact source equivalents remain unmapped. The controller's set_source_chain arguments are (source_chain, target_chain); this ordering was verified after an initial rejected mapping assertion.

[retargeter_results.json](retargeter_results.json) records every mapping and operation setting. No Phase 2 pelvis 0.01 correction is carried into clean candidates.

## 10. Retarget pose regeneration

Target poses are reset to reference and auto-aligned after final height, goal and chain choices. No manual pose corrections were applied. [pose_offsets.json](pose_offsets.json) records every local quaternion, including ankle, toe, finger, shoulder, elbow and knee offsets; [pose_height_comparison.json](pose_height_comparison.json) records affected bones and sign-insensitive quaternion comparisons.

The largest auto-offset difference between original-height and taller variants is 0.001079 degrees, consistent with numerical variation under uniform scaling. Scale did not materially change pose alignment in these tests. The full set of local offsets is preserved; no old Phase 2 offsets were reused except inside deliberately labelled raw runtime controls.

## 11. UE5 solver isolation

Every final height was tested with FK only, its sole FBIK solver enabled independently, and the full stack. FK/full each used five clips, isolated FBIK used run. All 2,750 main evaluated poses pass the project stability checks. Independent live SIE sampling then captured four source clips with actual component/world transforms and identity actor/component scales.

The raw controls duplicate the Phase 2 **rig/retargeter configuration into Phase3B**, use a separately imported raw mesh, and run simultaneously from the same source component. They preserve the Phase 2 0.01 pelvis scales specifically to reproduce that failure. The accepted clean assets do not reuse Phase 2 rigs.

| Live configuration | Run pelvis Z cm | Result |
|---|---:|---|
| RawUE5_FK | 48.40–53.72 | Pelvis stable; root-scale preflight fails |
| RawUE5_Solver0 | 4768.57–5287.90 | Reject: multi-metre pelvis displacement |
| RawUE5_Solver1 | 4768.57–5287.90 | Reject: multi-metre pelvis displacement |
| RawUE5_Full | 4768.57–5287.90 | Reject: multi-metre pelvis displacement |

Either solver independently introduces the same explosion. Full output reproduces it. FK establishes the numerically plausible pre-IK pelvis; matched configurations isolate the operation boundary without editing engine source or adding solver instrumentation. Idle/walk/reach also reproduce large displacement. The sanity gate rejects these outputs and their non-unit root representation.

Clean final 180 cm live run pelvis is around 90–97 cm; the entire five-height set remains bounded with IK active. The practical resolution is coherent unit-scale rest authoring and fresh solver setup. This is not a claim that the original FBX, Interchange globally or the engine's internal solver arithmetic has been repaired.

Evidence: [solver_isolation.json](solver_isolation.json), [live_solver_isolation.json](live_solver_isolation.json), [live_runtime_samples.json](live_runtime_samples.json), control_results.json and control_samples.json. Baked AnimPose WORLD is skeleton/component global space, not automatically real world space; only the live snapshots claim actual world measurements.

## 12. Mixamo foot investigation

The original auto goals attach to Foot/ankle, while Manny's leg goals attach to ball. Extending the leg chain to ToeBase alone leaves a goal/endpoint mismatch. Both Foot and ToeBase endpoints were tested with mapped/unmapped Root while holding the original Foot goals constant; then goal placement was changed independently.

| Mixamo 180 cm configuration | Run pelvis Z cm | Left sole minimum cm | Right sole minimum cm |
|---|---:|---:|---:|
| Foot_RootMapped | 93.68–101.23 | 3.340 | 2.980 |
| ToeBase_RootMapped | 80.63–94.77 | 0.266 | -0.269 |
| Foot_RootUnmapped | 78.67–89.92 | -5.164 | -5.777 |
| ToeBase_RootUnmapped | 73.89–82.46 | -10.410 | -13.392 |
| ToeGoal_RootMapped | 102.24–105.95 | 10.405 | 10.705 |
| ToeGoal_RootUnmapped | 88.85–96.12 | -0.665 | -0.524 |

The final ToeBase endpoint + ToeBase goal + unmapped Root preserves dynamic pelvis motion and improves toe/ankle behaviour. RootMapped configurations clamp Hips through FK; goal correction alone does not resolve that collision. Toe_End is inspected as a terminal orientation reference but is not chosen as the leg endpoint. Reference ankle/toe/terminal transforms and rotations, retarget offsets, knee angles, toe-pitch ranges, surface clearance and contact-pair movement are recorded in [mixamo_foot_tests.json](mixamo_foot_tests.json).

At 180 cm, final run minimum soles are about -0.665 cm left and -0.524 cm right, within the ±1.8 cm contact proxy. Walk reaches about -2.281/-2.044 cm, and right-foot reach about -2.280 cm, so contact quality remains open. A contact proxy based on foot-weighted surface vertices is preferable to ankle-joint Z. In-place rearward foot travel is expected during locomotion; without matching world speed and explicit stance events, it is not a valid foot-sliding verdict.

Native playback initially froze Hips at its reference height despite correct baked keys. Batch retarget inherited Manny's ForceRootLock. Clearing this flag on destination in-place Mixamo clips restores pelvis motion because Hips is itself the root. Corrected assets are listed in [baked_root_lock_correction.json](baked_root_lock_correction.json); final live and no-Manny checks verify the correction.

![Mixamo FK/full run geometry estimate](mixamo_run_cycle.png)

## 13. Height test matrix

| Rig | Requested cm | Imported cm | FK | IK | Feet | Hands |
|---|---:|---:|---|---|---|---|
| UE5 | 99.951175 | 99.951175 | Stable | Stable | Run proxy passes; walk contact open | Finite, lengths preserved |
| UE5 | 160.000000 | 159.999990 | Stable | Stable | Run proxy passes; walk contact open | Finite, lengths preserved |
| UE5 | 175.000000 | 174.999991 | Stable | Stable | Run proxy passes; walk contact open | Finite, lengths preserved |
| UE5 | 180.000000 | 179.999991 | Stable | Stable | Run proxy passes; walk contact open | Finite, lengths preserved |
| UE5 | 200.000000 | 200.000007 | Stable | Stable | Run proxy passes; walk contact open | Finite, lengths preserved |
| Mixamo | 99.951173 | 99.951173 | Stable | Stable | Run proxy passes; walk contact open | Finite, lengths preserved |
| Mixamo | 160.000000 | 159.999986 | Stable | Stable | Run proxy passes; walk contact open | Finite, lengths preserved |
| Mixamo | 175.000000 | 175.000001 | Stable | Stable | Run proxy passes; walk contact open | Finite, lengths preserved |
| Mixamo | 180.000000 | 180.000001 | Stable | Stable | Run proxy passes; walk contact open | Finite, lengths preserved |
| Mixamo | 200.000000 | 200.000001 | Stable | Stable | Run proxy passes; walk contact open | Finite, lengths preserved |

The CSV is [height_matrix.csv](height_matrix.csv). Stability and anatomical/contact quality are separate: all ten pass stability; the feet column explicitly preserves walk/contact limitations. Actor/component scale is 1 throughout accepted comparisons. A full production foot-plant acceptance is not inferred from this matrix.

## 14. Multi-animation validation

Validation uses idle MM_Idle, walk MF_Walk_Fwd, run MM_Run_Fwd, reach/upper-body JumpingJacks, and an additional Manny_upperarm_r_anim arm sweep. Walk is Quinn-authored on the shared Manny Skeleton; it is compatible source animation rather than a falsely renamed Manny clip. Read-only copies came from AnimationRetargeting; original project assets are unchanged.

MM_Run_Fwd contains approximately 10.1035 m of authored root translation even though normal live playback uses ForceRootLock. Installed batch code explicitly incorporates root motion into the source evaluation (IKRetargetBatchOperation.cpp line 461). Initial Root Motion-disabled batches therefore showed large pelvis drift already in FK. Separate cloned **in-place fixtures** set only Manny's root track to reference; all non-root tracks and originals remain unchanged. This separates locomotion authoring from stability. Root drift without a moving target root is rejected.

| Rig, 180 cm, full IK | Clip | Pelvis Z cm | Skin-height estimate cm | Lowest left/right sole cm |
|---|---|---:|---:|---:|
| UE5 | idle | 99.93–100.21 | 178.34–178.70 | -0.01 / -0.03 |
| UE5 | walk | 90.23–100.23 | 168.05–177.96 | -2.05 / -1.99 |
| UE5 | run | 89.95–97.18 | 162.66–167.26 | 0.35 / -0.46 |
| UE5 | reach | 83.44–112.86 | 172.58–183.43 | 0.31 / -0.58 |
| UE5 | arm_sweep | 101.98–101.98 | 179.67–200.69 | -0.25 / -0.23 |
| Mixamo | idle | 99.17–99.52 | 178.35–178.71 | -0.62 / -0.65 |
| Mixamo | walk | 89.79–98.96 | 167.86–177.00 | -2.28 / -2.04 |
| Mixamo | run | 88.85–96.12 | 160.85–167.18 | -0.67 / -0.52 |
| Mixamo | reach | 81.51–111.74 | 171.10–183.53 | 0.50 / -2.28 |
| Mixamo | arm_sweep | 101.59–101.59 | 179.80–200.89 | -0.73 / -0.71 |

All FK/full clips have 25 uniformly spaced samples per cycle; the isolated solver's run also has 25. Root Motion is additionally tested on the original authored run. Default generated Root Motion selected source pelvis, not source ground root, producing incorrect root height. Explicit source selector root corrected UE5: target root spans approximately 10.7045 m while pelvis remains about 90 cm above it and passes trajectory-aware gates. Destination extraction is enabled on that separate test clip.

Mixamo's target Root and Pelvis both select Hips. The same Root Motion operation writes Hips to ground height and destroys its anatomical pelvis role. All 25 corrected-selector Mixamo root-motion samples fail the standing pelvis-height gate. This branch is rejected; accepted Mixamo in-place baking remains valid. A future ground-root adapter or a deliberately designed pelvis-root motion strategy is required before claiming production root-motion extraction.

## 15. Quantitative runtime results

[runtime_samples.json](runtime_samples.json) holds 2,750 actual UE evaluated baked poses and points to live evidence. Each contains all local/component bone transforms, source/target identity, time and stated world assumptions. [live_runtime_samples.json](live_runtime_samples.json) has 100 actual SIE snapshots, 17 populated mesh components per snapshot, four animations and real component/world transforms. Fifty additional component observations verify baked playback with no live Manny component.

[quantitative_metrics.json](quantitative_metrics.json) contains 4,325 final/control/root-motion pose measurements; failures in deliberate controls remain visible. The 2,750 accepted main poses have zero sanity failures. Maximum accepted arm/leg segment relative-length error is 0.000001322, well below the 5% gate. Knee/elbow angles vary coherently, and all captured shoulders/hands/ankles/toes have finite position, orientation and scale. Fine shoulder twisting, finger contact and signed anatomical joint limits require richer fixtures.

Skin envelopes and sole clearances use CPU linear blend skinning from DCC weights and actual UE component poses. Weights are normalised per vertex for that estimate. This excludes UE influence quantisation, cloth, morphs, physics and GPU material effects. The software-rendered contact sheets are clearly labelled estimates. Live component bounds are also captured, but SkeletalMeshComponent bounds may be imported/fixed rather than deformed surface bounds and are not substituted for measured sole vertices.

The actual Unreal unlit viewport confirms populated live characters and coherent silhouettes; [live_unlit_view.jpg](live_unlit_view.jpg) is an observed screenshot. Supplied characters are untextured and the test lighting limits detailed surface inspection. The reference and run sheets provide clearer geometric comparisons.

## 16. Solver sanity gate

Working/Phase3B/solver_sanity.py implements prototype project rules, not Epic standards. Static checks reject non-finite reference transforms, non-unit bone scales >0.001, external scale >0.001, reference bone/goal positions farther than 3×stature from the asset origin, or requested-versus-imported height error >0.1 cm. Root-at-pelvis rigs are allowed.

Runtime checks reject non-finite transforms, any bone >3×stature from animated root, pelvis displacement >1×stature from its reference after permitted root trajectory subtraction, standing-test pelvis Z outside 0.2–1.5×stature, bone scale error >0.001, arm/leg length change >5%, or estimated animated skin height outside 0.1–2×stature. The standing pelvis threshold is specific to these idle/walk/run/reach fixtures; lying/falling clips need explicit alternative envelopes.

For root motion, origin distance alone is not a failure: coherent trajectory is subtracted and bone distance is checked relative to root. If root is pelvis, vertical displacement is not reinterpreted as ground motion; this detects Mixamo Hips collapse. Baked test result fields based on absolute-origin distance are retained as diagnostics, while quantitative_metrics applies the final trajectory-aware rules.

Six meaningful injected tests pass: 50 m pelvis, root scale 100, NaN transform, far goal, wrong output stature, and valid coherent 10 m root motion. See [gate_self_tests.json](gate_self_tests.json). Actual raw UE5 runtime outputs fail, actual main candidates pass, and Mixamo root-motion incompatibility fails. Initial reference goals are accessible and tested; instantaneous internal IK goal values are not exposed by this sampling route. Runtime outcome envelopes remain the complementary safeguard.

## 17. Bake-readiness findings

Installed UE 5.8 supports IKRetargetBatchOperationInputs and IKRetargetBatchOperation.run_batch_retarget. This was executed, saved and evaluated rather than inferred from documentation. Target sequences belong to each destination Skeleton. The five final full-IK validation clips per target form a small experiment set, not a production animation library.

All fifty final full-IK clips' hard/soft package closures stay in Phase3B or /Engine; no /Game/Characters/Mannequins or source IK Rig/Retargeter dependency appears. [bake_dependencies.json](bake_dependencies.json) records exact closure, target Skeleton and runtime flags. Both 180 cm clips played through AnimSingleNodeInstance after Manny_Source was destroyed, with zero remaining live Manny mesh components and advancing bounded poses. See [independence_verification.json](independence_verification.json) and [independence_live.json](independence_live.json).

Ready: bake destination-native **in-place** animations and build a destination runtime AnimBP. Not yet qualified: a complete production library, final foot planting/contact, Mixamo ground-root extraction or cross-project migration execution. UE5's separate corrected root-motion experiment passes numerical gates, but gameplay capsule/root-motion integration is still future validation.

## 18. Migration/independence implications

Migrate the chosen final Skeletal Mesh, its independently created Skeleton, its material assets and any textures if later supplied, and the accepted /Tests/InPlaceFull Animation Sequences. No Physics Asset was generated here; create and validate one later if collision/ragdoll needs it. Direct animation playback requires no Control Rig or authoring retarget asset.

The Phase3B ABP_Lara assets and BP_Phase3B_LiveTest are **live retarget authoring/test fixtures**. They intentionally depend on Manny and must not be mistaken for the final runtime migration pack. A later destination AnimBP should play baked sequences on the target Skeleton without RetargetPoseFromMesh. IK Rig/Retargeter can be retained separately for authoring and rebaking.

Package-closure checks and no-Manny playback establish dependency readiness, not proof of a migration into another project. Selected runtime assets are listed exactly in bake_dependencies.json. Materials contain no supplied texture library; importer/editor-only source file references are authoring provenance rather than runtime asset requirements.

## 19. Automation requirements

The future UE Authoring utility should automate this sequence:

1. Snapshot source units, import provenance, reference hierarchy/transforms, weights, bind warnings and protected hashes.
2. Detect semantic ground/crown regions; expose ambiguous crown/accessory cases and an explicit height override.
3. Repair or reject undefined weights explicitly; preserve all defined influences and geometry identity.
4. Apply a user-selected uniform factor to mesh, rest skeleton and bind relationship in one coordinated authoring transaction.
5. Import with an explicit supported route and independent Skeleton; save all created dependencies and reject unit/height/hierarchy failures.
6. Generate IK rigs idempotently after final stature; ensure one intended solver, matched leg endpoints/goals, and source/target role compatibility.
7. Create/reset retarget poses and mappings; detect root/pelvis aliasing before FK or Root Motion can overwrite pelvis.
8. Run FK, each solver and full-stack trials on diverse clips; use separate in-place/root-motion fixtures and enforce static/runtime gates.
9. Capture actual component/world output plus deformation/contact metrics; reject catastrophic output automatically.
10. Bake only accepted configurations, correct inherited root-lock/extraction flags for target hierarchy, and verify destination package closures and native playback without source.
11. Build a source-independent runtime AnimBP and an explicit migration manifest; keep authoring fixtures separate.

Prototype scripts are in Working/Phase3B. The principal reusable pipeline is normalise_dcc.py → build_candidates.py → evaluate_candidates.py → inspect_final.py → quantify.py → assemble_evidence.py. Execute authoring in one editor process: Windows locks loaded packages, so a concurrent commandlet cannot safely resave those same assets. The final build/evaluation ran through Unreal's existing local Python console. Remote Python execution was never enabled; its attempted security-setting change was rejected by automatic approval review and the local route completed the experiment.

Existing-asset iteration requires care: source fixtures must remain immutable, all failure evidence must be retained, auto poses must be reset before alignment, and batch overwrite should be verified against actual returned assets. The prototype deliberately keeps intermediate/control results for traceability; it is not packaged as a finished editor utility.

## 20. Recommended next phase

Build Phase 4 around the demonstrated coordinated authoring and in-place bake route. Add semantic crown/sole overrides, a native destination animation state machine, explicit root/pelvis role handling and a migration manifest. Use the ten candidates and intentionally failing raw controls as regression fixtures.

Prioritise foot contact at matched movement speed, signed knee/elbow/shoulder checks, hand-contact clips, runtime animation compression and a proper neutral preview environment. Resolve Mixamo ground-root extraction without silently changing its preserved source hierarchy. Also tighten FBX bind-pose validation/reconstruction and smoothing-data export so import warnings become an explicit recoverable state rather than a blanket success.

Self-review confirms required evidence files, ten height rows, clean reference gates, all five-clip FK/full tests, per-solver run isolation, four-clip actual live samples, deliberate negative gates and source-free native playback. A separate fresh Unreal commandlet reloaded all ten saved meshes, rigs, retargeters and fifty full-IK clips, confirming persisted settings and destination root-lock flags; see [saved_asset_verification.json](saved_asset_verification.json). [acceptance_verification.json](acceptance_verification.json) records the final acceptance checks. [protected_after_verification.json](protected_after_verification.json) verifies 110 protected project files unchanged and the copied reference animation originals unchanged. No protected namespace additions, engine-source edits, commits or pushes were made. No MetaHuman conform/Auto Solve/Identity/body-parameter or rig replacement path was used.

Required evidence: baseline_import.json; height_measurements.json; scaled_candidates.json; root_reference_transforms.json; ik_rig_results.json; retargeter_results.json; pose_offsets.json; solver_isolation.json; mixamo_foot_tests.json; runtime_samples.json; height_matrix.csv. Additional files retain control comparisons, actual live output, root-motion failures, warning evidence, dependency closure and independent-playback verification.

Primary API references: [Epic Run Batch Retarget, UE 5.8](https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/IKBatchRetarget/RunBatchRetarget?lang=en-US) and [Epic IK retargeting](https://dev.epicgames.com/documentation/unreal-engine/ik-rig-animation-retargeting-in-unreal-engine?lang=en-US). Version-specific behaviour here is corroborated by the installed UE 5.8 source/API stubs and executable experiments.
