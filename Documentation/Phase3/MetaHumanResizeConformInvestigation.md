🟠 **Medium confidence**

# Phase 3A — MetaHuman resize, conform and proportion investigation

Date: 30 September 2026 (Australia/Sydney). Installed engine: **UE 5.8.3**, changelist **58210709**, branch `++UE5+Release-5.8`, verified from `Engine/Build/Build.version` [S01]. Investigation only: no imports, resizing, rig generation, editor API calls, project-setting changes or Unreal asset saves were performed.

The capability findings are directly supported by installed source, bundled examples and Epic documentation. Applying the workflows to Lara, numerical MetaHuman model limits, and the exact Phase 2 displacement cause remain untested. Recommendations are therefore conditional on the experiments in section 15.

## 1. Executive summary

**The suspected capability exists, with a crucial qualification.** UE 5.8 introduces MetaHuman Creator **Import → From Custom Mesh → Auto Solve**, backed by `UMetaHumanCharacterEditorSubsystem::ConformToTargetMeshes`. It accepts a human mesh with arbitrary topology, fits MetaHuman head/body geometry and joints to that surface, and supports a subsequent MetaHuman rigging/assembly workflow. Both static and skeletal mesh inputs are accepted. This is different from the older **From Template / Body Conform** workflow, which requires MetaHuman topology and vertex correspondence. [S02–S09, S29; Epic's [5.8 release notes](https://dev.epicgames.com/documentation/metahuman/metahuman-5-8-release-notes-in-unreal-engine).]

**It does not automatically enlarge an existing Tripo mesh to Manny height while preserving its original rig.** Its fitting direction is MetaHuman model → custom surface. The body solver explicitly computes `targetHeight / meanHeight` and changes the MetaHuman state scale [S06:2603–2657]. Consequently a one-metre source can guide a small MetaHuman representation; selecting this conform workflow does not itself request a 180 cm target.

For the current body-animation project, recommend **Route D: automatic uniform height normalisation with original proportions preserved**, following a separate import/root-transform validation gate. Establish final mesh/skeleton dimensions before generating IK Rigs and retargeters. Offer MetaHuman conversion as a separately selected mode when replacement topology, rig and associated material work are acceptable. No generic, supported, one-call system was found that changes arbitrary imported Tripo proportions and maintains all original bind-pose, rig, skinning, physics and morph data together.

### Direct answers to the 13 questions

| Question | Answer |
| --- | --- |
| 1. Actual automatic humanoid resize/conform feature? | **Yes for MetaHuman conversion and fitting; no verified universal in-place character normaliser.** Uniform scale is separately available through import or component transforms. |
| 2. Name? | **From Custom Mesh / Auto Solve**; API `ConformToTargetMeshes`. Also **From Template**, parametric **Body Params**, and experimental **Mesh Resizing / Mesh Wrap**. |
| 3. Implementation? | `MetaHumanCharacterEditor` subsystem → `FMeshImportTaskRunner` → `FMetaHumanCharacterBodyIdentity::FState::ConformTarget` → `MetaHumanCreatorBodyAPI` → `BodyShapeEditor`. Paths in section 10 and S02–S09. |
| 4. Programmatically callable? | Yes, public C++ and reflected Blueprint/Python editor APIs; bundled Python examples are installed. This investigation did not execute them. |
| 5. Arbitrary humanoid meshes? | From Custom Mesh accepts arbitrary **human surface topology**. Usable results depend on anatomy, pose and mesh quality; arbitrary skeleton semantics are not imported as a retained rig. |
| 6. Requires MetaHuman topology? | Custom-mesh **input: no; output: MetaHuman topology**. Template conform and whole-rig DNA paths: yes. |
| 7. Overall scale or proportions? | Custom fitting solves scale, pose, proportions and surface detail of the MetaHuman representation. Body Params changes MetaHuman measurements. Uniform normalisation changes scale alone. |
| 8. Preserves skinning? | Uniform scaling can retain the source weight associations when mesh, bind/reference transforms and dependent data remain consistent. Custom conform generates/evaluates MetaHuman skinning; it does **not** retain Tripo weights. Whole-rig DNA import retains DNA weights. |
| 9. Already-rigged meshes? | Accepted as a geometry source for custom conform; original rig is not the output rig. Coordinated uniform normalisation of a rigged input is feasible but must be validated. |
| 10. Before or after rig/retarget generation? | Finalise dimensions and bind/reference representation **before** IK Rig, goals, retargeter and pose generation. MetaHuman mode: conform → A-pose finalisation → rig/assembly → retarget. |
| 11. Solve 100 cm versus 180 cm? | A measured uniform factor of approximately **1.8** addresses physical height. Conform by itself fits to the source size rather than choosing 180 cm. |
| 12. Prevent Phase 2 displacement? | Not established. A validated unit/reference-transform gate could detect the anomaly; no evidence proves conform or a 1.8 scale factor would prevent it. |
| 13. Eventual plugin automation? | Measure and report dimensions; validate units, bind/reference transforms and weight integrity; normalise uniformly; generate IK/retarget assets only after validation; measure motion/contact. Optional MetaHuman conversion should create separate outputs. |

## 2. Reference package contents

The copied directory is **flat: nine files, no subfolders**. Its structure was enumerated, both binary FBXs were parsed (including arrays, geometry, object types, unit metadata and connections), and all PNGs were decoded and visually inspected through a contact sheet.

    Reference/MetaHuman_Conform_Topology/
        body.fbx
        head.fbx
        T_Gray_Body_D.PNG
        T_Gray_Body_D_Guides.PNG
        T_Gray_Eyes_D.PNG
        T_Gray_Head_D.PNG
        T_Gray_Head_D_Guides.PNG
        T_Gray_Head_D_Guides_Annotated.png
        T_Gray_Teeth_D.PNG

| File/content | Verified contents |
| --- | --- |
| `body.fbx`, 3,120,128 bytes | FBX 7500; one static Mesh model named `body_lod0_mesh`; 30,455 control points; 30,408 polygons, 121,632 polygon corners; normals/tangents/binormals, material, smoothing and UV layers; one material/texture/video object. No skeleton or skin deformers. |
| `head.fbx`, 3,020,976 bytes | FBX 7500; four static Mesh models: head, teeth, left eye and right eye. Head: 24,049 control points/24,002 polygons; teeth: 4,246/4,288; each eye: 770/800. UV and shading layers; two materials and one texture/video object. No skeleton or skin deformers. |
| Body/head colour and guide PNGs | Five 8192×8192 RGB images. Colour regions, mesh edges, anatomical guide lines and marked points are visible. The annotated head variant contains additional visual guide markup. |
| Eyes/teeth PNGs | Two 1024×1024 RGBA images with eye and teeth layouts. |

Both FBXs contain an AnimationStack and AnimationLayer container, but **no AnimationCurve or AnimationCurveNode objects**; these containers are not evidence of supplied character animation. There are no `LimbNode` models, skin/cluster deformers, blend-shape deformers or bind-pose objects in these reference FBXs.

**Absent:** C++ classes, Python utilities, scripts, commandlets, DLL/EXE binaries, `.uasset`/Blueprint/editor assets, `.dna` files, machine-readable landmark tables, explicit mesh-to-mesh correspondence tables, topology-map files and body-size/proportion configuration. Mesh connectivity and UVs are present inside the FBXs; guide points in PNGs are visual aids rather than solver-readable correspondence data.

The unit metadata is centimetres (`UnitScaleFactor = 1`) and the up axis is Y. Body local Y spans about **142.432 cm**; the head reaches Y ≈171.980 cm. With the exported default transforms and shared placement, the combined template envelope spans about **172.058 cm** from lowest body point to highest head point. These are measured **example asset dimensions**, not a required MetaHuman height, a naked-body anthropometric measurement or an allowable range.

Evidence: [reference inventory](Evidence/reference_inventory.json), [FBX inspection](Evidence/fbx_inspection.json), [texture contact sheet](Evidence/reference_texture_contact_sheet.jpg). The local content agrees with Epic's [asset-pack announcement](https://forums.unrealengine.com/t/metahuman-conform-topology-asset-pack-released/2609293): archetype geometry and guide textures intended to support wrapping and template conform workflows. Provenance of this particular copy was not independently authenticated beyond its content.

## 3. What MetaHuman Conform Topology actually does

**The reference package itself performs no operation.** It supplies standard-topology meshes for an external wrapping process or an appropriate UE workflow. It neither executes topology transfer nor resizes Lara.

| Concept | Meaning and verified relationship |
| --- | --- |
| Topology conformity | Correct mesh connectivity, vertex identity/semantic locations and, where used, UV correspondence. Matching vertex count alone is insufficient. Template conform assumes this prerequisite. |
| Geometric surface fitting | Move template/model vertices towards a target surface. Custom conform implements ICP-based fitting and refinement. |
| Body proportion adjustment | Change relative anatomical dimensions, such as arm length and torso shape. MetaHuman's parametric model supports measurement constraints and fit regularisation. |
| Overall scale normalisation | Apply one factor to all spatial dimensions to hit a chosen height. Ordinary import/component scaling supports this; conform's scale solve aligns its model to the source. |
| Skeleton scaling | Change bone transform scales or joint translations. This is not equivalent to changing the source mesh and inverse bind transforms consistently. |
| Skeletal mesh deformation | Change neutral or posed vertex positions. MetaHuman state fitting and general deformation tools do this; automatic arbitrary-rig maintenance is a separate requirement. |
| Re-skinning | Create/transfer vertex-to-bone influences. MetaHuman uses its body skin model and joint mapping, not the original Tripo weight array. |
| Mesh wrapping | Deform a chosen topology to another shape, usually with correspondences. Reference meshes are useful inputs; experimental UE Mesh Wrap provides actual implementation. |
| Landmark alignment | Use corresponding anatomical points or tracked face curves to guide scale, orientation, pose and fit. The PNG guides are not those numerical inputs. |
| Retarget-pose adjustment | Change retarget reference rotations and pelvis offsets to improve animation transfer. It does not rebuild neutral mesh anatomy or original skinning. |

Older template head/body conform uses DNA mappings, a correct vertex array and optionally **Match Vertices by UVs**. The installed implementation checks static-mesh counts against archetype body/combined/head counts and rejects invalid data; skeletal extraction uses a DNA-to-mesh map [S03:7408–7567]. The old Identity template workflow also requires semantically correct topology; Epic's [From Template Mesh](https://dev.epicgames.com/documentation/en-us/metahuman/from-template-mesh) describes the strict edge-loop requirements.

UE 5.8 **custom** conform instead extracts LOD0 vertex positions and triangles from `MeshDescription`, builds an arbitrary target surface, then fits the MetaHuman model. It does not require Lara's triangles to correspond to template triangles [S03:8211–8264; S04:234–325,1333–1436].

## 4. UE 5.8 resize/conform capabilities found

Broad recorded searches covered installed `Engine/Source` and `Engine/Plugins`, including editor, runtime, experimental, MetaHuman, import, geometry and animation systems. C++ headers/sources, Python, JSON and INI were searched; generated `Intermediate` and `Binaries` trees were excluded from text searches. See [search manifest](Evidence/search_manifest.json) and the four raw search files. Search matches were followed into declarations, call sites and implementations; a search hit is not treated as a usable feature.

| System | What it does | Tripo classification |
| --- | --- | --- |
| MetaHuman **From Custom Mesh / Auto Solve** | Fits MetaHuman model scale, pose, body shape and face to arbitrary human surface geometry; permits keypoints and face tracking. | **Usable with preprocessing and output conversion.** No input MetaHuman topology/DNA required; produces MetaHuman representation. Not an in-place Tripo rig editor. |
| **From Template / Body Conform** | Fits the parametric MetaHuman body to correctly corresponding vertices; can repose and estimate hand/foot joints. | **Usable only with MetaHuman topology**, obtained by wrapping/reconstruction first. |
| **From DNA / Whole Rig** | Parametric DNA fit, or verbatim body mesh/joints/RBF/skin import as a fixed body. | **Usable only with compatible MetaHuman DNA**. Not an arbitrary FBX importer. |
| **Body Params** | Solves MetaHuman shape from measurements such as height and upper-arm length. | **MetaHuman character/model only**; useful after conversion, not directly on Lara's existing mesh. |
| **MetaHuman Identity / Mesh to MetaHuman** | Face identity fitting from neutral scan/landmarks/cameras or conformed template geometry; integration with MetaHuman characters. | **Usable with Identity preprocessing for face conversion**; not a general whole-body resize API. |
| **MetaHuman Animator** | Solves/retargets performance; consumes identity/rig information. | **Unsuitable as the source-mesh normalisation stage**. |
| FBX/Interchange import transform | User-specified uniform offset scale and unit conversion. No anatomical analysis or chosen target height. | **Directly usable for uniform scaling**, subject to imported-transform validation. |
| Actor/component transform | Changes world size without rebuilding source asset anatomy. | **Directly usable for presentation/runtime sizing**, with gameplay/contact consequences. |
| IK auto characterisation/FBIK/retargeting | Recognises known rig templates, generates chains/goals/solver setup and transfers pose across dimensions. | **Directly usable for animation adaptation** after scale validation; does not physically resize the asset. |
| Experimental **Mesh Resizing / Mesh Wrap / RBF** | Wraps source topology onto target shape with landmarks; transfers deformation from corresponding source/target samples. | **Usable with preprocessing and custom integration**. No end-to-end arbitrary skeleton, bind-pose and weight normaliser found. |
| Skeletal Mesh Editing `USkeletonModifier` | Explicit bone-transform/hierarchy edits and commit operations. | **Usable as a building block**; no automatic MetaHuman proportion inference or coordinated whole-character resizing contract. |
| Geometry Script transforms/deformation; Control Rig bone scaling; morph targets | Explicit geometry/pose changes using supplied inputs. | **Building blocks**, not turnkey anatomical normalisation. |

### Actual custom-conform call chain

1. `ConformToTargetMeshes` validates the Character and edit registration, then calls `ConformTargetMeshesAsync(..., bBlocking=true)` [S03:8136–8152].
2. The subsystem copies character body/face state into an import task runner and starts the solve. Completion commits results into the **MetaHuman Character**, not into the supplied Tripo asset [S03:7740–7805].
3. `FState::ConformTarget` validates target arrays, builds a combined/body/head target, clones model state, disables floor offset and clears existing vertex deltas [S04].
4. Auto mode calls `PipelineFitToArbitraryTarget`; manual mode calls body/face fits, optional seam adaptation and optional volumetric hand/foot joint estimation [S04:1376–1436].
5. `MetaHumanCreatorBodyAPI` resolves pipeline configurations/masks and invokes body-shape fitting. It loads PCA/DNA, skin and RBF models plus LOD/joint mappings [S05].
6. Finalise the solved state to MetaHuman A-pose, then complete rigging and assembly. Posed DNA export is an intermediate geometry/body-rig product, not proof that a complete facial rig has been assembled [S09, S29].

Installed `Content/Body/IdentityTemplate` includes `body_model.dna`, `skin_model.binary`, `rbf_model.binary`, combined LOD data, skin/joint mappings, region landmarks, physics descriptions/masks and `pipeline_presets.json`. Those engine resources contain the actual fitting infrastructure absent from the reference pack.

The newer feature is corroborated by Epic's [From Custom Mesh documentation](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-custom-mesh-tool-in-unreal-engine). The documented result uses standard MetaHuman topology, generally preserves source proportions, and may need manual keypoint/refinement work. Stylisation, loose clothing and damaged meshes can compromise results. Lara acceptance was not tested.

## 5. Scale normalisation options

Separate **unit correctness**, **desired physical height**, and **transform representation**. A metre-to-centimetre conversion of 100 and a design-height correction of about 1.8 address different things.

| Stage | Evaluation |
| --- | --- |
| DCC/export before import | Best-controlled representation when mesh, skeleton, bind matrices, animation translations and morph deltas are transformed together and export uses consistent units. For rigged data, scaling only visible geometry is inadequate. |
| FBX import | Supported `UFbxAssetImportData::ImportUniformScale` plus unit conversion. Reimport a separate candidate with its own skeleton; record effective settings and inspect the resulting root/reference transforms. Setting the field alone does not prove it was applied by the selected importer. |
| Interchange import | Supported `UInterchangeGenericAssetsPipeline::ImportOffsetUniformScale`. It creates a global offset transform; skeleton construction incorporates it at the root when baking meshes [S13–S15]. **It does not guarantee unit reference-root scale.** |
| Skeletal Mesh asset properties | Bounds changes are not geometry changes. Import-scale metadata requires an import/rebuild to affect geometry. No general equivalent to static-mesh build scale was verified that safely handles all skeletal dependencies in one call. |
| Skeleton/reference pose only | Changing the root scale or joint translations alone is not a safe asset fix. Geometry, inverse bind matrices and dependent data must be handled coherently. |
| Actor/component scale | Reversible and useful for a visual comparison; does not fix imported dimensions or root scale. Mesh-only scaling leaves capsule/gameplay dimensions separate. Character/actor scaling can scale children including capsule and hidden source meshes; attachment and root-motion behaviour need explicit checks. |
| Animation retargeting | Pelvis height ratio, Scale Source and retarget-pose controls adapt motion. They do not enlarge the neutral Lara asset or supply a production capsule. |

Use `factor = selected_target_height_cm / measured_target_height_cm`. For the Phase 2 UE5 bound height **99.951138 cm**, choosing **180 cm as a project experiment** gives ≈**1.800880×**. That numerical choice is not an Epic requirement. Prefer an upright neutral anatomical measurement with explicit ground/top landmarks; report mesh bounds separately because hair, clothing, raised hands and posed limbs can distort them.

Uniform scaling preserves relative limb proportions and dimensionless weight values. It is safe only when its implementation and dependent-data updates preserve mesh/bind/reference consistency. In particular, increasing import offset scale on a root-scale-100 asset must not be presented as repairing that anomaly.

## 6. Proportion normalisation options

MetaHuman Body Params is a statistical, constraint-driven body model, not a set of arbitrary per-axis mesh scales. Installed Python demonstrates active Height and Upper Arm Length constraints, then `SetBodyConstraints` and `CommitBodyState` [S10]. The source exposes measurement minima/maxima and height-conditioned ranges [S04, S06]. These controls apply to MetaHuman state.

Custom conform can solve non-uniform **shape/proportion changes of the MetaHuman representation** and posed surface refinement. It fits to the input anatomy rather than enforcing one Manny envelope. To alter the output to a project envelope, explicitly choose subsequent body constraints, validate remaining vertex deltas and regenerate the output rig/dependencies. Preservation of every stylised feature is not guaranteed.

For existing Tripo topology/rig, potential custom work includes authored morphs, skin-aware rest-shape deformation with joint relocation, or landmark wrapping plus re-skinning. UE supplies pieces, but the investigation did not find a supported automatic pipeline that performs all these together. Bone scaling at runtime is a pose effect; stretching neutral anatomy requires bind-pose and skin validation. Moving bones with `USkeletonModifier` is not evidence that mesh surface geometry automatically moves into a newly inferred anatomy.

The experimental Mesh Resizing plugin contains a concrete alternative to external wrapping: `FMeshWrapNode` calls `UE::Geometry::FWrapMesh::WrapToTargetShape`, using matched source/target landmark indices, projection and Laplacian stiffness [S23–S24]. Its output is a dynamic wrapped mesh. `FApplyRBFResizingNode` requires matching vertices between the driver source and target, even though the separate mesh being deformed may differ [S25]. These systems require prepared correspondences/driver meshes and custom skeletal integration; they are not a reason to choose an automatic proportion rewrite for this project.

## 7. MetaHuman body-size model

**No single mandatory MetaHuman height or Manny-equivalent envelope was found.** The installed model supports continuous parametric measurements and legacy fixed compatibility bodies. `EMetaHumanBodyType` contains 18 fixed identifiers: female/male × short/medium/tall × `nrw`/`ovw`/`unw`, plus `BlendableBody` [S11]. These are categories, not verified centimetre limits.

Scale is represented in model state (`ScaleFactor`/uniform scale); evaluation scales mesh vertices and joint translations, and measurement ranges can scale with character height. The source loads fixed/variable measurement inputs from model constraints, with evaluated fallback ranges, rather than defining a single global public stature constant [S06]. `GetBodyConstraints(character, true)` exposes the model's actual current min/max measurements through the editor API [S02, S04].

Verified values and their limits:

| Value | What it establishes |
| --- | --- |
| Reference combined envelope ≈172.058 cm | Size of this supplied archetype example only. |
| Phase 2 UE5 bounds ≈99.951138 cm | Recorded imported UE5 mesh bound height; consistent with fresh FBX analysis. |
| Phase 2 Manny ≈180 cm, Mixamo ≈100 cm | Historical Phase 2 report approximations, not newly measured exact heights. |
| `177.5f` in constraint-range code | A local initial value overwritten by an active Height target or actual measurement; **not a canonical height requirement** [S06:5397–5402]. |
| Bundled sculpt example: Height 190.0, Upper Arm Length 38.5 | Example API inputs only; **not model maxima or recommended proportions** [S10]. |

**Unverified:** numeric minimum/maximum valid height, universal skeleton-size bounds, standard shoulder/hip dimensions and acceptable limb-ratio deviation. The installed model data exists, but it was not evaluated through a registered MetaHuman Character in this read-only task. No limits are invented. Epic documents broader height support without publishing a universal number in its [5.7 conform improvements](https://www.metahuman.com/news/metahuman-5-7-brings-major-improvements-to-body-conforming-with-more-to-come); [Body Params](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-body-params-tool-in-unreal-engine) provides ranges and range controls.

A plugin should store configurable minimum/preferred/maximum target height and proportion thresholds, with no fabricated MetaHuman defaults. A future experiment can query model ranges and record them for a selected engine/model version; those ranges must be distinguished from the project's acceptance policy.

## 8. Applicability to the Tripo UE5 rig

Fresh FBX parsing found **27,725 mesh control points**, 28,636 polygons, one Skin plus 61 Cluster deformers, 61 limb bones, one bind-pose object, metre metadata and no UV layer in this tested untextured export. This differs from reference body/head topology. Manny-like bone names do not confer MetaHuman topology, DNA, hierarchy or deformation compatibility.

Uniform height correction can retain this character and its weight associations. First address the imported root scale **(100,100,100)** and time-zero/bind-pose warning, using separate imported candidates and quantitative checks. Do not share Manny's skeleton or edit Phase 2's root in place.

From Custom Mesh can consume the skeletal asset's LOD0 surface [S03]. Bone count/names are not inputs to the arbitrary surface target builder. This makes it a valid **candidate conversion input**, not a validated conversion success. The supplied body appears clothed/stylised in project context; assess the actual surface, shoulders, fingers, face, accessories and topology before solving. No conclusion about naked-body anatomy can be drawn from a clothing silhouette.

From Template and whole-rig DNA cannot directly consume this Lara as compatible MetaHuman data. Preprocessing would mean reconstructing/wrapping to appropriate topology and supplying appropriate rig/DNA where required.

## 9. Applicability to the Tripo Mixamo rig

The tested Mixamo FBX has the same **27,725 control points and 28,636 polygons**, one Skin plus 65 Cluster deformers, 65 limb bones, one bind-pose object, metre metadata and no UV layer. `Hips` is the deforming skeleton root/pelvis; it is not the UE5 variant's extra non-deforming `root`.

Uniform normalisation remains the simplest candidate while preserving its original proportions and Mixamo rig. Phase 2's stable generated IK pass does not prove every reference scale is one; that exact Mixamo reference-root scale was not in the supplied root probe. Measure it in the next authorised experiment.

Custom conform applicability is essentially the same as UE5 Lara because the fitter consumes geometry, not Mixamo semantic chains. It creates a MetaHuman output; it does not copy Mixamo terminal bones or original weights. Template/DNA restrictions remain identical. Existing retarget success is evidence that animation adaptation is possible without proportion normalisation.

## 10. Relevant Unreal APIs

All paths below are relative to the verified engine root `D:/Epic Games/UE_5.8/Engine`. [source_evidence.md](Evidence/source_evidence.md) supplies clickable absolute paths and original line numbers. [api_inventory.json](Evidence/api_inventory.json) records 19 subsystem declarations and reflection status; [systems_inventory.json](Evidence/systems_inventory.json) covers the other systems. Public visibility is distinguished from a long-term stability guarantee; MetaHuman Creator's descriptor marks it Beta, while Mesh Resizing is Experimental.

| Class/API | Public header and module/plugin | Scope and exposure |
| --- | --- | --- |
| `UMetaHumanCharacterEditorSubsystem` | `Plugins/MetaHuman/MetaHumanCharacter/Source/MetaHumanCharacterEditor/Public/MetaHumanCharacterEditorSubsystem.h`; `MetaHumanCharacterEditor` | **Editor-only**, exported public class. Blueprint/Python: edit registration, mesh extraction, `ConformToTargetMeshes`, `AlignToTargetMeshes`, face tracking, `CommitPosedStateAsAPose`, keypoints, constraints, `RequestAutoRigging`. S02–S03. |
| Template/DNA conform APIs on same subsystem | Same header: `GetMeshForBodyConformingFromTemplate`, `GetJointsForBodyConformingFromTemplate`, corresponding `FromDNA` methods, `ConformBodyToTarget` | Public reflected Editor APIs. Old unsuffixed FVector wrappers deprecated in 5.8; `ImportFromBodyTemplate`/older DNA fit deprecated in 5.7. Use current names. |
| Mesh/joint/whole-rig import on same subsystem | `SetBodyMesh`, `SetBodyJoints`, `ImportBodyWholeRig` | Public reflected Editor APIs; topology or compatible DNA required. Not general Tripo rig-preservation calls. |
| `UMetaHumanCharacterFactoryNew` | Same module `/Public/MetaHumanCharacterFactoryNew.h` | Editor factory, used with AssetTools in installed example. Creates Character assets; no creation performed here. |
| `FConformTargetParams`, `FConformTargetMesh`, `FBodyConformSolveSettings` | `Plugins/MetaHuman/MetaHumanCoreTechLib/Source/MetaHumanCoreTechLib/Public/MetaHumanConformTargetParams.h`, `MetaHumanConformSolverSettings.h` | Reflected input structures; core fitting module is Editor. Combined/body/head modes, geometry arrays, keypoints, camera/face curves, auto/manual solve settings. |
| `FMetaHumanCharacterBodyIdentity::FState` | Same core module `/Public/MetaHumanCharacterBodyIdentity.h` | Public C++ wrapper; Conform/ConformTarget and constraints. No generic UObject/Python subsystem equivalent at this layer. Prefer subsystem API for plugin integration. |
| `MetaHumanCreatorBodyAPI`, `BodyShapeEditor` | Same core module `/Private/api/MetaHumanCreatorBodyAPI.h`, `/Private/bodyshapeeditor/include/bodyshapeeditor/BodyShapeEditor.h` | **Internal private implementation**; not the recommended plugin dependency boundary. |
| `UE::Wrappers::FMetaHumanConformer` | Core module `/Public/MetaHumanConformer.h` | Public C++ face-fitting wrapper (scan/depth, camera, landmarks, Identity fitting); Editor module. Not the whole-body resize API. |
| `UMetaHumanIdentityFace::Conform` | `Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanIdentity/Public/MetaHumanIdentityParts.h` | Reflected face solve, tied to Identity data/workflow. S30. |
| `UFbxAssetImportData` / `UFbxSkeletalMeshImportData` | `Source/Editor/UnrealEd/Classes/Factories/FbxAssetImportData.h`, `FbxSkeletalMeshImportData.h` | Editor import configuration; reflected properties `ImportUniformScale`, scene/unit conversion. No automatic target-height detector. |
| `UInterchangeGenericAssetsPipeline` | `Plugins/Interchange/Runtime/Source/Pipelines/Public/InterchangeGenericAssetsPipeline.h`; `InterchangePipelines` | Public reflected pipeline properties including `ImportOffsetUniformScale`; authored import route. Runtime plugin location does not make MetaHuman authoring a runtime operation. |
| `UIKRigController`, `UIKRetargeterController` | `Plugins/Animation/IKRig/Source/IKRigEditor/Public/RigEditor/IKRigController.h`, `/RetargetEditor/IKRetargeterController.h` | Public Editor C++/Blueprint/Python controllers for setup/characterisation; not mesh sizing. |
| `FIKRetargetScaleSourceOp`, `UIKRetargetScaleSourceController` | `Plugins/Animation/IKRig/Source/IKRig/Public/Retargeter/RetargetOps/ScaleSourceOp.h` | Runtime pose operation plus reflected controller/settings. Scales source pose/IK goals, not target asset geometry. S27. |
| `USkeletonModifier` | `Plugins/Runtime/MeshModelingToolset/Source/SkeletalMeshModifiers/Public/SkeletonModifier.h` | Public reflected `SetSkeletalMesh`, `SetBoneTransform`, commit authoring tools; check editor build guards for asset commit. No inferred anatomical normalisation. S26. |
| `FMeshWrapNode`, `FMeshWrapLandmarksNode` | `Plugins/Experimental/MeshResizing/Source/MeshResizingNodes/Public/MeshResizing/MeshWrapNode.h`; descriptor module `MeshResizingDataflowNodes` | Public Dataflow structs, Experimental; C++/Dataflow integration. No high-level reflected Python humanoid resize function verified. |
| `FWrapMesh` | `Plugins/Runtime/GeometryProcessing/Source/DynamicMesh/Public/Operations/WrapMesh.h`; `DynamicMesh` | Public C++ geometry operation; shape wrapping, not skeletal rig generation. |
| `FRBFInterpolation`, `FBaseBodyTools`, `FCustomRegionResizing` | `Plugins/Experimental/MeshResizing/Source/MeshResizingCore/Public/MeshResizing/` headers | Exported C++ deformation/proxy tools in runtime module; Experimental. Prepared driver/correspondence data required. Dataflow RBF node headers are private. |
| `UGeometryScriptLibrary_MeshTransformFunctions` | `Plugins/Runtime/GeometryScripting/Source/GeometryScriptingCore/Public/GeometryScript/MeshTransformFunctions.h` | Reflected dynamic-mesh transforms; callers must perform separate skeletal asset integration. |

No dedicated MetaHuman automatic whole-body resize/conform commandlet was found in the investigated Creator source. Bundled Python examples demonstrate batch requests, but editor registration, models, face tracking and rigging/assembly remain prerequisites. A headless commandlet execution contract was **not tested**. A future plugin should use an Editor module and the public subsystem, handle solve failure/cancellation, then validate resulting anatomy before assembly. Full face autorigging has a separate request/service path; conform success alone does not verify service readiness or a finished playable character.

One read-only caution for future automation: `GetMeshDataForConforming` may call `MeshDescription->Compact()` when IDs need compacting [S03:8239–8243]. Therefore even this extractor should not be called on protected source assets when strict in-memory immutability is required; use a working copy. It was not called here.

## 11. Pipeline ordering and dependency consequences

| Option | Consequences |
| --- | --- |
| A: import → resize/conform → rig → retarget | Preferred for new unrigged inputs, particularly MetaHuman conversion. Finalise neutral shape/scale before skinning, physics and retarget setup. For an already-rigged input, discarding/replacing its rig is an explicit scope choice. |
| B: rigged import → normalise mesh and skeleton → retarget | Preferred for retaining Tripo rigs. Transform geometry and bind/reference representation consistently, verify weights/rest deformation, then build goals and retargeter from the final candidate. Rebuild dependent physics/morph/animation data as needed. |
| C: rigged import → retarget → runtime scale | Useful comparison/runtime presentation route. Retargeting still sees the small asset dimensions; world IK goals, contact, capsule, sockets and root motion require coordinated scale handling. It does not repair root/reference inconsistencies. |
| D: custom surface → MetaHuman conform → A-pose commit → body/face rig and assembly → retarget | Discovered UE route. Preserves target shape only approximately and replaces representation/rig. Adjust chosen output height/body constraints explicitly if required. |

| Dependency | Required treatment when dimensions change |
| --- | --- |
| Bind pose / inverse bind transforms | Keep neutral vertices and bone bind transforms in the same units/space. Changing only root scale or only geometry can double-apply scale or alter rest deformation. |
| Reference skeleton | Recompute and inspect local and accumulated component transforms; preserve hierarchy semantics. A unit-scale target root is an intended validated representation, not something to force by editing one transform. |
| Skin weights | Uniform scaling need not change dimensionless weights; anatomical reshaping/joint relocation can require new weights/correctives. Inspect influence sums and deformation. |
| Physics assets | Update/rebuild body shapes and constraints for new rest dimensions; validate runtime contacts and simulation. Phase 2 evidence lists no generated Physics Asset despite the script requesting one. |
| Morph targets | Scale delta vectors with uniform asset-space geometry scaling. Non-uniform rest-shape changes require equivalent morph reshaping/remapping; new topology breaks vertex-ID reuse. |
| Root scale | Distinguish FBX unit conversion from a deliberate actor-size factor. Validate accumulated scale, animation translations and neutral geometry; do not stack fixes blindly. |
| Retargeting / IK goals | Generate/reinitialise from final mesh dimensions; re-evaluate pelvis ratio, goals, chain lengths, retarget pose and solver stability. |
| Foot contact | Recheck ankle/toe endpoints, floor offset, sole thickness and planting/stride settings across a full cycle. Height equality is not evidence of planted feet. |
| Capsule | Set intended radius/half-height and mesh offset for final character height. Mesh scaling alone does not set gameplay collision. |
| Root motion | Test extracted and applied translation against world displacement, speed and capsule movement. World scale may change travelled distance depending on component/character integration; do not infer behaviour from the in-place Phase 2 clip. |

## 12. Relationship to the Phase 2 root-scale failure

### Verified observations

- Fresh FBX parsing: both Lara exports declare `UnitScaleFactor = OriginalUnitScaleFactor = 100` (metres), with raw geometry Z span ≈0.999512. This predicts approximately 99.9512 cm under consistent unit conversion, agreeing with the recorded UE5 bounds. **The small physical character is already present in the input**, rather than evidence that Unreal omitted all metre conversion.
- UE5 source `root` has no explicit `Lcl Scaling` property; its explicit transform properties include translation and rotation. The recorded imported reference root is scale 100 [Working/Phase2/root_probe.json]. That suggests an import/ancestor/unit/bind representation issue; raw local-property absence does not prove the FBX SDK's evaluated bind transform has no scale.
- Historical failed UE5 pelvis heights include **4958.440757 cm** and about 5200 cm. With Run IK Rig disabled, later pelvis heights are about 49–51 cm [Documentation/Phase2/runtime_samples.json]. Setting pelvis scales to 0.01 had not removed the vertical displacement.
- Phase 2 used `AssetImportTask` with `FbxImportUI`, but did not explicitly set scale/unit options or record the resolved importer settings. UE's AssetTools can route to Interchange, and the installed converter maps legacy FBX scale/unit options to Interchange. The exact effective route/options cannot be reconstructed definitively from the saved JSON alone.
- UE5 recorded two generated solvers; Mixamo recorded one. The auto-FBIK creation function appends a Full Body IK solver [S22]; the snapshot does not include enough solver type/settings information to attribute failure to duplicate/accumulated setup.

### Source-level mechanism and remaining uncertainty

The retargeter creates component-space reference positions and strips transform scale; it then resolves retarget-pose edits [S16:43–82]. Pelvis Motion computes a ratio from initial target/source pelvis heights [S21]. Run IK Rig passes the component pose to the IK processor, solves, then copies it back [S18]. Full Body IK initialises from the IK rig's reference positions and copies solver results into those transforms [S19]. PBIK explicitly carries incoming scale through `SetBoneTransform` and `GetBoneGlobalTransform`; it does **not** establish a simple universal rule that it resets every scale to one [S20]. Finally the runtime retarget node converts component to local pose and restores reference scale using `ScaleFromRetarget + (RefScale - 1)` [S17:195–207].

**Inference:** a root-scale-100 reference representation interacting with translation-only retargeting, goal generation, pose reconstruction or solver output can produce a second factor of 100 on a pelvis-sized translation. About 50 cm becoming about 5000 cm is consistent with that hypothesis. The operation isolation localises the observed failure to the enabled IK path and its subsequent output reconstruction; it does not prove a single defective multiplication inside FBIK.

Competing explanations remain: bind-pose/time-zero mismatch; incorrectly scaled IK goals/reference positions; accumulated solvers or differing generated configuration; pelvis scaling settings; animated/component-space versus local-space reconstruction. Component scale was not independently resampled in this investigation. Small mesh size alone is insufficient: Mixamo's similarly small mesh was stable, and Lara stayed small rather than uniformly exploding after the IK correction.

**Could conform have prevented it?** A newly assembled, consistently represented MetaHuman rig could avoid the original import representation, but that is a replacement workflow and an untested proposition. **Could normalisation have prevented it?** Only a validation gate that catches and resolves the underlying representation, not a cosmetic scale factor. Neither outcome is claimed as proven.

## 13. Automation feasibility

High-feasibility components are source/unit inventory, mesh-height measurement, root/reference-scale inspection, configurable uniform correction, explicit import configuration, semantic chain generation and measured output validation. Keep each result auditable and store source hash, importer settings, transformations, warnings, dimensions, skeleton roles and solver configuration.

MetaHuman conversion is feasible through public editor APIs and shipped examples, with preprocessing, optional face tracking/keypoint review and a subsequent rig/assembly stage. Requirements include installed Creator/model data, registered edit state, valid LOD0 MeshDescription, correct target-part slot, finite geometry/indices, camera correspondence for face curves and output validation. `ConformToTargetMeshes` returns the actual solve result; handle false, invalid input and cancellation rather than equating asset creation with success [S03]. The default values in `FConformTargetParams` are not a complete automatic solve recipe: the bundled example sets auto mode and the `combined` pipeline explicitly [S07, S09].

Fully automatic proportion rewriting **while preserving original arbitrary rig/topology** remains custom engineering with substantially higher risk. Experimental wrapping/RBF tools reduce geometry work, but do not supply the missing anatomy policy, skeleton relocation, bind update, re-skin/corrective, physics and animation validation pipeline.

## 14. Recommended implementation approach

Choose **Route D (hybrid), with Route A as its default height treatment**:

1. Preflight geometry, FBX units, root/ancestor/reference transforms, bind-pose validity, skin weights and measured anatomy. Separate physical smallness from suspicious scale representation.
2. Resolve import representation first using an isolated candidate and explicit importer settings. Require coherent neutral geometry/reference transforms; prefer unit bone-scale representation verified through actual output.
3. Apply a measured uniform size policy, preserving relative anatomy and original weight associations. Use coordinated DCC/export or a validated import path. Do not promise that `ImportUniformScale` alone produces a unit-scale root.
4. Finalise morph, physics, mesh offset and capsule requirements. Generate IK Rigs/goals/retargeters from the final candidate dimensions, then validate multiple motions and root motion.
5. Expose **MetaHuman conversion** separately: custom surface → conform → A-pose finalisation → chosen body constraints/height → rig/assembly → material/texture work → retarget. Create separate output assets and record that the source topology/weights are replaced.

Do not automatically push Lara into unspecified shoulder/hip/limb ratios. IK retargeting supports differing dimensions, and the project has no verified requirement for a particular MetaHuman anatomy envelope. Keep proportions unless the user selects a conversion or authored reshape mode with explicit acceptance criteria.

## 15. Recommended next experiment

**First run a controlled import-representation experiment; do not combine it with MetaHuman conversion.** It should be a separately authorised Phase 3B that creates only new candidates:

1. Record exact original asset import data, importer/translator choice, unit flags, import offset, reference local/component transforms, all solver types/settings/goals, mesh/component/world bounds, capsule settings and bind warnings for both rigs.
2. Establish a centimetre-exported candidate with coherent geometry, joints and bind matrices and unit local bone scales. Hold physical height near the original 100 cm initially. Compare with an explicitly configured UE import of the original metre file; distinguish these two representations without editing Phase 2.
3. Generate fresh candidate IK assets once, recording solver counts. Compare FK-only, each solver independently and the full IK stack with identical motion/pose settings. Sample pelvis/head/feet before IK, after IK, after conversion to local pose and in world space.
4. Once stable at the original height, make a separate **180 cm project-test candidate** using the measured factor. Repeat FK/IK measurements before judging height correction successful. Keep imported-root normalisation and intentional stature correction as independent variables.
5. Add idle, walk, run, reach and a root-motion clip. Check finite transforms, expected limb lengths, pelvis envelope, full-cycle foot contact/slide and capsule/root displacement. Choose and record acceptance tolerances; none are inferred here as Epic standards.

**Second, optional experiment:** duplicate the surface into a new MetaHuman conversion work area, try From Custom Mesh Auto Solve, inspect shoulder/hip/finger/face fit, finalise A-pose, query `GetBodyConstraints` ranges, and assemble. Compare measured input/output stature and skin deformation to show whether conversion adds value. The tested untextured files have no UV layer, so automatic preservation of their materials/textures is not assumed. Do not run the bundled examples unedited: they create/save assets and some failure paths delete newly created outputs.

### Evidence, validation and limits

- [source_evidence.md](Evidence/source_evidence.md), [source_evidence.json](Evidence/source_evidence.json): S01–S30 paths, SHA-256 and original numbered source excerpts.
- [reference_inventory.json](Evidence/reference_inventory.json), [fbx_inspection.json](Evidence/fbx_inspection.json): reference structure/hashes/image metadata and fresh geometry, unit, transform, deformer and connection evidence for the templates and two Lara files.
- [search_manifest.json](Evidence/search_manifest.json), `resize_search.txt`, `fit_search.txt`, `proportions_scale_search.txt`, `identity_search.txt`: recorded broad search scope/patterns/results. These are unfiltered source matches, including unrelated resize/wrap terms; counts do not imply capability counts.
- [api_inventory.json](Evidence/api_inventory.json), [systems_inventory.json](Evidence/systems_inventory.json), [relevant_file_inventory.json](Evidence/relevant_file_inventory.json): callable declarations, system classifications and source-file locations.
- [pipeline_presets_structure.json](Evidence/pipeline_presets_structure.json): installed auto-solve pipeline configuration and provenance; no solver run performed.
- [validation.json](Evidence/validation.json): SHA-256 comparison of **74 protected project/reference/Phase 2 files**, with no changes; indexed source hashes rechecked. No Git repository exists at the project path; no commit or push occurred.

Self-review checked all 15 requested report sections and the 13 direct questions. The key corrections during investigation were distinguishing the new arbitrary-topology 5.8 conform path from older template restrictions, distinguishing template scale-to-source from source height normalisation, and avoiding an unsupported claim that FBIK simply discards scale. Remaining gaps are explicitly bounded: no live Lara conform run, no evaluated model height limits, no controlled reimport, no solver-state instrumentation and no proof of the exact displacement cause.
