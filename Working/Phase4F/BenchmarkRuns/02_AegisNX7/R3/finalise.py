"""Aggregate R3 evidence and produce the bounded generalisation report."""
import json, hashlib, datetime, sys
from pathlib import Path
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parent;R=W.parents[4]
O=R/'Documentation/Phase4F/Benchmark/Runs/02_AegisNX7/R3'
load=lambda n:json.loads((O/n).read_text())
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
A=load('Initial/authoring_result.json'); N=load('Final/native_playback.json')
F=load('FemaleFinal/native_playback.json');I=load('import_inspection.json')
C=load('Initial/canonicalisation.json');S=load('Initial/semantic_mapping.json')
T=load('Initial/retarget_setup.json');P=load('preservation_audit.json')
U=load('appearance_audit.json');E=load('runtime_appearance_regression.json')
FR=load('FemaleRegression/read_only_replay.json')
policy=load('Final/playback_execution_identity.json')
assert policy['helper_sha256']==sha(W/'runtime_appearance_closure.py')
assert load('FemaleFinal/playback_execution_identity.json')['helper_sha256']==policy['helper_sha256']
assert N['assets']==A['assets'] and N['saved_assets_loaded']==[A['assets'][k] for k in ['mesh','skeleton']]+[x['path'] for x in A['clips']]
assert N['appearance_ownership_certificate']['status']=='PASS' and F['appearance_ownership_certificate']['status']=='PASS'
stages=[dict(stage='source_and_input_contract',status=I['status'])]+A['stages']+[
 dict(stage='authored_stature_preservation',status='PASS' if I['stature_classification']=='intrinsic_size_already_correct' and C['invariants']['height'] else 'FAIL'),
 dict(stage='appearance_UV_material_preservation',status=U['status']),
 dict(stage='native_four_clip_playback_and_fresh_reload',status=N['status']),
 dict(stage='typed_destination_runtime_closure',status=N['appearance_ownership_certificate']['status']),
 dict(stage='generic_ownership_regression_controls',status=E['status']),
 dict(stage='Female_input_unit_semantics_replay',status=FR['status']),
 dict(stage='Female_fresh_native_regression',status=F['status']),
 dict(stage='preservation',status=P['status'])]
assert all(x['status']=='PASS' for x in stages)
assert {x['role'] for x in N['phases']}=={'neutral','idle','walk','run'} and all(x['status']=='PASS' for x in N['phases'])
assert {x['role'] for x in F['phases']}=={'neutral','idle','walk','run'} and all(x['status']=='PASS' for x in F['phases'])
base=load('baseline.json')
completed=datetime.datetime.now(datetime.timezone.utc)
elapsed=(completed-datetime.datetime.fromisoformat(base['started_utc'])).total_seconds()
comparison=dict(Female_Body_Rigged=dict(height_cm=FR['input']['height_cm'],bones=FR['input']['bone_count'],vertices=FR['input']['vertex_count'],triangles=FR['input']['triangle_count'],unit_factor=FR['unit_classifier']['factor'],bindings=FR['destination_semantics']['semantic_binding_count'],native_regression=F['status']),
 Aegis_NX7=dict(height_cm=A['destination']['height_cm'],bones=I['native']['bone_count'],vertices=I['native']['vertex_count'],triangles=I['native']['triangle_count'],unit_factor=load('Initial/unit_classification.json')['detected_factor'],bindings=S['semantic_binding_count'],native=N['status']))
scale=dict(reported_18_classification=I['reported_18_classification'],evidence=I['reported_18_evidence'],stature_classification=I['stature_classification'],additional_stature_normalisation=False,source_units=I['source_units'],import_settings=I['import_settings'],original_root_reference=I['root_reference'],original_scene=I['scene'],final_intrinsic_height_cm=A['destination']['height_cm'],final_root_reference_scale=A['destination']['bones'][A['destination']['root']]['local']['scale'],final_actor_scale=[1,1,1],final_component_scale=[1,1,1],effective_final_reference_height_cm=A['destination']['height_cm'])
observations=dict(status='DIAGNOSTIC_ONLY',native_captures_reviewed=True,
 visual='Reference, idle, walk and run captures preserve white/dark/cyan robotic appearance, distinct locomotion poses and plausible limb orientation. No gross inversion/explosion or obvious tearing seen in these frontal samples.',
 limitations='Frontal still samples and native transform/bounds telemetry do not certify all-time rigid armour behaviour, hidden intersections, finger independence, natural thumb opposition or detailed contact quality.',
 contact='Sampled posed mesh minima include about 1.03 cm penetration in idle, 0.72 cm in walk and about 1.02 cm clearance in run. These are single snapshot mesh-bound diagnostics, not stance-certified sole metrics or contact acceptance.',
 repairs_performed=False,full_deformation_quality_accepted=False,finger_thumb_quality='NOT_RUN',source_contact_caveats_preserved=True)
result=dict(version='phase4f.rigged-character-r3/1.0.0',classification='GENERALISATION_PASS_WITH_GENERIC_FIX',status='PASS',
 first_unchanged_R2_run=dict(authoring='PASS',dependency_gate='FAIL',native_playback='NOT_RUN',evidence='Initial/native_playback.json',diagnosis='initial_failure_diagnosis.json'),
 generic_fix=dict(version=policy['policy_version'],helper_sha256=policy['helper_sha256'],accepted_R2_files_modified=False,scope='Runtime ownership only: explicitly bound typed appearance dependency closure; no transform, semantic, retarget or bake edits'),
 stage_matrix=stages,assets=A['assets'],clips=A['clips'],scale=scale,comparison=comparison,observations=observations,
 regression=dict(synthetic=E['passed'],synthetic_total=E['total'],Female_read_only_checks=len(FR['checks']),Female_read_only_status=FR['status'],Female_native_status=F['status']),
 preservation=dict(status=P['status'],protected_count=P['protected_count'],changed=P['changed'],missing=P['missing'],git_preserved=P['git_preserved']),
 manual_character_intervention=dict(bone_renames=0,reparenting=0,semantic_assignments=0,retarget_tuning=0,scale_multipliers=0,skin_repairs=0,material_edits=0),
 elapsed_wall_seconds=elapsed,active_time='NOT_MEASURED',completed_utc=completed.isoformat(),other_subjects_started=False,full_quality_accepted=False,cook_package_tested=False,stopped_at_R3_boundary=True)
(O/'result.json').write_text(json.dumps(result,indent=2)+'\n')
(O/'scale_transformation_ledger.json').write_text(json.dumps(scale,indent=2)+'\n')
(O/'generalisation_comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
(O/'appearance_deformation_observations.json').write_text(json.dumps(observations,indent=2)+'\n')
(O/'runtime_dependency_closure.json').write_text(json.dumps(dict(closure=N['runtime_dependency_closure'],certificate=N['appearance_ownership_certificate']),indent=2)+'\n')
def link(f): return f'[{f}]({f})'
def table(rows): return '\n'.join('| '+' | '.join(str(x) for x in row)+' |' for row in rows)
B=A['output_namespace']
motions=table([['Motion','Duration s','Rate','Keys','Native advance s'],['---','---:','---:','---:','---:']]+[[x['role'],f"{x['duration_s']:.6f}",'/'.join(map(str,x['frame_rate'])),x['keys'],f"{next(p for p in N['phases'] if p['role']==x['role'])['animation_time_advanced_s']:.6f}"] for x in A['clips']])
native=table([['Motion','Pelvis Z cm','Max limb error cm','Native skinned snapshot Z cm'],['---','---:','---:','---:']]+[[p['role'],' to '.join(f'{x:.3f}' for x in p['pelvis_z_range_cm']),f"{p['maximum_limb_error_cm']:.8f}",f"{p['geometry']['bounds_cm'][0][2]:.3f} to {p['geometry']['bounds_cm'][1][2]:.3f}"] for p in N['phases']])
assets='\n'.join('    '+p for p in A['assets'].values())+'\n'+'\n'.join('    '+x['path'] for x in A['clips'])+'\n    '+N['playback_map']
semantic='\n'.join(f"- {x['semantic']}: "+(' → '.join(x['bones']) if 'bones' in x else x['bone']) for x in S['bindings'])
matrix=table([['Stage','Result'],['---','---']]+[[x['stage'],x['status']] for x in stages])
report=f'''🟢 **High confidence**

# Module R3 — Aegis NX-7 second rigged-character generalisation

## 1. Executive result

**GENERALISATION_PASS_WITH_GENERIC_FIX.** Aegis passed input validation, unchanged R1 unit handling, automatic R2 semantic/IK/retarget authoring, four destination-native animations and advancing source-free native playback. No subject-specific rig, retarget, stature, weight or material repair was used.

The authoritative first unchanged R2 run passed all authoring stages, then failed before PIE at its folder-based runtime ownership screen: Aegis's correctly retained original material and texture were outside the derived folder. This failure is preserved in {link('Initial/native_playback.json')} and {link('Initial/first_failure_context.json')}. The diagnosis preceded the successor implementation: {link('initial_failure_diagnosis.json')}.

Generic correction: **{policy['policy_version']}**. Runtime seeds plus appearance assets reached from actual mesh material slots are certified by package graph and native asset types, including Engine/plugin parents. Unknown, unbound and foreign character/animation/rig dependencies fail. UE script/transient graph containers remain traversed. Accepted R1/R2 files are unchanged. The successor changes one ownership assignment in memory; native motion/scale tests remain identical. Exact statement/hash evidence: {link('Final/playback_execution_identity.json')}.

R3 evidence version: {result['version']}. Installed UE 5.8.3. This accepts the focused engineering route, not full deformation/contact/finger quality or packaging.

{matrix}

## 2. Aegis source/input

Archive: `Characters/Aegis+NX-7.zip`, 6,172,882 bytes. SHA-256 `eb4967bb254d96009e34192609e4d32082ec932143db15f2b5c8578572d0f5fd`. Safe extraction retained one FBX and one supplied 4096×4096 JPEG, without rewriting them. FBX 7400 contains one geometry, one skin deformer, 61 clusters/bones, one material, one base-colour texture, one bind pose and no animation objects. Source control points: 26,120; all weighted; maximum influence count 5. Native triangulation/splits produce 26,230 vertices and 51,785 triangles.

Exact inventory and all source hashes: {link('archive_inventory.json')}, {link('source_fbx.json')}. Normal import settings and native material/texture evidence: {link('import_inspection.json')}. The logging-only first inspection API failure is retained separately; it did not alter the source or implement a character repair.

## 3. v1 contract validation

**PASS.** One already-rigged/skinned humanoid Skeletal Mesh and one coherent connected 61-bone hierarchy rooted at `root`. Skeleton exists; parents resolve; reference transforms are finite/nonsingular. Zero invalid/unweighted native vertices; maximum weight-sum error {I['native']['max_weight_sum_error']:.12g}. Integrated robot/armour geometry is part of this same weighted mesh. No assembly, new skinning or scope expansion was required. Evidence: {link('Initial/input_validation.json')}.

## 4. Scale and stature representation

{table([['Layer','Original','Final'],['---','---','---'],['Source intrinsic / imported physical height','179.912110 cm','179.912110 cm'],['FBX UnitScaleFactor / OriginalUnitScaleFactor','100 / 100','Source unchanged; native unit representation handled'],['Root reference scale','100 / 100 / 100','1 / 1 / 1'],['Import uniform scale','1','1; no reimport correction'],['Actor scale','1 / 1 / 1','1 / 1 / 1'],['Component relative/world scale','1 / 1 / 1','1 / 1 / 1'],['Effective reference world height','179.912110 cm','179.912110 cm']])}

Reported possible 1.8 factor: **baked_into_geometry_or_reference**, in the limited sense that the source already has approximately 1.799121 m intrinsic stature. No standalone 1.8 Model, import, actor or component multiplier exists. The archive supplies no external actor/component scene. A historical multiplication by exactly 1.8 cannot be established without its unscaled predecessor; current physical size is directly measured. Decision: **intrinsic_size_already_correct**; no extra stature conversion.

FBX axes: Up Y positive, Front Z positive, Coord X positive. Normal import uses scene conversion, no extra uniform scale, zero import rotation/translation and no scene-unit conversion toggle. Full numeric root translation/quaternion, child reference transforms, source Model scales and scene stack are preserved in {link('import_inspection.json')} and {link('scale_transformation_ledger.json')}. The uniform root 100 is a separate FBX/UE unit representation, not an intentional 1.8 stature layer. No doubling or loss of stature occurred.

## 5. Unit/root canonicalisation

**canonicalisation_required**, detected uniform factor {load('Initial/unit_classification.json')['detected_factor']:.12g}. Existing `phase4f.rigged-unit-canonicalisation/1.0.0` applied unchanged to a private derived mesh/Skeleton. Root reference scale becomes 1; all non-root local translations receive the detected factor; root translation, rotations, names/parents, geometry and skin weights remain preserved. Physical bind size is invariant; maximum component bind-position error {C['bind_position_max_error_cm']:.12g} cm, below the existing 0.001 cm allowance. Geometry/skin hash remains `{A['destination']['geometry_skin_sha256']}`. All six existing invariants passed: {link('Initial/canonicalisation.json')}.

## 6. Semantic mapping

**23 automatic bindings: 22 chains plus pelvis**, including all ten fingers. UE automatic humanoid template resolution plus ancestry validation; no manual names/mappings. No unresolved requirement. Confidence is the exposed template match and structural validation; alternatives are not exposed by UE. Same binding structure as Female. Exact discovered names:

{semantic}

Evidence: {link('Initial/semantic_mapping.json')}.

## 7. Destination IK Rig

**PASS.** Preview destination mesh; pelvis retarget/FBIK root; root motion bone `root`; all 22 required chains. Four generated hand/foot goals. The unchanged R2 route aligns leg goals/endpoints with the discovered Foot-chain start (ball convention), validates chain ancestry/goal bones/transforms and saves the rig. FBIK remains automatic, with stretch disabled. No manual edit. Native saved configuration: {link('Initial/ik_rig.json')}.

## 8. Manny → Aegis Retargeter

**PASS.** Same isolated Manny source-rig copy route; missing LeftFoot/RightFoot chains derived automatically from Manny semantics. Original Epic assets unchanged. All 22 stored mappings are exact semantic matches, plus pelvis binding; finite automatic target alignment; native FIKRetargetProcessor initialisation passed. Default pelvis/FK/IK operations retained; in-place root-motion operation disabled exactly as R2. No per-character offsets, multipliers or tuned pose. Evidence: {link('Initial/manny_source.json')}, {link('Initial/retarget_setup.json')}.

## 9. Destination animation bake

**PASS.** Same fixed R2 source set; newly baked destination Skeleton ownership, preserved durations, finite native key validation and unit root keys. Native root-lock behaviour is retained. The dependency correction reused these first-run saved assets; no re-bake was needed.

{motions}

All exact final asset object paths:

{assets}

Evidence: {link('Initial/animation_bake.json')}, {link('result.json')}.

## 10. Native playback

**PASS** for reference, idle, walk and run, in a fresh main-project PIE world. Actual time advancement: one reference/idle cycle and two walk/run cycles. All 61 bone transforms finite; root, component and actor scales remain 1; unchanged limb-length tolerances pass. Distinct moving hands/feet are recorded. Neutral posed height matches 179.912 cm; no 100× elevation, 0.01× collapse or extra 1.8 multiplication.

{native}

Final authoritative native evidence: {link('Final/native_playback.json')}. Eight native captures: [Final/NativePlayback](Final/NativePlayback/). Frontal reference/idle/walk/run frames were inspected; captures and transform telemetry jointly establish advancing animation, not still frames alone.

## 11. Appearance/deformation observations

One unchanged material slot `tripo_mat_1c5da8ca`, with its original imported MaterialInstanceConstant and supplied sRGB 4096×4096 texture. Normal UE import parent is `/InterchangeAssets/Materials/FBXLegacyPhongSurfaceMaterial`; this standard material dependency remains required. One UV set; exact source/destination triangle-UV hash `{U['source']['triangle_uv_sha256'][0]}`. No artistic material or texture edit. White/dark/cyan robot appearance is visible in native captures.

No gross inversion/explosion or obvious tearing was seen in sampled frontal frames. This does not certify rigid armour behaviour, all-time intersections or hidden-side deformation. Idle/walk snapshots include roughly 1.03/0.72 cm mesh-bound penetration; run snapshot roughly 1.02 cm clearance. These are snapshot bounds, not certified stance/sole-contact metrics. No floor movement or contact repair. Independent finger motion/thumb naturalness and full quality suite were **NOT_RUN** under the fixed four-clip scope. Evidence: {link('appearance_audit.json')}, {link('appearance_deformation_observations.json')}.

## 12. Fresh reload

**PASS.** Authoring host closed; independent main project loaded saved destination mesh/Skeleton and all four native sequences from disk, with no authoring bridge loaded. Reference-root/height/Skeleton ownership verified before PIE. Final proof map was loaded from disk. Additional final native run used the exact final helper hash. All motion/reload checks passed.

## 13. Runtime independence

**PASS.** Recursive hard/soft/searchable/management package graph: {len(N['runtime_dependency_closure']['packages'])} packages, zero foreign or authoring packages. One destination character, AnimSingleNodeInstance, zero source actors/live retarget nodes. No Manny/Female/John/Jane/donor mesh, source animation, IK Rig, retargeter, Copy Pose, live retarget or bridge is required for playback. Normal Engine, Interchange material-parent and original bound appearance packages are required; these are explicitly enumerated, not hidden by a broad folder allowance. Exact closure and typed certificate: {link('runtime_dependency_closure.json')}.

## 14. Generalisation comparison

{table([['Property','Female_Body_Rigged','Aegis NX-7'],['---','---','---'],['Surface','Body-only','Integrated textured robotic/armoured humanoid'],['Native bones','61','61'],['Native vertices / triangles','27,699 / 52,540','26,230 / 51,785'],['Physical reference height','99.951173 cm','179.912110 cm'],['Detected root factor','100','100'],['Extra stature conversion','None','None'],['Automatic bindings / fingers','23 / 10','23 / 10'],['Native fixed four clips','PASS','PASS'],['Final corrected ownership policy','PASS','PASS']])}

Female regression is isolated R3 evidence/map only: unchanged R2 input inspection, R1 classifier and R2 semantics replay **10/10**; fresh native saved-mesh/four-bake playback **4/4**. No accepted Female assets/evidence regenerated or overwritten. Synthetic ownership regression **{E['passed']}/{E['total']}** covers valid bound appearance, unbound/same-folder content, unknown/missing/mixed classes, hidden foreign mesh/Skeleton/animation/rig/Blueprint, plugin-parent and transient-container edges. Evidence: {link('FemaleRegression/read_only_replay.json')}, {link('FemaleFinal/native_playback.json')}, {link('runtime_appearance_regression.json')}, {link('generalisation_comparison.json')}.

## 15. Product implications

R2 authoring generalised unchanged; its original folder-based closure gate did not. Aegis exposed a generic textured-input ownership defect, corrected by explicitly bound typed appearance ownership. Existing R1 already handles the measured root-unit representation. No new external-stature case was present or implemented. Robot/armour surface geometry did not prevent the one-mesh rigged/skinned humanoid path; supplied integrated appearance survived. This evidence gives no reason to alter v1 scope, and does not establish arbitrary rig-family support or finished skin/contact quality.

Manual character interventions: zero bone renames/reparents, manual mappings, tuned retarget offsets, stature multipliers, weight or material edits. Generic runtime policy work and instrumentation are engineering effort, not hidden subject repair. Elapsed wall time through result aggregation: {elapsed/60:.1f} minutes; active time not measured. No UI, another subject, broad animation library or cook/package work.

## 16. Preservation

**PASS: {P['protected_count']:,} protected files; zero changed, zero missing.** Aegis ZIP/extracted FBX/JPEG/original imported character assets; accepted R1/R2 code/assets/evidence; Female/Manny; John/Jane; frozen protocols preserved. All current 29 John and 29 Jane confirmations verified, immutable events John 218/Jane 205 valid. Git HEAD/index/previous tracked status unchanged; existing Jane changes remain untouched. No staging/commit/push/config change. New work is confined to R3/Aegis authoring/evidence namespaces, with ordinary generated editor runtime/cache files excluded by existing project rules.

Audit: {link('preservation_audit.json')}. Content/evidence/source hashes: {link('manifest.json')}. Original authoritative first failure and logging/inspection attempts are retained. Mandatory self-review checked input/scale provenance, exact AST change scope, final helper hash identity, four-clip source-free playback, Female regression and preservation. **Stopped at R3 classification.**
'''
(O/'README.md').write_text(report,encoding='utf-8')
manifest={}
for folder in [O,R/'Content/MetaHumanTo3DCharacter/Phase4F/BenchmarkRuns/02_AegisNX7']:
    for p in folder.rglob('*'):
        if p.is_file() and p.name not in ['manifest.json','manifest.sha256']:
            manifest[p.relative_to(R).as_posix()]=sha(p)
for p in W.glob('*'):
    if p.is_file() and p.suffix in ['.py','.json']:
        manifest[p.relative_to(R).as_posix()]=sha(p)
(O/'manifest.json').write_text(json.dumps(dict(version=result['version'],hashes=manifest,scope='R3 authored source/config/evidence and Aegis/import/derived/regression assets; logs/cache/host binary copies excluded'),indent=2)+'\n')
(O/'manifest.sha256').write_text(sha(O/'manifest.json')+'  manifest.json\n')
print('R3_RESULT',result['classification'],'stages',len(stages),'elapsed_minutes',round(elapsed/60,2),'manifest_files',len(manifest))
