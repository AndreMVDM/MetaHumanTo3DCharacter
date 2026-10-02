"""Regenerate the Phase4B report from authoritative current evidence, without refitting or authoring UE."""
import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B'
def read(n):return json.loads((O/n).read_text())
fit=read('automatic_fit_v2.json');frame=read('coordinate_frame.json');validation=read('anatomical_validation_v2.json');control=read('manual_control_comparison_v2.json');audit=read('protected_file_audit.json');imp=read('ue_import_validation.json');scene=read('ue_debug_scene.json');api=read('semantic_api_inventory.json');correction=read('correction_model_validation.json')
assert not validation['downstream_authorised'] and audit['passed'] and imp['geometry_vertex_positions_pass'] and imp['uv_at_position_pass']
pending=[r['role'] for r in fit['joints'] if r['status']=='ambiguous'];accepted=[r['role'] for r in fit['joints'] if r['status']=='automatically_accepted']
summary={'phase':'4B','engine':'5.8.3-58210709+++UE5+Release-5.8','primary_input':'Characters/Lara_UnRigged_Textured.zip','final_authoritative_proposal':'automatic_fit_v2.json','classification':'experimental assisted','classification_limit':'Usefulness of proposals observed; practical correction effort and general humanoid support not established','height_cm':180,'source_height_in_inferred_frame_cm':frame['source_height_cm'],'scale_factor':frame['factor'],'body_roles':23,'automatically_accepted_candidate_count':len(accepted),'ambiguous_body_role_count':len(pending),'accepted_role_limit':'Prototype score acceptance, not independent anatomical certification','actual_user_corrections':0,'pending_review_roles':pending,'fingers':{'surface_tracks_per_hand':5,'accepted_semantic_chains':0,'classification':'experimental unresolved'},'validation':{'numeric_checks':len(validation['checks']),'failed_checks':validation['failed'],'structural_geometric_passed':validation['structural_geometric_passed'],'anatomical_passed':False,'downstream_authorised':False},'manual_control':{'mean_cm':control['mean_difference_cm'],'max_cm':control['max_difference_cm'],'ground_truth':False},'auto_skin':{'status':'not_run_anatomical_gate_rejected','weight_coverage':None,'max_influences':None,'targeted_weight_edits':0},'ik_retarget':{'status':'not_run_anatomical_gate_rejected','mappings':[],'auto_characterisation_attempted':False},'bake':{'status':'not_run_anatomical_gate_rejected','animations':[],'requested_diagnostics':['idle','walk','run','upper_body_arm_motion']},'runtime_source_independence':{'status':'not_tested_no_accepted_phase4b_character','verified':False},'preservation':{'audit':'protected_file_audit.json','passed':audit['passed'],'protected_baseline_files':audit['protected_baseline_files']},'debug_assets':scene['assets'],'no_cloud_or_runtime_inference_dependency':True,'external_inference_executed':False}
(O/'experiment_result.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
joint_table='| Role | Parent | X | Y | Z (cm) | Score | State | Ambiguity |\n| --- | --- | ---: | ---: | ---: | ---: | --- | --- |\n'
for r in fit['joints']:
    x,y,z=r['position_cm'];joint_table+=f"| {r['role']} | {r['parent_role'] or '—'} | {x:.2f} | {y:.2f} | {z:.2f} | {r['confidence_score']:.3f} | {'accepted candidate' if r['status']=='automatically_accepted' else 'ambiguous'} | {', '.join(r['ambiguity_flags']) or 'None recorded'} |\n"
api_table='| Installed system | Finding / reuse |\n| --- | --- |\n'+''.join(f"| {s['name']} | {s['classification']} |\n" for s in api['systems'])
angle=max(r['parent_segment_angle_difference_deg'] or 0 for r in control['joints'])
reviewnote='Focused independent source review identified correction ordering, hash-binding and correction-aware acceptance gaps. Repairs additionally invalidate dependency-moved joints. Passing replay/negative fixtures and the rejected synthetic corrected proposal are retained; review is not certification of anatomical locations.'
text=f'''🟢 **High confidence**

# Phase 4B — Semantic Humanoid Joint Fitting

Recorded 1 October 2026. Project: `E:/Repo/UE/Projects/MetaHumanTo3DCharacter`. UE 5.8.3, build 58210709. Authoritative current proposal: [automatic_fit_v2.json](automatic_fit_v2.json). Overall automatic anatomical decision: **REJECTED**.

## 1. Executive summary

**Minimal-correction semantic auto-rigging is not proven, including for Lara.** Geometry analysis produces a coherent 23-role body proposal, but 17 roles require anatomical review. The six automatically accepted candidates are root, three spine points and two wrists; their deterministic acceptance is not anatomical ground truth. No real user correction was applied. No Phase4B Skeleton, Skeletal Mesh, skin weights, IK assets or animations were created.

Mode A is **experimental assisted** with this prototype. The proposal is recognisably useful as a starting layout, but a small predictable correction set and reduced rigging effort have not been measured. Finger fitting is experimental and unresolved: five geometric tracks per hand, zero accepted named digit chains. This is an accurate negative feasibility result, not a completed playable Mode A character.

The installed engine has a real MetaHuman arbitrary-target fitting pipeline. Its solved state uses MetaHuman topology/model semantics; a topology-preserving Lara joint-only contract was not verified. Extracting temporary donor joints is a promising **untested** next route. A universal absence of UE semantic fitting is not claimed.

[Machine-readable outcome](experiment_result.json) records explicit gate-blocked downstream results, rather than empty success statistics.

## 2. Existing-evidence recap

The six required reports and relevant Phase4A scripts, machine evidence and native helper were inspected before fitting. Their hashes/headings are in [existing_evidence_index.json](existing_evidence_index.json).

| Earlier evidence | Consequence for Phase4B |
| --- | --- |
| Retarget investigation / supplemental IK | Preserve source/destination architecture and explicit chain/goal configuration. |
| Phase2 | Destination retargeting and playback are established for a suitable existing rig. |
| Phase3 | Mesh Wrap needs correspondences; MetaHuman custom-mesh solve fits a MetaHuman model. Conform does not directly preserve Lara as its output topology. |
| Phase3B | Coordinated physical height normalisation is proven for Mode B; production representation uses authored geometry/reference transforms. |
| Phase4A medial64/128 | Sampling creates geometric hierarchies, not acceptable semantic humanoid rigs. Increasing sampling density is not the missing solution. |
| Phase4A assisted control | Supplied semantic joints enabled UE skinning, skeletal assets, IK/retarget and destination-native diagnostic baking. Clothing/feet quality remained limited. |

Phase4A was not rerun. Its manually authored control locations were read only by post-fit evaluation. No earlier helper or assets were overwritten.

## 3. Exhaustive UE semantic-fitting/API investigation

The installation and running editor independently identify `D:/Epic Games/UE_5.8` and UE `5.8.3-58210709+++UE5+Release-5.8`. Searches cover Engine Source, plugin Source, descriptors, text Content/config/model manifests, Dataflow wrappers, and installed resource filenames. Five primary query groups yielded semantic 275, geometry 819, templates 1164, MetaHuman 900 and ML 239 matching lines. Supplemental exact-concept and predictor searches include ThirdParty text and yielded 1633 and 90 lines. All return codes, commands, exclusions and output hashes are retained in [search_manifest.json](search_manifest.json), [supplemental_search.json](supplemental_search.json), and `Working/Phase4B/Search/`.

Search terms cover every requested concept, including anatomical/body landmarks, joint/skeleton fitting, bone placement, pose estimation, segmentation, symmetry, template rigs, Control Rig/IK/FBIK, MetaHuman Body Identity/region landmarks, correspondence, Dataflow/modeling tools and ML predictors. Implementations were traced; class names alone were not treated as capabilities. Binary models/uassets were enumerated through names/manifests rather than reverse-engineered. Opaque binary semantics, unavailable source, future versions and every possible synonym cannot be exhaustively disproven.

The [API inventory](semantic_api_inventory.json) contains {len(api['systems'])} installed systems. Each records exact file paths, existence, source hashes/excerpts, public/private/editor/runtime status, C++/Blueprint/Python exposure, inputs, outputs, arbitrary-geometry anatomy capability, topology constraints/change, Lara reuse, plugin callability/licensing limits, and classification.

{api_table}

The strongest candidate is `MetaHumanCharacterEditor/Public/MetaHumanCharacterEditorSubsystem.h`: `ConformToTargetMeshes` is an exported reflected editor entry when its plugin is loaded and a Character is editable. The bundled custom-mesh Python example passes arbitrary target vertices/triangles with Auto Solve. `MetaHumanCharacterBodyIdentity.cpp` traces `PipelineFitToArbitraryTarget` and volumetric hand/foot fitting. This can infer a semantic model fit; it outputs a fitted MetaHuman model, rather than a supported standalone Lara hierarchy.

The lower-level `bodyshapeeditor/src/BodyJointEstimator.cpp` uses model vertex/joint matrices (`vertices * jvm * jjm`). It expects the known model correspondence, so Lara vertices cannot be directly substituted. Region landmark JSON stores model vertex IDs. Mesh Wrap uses supplied correspondences. IKRig characterisation reads existing reference-bone names and parents. RigLogic ML predicts existing rig behaviour; ARKit consumes camera/device skeleton tracking. Neither is arbitrary static-mesh anatomical discovery.

The [live Python reflection probe](python_api_probe.json) found 255 relevant names and loaded SkeletonModifier/import construction APIs, but no loaded MetaHumanCharacter editor subsystem. That is a current plugin-loading constraint, not installation absence. Enabling plugins/rebuilding the project was not necessary for this bounded geometry prototype and no project configuration was changed.

Epic documents the [custom-mesh workflow](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-custom-mesh-tool-in-unreal-engine) and [5.8 release](https://dev.epicgames.com/documentation/metahuman/metahuman-5-8-release-notes-in-unreal-engine). Technical exposure must be distinguished from licence permission. Engine/MetaHuman use remains subject to the [Unreal Engine EULA](https://www.unrealengine.com/eula/unreal) and [MetaHuman licence information](https://www.metahuman.com/license). This investigation does not certify redistribution of Editor modules, private code or model resources. None were copied into a distributable product.

**Bounded conclusion:** no directly reusable supported arbitrary-Lara geometry-to-semantic-joint-only API was verified. UE does contain semantic MetaHuman fitting. A native authoring plugin could call its public editor boundary subject to prerequisites; donor joint extraction and final Lara semantics still require a separate experiment.

## 4. Candidate solution comparison

| Route | Evidence / decision |
| --- | --- |
| A. Existing UE fitter | MetaHuman conform is real. Donor extraction may retain Lara surface while borrowing solved anatomy, but was not executed. Internal estimators are topology dependent. |
| B. Semantic template | Connected fixed body hierarchy guarantees role availability, not joint accuracy. Used with target-derived positions. |
| C. Geometry landmarks | Sections/symmetry/limb curves are accessible without new compiled modules or trained models. Used and numerically tested. |
| D. Medial + semantic | Could support centreline evidence, but cannot cure hidden articulation semantics. Rejected as primary route; no denser medial rerun. |
| E. Assisted fitting | Explicit correction replay and uncertainty are necessary. Seventeen body roles are too many to claim practical minimal assistance. |
| F. Local learned inference | Investigated after bounded geometry improvements failed acceptance. Optional authoring dependency only; no cloud/runtime inference. |

External candidates and requirements are recorded in [external_inference_inventory.json](external_inference_inventory.json). [RigNet](https://github.com/zhan-xu/rignet) ([paper](https://arxiv.org/abs/2005.00559)) predicts skeleton/connectivity and skinning for meshes; variable topology does not guarantee these humanoid role names. [UniRig](https://github.com/VAST-AI-Research/UniRig) ([paper](https://arxiv.org/abs/2504.12451)) offers general object rigging, with local checkpoints and CUDA inference requirements. Neither was installed, downloaded or executed. Code/checkpoint licences and actual humanoid semantics need validation before adoption. They are possible local authoring experiments, not dependencies added by Phase4B.

## 5. Selected architecture and justification

The smallest executable prototype is **C + B + E**: fresh source surface → infer frame → bake 180cm surface coordinates → target section/limb features → 23-role canonical hierarchy → deterministic scores/ambiguity → hard validation → correction replay. Public UE construction/skinning remains a later stage gated on anatomy.

Method 1 fits each side independently. Method 2 jointly selects bilateral bend candidates and mirrors averaged pair positions. The second method supplies a bounded alternative after the first fails; it does not use manual control data. Torso shell grouping and spine end placement were repaired based on actual geometry. Boot openings and hair envelopes were subsequently flagged more conservatively. No architecture was accepted just because it generated points or assets.

Prototype geometry code is Python/NumPy; it demonstrates an authoring algorithm, not a shipped UE plugin. UE public DynamicMesh/symmetry/asset APIs are potential implementation boundaries. No final UI or production plugin was built.

## 6. Geometry analysis

The authoritative untouched ZIP hash is `45fa309b7b9114ff71618feac8d0951dd55596d091d4f03e2434b6cc1384f959`. Fresh working extraction contains an unrigged mesh with 27,725 vertices, 28,636 polygons, 49,508 triangulated faces, 106,780 UV loops and one original material. No Armature or vertex groups were present. [Input inventory](input_inventory.json) and [geometry input](geometry_input.json) record per-entry hashes and arrays.

Raw source Z height is 99.95117154cm. Height measured along the inferred up axis is {frame['source_height_cm']:.8f}cm. The policy factor is 180 / measured height = **{frame['factor']:.10f}**. The normalised mesh is grounded and exactly 180cm tall before final joint fitting. This changes the working geometry by one explicit frame conversion, grounding and uniform scale; original archive geometry/UV/material bytes remain preserved.

Hair, clothing, belt/holsters, boots and knee pads create disconnected/open section components and obscure internal articulation. Bounds centres are robust geometric candidates but not anatomical observations. Sections use actual triangle-plane intersections with 0.005cm endpoint grouping; width/depth and contour closure are retained in [cross_sections.json](cross_sections.json).

![Raw surface sections, front and side](raw_geometry_sections.png)

## 7. Coordinate-frame/symmetry method

The source FBX axes do not assign semantics. PCA supplies a long-axis candidate. Paired broad sole support chooses its sign. Reflection matching on lower legs/shoes reduces asymmetric holster/hair influence; a nine-angle search and three pair-direction refinements estimate the sagittal plane. A support-envelope pitch scan refines up. The larger shoe extension from the lower shank supplies forward, checked independently on both feet.

**Handedness is explicit:** in source right-handed coordinates, anatomical left is `up cross forward`. Canonical coordinates use +X anatomical left, +Y forward, +Z up, therefore form a left-handed basis. Its source-to-canonical determinant is −1, not a proper rotation. The retained JSON key `rotation_columns_world` stores this orthonormal basis; do not feed it directly to a quaternion constructor. Reflection alone cannot name left/right.

Up is approximately (0.000404, −0.021984, 0.999758), a 1.26° support-based tilt. There are 110 near-ground support points. Reflected lower-region mean/p95 distances at final height are approximately 0.297/0.915cm. This is surface symmetry evidence, not anatomical accuracy.

Three source rigid reorientations—90° yaw, an oblique yaw/pitch/roll and upside down—reproduce the same canonical geometry within 1.5e−13cm and 180cm height. See [coordinate_frame_validation.json](coordinate_frame_validation.json). These test axis independence on Lara, not different body proportions or poses.

The first UE import exposed a lateral reflection mismatch. It was repaired before final evidence: measured legacy FBX mapping is `(X, −Y, Z)`, so the export applies that same inverse compensation. [manual_control_basis_validation.json](manual_control_basis_validation.json) also verifies the old Phase4A static mesh mapping using 161 surface samples and eight sign candidates. Pre-repair evidence remains clearly suffixed and is superseded.

## 8. Landmark inference method

Torso sections combine eligible front/back surface shells instead of selecting a breast shell alone. A stable two-leg-to-central-pelvic contour transition supplies crotch; local minimum torso width supplies waist. Their regional midpoint proposes pelvis. Actual torso centres position the spine chain between pelvis and upper torso. These are explicit geometric/semantic priors, not medical joint estimates.

Arms split at empty lateral section gaps. Upper-arm centreline extrapolation is projected to the measured shoulder envelope. Piecewise line residuals propose elbow/knee bend candidates. Wrist narrowing estimates the hand/forearm transition. Upper-thigh extrapolation proposes hips. Lower-leg narrowing estimates ankle candidates, but boot opening can dominate. A forward forefoot width maximum proposes ball/toe, with metatarsal ambiguity flagged. Broad height windows and clavicle interpolation are disclosed canonical priors; positions are not copied from anthropometric percentage tables.

Each role has side, parent, position, evidence, component scores, ambiguity flags and competing candidates where available. Candidate alternatives are not fabricated for roles with only a regional estimate.

![Automatic major landmark candidates](automatic_major_landmarks.png)

Finger sections track components over at least four adjacent samples with a 2.2cm association limit. Five tracks occur on each hand; each gets three connected geometric samples. They are named `digit_branch_*`, not thumb/index/middle/ring/pinky. Identity, palm roots and real articulation positions are unresolved; tracking can split/merge components. No finger chains are accepted or attached to the body hierarchy.

![Unresolved left-hand surface tracks](hand_finger_evidence.png)

## 9. Skeleton-template/hierarchy method

The 23-role template is one root → pelvis → three spines → neck → head; bilateral spine-to-clavicle-to-upperarm-to-lowerarm-to-hand and pelvis-to-thigh-to-calf-to-foot-to-ball branches. `thigh` denotes hip origin, `calf` knee origin, `foot` ankle origin and `hand` wrist origin. Root is grounded and distinct from pelvis.

The template gives a coherent hierarchy rather than adopting medial graph branches. Coordinates/reference axes remain proposals. Correction replay computes primary-child aim axes, deterministic roll and true parent-frame local translation/rotation matrices; a round trip reconstructs amended world positions within {correction['parent_frame_roundtrip_max_error_cm']:.2g}cm. These matrix checks do not establish deformation-quality bone roll in UE.

## 10. Confidence and ambiguity model

Scores are deterministic **support scores, not probabilities**:

    Score = 0.30 × min(sectionPoints / 30, 1)
          + 0.60 × authoredFeatureSpecificity
          + 0.10 × hierarchyPrior

Automatic candidate threshold is 0.80; any ambiguity flag overrides score. The feature-specificity values are documented prototype judgements, not learned or statistically calibrated reliability. Root uses measured ground support. Spine acceptance means a useful geometric chain position, not discovered vertebral articulations. Wrist acceptance remains provisional candidate acceptance on this one clothed mesh.

Green = automatically accepted candidate; amber = ambiguity; blue is reserved for actual manual corrections; red denotes rejected proposals. The whole proposal is rejected even though some individual candidates are green. There are zero manually corrected real joints. Figures explicitly state the overall rejection.

## 11. Automatic Lara fitting results

Both methods create 23 connected roles and pass current numeric structural/coarse geometric screens. Method 1 has nine score-accepted candidates and 14 ambiguities. Method 2 adjusts 16 paired roles by at most 1.1671cm; its bilateral equality is enforced by construction, so it is not independent accuracy evidence. More conservative ankle/head flags leave **six accepted candidates and 17 ambiguities**. This confidence reduction reflects recognised ambiguity, not a measured accuracy regression.

{joint_table}

The {len(validation['checks'])} numerical checks include root/height, graph reachability/unique roles, finite nonzero segments, left/right separation, bilateral consistency, descending limbs, ball direction, neck order, handed orthonormal frame, sole support, per-foot geometry facing and actual section envelopes. Seventeen essential anatomical-role checks fail. Section bounding envelopes allow 0.8cm tolerance and do not certify concave/internal volume. Bend-height ordering does not prove elbow/knee articulation or pole direction. Unresolved articulation flags therefore block the whole proposal.

![Full proposal front](fitted_skeleton_front.png)

![Full proposal side](fitted_skeleton_side.png)

![Foot, boot-opening ankle and ball candidates](foot_ankle_ball.png)

[Numerical gates](anatomical_validation_v2.json) explicitly set `downstream_authorised=false`. Head/neck, shoulders, elbows, pelvis/hips, knees, ankles and balls still require review; named fingers remain unresolved separately.

## 12. Automatic-versus-manual-control comparison

Control evaluation occurs **after** automatic fitting. The fitter/refinement modules do not import Phase4A landmarks. Evaluation hashes the proposal before/after and asserts unchanged bytes. Alignment inverts Phase4A uniform scaling and the verified Y handedness conversion, then applies the Phase4B inferred basis, grounding and height factor. No control-driven best-fit translation/rotation was used to improve error.

Method 1 mean/max differences are 4.1985/6.5023cm. Method 2 mean/max are **{control['mean_difference_cm']:.4f}/{control['max_difference_cm']:.4f}cm**, or 2.3116%/3.6124% of 180cm. Body hierarchy equivalence is true; each joint records absolute difference, normalised difference and parent-segment angular difference. Maximum segment-angle difference is {angle:.2f}°. The grounded-root comparison includes the different frame-origin policy and is not a root accuracy estimate.

The manually authored control is approximate, not anatomical ground truth. These errors neither prove semantic correctness nor establish the number/distance of required user edits. Bilateral consistency and angular values are available in [manual_control_comparison_v2.json](manual_control_comparison_v2.json) and the gate JSON.

## 13. User corrections required, if any

**Actual user corrections: zero. Necessary review: 17 body roles plus all five digit identities/roots per hand.** Review may accept some existing candidates, move others or reject the fit; the minimum correction count, total edit distance and authoring time are unknown. No synthetic fixture is presented as a real anatomical correction.

`Working/Phase4B/corrections.json` binds patches to the input fit hash and records the empty real correction list. Corrections require a role, finite XYZ or valid competing-candidate index, reason and provenance. Replay requires a matching hash, rejects unknown/duplicate roles, invalid values/indices and zero-length segments, and canonicalises patch order. Explicit child corrections override propagated dependency moves. Pelvis adjustment blends dependent spine positions and shifts hips; shoulder adjustment updates clavicle. All local transforms/axes are recomputed.

Dependency-moved candidates lose prior automatic acceptance and require fresh anatomical review. The `--fit`/`--review` validator route requires an exact proposal hash, explicit human anatomical-review provenance, checked role position, acknowledged/resolved ambiguity flags, review method and hashed Phase4B evidence artefact; numeric gates still run. The record's integrity cannot itself prove anatomical judgement. There is no actual human review/sign-off record here.

The synthetic pelvis replay is deterministic, reversible by replaying the original immutable fit, order independent and hash bound. Its 23 transforms round-trip successfully. Six negative cases reject invalid/stale patches. A synthetic corrected proposal without review still fails anatomy, including all moved spine points. [Correction validation](correction_model_validation.json) and [rejected corrected fixture gates](anatomical_validation_corrected.json) retain this evidence.

{reviewnote}

## 14. UE skeleton creation

**Not run: anatomy rejected.** No Phase4B Skeleton or Skeletal Mesh was constructed, and no rejected semantic proposal was passed into the Phase4A native helper. Candidate world positions/local transforms exist only as data/debug primitives.

UE authoring created only a Static Mesh, original-texture debug material/texture, three marker/edge materials, a ghost material and a debug map. `/Game/MetaHumanTo3DCharacter/Phase4B/Maps/L_SemanticFitDebug` has 47 static actors; [readback](ue_debug_scene.json) verifies zero skeletal/animation/IK assets and unit scales on both Lara surface actors. The surface itself reads 180cm. Marker sizes use display scaling; physical character size is baked geometry.

Final import has 49,508 triangles, 28,189 DynamicMesh vertices (split/index representation differs from the 27,725 DCC vertices) and one UV set. Bidirectional maximum vertex error is {imp['source_to_ue_max_cm']:.9f}cm. All {imp['uv_corner_count']:,} imported corners match source UV-at-position, maximum UV difference {imp['uv_at_position_max_difference']:.3g}, after UE V inversion. Export preserved polygon indices and UV arrays. Exact UE triangle connectivity was not certified; matching counts/positions are not that proof. Initial import's nine-triangle deficit is retained as superseded evidence. Nearly-zero tangent/binormal warnings remain a shading-quality limitation; the diagnostic material is unlit.

![UE textured raw surface and rejected static joint overlay](ue_fit_front.png)

![UE rejected proposal side view](ue_fit_side.png)

## 15. Auto-skin results

**Not run: anatomy rejected.** Coverage, influence counts and deformation statistics are null/unmeasured in `experiment_result.json`, rather than zero-valued successes. Targeted weight edits: zero. The established later route remains UE GeometryScript smooth/geodesic voxel weights with an explicitly supplied valid skeleton, followed by Skeletal Mesh asset construction. Phase4A's proof is preserved and is not claimed as a Phase4B skin result.

## 16. Deformation review

No skinned reference pose or animated Phase4B validation poses exist because binding was intentionally gated out. The displayed surface is an unrigged reference surface with static proposals. Inspection shows why shoulders, hips, knee pads, boot openings, hand/glove transitions and clothing accessories need more than silhouette centres. A future accepted fit must review shoulders/elbows/wrists, pelvis/hips/knees, ankles/fingers and clothing transitions under motion, measuring any local weight edits.

## 17. IK/retarget setup

**Not run: anatomy rejected.** No auto-characterisation attempt, chains, goals, mappings, retarget pose or Manny retargeter were created. Mode B's accepted IK architecture remains unchanged. If anatomy is accepted later, reuse the established explicit chains/goals and source/destination separation; names alone cannot establish useful reference articulation.

## 18. Baked animation results

**Not run: anatomy rejected.** Idle, walk, run and upper-body/arm diagnostic animations have not been retargeted/baked for Phase4B. Animation list is empty with explicit blocked status. Compile success, static marker appearance and earlier-phase playback do not count as this proof.

## 19. Source-independent playback verification

**Not tested: no accepted Phase4B character package.** Manny removal/native destination playback verification is false/unverified for this phase. There is no runtime inference dependency or cloud service. The scripts and debug map are authoring evidence, not a destination-native animated package. Earlier proven Mode B and assisted Phase4A playback remain separate evidence.

## 20. Limitations

Only Lara in this pose was fitted. Search windows assume a standing separated-limb humanoid; pose changes, skirts/coats, unusual shoes, asymmetric proportions, occlusion or different topology may break segmentation. Open/disconnected shells and accessory surfaces can dominate bounds and widths. The ground fit is a geometric support heuristic, not a medical upright-body estimate.

Scores depend partly on authored reliability priors. Coarse section bounding boxes can admit points outside concave tissue. Mirrored refinement suppresses actual asymmetry and cannot discover hidden articulation. Fingers lack semantic identities/root/pole evidence. Bone-roll quality, real manual correction effort, skin weights, deformation and playback are unverified. The MetaHuman donor and learned alternatives were investigated but not executed. Binary-model search/licensing conclusions remain bounded to recorded evidence.

The native editor debug step initially failed serialising a UE Array after saving the map; the script now converts it to a list, and separate readback/capture succeeded. Initial frame/torso/axis attempts remain with explicit attempt/pre-repair suffixes. Current files without those suffixes and `_v2` where specified are authoritative.

## 21. Product implications for Mode A

For **Lara**, automatic useful body layout/frame/height is proven; a semantically correct skeleton with minimal correction is not. Geometry-only fitting here is experimental assisted. It is not yet practical assisted or mostly automatic. There is enough structure to continue investigation rather than declare all auto-rig architectures nonviable, but the current geometry route alone does not meet product acceptance.

Architecturally reusable pieces are immutable working copies/hashes, physical-height policy, explicit handed coordinate frame, canonical roles, evidence/ambiguity records, deterministic hash-bound correction replay, and anatomy-before-binding gates. Preserve Mode B as the validated public path. Mode A should remain an experimental authoring path until anatomy and correction-effort evidence improve.

General support needs additional humanoids with different proportions/topologies, poses and clothing plus independent reference landmarks, true left/right annotations, correction count/time and deformation/bake tests. Lara alone cannot establish arbitrary-humanoid support.

## 22. Recommended Phase 4C or production next step

**Recommended experiment, not verified outcome:** prioritise the actual installed MetaHuman custom-mesh semantic solver as a temporary donor. In an isolated authoring project enable the required editor plugin; fit a temporary Character to normalised Lara; capture solved posed body joints/state via the public C++/DNA boundary; map a limited semantic subset into the unchanged Lara surface/frame. Do not output a MetaHuman-converted Lara or assume donor joints are correct. Validate source-pose handling, handedness, shoulder/hip/foot correspondence, clothing bias, finger mapping and permitted model usage before skinning. If donor extraction/API access fails, record that failure rather than copying private matrices into the product.

A second optional local authoring experiment may compare a trained rig predictor with independently annotated Lara joints. Keep all inference out of runtime and avoid cloud services. A geometry-assisted editor remains fallback; measure actual review/edit effort for grouped landmarks rather than asserting 17 ambiguities require 17 separate edits.

Before release, use a small diverse benchmark, fixed semantic acceptance criteria and blind landmark/deformation evaluation. After a fit passes, reuse Phase4A skinning and earlier IK/retarget architecture, then perform all four diagnostic motion categories and Manny-removed destination playback. Do not build the polished Authoring Master UI until this bottleneck is resolved.

Reproduction source is retained under `Working/Phase4B`. CPython requires NumPy/Pillow; Blender 5.2 is used headlessly for fresh extraction/export; UE editor Python/GeometryScript authors only Phase4B debug assets. No new package/model installation was required. Run from the project root:

    python Working/Phase4B/investigate.py
    python Working/Phase4B/api_inventory.py
    python Working/Phase4B/supplement_search.py
    python Working/Phase4B/supplement_api.py
    & 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python Working/Phase4B/prepare_geometry.py
    python Working/Phase4B/inspect_geometry.py
    python Working/Phase4B/fit_semantic.py
    python Working/Phase4B/refine_template.py
    python Working/Phase4B/validate_fit.py
    python Working/Phase4B/validate_fit.py _v2
    python Working/Phase4B/validate_frame.py
    python Working/Phase4B/correction_model.py
    python Working/Phase4B/validate_fit.py --fit Working/Phase4B/correction_replay_fixture.json
    python Working/Phase4B/render_fit.py

For debug reproduction run `export_debug_geometry.py` and `source_uv.py` via the same Blender invocation; then in an already-saved UE editor run `ue_debug_scene.py`, followed by `ue_capture.py` (which also records UVs and reads the earlier control surface without saving it). These scripts reimport/rebuild **only** Phase4B static assets/map. Run `validate_import.py`, `validate_control_basis.py`, `compare_control.py` with both no suffix and `_v2`, `protected_audit.py`, then `write_report.py`. Existing `protected_before.json` is intentionally retained; a new environment should establish its own pre-run baseline. `ue_probe.py` provides read-only live reflection.

## 23. Preservation/protected-file audit

[Protected audit](protected_file_audit.json) verifies **{audit['protected_baseline_files']} baselined files unchanged**, zero missing and zero new files in protected scopes outside Phase4B. It covers all Characters, existing Content/Config/Reference/Documentation, Phase4A authored working files and the project descriptor, excluding caches. All extracted source entries match archive entry hashes; the authoritative ZIP hash remains unchanged. Inventoried Engine source hashes are unchanged. The whole engine filesystem and Working/Phase2/3/3B were not comprehensively hashed; no authored writes were made there.

All new scripts/data/images are in `Working/Phase4B` or `Documentation/Phase4B`; UE authored assets are solely below `/Game/MetaHumanTo3DCharacter/Phase4B`. No Engine source, reference projects, original ZIPs, earlier accepted assets/evidence or project configuration were changed. Execution may update normal Saved/Intermediate/DDC caches. No commit/push was attempted; this directory did not report as a Git repository.

**Final decision:** this experiment cannot support the claim that MetaHumanTo3DCharacter generates a semantically correct skeleton from arbitrary unrigged humanoid geometry with only minimal correction. It proves a useful rejected Lara proposal and reusable authoring/gating architecture. Better semantic inference, actual assisted acceptance and multi-character validation are required before that claim is defensible.
'''
(O/'Phase4BSemanticJointFitting.md').write_text(text,encoding='utf-8')
print('REPORT_WRITTEN',len(text),len(pending),len(accepted))
