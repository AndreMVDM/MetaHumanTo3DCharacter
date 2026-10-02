import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4C';O=P/'Documentation/Phase4C'
def read(n):return json.loads((O/n).read_text())
fit=read('automatic_fit_v2.json');cmp=read('phase4b_comparison.json');gate=read('anatomical_validation.json');tr=read('transform_mapping.json');audit=read('protected_file_audit.json')
body_table='\n'.join(f"| {r['role']} | {r['source_joint_name']} | {r['position_cm'][0]:.2f}, {r['position_cm'][1]:.2f}, {r['position_cm'][2]:.2f} | {'Provisional' if r['status']=='automatically_accepted' else 'Review'} |" for r in fit['joints'])
compare_table='\n'.join(f"| {r['role']} | {r['absolute_difference_cm']:.2f} | {r['difference_percent_180cm']:.2f}% | {r['parent_segment_axis_difference_deg']:.1f}° |" for r in cmp['B_4C_vs_C_4A']['joints'] if r['role'] in ['pelvis','neck_01','clavicle_l','clavicle_r','upperarm_l','upperarm_r','lowerarm_l','lowerarm_r','hand_l','hand_r','thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r','ball_l','ball_r'])
text=f'''🟢 **High confidence**

# MetaHumanTo3DCharacter — Phase 4C MetaHuman Semantic Donor

Investigation executed 1 October 2026. Installed engine: UE **5.8.3**, changelist **58210709**. Level 1 execution with self-review. This is an experimental investigation, not a product release; no Git actions or Mode B changes were made.

## 1. Executive summary

**Yes: the installed custom-mesh solver can supply a temporary, publicly extractable semantic donor for Lara. No: this experiment does not establish practical assisted or mostly automatic Mode A.** The successful combined solve returned true in 43.203 seconds, exported posed DNA and exposed 342 named joints with parents and solved positions. A fresh process reloaded the saved temporary MetaHuman Character. The two public joint extraction paths agree exactly.

The unchanged source remains unrigged, with its original polygon topology, UVs and material source. Donor positions are stored independently as JSON and mapped back to original Lara authoring space. The numerical inverse is sound, but anatomical acceptance fails: **19/23 body roles need review; 0/10 finger chains are accepted**. The final gate has 22 failures including unresolved articulations and digit collisions. **No downstream Lara skeleton, skinning, IK, retarget, bake or playback was run.**

Classification: **body — experimental assisted; fingers — unsuitable for automatic mapping in this zero-keypoint solve, with assisted correction effort unmeasured**. Four root/axial points are provisional candidates under the existing gate policy, not proof of a usable whole-body skeleton. Actual corrections: zero; minimal correction remains unproven. [Experiment result](experiment_result.json).

## 2. Phase 4B starting point

All seven requested prior reports and the seven mandatory Phase 4B evidence files were read before implementation. [Evidence index](existing_evidence_index.json) records their hashes. Phase 4B remains rejected: 23 connected body roles, six provisional candidates, 17 ambiguous roles, unresolved named fingers and downstream work blocked. Phase 4A remains an approximate authored control and earlier downstream feasibility proof, not anatomical ground truth. Mode B architecture is unchanged.

Only Phase 4B's body-frame function, canonical body role schema, validation architecture and deterministic correction framework were reused. Its landmark positions and Phase 4A control coordinates did not initialise the donor solve or mapping. Existing helpers were imported read-only with bytecode writing disabled. There was no additional geometry-based fitting method or external learned fallback.

## 3. MetaHuman plugin/API verification

The existing project already enables PythonScriptPlugin and EditorScriptingUtilities. **MetaHumanCharacter** was loaded per command using `-EnablePlugins=MetaHumanCharacter`; the project descriptor and Config files were not edited. Its installed descriptor pulls in the MetaHuman ecosystem, including RigLogic, MetaHumanSDK, modelling, Dataflow and other dependencies. **MetaHumanCoreTech** supplies the core body library. [Installed plugin/public API inventory](semantic_api_inventory.json) records descriptors, public header hashes and required installed resource paths.

`unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)` returned a real subsystem. Its Python `conform_to_target_meshes` was executed, not merely found in reflection. C++ extraction through exported public headers was compiled and executed. Blueprint-callable declarations were inspected; no Blueprint graph was executed. [Python probe](python_api_probe.json).

The extraction helper is an isolated editor module, **Phase4CTools**, under `Working/Phase4C/NativeHost/Plugins`. It links public RigLogicModule and MetaHumanCoreTechLib. No helper was installed into the main project or Engine. The template `SKM_Body` and installed body model resources were available.

## 4. Actual fitting path

The concrete execution sequence is:

1. Obtain the editor subsystem and the Phase4C temporary static mesh.
2. Read target vertices/triangles with `get_mesh_data_for_conforming`.
3. Create a MetaHumanCharacter using MetaHumanCharacterFactoryNew.
4. Call `try_add_object_to_edit`; abort if the character cannot enter edit state.
5. Populate ConformTargetMesh, ConformTargetParams and MetaHumanCharacterTargetMeshKey.
6. Call `conform_to_target_meshes(character, key, params)` and check its Boolean result.
7. Save the temporary Character, then call the public `export_posed_dna` with an external-only path.
8. Read the posed result with the public Python API and public DNA reader/helper.

The primary input uses `COMBINED`, `pipeline_name=combined`, `auto_solve=True`, `estimate_body_joints_from_mesh=True`, zero keypoints and zero supplied face tracking curves. `face_iterations=0` was passed, but Auto Solve uses pipeline presets; this manual setting does **not** demonstrate that the combined preset omits head stages. This is an untracked combined fit used for body-joint evaluation, not a validated facial fit. [Full solve configuration](solve_configuration_combined.json), [execution script](../../Working/Phase4C/ue_solve.py).

**Can head/face fitting be omitted?** Body-only mode exists and was executed successfully, without face curves. The diagnostic supplied the full head-and-body Lara surface to BODY_ONLY, however, and produced a badly displaced result. A correctly separated headless-body input was not tested. The selected attempt uses the representation appropriate to the actual full surface. Epic documents separate body-only and combined modes, A-pose guidance, clothing/stylisation limits and keypoints for difficult fingers/toes. [Official custom-mesh workflow](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-custom-mesh-tool-in-unreal-engine).

## 5. Temporary donor construction

The primary archive was freshly extracted under `Working/Phase4C/Inputs`. Its SHA-256 is `{audit['archive_sha256_after']}`. Original data contains **27,725 vertices, 28,636 polygons, 49,508 Blender triangles and 106,780 UV loops**, one material and no armature or vertex groups. [Input inventory](input_inventory.json), [source geometry](geometry_input.json).

The fresh source was normalised by the established robust frame. Measured frame-aligned stature is **99.748171 cm**; `180 / measured height` gives scale **1.8045443647800623**. Raw DCC world Z height is 99.951172 cm; the difference comes from the inferred body frame, not a second scaling policy. The normalised source is 180 cm high.

Temporary assets:

- `/Game/MetaHumanTo3DCharacter/Phase4C/Geometry/SM_Lara180`
- `/Game/MetaHumanTo3DCharacter/Phase4C/Donor/MHC_LaraDonor_combined`
- External posed DNA: `Working/Phase4C/Donor/LaraDonor_combined_Posed.dna`

The target static mesh was duplicated into Phase4C from the existing read-only 4B import, then numerically compared with the fresh ZIP-derived vertices. Maximum indexwise position difference is **{tr['ue_target_indexwise_vertex_max_difference_cm']:.9f} cm**. Counts and positions agree; **UE triangle connectivity differs from Blender triangulation**, so exact temporary UE topology equivalence is not claimed. The original polygon topology is preserved separately and verified after the experiment. The temporary mesh references an existing 4B material read-only; it is an authoring evidence dependency, not a destination-native package. No Lara geometry was replaced with donor topology.

## 6. Solve results

| Attempt | Actual solve result | Interpretation |
| --- | --- | --- |
| BODY_ONLY, full surface | True; 24.532 s; posed export retained | Diagnostic representation mismatch; donor crown near 201.7 cm and severe torso/head displacement. Rejected. |
| COMBINED, full surface | True; 43.203 s; saved Character, export and joint readback completed | Selected temporary donor; broad surface alignment improves, but body articulation and fingers remain rejected. |

The first commandlet crashed in Slate asset-browser synchronisation after writing external DNA. The log and extracted result are retained; it is not presented as a clean completed export call. The second run saved the Character before export and used `project_path=''`, avoiding the browser-sync path. [First solve state](solve_result_bodyonly_fullsurface.json), [selected solve state](solve_result_combined.json), [first diagnostic visuals](BodyOnlyFullSurface/temporary_donor_overlay.png).

The selected DNA hash is `a88062db0b7d6c8dbb8d470e0b241d80b235b20b37e8545d68dd833f486cacb4`. Its public LOD0 surface contains one combined mesh, 54,412 vertices and 54,410 polygon faces. Its approximate crown is 176.94 cm; source Lara's 180 cm envelope includes hair/clothing. This is not silently rescaled to force agreement.

The environment had no writable installed DDC node. `-DDC-ForceMemoryCache` allowed execution while preserving configuration, but logged a DDC error. A separate fresh-process dependency query returned exit code 1 for that logged DDC condition even though Python completed and reloaded the donor. Application-level solve/extraction evidence is used; no blanket clean-commandlet claim is made. Native UBT's UBA executor also failed; exported UBT compiler/linker/metadata actions were executed with output-path checks confined to Phase4C. The resulting module loaded and executed. Toolchain preference warnings remain in the build log.

## 7. Semantic donor data exposed

**342 joints** are available with semantic names, original parents, source local translations/rotations and posed world translations. Python `get_joints_for_body_conforming_from_dna` reports SUCCESS and 342 positions. The C++ public route uses `LoadDNAFromFile(Source/Transform)`, `IDNAReader` and `UE::MetaHuman::GetJointWorldTranslations`; maximum position difference between routes is **0 cm**. [Extraction evidence](donor_extraction.json), [complete solved joint data](solved_donor_joints.json).

Exposed anatomy includes root, pelvis, five spines, two neck joints, head, clavicle roots, upper-arm shoulder pivots, lower-arm elbow pivots, hand/wrist pivots, thigh/hip, calf/knee, foot/ankle, ball joints, finger chains and eight long-digit metacarpals. Twenty toe joints are named in the complete readback; toes hidden by boots are unvalidated. A separate palm-centre joint was not extracted: `hand` is treated as wrist, not silently relabelled as a palm centre. No inferred hand centre or missing donor landmark was filled from 4B.

The public posed-DNA export is an intermediate combined body/head representation, not a fully assembled character or a facial rig. [Official Save Pose description](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-custom-mesh-tool-in-unreal-engine). No private matrices, private model data or donor skin weights were copied into a Lara rig.

## 8. Donor-to-Lara transform

Row-vector forward mapping:

    canonical_cm = (source_world_cm @ R - origin) * scale
    source_world_cm = (canonical_cm / scale + origin) @ R.T

`R`, origin, grounding and scale are fully stored in [transform_mapping.json](transform_mapping.json). `det(R)=-1` explicitly converts the right-handed DCC source to the left-handed UE canonical basis: +X anatomical left, +Y forward, +Z up. Source-DNA coordinates are left/up/front; the public joint helper yields UE positions by the Y/Z axis exchange. Source local rotations remain recorded in their declared DNA basis.

No extra donor offset, best-fit alignment, recentering or rescaling was applied. Posed export preserves the fitted pose; the world root remains `[0,0,0]`. Ground origin belongs to the target preprocessing and is inverted explicitly. The mesh vertex round-trip error is **{tr['round_trip_max_cm']:.3g} cm**; all 342 donor joints round-trip within **{tr['donor_round_trip_max_cm']:.3g} cm**. Equality between public joint paths and target readback checks accompanies the numerical inverse; an inverse alone would not prove anatomical correctness.

Independent JSON contains both the solved canonical points and mapped original-Lara-world points. Analysis/rendering runs outside UE from these files. Physically removing the donor asset and testing a generated runtime package was not performed, because no accepted final Lara package exists.

## 9. Joint mapping

For comparison, the five donor spines are explicitly contracted to three canonical roles: donor spine_02/04/05 become canonical spine_01/02/03. Neck_02 is omitted from the canonical body comparison. This topology policy was fixed before reading control coordinates; it moves no retained point. Full original hierarchy remains available, and no canonical reference bone orientation is authored after rejection. Native hierarchies are **not** equivalent; the contracted 23-role parent schema is equivalent.

Every mapped role has source name/index/API, original MetaHuman-space position, canonical position, original Lara-space position, parent information, direct/inferred provenance and review flags in [donor_to_lara_mapping.json](donor_to_lara_mapping.json). All 23 body positions come directly from solved joints; hierarchy contraction is explicit post-processing. Scores are prototype evidence scores, not probabilities.

| Canonical role | Donor source | Canonical XYZ cm | Gate status |
| --- | --- | --- | --- |
{body_table}

The four provisional root/spine candidates reuse 4B's score/no-flags policy and have target section support. They do not authorise downstream construction. Internal joints and convention-sensitive pivots require independent target review; MetaHuman names do not provide that review.

## 10. Phase 4B comparison

| Measure | Phase 4B | Phase 4C |
| --- | --- | --- |
| Connected canonical body roles | 23 | 23 |
| Provisional candidates | 6 | 4 |
| Body review set | 17 | 19 |
| Named finger chains accepted | 0 | 0 |
| Maximum mirrored body difference | 0.00 cm, constrained symmetric fit | 1.523 cm, unconstrained donor fit |
| Mean difference from approximate 4A control | 4.161 cm | 5.243 cm |

4B-versus-4C positional difference averages **5.297 cm**, maximum **13.361 cm**. The full three-way comparison includes every role, height percentage, parent-segment axis angle, bilateral measurements and hierarchy limits. [Comparison evidence](phase4b_comparison.json). The frame is identical to 4B's freshly reproduced frame.

The donor eliminates naming uncertainty **inside the donor model**. It does not resolve anatomical correspondence on Lara. The acceptance counts use conservative gate policies rather than independent accuracy labels; their difference cannot alone rank solvers. Ankles/knees agree more closely with the authored control, whereas wrists, neck and clavicle pivot conventions need substantial review. Phase 4B's rejected conclusion is preserved.

## 11. Phase 4A control comparison

Controls were read only after the independent donor proposal was saved and hash-bound. The established control alignment inverts Phase4A uniform scale and UE Y conversion, then applies the inferred body frame. Finger controls are separately transformed using that same documented rule. The proposal hash was verified unchanged after evaluation.

4C versus the approximate control: mean **5.243 cm**, maximum **12.524 cm** (left wrist). 4B versus the same control: mean 4.161 cm, maximum 6.502 cm. Root origins differ by 2.247 cm due to the frame-grounding convention. Clavicle roots are especially convention-sensitive: MetaHuman clavicle roots are near the torso centre, while 4A/4B approximate landmarks lie farther along the shoulder girdle. These differences are not all literal anatomical errors.

| Role | 4C–4A cm | % of 180 cm | Parent axis difference |
| --- | --- | --- | --- |
{compare_table}

[Control comparison](manual_control_comparison.json). Agreement with a manual approximation does not certify anatomy; disagreement identifies review targets rather than automatically prescribing corrections.

## 12. Anatomy validation

The 4B validator was copied into Phase4C with only namespace/import routing adapted. Its existing **61 checks** were executed unchanged in philosophy: connected hierarchy, finite segments, grounded root distinct from pelvis, height, side signs, bilateral consistency, feet-forward, monotonic knees/elbows, target triangle-section envelopes, role resolution and frame/ground evidence. [Unextended 4B-style results](anatomical_validation_v2.json).

Twenty baseline checks fail: 19 unresolved articulation checks and the strict right-clavicle side-sign screen. The right clavicle root is about **+0.069 cm** in X; that convention-sensitive central origin is not evidence that the actual right arm crossed the body. It requires review, and the inherited gate was not silently weakened. The maximum paired mirror difference is 1.523 cm, below the existing 6 cm prototype limit; limb-height ordering and foot-forward screens pass.

All section-bounding-envelope screens pass, including wrists. This demonstrates their limit: an internal point somewhere inside hand/clothing volume can still be the wrong articulation. The 19-role review set prevents that coarse pass from being mistaken for anatomy acceptance. Fingers extend the gate with collapsed-target-track and named-chain-resolution checks; both fail. [Final anatomy gate](anatomical_validation.json): **22 failed checks; downstream_authorised=false**.

## 13. Actual user-review/correction count

Body review set: pelvis, neck, head and both clavicle/shoulder/elbow/wrist/hip/knee/ankle/ball groups: **19 roles**. Fingers add **30 phalange roles across ten chains**; optional metacarpals also remain unaccepted. This is at least **49 required body/phalange reviews**, excluding optional metacarpals and toes, not 49 proven necessary movements.

**Actual corrections applied: 0. Total moved distance: 0 cm. Maximum moved distance: 0 cm. Real correction effort: unmeasured.** No human approval was manufactured and no control coordinate was applied as a correction. The existing SHA-bound 4B correction framework successfully replayed an empty Phase4C patch without changing donor points. Future corrections must retain independent anatomical review and re-run all gates; no correction can automatically bypass them. [Correction measurements](correction_measurements.json), [empty patch](../../Working/Phase4C/corrections.json).

Grouped opportunities are coupled pelvis/hips, axial convention and neck/head, paired shoulder girdles, elbow/wrist pose, lower-limb articulation, and each hand's wrist plus five digit assignments. Categories include articulation review, pivot convention, pose alignment and correspondence. Their grouped edit count and effort have not been measured; **minimal correction is not established**.

## 14. Finger results

Both wrists, all thumb/index/middle/ring/pinky phalange chains and eight long-digit metacarpals are publicly exposed. The source model has stronger semantic identity than 4B's anonymous geometric branches, but its fit does not map those identities reliably to Lara.

An evaluation-only nearest-point check uses all five 4B target section-centre polylines per hand. The four left long-digit distal joints choose **one** target track; the right four choose **two** tracks, with middle/ring/pinky collapsing together. This is a 3D polyline collision screen, not semantic identification or complete surface correspondence. It can reject a collapse; it cannot certify a correct digit. Distances, branch IDs and all finger-control differences are retained in [finger_validation.json](finger_validation.json).

**0/10 chains accepted; all 30 phalange positions need review.** A named donor skeleton is not a solved target hand. The left and right side-view close-ups show the collapse without helper-bone clutter. No fingers were forced into acceptance. Keypoint-guided correction remains a separate, unexecuted refinement experiment.

## 15. UE skeleton/skinning results

Not run: anatomy rejected. No Phase4C Lara Skeleton or Skeletal Mesh, bone orientation, skin weights or geodesic binding was created. The existing Phase4A geodesic feasibility result was not rerun or promoted as Phase4C success. Donor skin data was not used. [Skinning status](skinning_results.json).

## 16. IK/retarget results

Not run: anatomy rejected. No Phase4C IK Rig, Retargeter or Manny mappings. Mode B and prior phases remain untouched. [IK/retarget status](ik_retarget_configuration.json).

## 17. Baked animation results

Not run: anatomy rejected. Idle, walk, run and upper-body motion have no Phase4C bake result. [Bake status](animation_bake_results.json).

## 18. Manny-removed playback

Not run: no Phase4C destination-native character/animation package exists. Source-independent playback is unproven for this donor route. [Playback status](source_independent_playback.json).

## 19. Runtime/dependency implications

| Requirement | Evidence-calibrated result |
| --- | --- |
| MetaHuman Creator/editor plugin | Required for the executed solve; installed MetaHumanCharacter loaded per command. |
| MetaHuman model data | Required locally; installed template/body/skin/RBF resources were used in place, not redistributed. |
| Editor-only processing | Executed via editor subsystem and an Editor helper module. No packaged runtime solve was tested. |
| Internet/cloud/service | No cloud fitting call or external inference service was invoked by the experiment scripts. Computation used installed resources; an offline-disconnection/network-isolation test was not performed. Engine startup did load normal online-service modules. Universal offline operation is not claimed. |
| Authoring dependency closure | Fresh reload proves the temporary donor remains a MetaHumanCharacter authoring asset. Direct package edges include MetaHuman scripts/pipeline and Phase4C target; target references the read-only 4B material. |
| Final Lara runtime closure | Not tested, because the anatomy gate prevented final assets. Independent joint JSON itself contains data, no UE asset references needed to evaluate it. |
| Private implementation redistribution | Not required for this local prototype: it uses installed public boundaries. No permission to redistribute models or editor binaries is inferred. |

[Dependency evidence](dependency_evidence.json) records direct external edges and traverses Phase4C packages only; it is not an exhaustive engine/plugin runtime closure. Likely product architecture is an editor-time donor stage followed by independently authored Lara-native assets and baked animations. That remains an architectural inference, requiring a later successful anatomy gate and explicit closure test.

## 20. Licence/redistribution boundaries

Epic's MetaHuman licence page places MetaHuman under Unreal Engine's standard terms and describes cross-engine creative use. That does not itself grant unrestricted redistribution of model data, editor modules or this derivative joint pipeline. [MetaHuman licensing](https://www.metahuman.com/license).

The Unreal EULA contains Engine Tools distribution constraints, seat/royalty provisions and restrictions concerning MetaHuman data and machine-learning databases/training/testing. Before commercialising an editor tool, shipping helper binaries or derivative joint assets, or considering any later learned pipeline, obtain professional licence review for the concrete distribution model and asset provenance. No legal clearance is asserted here. [Current Unreal EULA](https://www.unrealengine.com/eula/unreal). URLs and verification date are recorded in [web_sources.json](web_sources.json).

## 21. Limitations and visual evidence

One stylised, clothed Lara at one target height and one untracked pose is not arbitrary-humanoid proof. Hair, holsters, clothing, boots and fingers obscure articulation. Zero supplied keypoints/face curves, no real correction trial, a topology convention reduction and approximate controls limit quality conclusions. Body-only input separation, alternative presets, facial accuracy, strict offline operation, final runtime closure and model redistribution are untested. The temporary UE import has different triangulation from the retained source. Public source/export boundaries are installed-version evidence, not a forward compatibility promise.

Fourteen orthographic views were generated from actual fresh source arrays and public donor readback at the same scale/origin. Grey is the retained Lara surface; cyan is the temporary donor; coloured joints are donor points; gold is the rejected 4B proposal. These are numerical debug renders, not UE viewport or animated playback captures.

| Evidence | View |
| --- | --- |
| Original source | [Original Lara](original_Lara_surface.png) |
| Temporary donor surface | [Donor overlay](temporary_donor_overlay.png) |
| Semantic model skeleton | [Donor skeleton](donor_semantic_skeleton.png) |
| Joint mapping | [Front](mapped_donor_front.png), [side](mapped_donor_side.png) |
| Three-dimensional fit comparison projections | [Front comparison](front_comparison.png), [side comparison](side_comparison.png) |
| Pelvis/hip | [Close-up](pelvis_hip_closeup.png) |
| Shoulder/elbow | [Close-up](shoulder_elbow_closeup.png) |
| Knee | [Close-up](knee_closeup.png) |
| Ankle/ball/foot | [Close-up](ankle_ball_foot_closeup.png) |
| Fingers | [Left hand](hand_finger_closeup.png), [right hand](hand_finger_right_closeup.png) |
| 4B versus 4C | [Overlay](Phase4B_vs_Phase4C_overlay.png) |

![Selected temporary donor against original Lara](temporary_donor_overlay.png)

![Left hand donor digits collapse toward one target track](hand_finger_closeup.png)

## 22. Mode A product implication

| Decision category | Conclusion |
| --- | --- |
| Proven for Lara | Real solve; public semantic extraction; 342 named joints; independent deterministic mapping; original source preservation; gates correctly reject downstream work. |
| Likely reusable architecture | Optional installed editor-time MetaHuman donor with public posed-DNA bridge, explicit role conventions and independent Lara joint storage. |
| Unproven generalisation | Accuracy, small correction set and performance across arbitrary human topology/clothing/poses/heights. |
| Finger-specific result | Naming exposed; target correspondence collapsed; automatic fingers rejected. |
| Dependency/licence constraints | Installed editor/model resources required; final dependency-free package and redistribution rights not established. |

**Can the solver act as a temporary semantic donor for unchanged unrigged Lara? Yes, technically, as a proposal source. Does it make Mode A practical assisted or mostly automatic? No evidence of that in this experiment.** The body route remains experimental assisted and has not reduced the verified review burden; fingers remain rejected. Anatomical correctness, not asset creation or public extraction, determines product readiness.

## 23. Recommended next phase

Run a bounded **MetaHuman keypoint/refinement and real correction trial**, with explicit user-reviewed target correspondences for wrists, shoulder pivots, neck and all digit tracks. Treat pivot-convention conversion separately from anatomical movement. Retain this raw zero-keypoint result as baseline, measure real corrections/time/distance and rerun the same gates. A separated body-only source could be a distinct diagnostic, retaining original source topology. This recommendation is unexecuted and does not authorise bypassing failed anatomy.

Only after all required body/finger gates pass should a fresh Lara-native skeleton proceed through the established geodesic skinning, Manny retarget, four-motion bake and Manny-removed playback proof. Do not switch to RigNet/UniRig or another learned architecture inside this phase. Keep Mode B as established.

## 24. Protected-file audit and verification

**{audit['protected_file_count']:,} protected authored files are byte-identical; no missing files or new authored files outside Phase4C were found.** Original ZIP hash matches the baseline. Config and the project descriptor are byte-identical. Prior Documentation, Working assets, Content, Characters and project Reference files are unchanged. [Protected audit](protected_file_audit.json), [baseline](protected_before.json).

A fresh Blender reload independently confirms retained source world vertices, polygon topology, UVs and original material name; extracted FBX/texture bytes still match archive entry hashes. It remains unrigged with zero vertex groups. [Source preservation](source_preservation.json). Engine source was never a write target; no exhaustive pre-run hash of the entire external Engine installation exists, so that is an action-scope assurance, not a blanket external-installation cryptographic proof.

All new authored work is under Documentation/Phase4C, Working/Phase4C and Content/MetaHumanTo3DCharacter/Phase4C. Standard UE/build/cache outputs are excluded from the authored-file audit and explicitly disclosed. No Git repository was present; no stage, commit, push, branch/configuration operation or release was attempted.

The self-review checks solve/extraction artefacts, proposal hash and mapping, numerical transforms, source preservation, inherited validator adaptation, finger collision evidence, fail-closed downstream statuses, visual/evidence links and the final preservation audit. [Self-review](self_review.json) and [execution/evidence manifest](execution_manifest.json) record the results. The Phase4C investigation is complete at the rejected anatomy gate; future refinement is a separate experiment, not unfinished downstream work.
'''
(O/'Phase4CMetaHumanSemanticDonor.md').write_text(text,encoding='utf-8')
print('REPORT',len(text),'characters')
