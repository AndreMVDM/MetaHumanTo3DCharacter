"""Append continuation findings, preserving the Bill/Jill historical bytes."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4F';O=P/'Documentation/Phase4F';A=O/'APoseContinuation'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
def append_history(name,text):
    original=(A/'Before'/name).read_bytes();current=(O/name).read_bytes()
    assert current.startswith(original),'Historical prefix changed'
    (O/name).write_bytes(original+b'\r\n\r\n'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
compare=read(A/'pose_control_comparison.json')['comparison'];new=['John','Jane']
original=read(A/'Before/product_generalisation_matrix.json')
values={}
for ch in new:
    g=read(O/ch/'geometry_summary.json');r=compare[ch]
    values[ch]={
        'Input topology type':f"1 mesh / {g['vertices']:,} source vertices",
        'Clothing classification':g['clothing_classification'],
        'Body roles requiring human review':'19 initially; 0 performed',
        'Actual moved landmarks':'0 performed; required unknown',
        'Actual human reviews':'0',
        'Accepted without movement':'0',
        'Finger mapping interactions':'0; ten identities pending',
        'Manual phalange placements':'0 performed',
        'Measured review session time':'not started',
        'Anatomy gate':f"{r['anatomy_checks_passed']}/106; blocked",
        'Skeleton built':'no; anatomy blocked',
        'Shoulder accepted':'not tested',
        'Pelvis/pants accepted':'not tested',
        'Fingers accepted':'identity/review pending',
        'Thumb accepted':'not tested',
        'Foot/contact accepted':'not tested',
        'Conventional manual painting required':'unknown; none used',
        'Source-free playback':'not built/tested',
        'Clean-project playback':'not performed',
        'Overall result':'awaiting real anatomy review; generalisation pending'}
rows=[['Source pose','A (benchmark)','A','A','T','T']]
for metric,lara,bill,jill in original['rows']:
    rows.append([metric,lara,values['John'][metric],values['Jane'][metric],bill,jill])
rows.insert(-1,['Clean/cooked playback','not performed','not performed','not performed','not performed','not performed'])
matrix={'status':'interim_apose_human_review_boundary','columns':['Metric','Lara','John','Jane','Bill T-control','Jill T-control'],'rows':rows,'original_control_cells_preserved':True}
save(O/'product_generalisation_matrix.json',matrix)
table='\n'.join(['| '+' | '.join(matrix['columns'])+' |','| '+' | '.join(['---']*6)+' |']+['| '+' | '.join(row)+' |' for row in rows])
controltable='| Metric | Bill T-pose | John A-pose | Jill T-pose | Jane A-pose |\n| --- | ---: | ---: | ---: | ---: |'
for label,key in [('Anatomy checks passed','anatomy_checks_passed'),('Body roles requiring review','body_roles_requiring_review'),('Shoulder envelope failures','shoulder_envelope_failures'),('Elbow envelope failures','elbow_envelope_failures'),('Wrist envelope failures','wrist_envelope_failures'),('Bilateral mismatch max cm','bilateral_mismatch_max_cm'),('Finger tracks detected','finger_tracks_detected')]:
    cells=[]
    for ch in ['Bill','John','Jill','Jane']:
        value=compare[ch][key]
        cells.append('5 + 5' if isinstance(value,dict) else f'{value:.4f}' if isinstance(value,float) else str(value))
    controltable+='\n| '+label+' | '+' | '.join(cells)+' |'
append_history('Phase4FQualityGeneralisationGate.md',f'''## 24. A-pose replacement subjects — John/Jane

**CURRENT continuation checkpoint: genuine human-review boundary.** Sections 1–23 above are preserved Bill/Jill interim history. Their recommendations to review Bill/Jill as primary subjects are superseded by this section. Bill/Jill remain retained T-pose diagnostic controls; every input, proposal, gate, scene, log and ledger remains unchanged. The primary Phase4F evaluation is now Lara benchmark + John/Jane. The phase and frozen budget were not reset.

### 24.1 Supported input and fresh preservation boundary

Mode A v1 supports a **clean unrigged humanoid in a neutral A-pose**, with a reasonable range of lowered arm angles. T-to-A or arbitrary-pose normalisation is deferred. No source pose was converted. Generation intent is not used as evidence. The replacement test explicitly examines whether better source/donor pose alignment improves correspondence; it does not certify all A-pose humanoids.

[Continuation policy](APoseContinuation/evaluation_policy.json) extends the frozen starting policy without editing the original. Each new character has a separate three-pass semantic budget, four skin variants per region including baseline, 180 cm physical height, the same anatomy gate, full stress suite and bounded contact policy. [Budget](APoseContinuation/budget_consumption.json): John 1/3, Jane 1/3; skin candidates zero; two semantic passes remain each. Bill/Jill consumption remains in the original budget file. Further solves are not required merely to spend the budget.

[Extended protection baseline](apose_protected_before.json) captures 3,614 authored files before new-character processing, including all current Phase4F history, all source archives and Phase4D human events. Byte-exact historical report/status/policy/matrix snapshots are in APoseContinuation/Before. [Continuation audit](APoseContinuation/protected_file_audit.json) is the authority for final preservation status. No commit, push, Engine-source edit or reference-project edit is authorised or performed.

### 24.2 Fresh source inventory and observed pose

John ZIP SHA256: f52193505c74f5200fa252db260769bad999d7f990b34e09260fd67360f2a27d. Jane: 791989d75aa9024ecc6c686623645cf82229f79d8bdcc932e27aaae6e91ae839. [John archive/FBX](John/input_inventory.json), [Jane archive/FBX](Jane/input_inventory.json) enumerate every entry, CRC, byte count and entry hash.

| Source | Vertices | Polygons | DCC triangles | UE triangles | Raw / seam components |
| --- | ---: | ---: | ---: | ---: | ---: |
| John | 26,166 | 27,876 | 50,943 | 50,925 | 37 / 37 |
| Jane | 28,328 | 30,279 | 55,109 | 55,103 | 26 / 26 |

Both contain one FBX Mesh Model, Material, Texture and Video, no Deformer/skin cluster/skeleton nodes; Blender readback finds no armature, vertex group or modifier. Both have one UV layer and one 4096×4096 basecolour JPEG, resolved to the freshly extracted archive texture. Original polygon/UV arrays remain unedited. [John geometry](John/geometry_summary.json), [Jane geometry](Jane/geometry_summary.json) include UV hashes, finite checks, matrices and component bounds. UE retains indexwise vertex correspondence within 0.001 cm; triangulation/degenerate removal changes the triangle counts above, explicitly recorded in each source_ue_comparison.json. Near-zero tangent/binormal import warnings remain in logs.

FBX declares +Y up/+Z front/+X coordinate axis, unit factor 100. Blender imports +Z up, and directly inspected face/belt/front-clothing images establish -Y facing. The toe-only heuristic disagreed and was not accepted. Canonical +X anatomical left/+Y forward/+Z up has determinant -1 and round-trip error below 1.5e-14 cm. Uniform height normalisation preserves individual proportions and does not imply intended real-world stature.

Pre-donor [John pose measurements](John/source_pose_validation.json) and [Jane measurements](Jane/source_pose_validation.json) use actual section centrelines and source front/side views. They measure clothed surface proxies, not internal medical joint centres:

| Pose proxy | John left / right | Jane left / right |
| --- | --- | --- |
| Arm chord below horizontal | 68.997° / 69.257° | 55.169° / 51.782° |
| Elbow surface-axis change | 18.332° / 18.202° | 20.411° / 6.693° |
| Wrist narrowing XYZ cm | [42.056,-3.686,90] / [-42.056,-3.686,90] | [45.653,-9.685,96] / [-42.915,6.406,97] |
| Mirrored arm curve mean / max cm | 0.661 / 10.708 | 16.225 / 20.237 |
| Foot-centre lateral separation cm | 41.593 | 64.104 |

Both are observed neutral A-pose variants, with separated legs and mildly bent rather than perfectly straight arms. John has relaxed partly curled digits; Jane has more splayed digits and substantial fore/aft asymmetry, including ~16.09 cm between wrist Y proxies. These limitations were reported before fitting. Jane's asymmetry is actual source geometry, not automatically attributed to solver error. Thumbs are medial and palms appear approximately inward/forward from front/side; exact palm normals/wrist articulation remain human-review tasks. No strict single-angle tolerance was invented. [John source front](John/source_front.png), [side](John/source_side.png), [back](John/source_back.png); [Jane front](Jane/source_front.png), [side](Jane/source_side.png), [back](Jane/source_back.png).

### 24.3 Clothing classification

John has separable principal trouser, shirt and belt shells, alongside mixed skin/accessory pieces: trouser component 25 has 3,420 vertices, shirt-region component 34 has 2,963 and belt component 24 has 1,146. Jane is **mixed**, with an integrated central top/pelvis/upper-leg component 20 (9,161 vertices) and distinct sleeve/hand/boot pieces. Her principal top and trousers cannot be independently isolated as complete connected shells. The requested integrated-envelope comparison applies to that central surface; describing all Jane geometry as merged would be inaccurate.

[John connectivity evidence](John/clothing_classification.json), [Jane evidence](Jane/clothing_classification.json) and connectivity_front.png record actual canonical extents. Seam welding at 0.00001 cm is analysis-only. Component IDs are diagnostic inventory labels, never final hardcoded vertex masks. A complete correctly weighted underlying body donor is not established on either mesh; no transfer result is claimed. Shell-aware John and integrated-central Jane refinements remain authorised only after anatomy passes.

### 24.4 Character-local donor solve and control comparison

Each mesh received its own temporary authoring MetaHuman and combined custom-mesh solve, with no Lara/Bill/Jill coordinate initialisation. John solved in 47.235 s; Jane in 43.937 s. Each exposes 342 joints; native posed-DNA extraction and the public body-conforming Python API agree at **0.0 cm maximum**. Canonical 23-role proposals and ten unnamed source tracks were produced independently. [Solve provenance](APoseContinuation/automatic_proposal_execution.json), [John proposal](John/automatic_starting_proposal.json), [Jane proposal](Jane/automatic_starting_proposal.json).

{controltable}

[Machine comparison and per-role measurements](APoseContinuation/pose_control_comparison.json). John donor wrists are 1.660/1.764 cm from pre-solve wrist narrowing proxies; Jane 2.469/3.632 cm. Elbow-to-section proxies are 3.705/3.610 cm John and 1.482/1.112 cm Jane. These are landmark-to-surface-proxy distances, not anatomical correction prescriptions. All six shoulder/elbow/wrist envelope screens pass on both A-pose inputs, versus three failures on Bill and six on Jill. This is a **material numerical arm-correspondence improvement** on these replacements. The overall gates improve only 1 and 3 checks because retained human-review requirements dominate.

Pose-only causation is not established: meshes, proportions, topology, clothing and symmetry also differ. A better section envelope is not anatomical truth, skin quality, fewer actual moves or novice usability. John bilateral maximum drops to 1.595 cm; Jane remains 17.777 cm and fails the <6 cm screen, consistent with substantial source fore/aft asymmetry but not proved harmless. A focused [Jane frame diagnostic](Jane/frame_asymmetry_diagnostic.json) tested whether one global yaw explains this: lower-leg reflection optimum is -2° (mean nearest 1.206 cm), whereas distal arm/hand optimum is -12° (1.805 cm). The differing regional optima do not support silently applying one global yaw as a fix; no limb rotation, pose normalisation or extra semantic solve was performed. [John diagnostic](John/frame_asymmetry_diagnostic.json) finds 0° in both regions. These reflection screens are diagnostics, not anatomy ground truth.

### 24.5 Full anatomy gate and exact stop reason

**John 66/106, 40 failures. Jane 65/106, 41 failures. downstream_authorised=false for both.** Every inherited numeric threshold and exact position-bound human-review provenance check remains in force. No points were moved, identities assigned or approvals fabricated.

Each has 19 unresolved articulation roles and ten unresolved digit chains. Four root/spine policy roles are provisional. Numerical body flags for John: spine_03 and both clavicle section envelopes. Jane: parent-relative left clavicle side, bilateral consistency, spine_03 envelope and paired sole evidence (26 supporting vertices versus retained >=40). Both aggregate finger track/collision gates fail because no real identities/chains exist yet. [John full gate](John/anatomical_validation.json), [Jane gate](Jane/anatomical_validation.json).

The sole-support count is a source/frame sampling screen, not a landmark approval that the reviewer can clear. Bilateral and clavicle convention flags also require diagnosis against source evidence after review; do not force a sound point into a numeric target. Thin/overlapping garment section envelopes may flag internal pivots even when a proposal looks plausible. No gate was silently weakened. Real review can return unresolved categories where numeric screens and sound anatomy disagree.

Each saved native review map contains 22 body controls and the character-local source at unit scale/180 cm. [Fresh-process readback](APoseContinuation/native_review_fresh_readback.json) verifies maps, zero control position error, local materials/textures and no human events. CPU source-data front/side and per-hand projections are in John/Jane subfolders. [John native editor capture](John/native_review_front.png), [Jane native capture](Jane/native_review_front.png) and [capture manifest](APoseContinuation/native_visual_evidence.json) independently verify the interactive static review. John is left open on the user's desktop, with no real trial started. The first sandbox-launched editor was inaccessible to the native desktop tool and was replaced by the scoped interactive launch; the launcher now explicitly names the John map. Use [current exact review instructions](HumanReviewInstructions.md#johnjane-current-primary-review); historical Bill/Jill sections remain intact. No external Tk panel is recreated.

### 24.6 Correction effort and downstream boundary

[John effort](John/correction_metrics.json), [Jane effort](Jane/correction_metrics.json): 19 initial unresolved body roles each; zero actual reviewed roles, moved landmarks, move distances, accepted-without-movement, digit interactions and manual phalange placements; review duration null because neither real trial has started. Zero performed never means zero required. Actual final anatomy result remains blocked. Reduced correction burden versus Lara or the controls cannot be measured yet.

Tasks 7–16 are unperformed because neither full anatomy gate passes: no new Skeleton/SkeletalMesh/weights/IK/retarget/native animation; no conventional painting; no shoulder/pelvis/finger/thumb/contact acceptance; no runtime closure, clean-host migration or cooked proof. Authoring review map reload is not runtime playback. No Bill/Jill runtime asset or Lara Skeleton is reused.

After a complete gate pass, retain GEODESIC_VOXEL 128 / stiffness 0.2 / max five influences. Parameter formulas must be documented from height, pelvis-to-thigh span, shoulder width and limb length before refinement candidates; Lara centimetre thresholds are not copied. Apply the same frozen neutral, arms45, horizontal, overhead, elbow-bend, wide-stance, strong-knee-bend, idle/walk/run, reach/JumpingJacks, independent-finger and thumb-opposition suite on Lara/John/Jane with equivalent relative regions. Track mean AND worst-frame shoulder/crotch/clothing compression. Contact retains max five iterations, 0.033333×height lift limit, 60 Hz bake/120 Hz dense checks, no actor/root/pelvis offsets. Final seeds require source-free closure/native motion plus clean-host and cooked validation where practical. None is inferred from compiled authoring assets.

### 24.7 Updated generalisation matrix

{table}

The matrix retains the original Lara/Bill/Jill cells and clearly marks the controls. Lara values are inherited accepted benchmark evidence with the same Phase4E quality limitations, not a new stress-suite run.

### 24.8 Product decision and required answers

**Definitive GO/HOLD/NO-GO remains incomplete at the authorised real human-review boundary. Phase5 is withheld pending evidence.** This administrative pending state is not the technical HOLD verdict, which requires demonstrated generalisation with one bounded quality issue. Neither GO nor NO-GO is forced from unperformed downstream tests.

| Product question | Evidence-calibrated answer now |
| --- | --- |
| Is clean A-pose effective and reasonable for Mode A v1? | Effective for the measured arm-envelope correspondence on these two examples; reasonable as the chosen v1 constraint. Full acceptance and beginner effort remain unproved. |
| Does Assisted Rigging generalise beyond Lara with pose controlled? | Character-local solve/proposal extraction generalises; full accepted anatomy and animated quality are pending. |
| Is John/Jane semantic correspondence materially better than Bill/Jill? | All six primary arm envelopes pass on both, against 3/6 and 0/6 on controls. Pose-only causation is not established. |
| Can both be rigged/skinned/refined/animated without full manual painting? | Unknown until full anatomy passes and the authorised downstream tests run. No painting has been used. |
| Does deformation quality generalise across clothing/proportions? | Unknown; no new weighted surface exists. |
| Is correction burden suitable for beginners? | Unknown; new measured trials have not started. Real role/digit review remains required. |
| Should Phase5 native plugin development begin? | No authorisation at this boundary. Complete the true review and quality/runtime gates first. |

Level1 self-review checks provenance exclusion, approval invalidation, duplicate tracks, zero real events, budget, syntax and historical prefixes. [Self-review](APoseContinuation/self_review.json). Donor and first review commandlets produced valid saved outputs but returned exit1 because their default DDC was unwritable; original failure logs are retained. A Phase4F-local DDC resolved fresh readback (exit0) and is used by the interactive launcher. No solve was repeated to conceal the infrastructure error. The continuation preservation audit must pass before handoff; Engine/external reference trees are used read-only and are not claimed exhaustively hashed.
''')
instructions='''## John/Jane current primary review

This section supersedes the primary-subject directions above. Bill/Jill instructions remain historical T-pose-control instructions; do not review them to unlock the current generalisation path. John and Jane require real review. No measured trial has started.

Open the current interactive review (John is the startup map):

    & .\\Working\\Phase4F\\apose_launch_review.ps1

Use **Python** in the bottom console dropdown. Bind the current utility once if needed:

    import apose_ue_review; rigreview = apose_ue_review.rigreview

If module search paths are absent:

    import sys; sys.dont_write_bytecode=True; sys.path.insert(0,'E:/Repo/UE/Projects/MetaHumanTo3DCharacter/Working/Phase4F'); import apose_ue_review; rigreview=apose_ue_review.rigreview; rigreview.open('John')

Maps: /Game/MetaHumanTo3DCharacter/Phase4F/John/Maps/L_JohnReview and /Game/MetaHumanTo3DCharacter/Phase4F/Jane/Maps/L_JaneReview. Stay out of Play/Simulate. Normal translation gizmos act on F4 CONTROL actors; disable snapping for small edits. Amber requires review; green root/spines are provisional; purple lines are procedural. The ghost is the review surface and textured source is alongside. Press G in the viewport to hide light icons if needed.

Start only when beginning your real anatomical review:

    rigreview.start()

For each character review all these 19 roles against its actual A-pose, in front AND side:

- pelvis; neck_01; head;
- clavicle_l, upperarm_l, lowerarm_l, hand_l;
- clavicle_r, upperarm_r, lowerarm_r, hand_r;
- thigh_l, calf_l, foot_l, ball_l;
- thigh_r, calf_r, foot_r, ball_r.

upperarm is shoulder, lowerarm elbow, hand wrist; thigh hip, calf knee, foot ankle, ball metatarsal/forefoot. Assess elbow/knee bend direction as well as point position. Source asymmetry is not automatically an error. Body arms are now correctly aligned by coarse envelopes: do not perform the old T-pose-control arm relocation.

John priorities: inspect both clavicles and generated spine_03 in depth; neck/head, wrists, hips and hidden boot articulations still require judgement. Jane priorities: inspect pelvis/upper-spine lateral bias, clavicle roots and real fore/aft arm asymmetry. Jane left clavicle is on the wrong side relative to donor spine_03 under the retained convention; bilateral max17.777cm and the source sole-count screen also fail. Do not move a sound source point just to force symmetry or satisfy a screen. The sole count cannot be cleared with a human placement. Report convention/sampling conflicts for diagnosis.

Select and inspect:

    rigreview.select('hand_l')
    rigreview.view('front')
    rigreview.view('side')

Other views: arms, pelvis, feet, hand_l_top, hand_l_front, hand_r_top, hand_r_front. Drag only if the selected point actually needs correction, then record:

    rigreview.record()

After personally inspecting the final point, accept it (example only, not an approval recommendation):

    rigreview.accept('hand_l')

Keep uncertainty explicit:

    rigreview.unresolved('clavicle_l','pivot_convention_or_surface_ambiguity')

Record and accept are separate. No automatic mirroring. Pelvis/shoulder movements update dependent hips/spines/clavicles and invalidate affected approvals. Review moved/generated spines as necessary. Existing exact named groups remain available: Pelvis / hips / lower spine; Left shoulder / clavicle; Right shoulder / clavicle; Neck / head. Accept a group only after reviewing every member. discard() restores unrecorded drags; save() preserves progress.

Each character has five independent **unnamed** tracks on each side, numbered1–5 within that hand. Track numbers do not inherit Lara/Bill/Jill identities. John tracks follow relaxed partly curled fingers; Jane tracks have asymmetry. Use the per-hand top/front images in Documentation/Phase4F/John or Jane as additional views.

Highlight each actual track and identify it yourself:

    rigreview.track('l',1)
    rigreview.view('hand_l_top')
    rigreview.view('hand_l_front')

Only after identification, assign its actual identity. This is an API example, not the identity of track1:

    rigreview.identify('l','index',1)

Identities: thumb,index,middle,ring,pinky. Review each side independently. Duplicate track assignments are rejected. Inspect each generated chain's palm attachment, root/tip and all three procedural phalanges. If needed, select index_l:root or index_l:tip (substitute actual digit), move its gizmo and record(). Intermediate phalanges stay procedural; report a chain limitation rather than manually placing all joints. After actual identity/root/tip/chain review:

    rigreview.accept('index_l')

Repeat all five on each side; natural motion/thumb opposition is tested downstream, not certified by this acceptance.

Check progress and finish the real trial:

    rigreview.status()
    rigreview.finish()

Then independently review Jane:

    rigreview.open('Jane')
    rigreview.start()

Timing is Start-to-Finish and includes pauses. save() can preserve an unfinished trial. Moving anything after approval invalidates relevant position-bound evidence; never edit approval JSON or borrow Phase4D events.

Return when both reviews are ready, or report roles/tracks you cannot resolve. The agent will rerun Working/Phase4F/John/validate.py and Jane/validate.py, diagnose surviving geometry/convention flags without fabricating reviews, and proceed downstream only after the full gate passes. No manual weight painting or external Tk panel is required at this boundary.
'''
append_history('HumanReviewInstructions.md',instructions)
state=read(A/'Before/phase_status.json')
state.update(status='awaiting_apose_human_review',primary_subjects=['John','Jane'],retained_controls=['Bill','Jill'],supported_input='Clean unrigged humanoid in neutral A-pose',
    decision_complete=False,phase5_authorised=False,current_phase5_recommendation='WITHHOLD_PENDING_EVIDENCE',
    stop_reason='John/Jane ambiguous body anatomy and independent digit identities require real human judgement; full gates rejected.',
    completed=['fresh John/Jane archive/FBX/DCC inventory','pre-solve pose validation','clothing connectivity classification','character-local donor extraction','23-role proposals and five tracks per hand','retained full anatomy gates','T-control comparison','native review scenes and fresh-process readback','self-review and preservation audit'],
    pending=['real John/Jane review','full anatomy acceptance and numeric-flag diagnosis','fresh native build/binding','relative bounded refinements','same full stress suite incl Lara','shoulder/pelvis/finger/thumb/contact acceptance','source-free native closure/playback','clean-host/cooked tests','definitive GO/HOLD/NO-GO'],human_actions_recorded={'John':0,'Jane':0,'Bill':0,'Jill':0})
save(O/'phase_status.json',state)
save(A/'subject_registry.json',{'primary':['John','Jane'],'benchmark':'Lara','superseded_primary_retained_T_pose_controls':['Bill','Jill'],'bill_jill_files_changed':False,'source_pose_normalisation_deferred':True})
print('REPORT_APPENDED; historical prefixes preserved; primary subjects John/Jane; decision pending real review')
