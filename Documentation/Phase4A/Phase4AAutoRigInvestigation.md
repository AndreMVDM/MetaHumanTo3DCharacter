🟢 **High confidence**

# Phase 4A — UE auto-rig investigation

Observed engine: **5.8.3-58210709+++UE5+Release-5.8**, installed at `D:\Epic Games\UE_5.8`. Investigation date: 1 October 2026, Australia/Sydney. Project: `E:\Repo\UE\Projects\MetaHumanTo3DCharacter`.

## 1. Executive summary

**The investigation is complete; a production-quality automatic humanoid rig is not established.** Installed UE code can generate a medial skeleton and skin directly from Lara geometry. Four such Skeletal Meshes were produced without imported joints or weights. Their branched skeletons fail humanoid characterisation and FBIK generation, and their anatomical structure is unsuitable for the Phase 3B pipeline.

A separate **assisted control** proves the remaining stages: 53 manually placed semantic bones, UE automatic geodesic weights, configurable physical height, IK Rig, Manny retargeter, destination-native diagnostic clips, and native playback after Manny's runtime component is removed. This control is explicitly not evidence of automatic anatomical fitting. Deformation flags, approximate fingers and mixed floor contact prevent production acceptance.

| Requested answer | Observed result |
| --- | --- |
| Can UE auto-rig unrigged Lara? | It generates a skeleton automatically, but the tested medial output is not an acceptable humanoid rig. No turnkey semantic joint fitter was verified in this installation. |
| Can UE auto-skin to acceptable quality? | Weight generation succeeds with full coverage; acceptable final deformation quality is not established. |
| Do the recovered and unrigged paths converge? | Yes for rest geometry and assisted downstream behaviour; source UV/material data differ. |
| Does the Mixamo foot issue improve? | No consistent improvement. Correcting an assisted toe landmark removes hover, but walking penetration is worse than Phase 3B. |
| Are textures/materials preserved? | Yes for the textured source after restoring its original diffuse connection and validating persisted material assignments. Mixamo input has no texture or UV data to preserve. |
| Do independent baked animations work? | Yes, as diagnostic clips on the new Skeletons, including actual SIE playback with Manny removed. |
| Which inputs should be supported? | Mode B as the primary validated contract; Modes A and C remain experimental assisted workflows. |

All authored UE assets are under `/Game/MetaHumanTo3DCharacter/Phase4A/`; external scripts, native helper, extracted inputs and images are under `Working/Phase4A`. Evidence is under `Documentation/Phase4A`. No commit or push occurred. The workspace did not resolve as a Git repository. The final protected-file audit compares 505 baseline files: source archives, protected Content/Config, reference packages and earlier documentation. Engine code was inspected and was not edited; an engine-wide before/after hash baseline was not captured.

## 2. Input ZIP inventories

| Property | Case A: MixamoRecovered | Case B: Unrigged |
| --- | --- | --- |
| ZIP | `Characters/Lara_Rigged_Mixamo.zip` | `Characters/Lara_UnRigged_Textured.zip` |
| ZIP bytes | 1,386,256 | 5,739,330 |
| FBX | `tripo_convert_c86468c2-b692-4f02-a7aa-d0b57cca6741.fbx` | `Lara_UnRigged_Textured.fbx` |
| FBX bytes / version | 1,621,724 / 7400 | 1,759,072 / 7400 |
| Meshes / materials | 1 / 1 | 1 / 1 |
| Control points / polygons / polygon corners | 27,725 / 28,636 / 106,780 | Same |
| Triangulated faces | 49,508 | 49,508 |
| Limb nodes / skin / clusters | 65 / 1 / 65 | 0 / 0 / 0 |
| Animation stacks | 0 | 0 |
| Source UV sets | 0 | 1, with 56,329 UV coordinate pairs |
| Textures | None | One JPEG, 4,026,618 bytes |
| Separate material files / GLB / OBJ | None | None |

The JPEG is `Lara_UnRigged_Textured.fbm/Lara_UnRigged_Textured_basecolor.jpg`. Its SHA-256 is `e54248a0d64cc4e4b40ade553e679f2b6919b87e79dbdb66adcf73e253a6b585`; the extracted source remains byte-identical. Materials are embedded FBX material definitions, not fully portable shader graphs. The unrigged FBX declares the JPEG as its diffuse texture.

Both FBXs declare Y up and `UnitScaleFactor=100`. Blender's scene conversion resolves an approximately 0.999512 m tall world-space mesh. The Mixamo Armature and mesh nodes contain approximately −90° X rotation; the mesh translation is near floating-point zero. Its Hips node has a nonidentity transform. The unrigged mesh node has no explicit local translation/rotation/scale properties, so FBX defaults apply. Full model transforms, arrays, connections and archive hashes are retained in `fbx_inspection.json` and `zip_inventory.json`.

## 3. Geometry comparison

The source meshes are geometrically equivalent within export precision, but their vertex ordering differs. After independent scene conversion, grounding and uniform 180 cm scaling, a bijective nearest-position correspondence has maximum separation **0.0000255409 cm** and mean **0.0000128519 cm**. Faces match after remapping, ignoring winding. Index-to-index comparison alone produces a misleading 96.1506 cm maximum discrepancy.

Their UVs and materials are not equivalent: the Mixamo archive has neither UVs nor texture resources, while the unrigged archive contains both. Thus geometry convergence does not imply appearance equality.

The normalised rest bounds are approximately **72.0176 × 37.5476 × 180 cm**, grounded at Z=0, with the character facing +Y. UE DynamicMesh has **28,189 vertices**, because conversion splits nonmanifold source vertices, and retains **49,508 triangles**. This is an engine representation change, not MetaHuman topology replacement or a new character mesh. Mesh build settings initially removed nine degenerate triangles when read through the render/build path; subsequent source comparison disables those build settings and preserves the source triangle count. See `geometry_comparison.json` and `geometry_landmark_view.png`.

## 4. UE 5.8 auto-rig systems found

The actual installed headers, implementation and Python reflection were inspected. `autorig_api_inventory.json` records exact absolute source paths, line matches, source SHA-256 and exposure. The engine-specific evidence takes precedence over feature names.

| System | Exposure and status | What it actually does |
| --- | --- | --- |
| `USkeletonModifier` | Public C++ authoring API; Blueprint/Python subset; Skeletal Mesh editing is an editor workflow | Adds, reparents, mirrors, transforms and orients explicitly supplied bones. It does not infer humanoid joint positions. `SetDynamicMesh` and `CommitSkeletonToDynamicMesh` are C++ only. |
| `FSkeletonViaSampling::ComputeSkeleton` | Public low-level GeometryAlgorithms C++ API; no direct Python entry found | Computes a geometry medial sphere skeleton. It is genuinely automatic, but supplies geometric branches rather than semantic human anatomy. |
| `FMedialSkeletonToTreeSkeletonOptions::ToHierarchy` | C++ conversion | Converts the sampled medial skeleton into a hierarchy suitable for animation storage. It does not supply a humanoid fit. |
| Geometry Collection medial Dataflow nodes, latest `_v2` | GeometryCollectionPlugin has `IsBetaVersion=true` and is disabled by default; conversion declarations are in Private/Dataflow | `MeshMedialSkeletonSampling_v2`, animation skeleton conversion and medial skin nodes wrap related native algorithms. Latest nodes use `UDataflowMesh`; legacy DynamicMesh variants are deprecated in 5.8. The graph itself was not executed in this test. |
| Static-to-Skeletal Mesh factories | Private/Hidden editor factories | Creates a root-only rig or uses a supplied Skeleton; no anatomical fitting. Python factory property assignment was not a usable route. |
| `GeometryScript_NewAssetUtils` | Public editor asset creation API, reflected to Python/Blueprint | Persists DynamicMesh plus a supplied Skeleton and weights as a Skeletal Mesh. |
| Control Rig / IK Rig automatic characterisation | Existing-skeleton authoring and semantic recognition | Generates controls, chains or FBIK from suitable bones; it is not unrigged mesh joint discovery. |

The thin `Phase4ATools` helper in `Working/Phase4A/NativeHost/Plugins` exposes the installed medial algorithm to Python, creates a blank Skeleton and synchronises a Phase4A Skeleton reference pose from its mesh. It does not implement a custom automatic joint predictor. Its mutation functions restrict output to the Phase4A asset prefix. No engine source or project plugin/configuration was edited to add it; test sessions load it through command-line plugin arguments.

The source-traced sequence actually run was:

    Static Mesh → DynamicMesh → FSkeletonViaSampling
    → medial-to-tree hierarchy → native medial skin weights
    → fresh Skeleton / Skeletal Mesh → characterisation attempt

UE's documented skeleton editing workflow describes authoring bones and skinning, and its auto-retargeting workflow describes existing character skeleton recognition. These are consistent with the installation findings: [Epic Skeleton Editing](https://dev.epicgames.com/documentation/en-us/unreal-engine/skeleton-editing-in-unreal-engine) and [Epic Auto Retargeting](https://dev.epicgames.com/documentation/unreal-engine/auto-retargeting-in-unreal-engine?lang=en-US).

Mesh Deformer and ML Deformer are deformation infrastructure; no generic unrigged humanoid fitter was verified through them. MetaHuman From Custom Mesh/Auto Solve, topology replacement, Tripo rig generation and preserved Mixamo rigging were not used as conversion paths.

## 5. UE 5.8 auto-skin systems found

| System | Actual requirement / test |
| --- | --- |
| `GeometryScript_BoneWeights.compute_smooth_bone_weights` → `FSkinBindingOp` | Public C++/Blueprint/Python API. Requires a Skeleton. Supports DirectDistance and GeodesicVoxel. Assisted controls used GeodesicVoxel, voxel resolution 128, stiffness 0.2, maximum five influences. |
| `SkinBinding::CreateSkinWeightsFromMedialSkeleton` | Public DynamicMesh C++ API. Computes cluster-constrained weights from the engine-generated medial skeleton. Tested through the native helper using DirectDistance and maximum five influences. |
| `GeometryScript_BoneWeights.transfer_bone_weights_from_mesh` | Public transfer API, requiring a donor mesh/skeleton/weights. Closest-surface/inpainting options were inspected; donor transfer was not used in this proof. |
| Skeletal Mesh Editing Tools | Interactive skeleton, binding and weight authoring; SkeletalMeshModelingTools is an Editor plugin enabled by default and its descriptor has no beta/experimental flag. |

Automatic skin generation is therefore verified independently of automatic anatomical joint placement. No heat-binding implementation was used or validated. Do not advertise every rigging API as experimental merely because the medial Dataflow integration is in a beta plugin. Full source/exposure details are in `autoskin_api_inventory.json`, `python_api_probe.json` and `additional_python_apis.json`.

## 6. Case A Mixamo recovery method

Blender imports the original FBX, reads its undeformed mesh data and world transforms, clears the armature parent, removes modifiers and vertex groups, and removes armature objects before export. It retains geometry and existing material data, applies scene/unit conversion, grounds the mesh and uniformly scales to the requested height. It exports no animation. The recovered FBX has no retained Mixamo bone names, weights or Skeleton dependency.

For this neutral source, the safe recovery is raw/reference geometry rather than evaluating an arbitrary animation or current armature pose. That distinction must become explicit in a future external-rig contract: posed sources, multiple meshes, cloth bind shapes and arbitrary rig constraints were not tested here.

The original neutral `tripo_mat_c86468c2` material is imported separately through a static import with automatic FBX type detection explicitly disabled. Its original material slot is restored on generated meshes. No absent texture or UV data is synthesised from the textured input. UE allocates a UV channel in its mesh representation, but this does not recover meaningful source UVs.

Separate outputs exist under `Phase4A/MixamoRecovered/Geometry`, `PreservedSource`, `Medial64`, `Medial128`, `Assisted180` and `Assisted180BallForward`. Original Mixamo Phase 3B assets are only read as comparison evidence.

## 7. Case B unrigged import method

The ZIP is safely extracted under `Working/Phase4A/Inputs/Unrigged`. The FBX inspection confirms one mesh, one material, one UV set, a declared diffuse JPEG, and no skeleton, skin cluster or animation stack. Geometry preparation uses the same unit conversion and height logic as Case A, without armature removal because none exists.

The 180 cm baseline is `Phase4A/Unrigged/Geometry/SM_Lara`. A separate original textured source import is retained as `PreservedSource/SM_Lara_Source`, with the original material slot name and JPEG resource. Scene conversion establishes Z up and +Y facing. The geometry, UV hashes and before/after states are recorded in import, medial and assisted evidence. Both cases follow the same UE DynamicMesh and fresh asset creation pipeline.

## 8. Texture/material preservation

**Preservation passes for the unrigged source diffuse appearance.** Material slot count remains one. The importer initially omitted the diffuse texture reference; the unchanged archived JPEG was imported as `T_Lara_BaseColor` and connected to Base Color on the original imported material, restoring the FBX-declared diffuse connection. This is a reference repair, not texture authoring or material optimisation.

The source UV coordinate set matches the UE imported coordinate set after the conventional V-axis flip to within **2.98023224×10⁻⁸**. A rounded set comparison initially reported 70 differences at rounding boundaries; a numerical nearest-coordinate comparison resolves them. Coordinate-set equivalence alone does not prove corner attachment. Within-UE triangle/corner UV hashes remain exactly unchanged through binding, height scaling and fresh disk reload; before/after front and back rendering additionally verifies attachment visually.

The final material correction explicitly replaces array elements and reads them back before saving. A first loop modified detached reflected struct copies, so reported intended assignment was insufficient; fresh reload exposed the missing recovered material. The corrected assignment and repeated disk audit are the final authority.

Clear visual evidence:

- `Working/Phase4A/texture_front_unlit.png`: source and animated textured candidate from the front.
- `Working/Phase4A/texture_before_after_unlit.png`: back view showing clothing and hair texture attachment.
- `Working/Phase4A/native_playback_ball_forward.png`: corrected animated candidate with Manny removed; leftmost is the static textured source, followed by Unrigged, recovered Mixamo and the Phase 3B comparison.

The Unlit viewport makes the source colour texture readable without lighting/exposure differences; it does not change the material. The early `native_playback.png` had an incorrect camera and is not quality evidence. The early lit texture capture was overexposed and is superseded. See `material_uv_validation.json`, `material_render_probe.json` and `uv_import_validation.json`. Cross-renderer shader equivalence is not certified beyond the source diffuse appearance. Hair/shoulder deformation remains a rig-quality issue despite preserved texture mapping.

## 9. Height-ordering decision

**Choose height normalisation before joint placement and binding for unrigged inputs.** For already bound input, coordinated scaling is viable only when geometry, Skeletal Mesh reference pose and the separate Skeleton reference pose are synchronised together. Actor/component or bone scale is not the final physical-height mechanism.

The source height is approximately 99.95117 cm; its uniform 180 cm factor is approximately 1.80087934. Main rigs use 180 cm. Four 175 cm ordering controls compare two routes for each input:

| Measurement | ScaleThenBind | BindThenScale |
| --- | --- | --- |
| Final physical height | 175 cm | 175 cm |
| Geometry scaling error | 0 | 0 |
| Skeleton component translation scale error | ≤2.93×10⁻¹⁴ cm | Same bound |
| Bone local/component scales | Unit | Unit |
| UVs / triangle indices | Unchanged | Unchanged |
| Weight change | Voxel recomputation changes weights; maximum absolute difference about 0.15244 | Every weight unchanged |

The ScaleThenBind control copies the same authored joint positions to the scaled final reference state and recomputes weights; it isolates ordering, rather than claiming a second autonomous anatomical fit. Finite voxel sampling/tie choices prevent assuming exact scale invariance. The weight change is material enough to record, even though all vertices remain normalised.

An initial route updated mesh bones without synchronising the separate Skeleton; geometry reached 175 cm while Skeleton dimensions remained at 180 cm. That attempt is invalid and retained only as failure evidence. The helper's `UpdateReferencePoseFromMesh` correction makes both reference representations consistent. Failed assets outside `HeightOrdering/Corrected*175` are not migration candidates.

The corrected 175 cm controls scale root, pelvis, shoulders, hands, ankle and ball translations consistently. Fresh IK Rigs and one FBIK solver per control are generated after this final state, with hand/ball goals in the scaled reference pose. `height_ik_results.json` records these goals. Retargeter/bake quality at 175 cm was not evaluated; the animation acceptance dataset is 180 cm.

Reusable geometry and assisted builders accept target height (`--height` or `PHASE4A_TARGET_HEIGHT_CM`, finite range 20–300 cm), with 180 as a default/test profile rather than a required target. The manual landmark template is defined in nominal 180 cm coordinates then uniformly scaled. A future general fitter must infer subject proportions, not reuse this Lara-specific coordinate template.

## 10. Generated skeleton analysis

| Automatic trial | Bone count | Humanoid characterisation / FBIK |
| --- | --- | --- |
| Unrigged, sampling 64 | 66 | Both fail |
| Unrigged, sampling 128 | 134 | Both fail |
| MixamoRecovered, sampling 64 | 65 | Both fail |
| MixamoRecovered, sampling 128 | 133 | Both fail |

The sphere count parameter is not an exact final bone count. Joint positions and graph connectivity were inspected, rather than rejecting on names alone. There is a grounded artificial root followed by an off-centre medial origin near pelvis height; torso, clothing and hair create irregular branches. Long arm segments do not establish connected, correctly located shoulder/elbow/wrist chains. Finger and foot branches lack validated human correspondence. Branch points have up to 9–12 children and mirror-nearest errors are approximately 2.5–3.3 cm on average, 8.5–10.8 cm at maximum. Doubling sampling does not fix semantics or bilateral connectivity.

The schematic `skeleton_comparison.png` overlays actual bone positions/edges on geometry and makes this failure visible. `skeleton_analysis.json` records roots, parents, bone lengths, unit scales, branching and nearest approximate anatomical landmark distances. Those landmarks are manual comparison proxies, not anatomical ground truth. Small nearest distance alone cannot establish a valid humanoid hierarchy or usable axes. The automatic candidates are rejected before Manny retargeting; no forced renaming conceals their structural failure.

The assisted controls contain **53 independent bones**: grounded root; pelvis; three spine bones; neck/head; paired clavicle, upper arm, forearm and hand; three joints for each of five fingers per side; thigh, calf, ankle and ball. UE `SkeletonModifier` authors and orients these supplied joints. Pelvis is distinct from root. Fingers and several anatomical pivots are approximate, so this is a diagnostic semantic hierarchy.

The first assisted ball positions had Y=−10 while the shoes face +Y. A separate `Assisted180BallForward` profile changes only the supplied ball Y to +10, recomputes UE skin weights, and regenerates IK/retarget/bakes. The original controls remain for failure comparison. Foot correction is manual assistance and must not be presented as successful auto-fitting.

## 11. Generated skin-weight analysis

All automatic and assisted meshes have **28,189 weighted DynamicMesh vertices**, no zero/unweighted vertices, normalised sums approximately 0.99999995–1.00000005, and at most **five positive influences**. Earlier raw medial records include padded zero entries/duplicate bone indices; raw entry counts up to ten are not positive-influence counts. `skin_weight_analysis.json` filters positive weights correctly and uses each case's own vertex ordering.

A coarse wrong-side influence screen outside the central 8 cm band below 95 cm finds zero flagged vertices except three in MixamoRecovered Medial64. This is a numeric screen based on reference bone X, not semantic segmentation of clothing and limbs. Full coverage and a low bleed count do not validate a malformed skeleton.

The assisted 400-pose dataset drives CPU linear blend skinning of the actual UE-generated weights. It screens triangle area below 10% or above five times its reference area, excluding tiny reference triangles. These are screening flags, not formal pass thresholds. For corrected Unrigged Full mode, maximum counts are:

| Clip | Collapsed-area flags | Stretched-area flags |
| --- | ---: | ---: |
| Idle | 7 | 20 |
| Walk | 27 | 46 |
| Run | 77 | 169 |
| Upper-body fixture | 60 | 292 |

Recovered Mixamo has closely comparable counts (idle 7/21, walk 26/48, run 81/169, upper-body 60/293). Shoulder/hair and clothing distortion remain visible; fingers use approximate placements and were not validated with dedicated articulated finger clips. Knee/elbow angles, ankle/ball direction, root/pelvis translation and segment-length stability are recorded per pose. Unit scales and stable segment lengths rule out gross scaling/solver stretching in the tested poses, but do not certify every joint deformation, candy-wrapper twist or foot tearing.

The automatic medial rigs are structurally rejected, so no claim is made that their native skinning has passed animation-quality validation. Their reference coverage is recorded. The assisted controls isolate automatic weighting and the downstream pipeline on a semantic Skeleton. CPU metrics exclude GPU influence quantisation, morphs, cloth, collisions and contact solving. See `deformation_metrics_ball_forward.json`, original `deformation_metrics.json`, and `deformation_contact_sheet_ball_forward.png`.

## 12. IK Rig generation

Both corrected 180 cm assisted candidates successfully run `IKRigController.apply_auto_generated_retarget_definition` and `apply_auto_fbik`. Each has exactly one intended FBIK solver, pelvis as retarget/solver root, `root` as root-motion bone and a root-to-root Root chain. Root/pelvis aliasing is avoided structurally.

Leg chains end at `ball_l` / `ball_r`; the corresponding foot goals also use those ball bones. Hand goals use `hand_l` / `hand_r`. The same leg endpoint and goal choice keeps FK and IK comparisons consistent. The solver disallows stretch. All goal and solver settings are retained in `ik_rig_results_ball_forward.json`; original controls are in `ik_rig_results.json`.

These rigs are diagnostic because the character has not passed anatomical/deformation acceptance. Automatic medial IK asset creation/characterisation attempts failed and are recorded in `medial_trials.json`. They are not production IK outputs. The 175 cm rigs provide ordering/goal generation evidence only.

## 13. Retargeter generation

The source is `/Game/Characters/Mannequins/Rigs/IK_Mannequin`, using `SKM_Manny_Simple` for source evaluation. Each assisted candidate receives its own `RTG_Manny_Lara`. Default retarget operations are created, chains use exact semantic mapping, the target pose is reset and all bones are auto-aligned from the final rig.

Root Motion, Speed Plant IK Goals and Stride Warp IK Goals are disabled for the in-place comparison. FK mode disables Run IK Rig; Full mode enables it. Pelvis Motion and FK mapping remain active. Root maps to Root; spine, neck, head, legs, arms, clavicles and finger chains map by semantic name. The target-only LeftFoot/RightFoot single-ball chains remain unmapped because the source has no exact corresponding chains; ball endpoints are handled by mapped leg chains. This is recorded rather than describing every chain as mapped.

See `retargeter_results_ball_forward.json` for mappings, operation states and pose offsets, and `retargeter_results.json` for the original control. Generating a valid retargeter is not a deformation acceptance result.

## 14. Animation validation

The same Phase 3B in-place source fixtures are used: **MM_Idle, MF_Walk_Fwd, MM_Run_Fwd and JumpingJacks**. JumpingJacks supplies upper-body/reach motion but is a full-body fixture, not an isolated reach or finger test.

`IKRetargetBatchOperation.run_batch_retarget` produces four clips for FK and four for Full, separately for both cases and both assisted profiles: **32 diagnostic sequences in total**. Every sequence is saved with its destination Skeleton. Each profile has **400 UE AnimPose samples**: two cases × two solver modes × four clips × 25 uniformly spaced poses. All sampled transforms are finite and bone scales are unit; corrected limb-length relative error is on the order of 4×10⁻⁸.

Samples contain local and component/skeleton-global transforms. They are not described as live actor-world results; actual component/world playback samples are separately recorded in the independence evidence. CPU surface estimates show deformation flags despite stable bones. Root remains a separate grounded representation while pelvis carries body motion. No world-speed, root-motion traversal, gameplay collision or final contact-locking acceptance is implied by an in-place test.

`animation_results_ball_forward.json`, `runtime_samples_ball_forward.json` and `deformation_metrics_ball_forward.json` are the corrected candidate authority. Unsuffixed evidence retains the original bad toe placement for diagnosis. An output suffix variable initially collided with a limb-loop variable and wrote `*r.json`; its loop variable was fixed and verified complete corrected outputs were copied to the intended `_ball_forward` files. The erroneous duplicate files are historical evidence, not the report's primary dataset.

## 15. Mixamo foot comparison

The comparison uses the original Phase 3B Mixamo Height180 Full result and both corrected assisted candidates: same four clips, 25 sampled poses, 180 cm, weighted foot/ball surface minimum Z relative to the grounded reference. Negative values indicate estimated floor penetration. Values below are Unrigged; recovered Mixamo differs by less than 0.000001 cm at these minima.

| Clip | Phase 3B left / right minimum Z (cm) | Corrected Phase 4A left / right (cm) | Interpretation |
| --- | --- | --- | --- |
| Idle | −0.620 / −0.646 | −0.411 / −0.471 | Less penetration |
| Walk | −2.281 / −2.044 | −2.536 / −2.429 | Worse penetration |
| Run | −0.665 / −0.524 | −0.490 / −1.097 | Mixed; right worsens |
| Upper-body fixture | +0.505 / −2.280 | +0.051 / −0.700 | Better minima/contact proximity |

The original assisted toe direction produced roughly 4–5 cm sole hover; the corrected forward ball placement removes that artefact. This is a useful diagnosed joint-placement correction, but **does not establish overall improvement over the original Mixamo foot issue**. Extreme toe pitch during locomotion, penetration, lifted swing feet and remaining deformation flags require contact-aware review. A minimum across a clip cannot distinguish legitimate swing clearance from sliding; no world-speed or contact solver proof is claimed.

Original `foot_comparison.json` links the corrected authority `foot_comparison_ball_forward.json`. Per-pose ankle and ball positions, toe pitches, knee/elbow angles and surfaces are in deformation metrics. These numbers separate landmark/skin/retarget effects from skeleton-scale drift without asserting a universal rig-quality score.

## 16. Baked-animation independence

Both profiles were tested in actual Simulate In Editor using `AnimSingleNodeInstance` and their destination-native Full clips. The Phase4A runtime test explicitly destroys the Manny source SkeletalMeshComponent, then switches through idle, walk, run and upper-body fixtures. Corrected candidates are swapped onto the runtime components and use the corrected sequences.

Each profile records **100 live frames**, with component and world bone transforms for Unrigged, MixamoRecovered and the Phase 3B comparison. Every frame reports no remaining Manny mesh component; the corrected log has no errors. Components have unit world scale. Poses change through native sequence playback and require no RetargetPoseFromMesh AnimBP. The corrected screenshot shows source textures rendering while animated without Manny.

`independence_live_ball_forward.json` and `independence_live.json` are actual live evidence. Fresh commandlet disk reload works without loading Phase4ATools. Package dependency closure confirms no foreign `/Game` package, no Manny/source IK/retargeter, and no native helper dependency in the selected baked character seeds. The diagnostic map/BP intentionally still contains an editor Manny comparison component and is excluded from the finished-character migration set. Manny removal is a runtime test, not destructive editing of the source assets.

## 17. Migration readiness

Dependency readiness is verified; **clean-project migration and a packaged/cooked executable were not tested**. `migration_manifest.json` and `bake_dependencies_ball_forward.json` list exact current closures separately for each case.

For each corrected character, migrate `Assisted180BallForward/SK_Lara`, `SKEL_Lara`, and the four Full diagnostic Animation Sequences. Include the referenced preserved material; Unrigged also requires `PreservedSource/T_Lara_BaseColor`. The current Skeleton preview reference includes `SK_Lara_Authoring` in the hard/soft closure: include that mesh as presently authored, or deliberately clear the editor preview reference and re-audit before claiming a minimal package.

No Physics Asset, destination AnimBP or playable Character pawn was created. A future package should generate and validate these if required. Manny, source IK Rig, IK Retargeter and the native helper are authoring dependencies, not dependencies of the tested baked asset closure. Engine/Script package dependencies remain and are listed; editor class metadata is not a live source actor requirement. The diagnostic level/BP, failed height attempts and rejected medial rigs should not be migrated as a finished character.

## 18. Automation requirements

The utility must make the manual/automatic boundary explicit: geometry recovery and height conversion; joint fitting/landmarks; skeleton authoring; automatic binding; IK generation; retargeting; bake; independent playback and package audit. This proof automates stages around a Lara-specific manual landmark template. It does not implement arbitrary-humanoid semantic fitting.

Required safeguards are deterministic source inventory and hashes, transform/unit resolution, reference-pose recovery, UV/material readback after save/reload, separate mesh/Skeleton reference synchronisation, structural anatomy gates, positive-weight coverage/normalisation, root/pelvis distinction, explicit ball/ankle endpoint selection, solver count validation, per-clip deformations and migration closure. Reject or route to assistance when landmarks, connected chains, anatomical proportions or skin/contact quality fail.

| Failure / smallest correction | Evidence retained |
| --- | --- |
| Python UV accessor mismatch | Used GeometryScript mesh/UV queries; original import attempt retained. |
| Render/build copy removed nine degenerate triangles | Disabled build settings for source geometry comparison. |
| No callable Skeleton factory / static converter property route | Used prefix-restricted blank Skeleton helper and public asset creation APIs. |
| Medial tree lacks humanoid semantics | Increased sampling 64→128, inspected positions/connectivity, rejected; separate manual control follows. |
| FBX diffuse texture reference omitted | Imported unchanged JPEG and restored its declared original material connection. |
| Detached Python material struct modifications | Replaced material array elements explicitly, asserted readback, repeated fresh reload. |
| Mesh scaled but separate Skeleton stale | Synchronised Skeleton from mesh, reran both ordering controls and generated final-state goals. |
| Assisted ball placed behind shoe | Created BallForward profile, changed only ball Y, rebuilt weights/IK/retarget/bakes. |
| Wrong camera from positional Rotator arguments | Used explicit pitch/yaw/roll and front +Y camera; earlier black capture excluded. |
| Loaded assets blocked commandlet saves (Windows Error 32) | Saved only own loaded assets in the editor; no Save All or forced shutdown. |
| Retarget evidence suffix shadowed by limb variable | Renamed loop variable and validated complete corrected files. |
| Build host attempted protected log/trace paths and UBA fallback | Used local log/session paths; executed existing UBT-exported compiler/link actions after UHT, keeping helper entirely in Working. |

Toolchain 14.51 was newer than UE's preferred 14.50 and emitted a warning; compilation and reflected helper calls succeeded. This is an installation-specific build workaround, not a recommendation to edit the engine. DDC fallback and normal Saved/Intermediate execution caches were produced by UE; authored external deliverables remain in Working/Phase4A. Historical failed logs/attempts are preserved and are not success evidence.

Reproduction entry points are `inspect_inputs.py`, `prepare_geometry.py`, `compare_geometry.py`, `import_assets.py`, `test_medial.py`, `build_assisted.py`, `retarget_and_test.py`, `test_height_routes.py`, `check_height_ik.py`, `live_verify_forward.py`, `audit_assets.py`, `quantify.py` and `final_evidence.py` under Working/Phase4A. UE creation scripts are proof scripts, not an idempotent production service; do not blindly rerun against existing asset names. Builder/retarget/audit profile environment variables select BallForward separately. Native wrapper source and compiler actions are retained under NativeHost.

## 19. Supported input modes

| Mode | Recommended final contract | Evidence boundary |
| --- | --- | --- |
| A — Unrigged Humanoid | Experimental, assisted landmarks/anatomical fitting required; do not make fully automatic unrigged conversion the primary promise yet | Native skeleton generation exists, but tested automatic hierarchy fails; assisted automatic skinning/bake works only diagnostically. |
| B — UE-compatible Rigged Humanoid | Primary supported workflow with explicit Skeleton, reference pose, hierarchy, height, skin and contact validation | Reuses the proven Phase 3B resize/retarget/bake path; compatibility must be validated, not inferred from bone names alone. |
| C — External Rig | Experimental recovery workflow for qualified neutral/reference sources, then the assisted path | Lara rest geometry recovery converges; arbitrary rigs, posed bind shapes, multiple pieces and material formats are untested. |

These recommendations are limited to the installed version and tested Lara sources. The unrigged workflow remains the desired product direction; it needs a semantic fitting solution and a quality gate before broad public support. No universal “any humanoid mesh” guarantee follows from this result.

## 20. Recommended Phase 4B

Build an assisted fitting and acceptance prototype before a broad automatic-input utility: expose anatomical landmarks, preserve source shape/materials, fit connected semantic joints from those landmarks, orient axes, and bind in UE at final height. Concentrate on shoulders, fingers, ankle/ball placement and local clothing weights. Compare voxel resolution/settings and targeted weight edits without conflating those with automatic joint prediction.

Add dedicated reach, twist, wrist/finger and foot-contact fixtures, contact phase/slide measurements and rendered deformation review. Test several meshes with different proportions, poses and clothing. Then validate clean-project migration, cooked runtime, Physics Asset/AnimBP requirements and configurable heights with full animation tests. A future external fitter may be evaluated separately, but it would change the “UE alone places anatomical joints” product claim.

### Completion criteria and evidence

| # | Criterion | Result |
| --- | --- | --- |
| 1 | Unrigged textured import | Complete; import and preservation evidence. |
| 2 | Real UE auto-rig capability | Complete; installed source/reflection inventory and four executed medial trials. |
| 3 | Real UE auto-skin capability | Complete; native medial and public geodesic binding executed. |
| 4 | UE-generated unrigged rig | Complete as generated assets; anatomical quality rejected. |
| 5 | Mixamo recovery | Complete; external rig/weights discarded and equivalent geometry established. |
| 6 | Texture/material/UV preservation | Complete for source data present; corrected assignment, UV hashes and rendering validated. |
| 7 | Height normalisation | Complete at 180 and 175 cm; animation tests limited to 180. |
| 8 | Final-state IK/retargeter | Complete on explicitly labelled assisted controls; automatic rig fails the structural gate. |
| 9 | Idle/walk/run/upper-body | Complete; 800 evaluated bake poses over both profiles, with quality limitations recorded. |
| 10 | Foot comparison | Complete; mixed result, no overall improvement accepted. |
| 11 | Destination-native bake | Complete as diagnostic sequences, not production-qualified clips. |
| 12 | Manny removed/native playback | Complete; 100 actual live frames per profile, no remaining Manny component. |
| 13 | Primary unrigged input decision | Complete; not ready for primary fully automatic support. |

Level 1 execution and mandatory self-review were used. `acceptance_self_review.json` checks required files, numeric claims, asset boundaries, saved materials, dependencies, samples and protected hashes. The investigation's negative automatic-quality conclusion is a completed result, not a successful production character certification.

Automatic approval review rejected closing Unreal Editor because unsaved state could be lost. Simulation was ended safely and the editor was left open; no forced close or Save All was used.
