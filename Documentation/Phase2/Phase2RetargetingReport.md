# Phase 2 — Manny to Tripo Lara runtime body retargeting

Date: 30 September 2026  
Engine: Unreal Engine 5.8.3  
Project: `E:\Repo\UE\Projects\MetaHumanTo3DCharacter\MHTo3DCharacter.uproject`

## 1. Objective and result

Build the same runtime Manny animation source against two independently imported Lara skeletons, using generated target IK Rigs, IK Retargeters and target Animation Blueprints. Both variants imported, compiled and visibly followed `MM_Run_Fwd` during Play in Editor (PIE). The Mixamo variant worked with the generated IK pass. The UE5 variant required a targeted operation change after its generated IK pass displaced the mesh roughly 50 m above the scene. This is a **body motion proof of concept**, with no production quality claim for foot contact or fine finger deformation.

The earlier [investigation](../RetargetingInvestigation/InvestigationReport.md) and [supplemental IK configuration](../RetargetingInvestigation/SupplementalIKConfiguration.md) established the StackOBot `Retarget Pose From Mesh` runtime pattern used here. The AnimationRetargeting reference project and the unrelated open Austra project were left untouched.

At the start, the named target directory contained character ZIPs and investigation documents but no `.uproject` or Content tree. To make the experiment runnable, a minimal `MHTo3DCharacter.uproject`/Config shell was created and the required Manny and StackOBot template dependencies were copied into that new target project's original `/Game/Characters/...` and `/Game/ExampleContent/...` package paths. Those dependency copies are outside the Phase2 namespace; all **new Lara, rig, retargeter, AnimBP, actor and map assets** are inside it. The reference project itself was not edited.

## 2. Input ZIP inventory

| Input | Archive bytes | Contents | FBX bytes | Result |
| --- | ---: | --- | ---: | --- |
| `Characters/Lara_Rigged_UE5.zip` | 1,403,142 | One `tripo_convert_d5fc96b7-496c-4293-922d-2da2b1716bc5.fbx` | 1,631,692 | Extracted to `Working/Phase2/UE5`; imported |
| `Characters/Lara_Rigged_Mixamo.zip` | 1,386,256 | One `tripo_convert_c86468c2-b692-4f02-a7aa-d0b57cca6741.fbx` | 1,621,724 | Extracted to `Working/Phase2/Mixamo`; imported |
| `Characters/Lara_Rigged_TexturedUE5.zip` | 6,037,048 | Inventoried only | — | Not extracted or imported |

Each tested FBX is version 7400, with one mesh, one embedded material definition, no embedded textures, no animation stacks or animation curves, and no support files in its ZIP. Neither source archive was changed. See [`zip_inventory.json`](../../Working/Phase2/zip_inventory.json) and [`fbx_analysis.json`](../../Working/Phase2/fbx_analysis.json).

## 3. FBX comparison before import

| Feature | Lara UE5 preset | Lara Mixamo preset |
| --- | --- | --- |
| Bone count | 61 | 65 |
| Root / pelvis | `root` → `pelvis` | `mixamorig:Hips` is both root and pelvis |
| Spine | `spine_01` → `spine_02` → `spine_03` | `Spine` → `Spine1` → `Spine2` |
| Neck / head | `neck_01` → `head` | `Neck` → `Head` → `HeadTop_End` |
| Clavicle / arm | `clavicle_{l,r}` → `upperarm` → `lowerarm` → `hand` | `Left/RightShoulder` → `Arm` → `ForeArm` → `Hand` |
| Leg / toes | `thigh` → `calf` → `foot` → `ball` | `UpLeg` → `Leg` → `Foot` → `ToeBase` → `Toe_End` |
| Fingers | Five bilateral digits, three numbered joints each | Five bilateral digits, four numbered joints each, including terminal ends |
| Twist bones | Eight arm/forearm twist bones | None |
| IK helper bones | None | None |
| Naming | Manny-like lowercase names and `_l`/`_r` suffixes | Mixamo names with `mixamorig:` FBX prefix; Unreal imported the names without this prefix |
| Hierarchy distinction | Separate `root` before `pelvis`; twist branches | `Hips` is top deforming bone; extra head, toe and finger terminal bones |
| A/T arm angle | Not measured numerically | Not measured numerically |

The common body topology and bilateral branches supported semantic assignment, but the UE5 preset is **not** Manny's skeleton: its bone count, twist structure, lack of IK helpers and root reference transform differ. Reference-pose shoulder/arm angle classification remains unresolved; no numeric A/T claim is made. [`bone_comparison.csv`](bone_comparison.csv) gives all selected paired roles, and [`fbx_bones.csv`](../../Working/Phase2/fbx_bones.csv) contains the parsed bone hierarchy.

## 4. Unreal import results

Both files imported as valid independent `SkeletalMesh` and `Skeleton` objects under their Phase2 subfolders. Neither target was assigned Manny's Skeleton. Each import also generated a material instance; no Physics Asset was generated. The FBX importer reported a UE5 bind-pose issue and fell back to the time-zero pose, as well as cluster-versus-FBX-pose transform warnings for the tested files. These warnings did not prevent mesh/skeleton creation or the observed runtime test. They do warrant stricter import validation for a plugin. [`unreal_import.json`](../../Working/Phase2/unreal_import.json) records imported objects and skeleton ownership.

| Variant | Skeletal Mesh | Skeleton | Material instance |
| --- | --- | --- | --- |
| UE5 | `/Game/MetaHumanTo3DCharacter/Phase2/UE5/SK_Lara_UE5.SK_Lara_UE5` | `/Game/MetaHumanTo3DCharacter/Phase2/UE5/SK_Lara_UE5_Skeleton.SK_Lara_UE5_Skeleton` | `/Game/MetaHumanTo3DCharacter/Phase2/UE5/tripo_mat_d5fc96b7.tripo_mat_d5fc96b7` |
| Mixamo | `/Game/MetaHumanTo3DCharacter/Phase2/Mixamo/SK_Lara_Mixamo.SK_Lara_Mixamo` | `/Game/MetaHumanTo3DCharacter/Phase2/Mixamo/SK_Lara_Mixamo_Skeleton.SK_Lara_Mixamo_Skeleton` | `/Game/MetaHumanTo3DCharacter/Phase2/Mixamo/tripo_mat_c86468c2.tripo_mat_c86468c2` |

## 5. UE5 Lara skeleton analysis

Unreal exposes 61 imported bones. `root` is above `pelvis`; the spine, neck, shoulders, bilateral arms, legs, toes and all five digits per hand follow the expected branches. Eight twist bones occur on the arm/forearm branches. No target IK helper bones were found. The imported `root` reference transform has scale `(100, 100, 100)`, while `pelvis` has unit local scale; this is the leading observed clue for the later IK-pass displacement, not a proven engine root cause. [The root probe](../../Working/Phase2/root_probe.json) records the transform.

The 32 selected semantic assignments are marked High in [`anatomy_mapping.json`](anatomy_mapping.json) because names, parent-child relationships and bilateral counterparts agree. This confidence applies to *role identification in these two known rigs*. Spatial scoring, skin-weight checks and quantitative limb-direction checks were not implemented, so this is not evidence that the detector generalises to arbitrary generated skeletons. No selected role remained ambiguous; precise reference-pose arm angle remains unresolved.

## 6. Mixamo Lara skeleton analysis

Unreal exposes 65 imported bones. The FBX `mixamorig:` prefix was removed on import, leaving `Hips`, `Spine`, `LeftArm`, etc. `Hips` serves as both skeleton root and retarget pelvis. The skeleton has bilateral toes with terminal end bones and longer finger chains than the UE5 variant. It has no twist or IK helper bones. The same 32 selected semantic assignments are marked High on naming, hierarchy and bilateral structure, with the same generalisation limits. [`anatomy_mapping.json`](anatomy_mapping.json) records each role and its basis.

## 7. Manny source configuration and route choice

Manny uses `/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple`, source IK Rig `/Game/Characters/Mannequins/Rigs/IK_Mannequin.IK_Mannequin`, and looping direct single-node animation `/Game/Characters/Mannequins/Animations/Manny/MM_Run_Fwd.MM_Run_Fwd`. Source rig retarget root is `pelvis`; it contains 28 chains. These are copied project dependencies from the Epic sample content, with the reference project read-only.

`Copy Pose From Mesh` could only be considered for a target with a highly compatible hierarchy and bone transforms. The UE5 naming similarity alone is insufficient, and the Mixamo hierarchy differs substantially. Both test paths therefore use IK retargeting, as planned.

## 8. Generated IK Rig configuration

`UIKRigController` created a target rig per mesh, then UE 5.8 auto retarget definition and auto FBIK were applied and inspected. Auto definition made 21 chains per variant. Each rig needed the same three deterministic corrections: add missing `Root`, extend `LeftLeg` from foot to toe/ball, and extend `RightLeg` likewise. Each final rig has 22 chains: 20 Manny-compatible semantic chains plus `LeftFoot` and `RightFoot` generated target-only chains. The latter remain deliberately unmapped because Manny's source rig has no corresponding chain. The retarget roots are UE5 `pelvis` and Mixamo `Hips`; root-motion bones are UE5 `root` and Mixamo `Hips`. Auto FBIK added two UE5 solvers and one Mixamo solver. Limb chains have generated hand/foot goals; no source-speed-driven planting was configured. [`retarget_build.json`](../../Working/Phase2/retarget_build.json) records raw generated and corrected rigs.

| Variant | Target IK Rig | Root / leg correction |
| --- | --- | --- |
| UE5 | `/Game/MetaHumanTo3DCharacter/Phase2/UE5/IK_Lara_UE5.IK_Lara_UE5` | `root`; `thigh_l`→`ball_l`; `thigh_r`→`ball_r` |
| Mixamo | `/Game/MetaHumanTo3DCharacter/Phase2/Mixamo/IK_Lara_Mixamo.IK_Lara_Mixamo` | `Hips`; `LeftUpLeg`→`LeftToeBase`; `RightUpLeg`→`RightToeBase` |

## 9. Generated IK Retargeter configuration

Supported UE 5.8 retargeter controller APIs created each retargeter with Manny's IK Rig as source. Automatic chain mapping matched all 20 common target chains semantically on both variants; the two extra foot chains have no source equivalent. No manual source-to-target chain reassignment was needed. [`chain_mapping.csv`](chain_mapping.csv) gives every final mapping.

| Operation, in stack order | UE5 | Mixamo | Reason |
| --- | --- | --- | --- |
| Pelvis Motion | On; horizontal and vertical scales `0.01` | On; defaults (`1.0`) | Carry pelvis motion while adapting target size/root scale |
| FK Chains | On | On | Primary body and finger transfer |
| Run IK Rig | **Off after runtime correction** | On | UE5 generated pass caused approximately 50 m displacement; Mixamo pass was stable |
| Root Motion | Off | Off | `MM_Run_Fwd` test is kept in place |
| Remap Curves | On | On | Default stack operation; no curve quality claim |
| Stride Warp / Speed Plant / Pole Vector | Not added | Not added | No validated speed curves or need established by this single test |

The initial [`retarget_build.json`](../../Working/Phase2/retarget_build.json) snapshot shows `Run IK Rig` enabled on UE5. [`runtime_correction.json`](../../Working/Phase2/runtime_correction.json) and [`ik_isolation.json`](../../Working/Phase2/ik_isolation.json) record the later saved correction. Final assets use the table above.

| Variant | IK Retargeter |
| --- | --- |
| UE5 | `/Game/MetaHumanTo3DCharacter/Phase2/UE5/RTG_Manny_Lara_UE5.RTG_Manny_Lara_UE5` |
| Mixamo | `/Game/MetaHumanTo3DCharacter/Phase2/Mixamo/RTG_Manny_Lara_Mixamo.RTG_Manny_Lara_Mixamo` |

## 10. Retarget pose differences

The UE 5.8 automatic target pose alignment produced 33 non-identity local rotation offsets among 61 UE5 bones and 33 among 65 Mixamo bones. Affected regions include shoulder/upper arm, forearm, spine, thighs, feet and some digit bases or middle joints. This is evidence of computed alignment, including arm-angle compensation, but does **not** establish a measured A-pose versus T-pose classification or prove every finger is anatomically correct. No rotation was hand-adjusted. [`pose_offsets.json`](pose_offsets.json) records the per-bone results and the empty manual-offset lists.

## 11. Runtime Animation Blueprints

The known StackOBot runtime AnimBP graph was duplicated per target, retargeter input set to the corresponding Phase2 asset, skeleton rebound to that target, profile chain overrides removed, and compiled. Each graph has one `Retarget Pose From Mesh` node feeding `Output Pose`, with `RetargetFrom = ParentSkeletalMeshComponent`. Both generated classes were `BS_UP_TO_DATE`; [`anim_bp_build.json`](../../Working/Phase2/anim_bp_build.json) records the compiled paths and retargeter pins.

| Variant | Animation Blueprint |
| --- | --- |
| UE5 | `/Game/MetaHumanTo3DCharacter/Phase2/UE5/ABP_Lara_UE5_Retarget.ABP_Lara_UE5_Retarget` |
| Mixamo | `/Game/MetaHumanTo3DCharacter/Phase2/Mixamo/ABP_Lara_Mixamo_Retarget.ABP_Lara_Mixamo_Retarget` |

## 12. Test actor and map

The compiled actor `/Game/MetaHumanTo3DCharacter/Phase2/BP_Phase2_RetargetTest.BP_Phase2_RetargetTest` has a Manny source SkeletalMeshComponent and two child target SkeletalMeshComponents. Manny plays the run clip directly; each target has its own AnimBP and retargeter. Child attachment supplies the parent mesh lookup and source-before-target evaluation relationship; components were configured to continue ticking. World Y locations are Manny `-250 cm`, UE5 `0 cm` and Mixamo `+250 cm`. The map `/Game/MetaHumanTo3DCharacter/Phase2/Maps/L_Phase2_RetargetTest.L_Phase2_RetargetTest` contains the actor, floor, lights, comparison camera and PlayerStart. The camera looks from positive X, so the **screen order is Mixamo, UE5, Manny**, although the world-space arrangement is Manny, UE5, Mixamo. This ordering has no retargeting effect. The project's startup and game maps point to this test map.

The first scene script encountered a UE Python API mismatch (`unreal.PlayerIndex`); the camera property was corrected in a follow-up script. A spawned pawn initially occluded the camera; moving PlayerStart behind it fixed the PIE view. The saved map and correction evidence are [`scene_finish.json`](../../Working/Phase2/scene_finish.json) and [`camera_fix.json`](../../Working/Phase2/camera_fix.json).

## 13. Runtime validation

PIE observation showed Manny running and both Lara meshes visibly following the same loop after the UE5 correction. All three components had live animation instances. Captured world-space bone positions changed across samples, including hand and foot positions, while the corrected target pelvis/head heights stayed within the small imported mesh bounds. At one corrected sample: Manny pelvis/head/left foot Z were `86.47/145.26/8.40 cm`; UE5 `50.87/77.10/6.94 cm`; Mixamo `56.36/83.73/14.46 cm`. These are different-sized characters, so absolute height equality is not expected. [`runtime_samples.json`](runtime_samples.json) preserves four snapshots, including the failed UE5 states for comparison.

| Check | UE5 | Mixamo | Evidence limit |
| --- | --- | --- | --- |
| Source animation and target runtime evaluation | Pass | Pass | PIE visual observation and live AnimBP instances |
| Facing, pelvis/spine/limb motion, gross stability | Pass at overview scale | Pass at overview scale | No visible explosion, inversion or sustained drift in the observed run loop |
| Foot height | Sampled | Sampled | Single foot transforms at several times; not a contact or slide metric |
| Foot planting / obvious sliding | Inconclusive | Inconclusive | No tracked contact phase or ground-relative displacement test |
| Fine wrists, fingers, twists | Inconclusive | Inconclusive | Small ~100 cm white target meshes and basic lighting prevented confident close inspection |
| Compile / runtime issues | Compiled; UE5 IK displacement corrected | Compiled | Tool-probe and deprecation messages occurred; no final AnimBP compile failure observed |

The Lara meshes have approximately 100 cm bounds versus Manny's approximately 180 cm bounds. Their ZIPs contain no textures, and the test uses default white material/lighting. This limits inspection of fingers, shoulders and twists. The target's body motion passes the POC criterion; foot contact and detailed anatomical quality remain open validation items.

## 14. UE5 versus Mixamo comparison

| Criterion | UE5 Lara | Mixamo Lara |
| --- | --- | --- |
| Import | Pass; bind-pose fallback and transform warning | Pass; transform warning |
| Anatomy detection | 32/32 selected roles assigned; no selected ambiguity; no spatial scoring | 32/32 selected roles assigned; no selected ambiguity; prefix removed on import |
| IK Rig | Auto 21 chains; add Root and extend two leg endpoints; two generated FBIK solvers | Auto 21 chains; same three chain corrections; one generated FBIK solver |
| Chain mapping | 20/20 shared chains auto-mapped; 2 extra foot chains intentionally unmapped | Same |
| Retarget pose | 33 automatic non-identity offsets; no manual rotation | 33 automatic non-identity offsets; no manual rotation |
| Runtime body | Pass after disabling Run IK Rig and setting pelvis scales to `0.01` | Pass with Run IK Rig enabled and default pelvis scales |
| Feet/hands/fingers | Moving; fine contact and deformation unresolved | Moving; fine contact and deformation unresolved |
| Overall automation effort | **Requires significant correction** for import/root-scale and IK-pass interaction; corrections are scriptable, but a plugin cannot blindly accept auto FBIK | **Automatic with minor correction** for Root and toe endpoints |

The UE5 naming preset was not automatically the easier runtime case. Its imported root scale and generated IK pass made operation validation more important than naming similarity.

## 15. Automation findings

The common pipeline can discover a target Skeleton, inspect axial and bilateral branches, create IK Rigs, run auto definition/FBIK, repair Root and toe endpoints, map common chains, generate target pose offsets, create retargeters/AnimBPs, and build a live comparison actor. On these rigs, name plus hierarchy plus bilateral checks identified every selected role; a general plugin also needs reference-position, chain-length, topology and skinning checks before promoting confidence.

UE5-style names allow convenient Manny chain matching, but do not justify skeleton sharing or unvalidated FBIK. Mixamo support must normalise optional `mixamorig:` prefixes, handle `Hips` as both top root and pelvis, and ignore extra terminal finger/toe bones when mapping to Manny. UE5 twist bones and Mixamo terminal digits should be preserved as target skeleton features without inventing source matches. Hand/foot IK goals should be enabled only after checking imported scale and solver behaviour. Human validation was needed to inspect auto chains, choose toe endpoints, diagnose the UE5 out-of-scene result and judge overview motion. [`asset_inventory.json`](asset_inventory.json) records exact package/object paths.

## 16. Failures and corrections

| Original state / failure | Evidence | Correction / outcome |
| --- | --- | --- |
| UE5 FBX bind pose inconsistent; importer used time zero | Import observation | Keep separate imported skeleton and flag the warning for future preflight; runtime mesh remained usable |
| Auto rigs omitted Root and stopped legs at feet | [`retarget_build.json`](../../Working/Phase2/retarget_build.json) | Add Root; extend both leg chains to UE5 `ball` or Mixamo `ToeBase` |
| UE5 auto FBIK runtime output placed pelvis about `4,958–5,200 cm` high | First two [`runtime_samples.json`](runtime_samples.json) snapshots | Set Pelvis Motion horizontal/vertical scale to `0.01`; this fixed horizontal scale but not vertical displacement. Disable UE5 `Run IK Rig`; corrected pelvis became about `49–51 cm` high. The precise solver/scale mechanism remains to be isolated. |
| Initial map script used an unavailable `unreal.PlayerIndex` symbol | [`scene_build.json`](../../Working/Phase2/scene_build.json) | Use available camera input property/API and finish the map in the follow-up script |
| Default pawn blocked the comparison camera in PIE | [`camera_inspection.json`](../../Working/Phase2/camera_inspection.json) | Move PlayerStart behind the camera; save map |
| Tool probes hit PIE-only API restrictions and a deprecated mesh property | Editor log | Corrected probe calls where needed; no retarget asset change required |
| Target directory had no `.uproject` or content dependencies | Initial directory inspection | Created the minimal project shell and copied only needed Epic sample dependencies into the target; kept all generated experiment assets under Phase2 |

No manual bone-name remapping or target-pose rotation edits were needed. The UE5 operation change is a real automated-setup failure to handle in the plugin, not evidence that its generated FBIK works correctly.

## 17. Plugin architecture implications

Build the future plugin as a staged pipeline with inspectable results: archive/FBX preflight; import and bind-pose/root-scale diagnostics; semantic anatomy with explicit evidence and confidence; target IK Rig generation plus chain/goal validation; source-target chain mapping; automatic pose alignment with per-bone offset report; retargeter operation profile selection; runtime AnimBP/test-harness generation; and measured validation. Keep each stage repeatable and expose corrections as recorded decisions. A solver sanity gate should reject out-of-bounds pelvis or limb positions, try a diagnosed operation change, and require review when it cannot maintain foot/hand quality. Store package paths, warnings, chain mappings, pose offsets and before/after runtime samples as machine-readable evidence.

Do not assume UE5-style naming means Manny compatibility. Do not enable Speed Plant without usable curves. Do not count an imported mesh or a successful compile as a runtime pass. The two reference projects remain read-only dependencies; the actual generated Unreal assets live only under `/Game/MetaHumanTo3DCharacter/Phase2/`.

## 18. Recommended Phase 3

1. Isolate the UE5 root scale and FBIK interaction with controlled reimport/unit-scale tests; restore a safe IK pass if possible, then compare foot and hand quality with the current FK-only fallback.
2. Add numeric reference-pose arm-angle, bilateral position, chain-length and skin-weight checks to the anatomy confidence model; make ambiguous roles explicit.
3. Evaluate at least idle, walk, run and a hand/arm reach, sampling knee/elbow bend, toe height, limb length, root drift and foot contact over complete loops.
4. Test the same generated pipeline on new Tripo characters and skeleton variants, including missing digits, different proportions and optional IK helpers.
5. Improve the visual test with neutral materials, labelled screen order and close-up views, then build an editor-facing review step around the measured results.

### Evidence index

- [`asset_inventory.json`](asset_inventory.json): exact Unreal object paths, including source, generated rigs, retargeters, AnimBPs, actor and map.
- [`anatomy_mapping.json`](anatomy_mapping.json), [`bone_comparison.csv`](bone_comparison.csv): semantic roles and paired skeleton comparison.
- [`chain_mapping.csv`](chain_mapping.csv), [`pose_offsets.json`](pose_offsets.json): final chain assignments and generated local pose rotations.
- [`runtime_samples.json`](runtime_samples.json): raw PIE bone samples before and after the UE5 operation correction.
- [`Working/Phase2`](../../Working/Phase2/): scripts and lower-level import, retarget, scene and diagnostic JSON. These are experiment evidence, not a packaged production plugin.

The project had no Git repository at the target path when this work began. No commit, push or reference-project asset edit was performed.
