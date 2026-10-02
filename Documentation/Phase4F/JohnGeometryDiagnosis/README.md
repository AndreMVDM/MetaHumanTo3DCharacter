🟢 **High confidence** — The 13 failures are explained by reproducible validation/sampling defects. Current accepted anatomy is geometrically supported; the diagnostics do not certify medical joint locations or later deformation quality.

# John Phase 4F — geometry failure diagnosis

Date: 2026-10-02 (Australia/Sydney). Scope: diagnosis and proposed corrective action only.

Persisted gate remains **173/186**, with **13 hard geometry failures**, all **39 anatomical-kind checks passing**, and **downstream_authorised = false**. The existing validator was not rerun or changed during this diagnosis.

Proposal SHA-256: 57d4c45a3f0ddda765d66e76c7453f99f754affba4fc067c75775095b677fad2

## 1. Body section-envelope failures

The reported enclosing_contour_count = 0 does not mean the source has no section intersections. The sampler returns connected fragments, and the validator asks whether an individual fragment bounding box contains the accepted pivot.

Exact existing method:

- Working/Phase4B/geometry_tools.py:11–32 intersects triangles with the horizontal plane at the pivot Z. Triangles must strictly straddle the plane; edges must have strictly opposite signed distances. Coplanar triangles and exact vertex hits are omitted.
- Intersection points are grouped by a rounded 0.005 cm coordinate key, then traversed as graph components. Components with fewer than five points or bounding diagonal under 0.15 cm are discarded.
- Each retained component receives an axis-aligned bounding box, its box centre, and a closed flag. The points are graph traversal order, not an ordered polygon.
- Working/Phase4F/John/inherited_validate.py:46–53 tests each fragment box independently with the existing +/-0.8 cm allowance. It ignores the closed flag and does not reconstruct a garment outline across source boundary gaps.

Measured pivots and local source support (canonical centimetres):

| Role | Accepted X, Y, Z | Raw / retained fragments | Nearest source triangle | Shirt support along -Y / +Y |
| --- | --- | --- | --- | --- |
| spine_03 | 0.2327, -3.6841, 129.2114 | 4 / 4 | 12.3708 cm, component 20 | 16.9427 / 17.6566 cm |
| clavicle_l | 1.5555, -7.2283, 141.7052 | 7 / 6 | 4.6737 cm, component 34 | 13.4011 / 9.6700 cm |
| clavicle_r | -1.5770, -7.1977, 141.6527 | 7 / 6 | 4.7135 cm, component 34 | 13.4056 / 10.1135 cm |

At spine_03, the main front shirt fragment has Y = 0.5648 to 13.9984 cm and the back fragment Y = -20.8819 to -17.8166 cm. The pivot Y = -3.6841 cm is between them. At clavicle_l, front Y = -3.6873 to 9.0230 and back Y = -20.6470 to -16.6690; the pivot Y = -7.2283 is between them. At clavicle_r, front Y = -3.6148 to 9.0171 and back Y = -20.6668 to -16.7285; the pivot Y = -7.1977 is between them. The side fragments occupy lateral sleeve positions. No individual fragment box contains the pivot, even with the original allowance.

Component 34 is the principal shirt shell; component 1 is a separate lateral sleeve piece. Component 20 contains the neck/chest/head region and is not a complete underlying torso donor. The front and back shirt triangle intersections bracket all three pivots at their actual X and Z. A nearest-surface distance is expected to be large for an internal torso pivot and does not establish an anatomical error.

Every open section endpoint lies on an actual source boundary edge after diagnostic 0.00001 cm coordinate welding: 8/8 at spine_03 and 14/14 at each clavicle. Thus the dominant breaks are genuine geometric boundary gaps, not merely duplicate vertex indices or rounding errors. These are clothing/topology sampling gaps in a fragmented garment. Exact authoring intent for the seams is not encoded in the mesh.

A read-only counterfactual joins the closest unmatched endpoints of distinct shirt/sleeve section fragments, within 0.8 cm. It uses the observed component labels only for this diagnostic, never as a proposed production whitelist. The resulting ordered outer polygons contain the unchanged pivots:

| Role | Diagnostic seam gaps, cm | Interior distance to reconstructed XY outline, cm |
| --- | --- | --- |
| spine_03 | 0.0662, 0.1574, 0.2248, 0.3542 | 16.9350 |
| clavicle_l | 0.2045, 0.2832, 0.3244, 0.3955, 0.5055 | 9.2429 |
| clavicle_r | 0.2045, 0.2777, 0.3306, 0.3884, 0.4970 | 9.5352 |

This reconstruction changes no mesh, proposal, review record or gate result. It demonstrates an enclosing garment outline using short, witnessed boundary gaps; it does not manufacture an underlying body. The tiny three-point collar fragment discarded by the original sampler is not needed to enclose either clavicle.

Sensitivity: all 84 combinations of plane offsets (-1, -0.2, -0.01, 0, +0.01, +0.2, +1 cm) and quantisation (0.00001, 0.001, 0.005, 0.01 cm) retain zero original enclosing fragment boxes. Consequently, changing only the rounding grid or plane height would not correct these body failures.

**Classification for all three body failures:** clothing/topology sampling issue producing a brittle fragment-envelope false negative. There is no demonstrated contradiction between the accepted pivots and the observed source/clothing envelope. Precise internal anatomy remains governed by the existing resolved human/automatic anatomical evidence, not by garment volume alone.

## 2. Finger surface-support failures

Working/Phase4F/John/validate.py:39 measures unsigned nearest-vertex distance for all three procedural phalange centres and requires the chain maximum to be strictly less than 1.2 cm. It queries all source vertices, without digit membership or an inside/outside test.

The accepted track is a polyline of horizontal-section bounding-box centres, not points on the skin. apose_prepare_review.py samples at 0.4 cm intervals, filters wide components (width < 4.68 cm at the canonical 180 cm height), and follows neighbouring centres. Branches can stop before entering the palm because the sections merge or become too wide. This is why partial-track warnings remain relevant; that warning does not explain the measured failures by itself.

The current generator reverses the distal-to-proximal track. It uses donor lengths l1 and l2, a terminal extension of 0.65*l2, and arc-length fractions [0, l1/(l1+1.65*l2), (l1+l2)/(l1+1.65*l2)]. The first phalange equals the accepted proximal track root.

For every chain, root, tip and complete path exactly equal the original source-derived track. All 30 generated centres lie on that accepted path to numerical precision. Independent recomputation from the saved donor lengths gives zero fraction error and maximum position error below 1.5e-14 cm. No endpoint movement, identity substitution or interpolation bug was found.

Every failed maximum is **phalange 01, the accepted track root**:

| Chain | Track / samples | Maximum nearest vertex, cm | Nearest triangle at that root, cm | Root XY section boundary clearance, cm |
| --- | --- | --- | --- | --- |
| thumb_l | digit_branch_5_l / 14 | 1.60673 | 1.57324 | 1.75932 |
| index_l | digit_branch_3_l / 22 | 1.76650 | 1.71553 | 1.74015 |
| middle_l | digit_branch_1_l / 25 | 1.69266 | 1.67025 | 1.76987 |
| ring_l | digit_branch_2_l / 24 | 1.67737 | 1.62974 | 1.76476 |
| pinky_l | digit_branch_4_l / 17 | 1.47037 | 1.43964 | 1.43967 |
| thumb_r | digit_branch_5_r / 14 | 1.60673 | 1.57324 | 1.75614 |
| index_r | digit_branch_3_r / 22 | 1.76650 | 1.71553 | 1.73310 |
| middle_r | digit_branch_1_r / 25 | 1.69077 | 1.66763 | 1.76694 |
| ring_r | digit_branch_2_r / 24 | 1.67737 | 1.62974 | 1.76476 |
| pinky_r | digit_branch_4_r / 17 | 1.47037 | 1.39663 | 1.41619 |

Every generated centre has nearest vertex and triangle support on the appropriate hand component (36 left, 0 right). At the roots the true nearest-triangle distances are 1.39663–1.71553 cm, so adding more vertices or switching only to triangle distance still fails all ten chains. The unsigned 1.2 cm cap measures finger thickness/interior depth as if a joint centre should be close to the exterior skin.

Independent source containment checks:

- All 30 centres are inside actual ordered closed XY section polygons at 0.00001 cm diagnostic quantisation, not merely their bounding boxes. At the original 0.005 cm grid two right-hand generated sections were flagged open; finer quantisation recovers their actual closed loops without closing gaps. This is a secondary sampler aliasing issue, distinct from the primary fixed-distance failures.
- Six oblique rays restricted to the corresponding hand component give odd crossing parity for every centre (180/180 directions). Six original axial rays provide an additional agreement check.
- Original track samples plus quarter/mid/three-quarter segment samples total 786 points. All 786 give odd local hand parity in all six oblique directions. This is sampled support, not a proof for every infinitesimal path location.
- Tip nearest-triangle distances are 0.01960–0.35337 cm. The paths run from supported proximal interior roots toward the fingertip surface. Their observed sample extents do not demonstrate that a root has been placed at the anatomical MCP centre; that location is covered by genuine accepted review, not inferred solely from topology.
- Ten explicitly synthetic outside control points, each approximately 0.2 cm beyond the local root surface, give even parity in all six directions. Nevertheless their nearest-vertex distances are only 0.33965–0.52590 cm, which would satisfy the present surface check. These controls were never written into the proposal. This demonstrates the present check can both reject interior centres and accept exterior ones.

**Classification for all ten finger failures:** inadequate support definition for internal procedural joints. Sparse vertices contribute small errors but are not the dominant cause. Partial tracks are a documented coverage limitation, not the measured cause of these 1.2 cm failures. There is no demonstrated bad generated placement or genuine endpoint/identity error.

All generated phalanges, with exact nearest source triangle IDs (zero-based) and positions in centimetres:

| Role | Centre X, Y, Z | Nearest vertex | Nearest triangle | Triangle ID | XY boundary clearance |
| --- | --- | --- | --- | --- | --- |
| thumb_01_l | 36.41102, 4.26840, 81.46744 | 1.60673 | 1.57324 | 34112 | 1.75932 |
| thumb_02_l | 35.57364, 4.94013, 78.89190 | 1.56863 | 1.54338 | 33997 | 1.55425 |
| thumb_03_l | 35.17910, 5.71566, 77.31629 | 1.22221 | 1.20397 | 33001 | 1.53564 |
| index_01_l | 43.71344, 3.91430, 77.06744 | 1.76650 | 1.71553 | 34617 | 1.74015 |
| index_02_l | 42.26076, 3.98367, 72.59500 | 1.33180 | 1.31680 | 33226 | 1.49321 |
| index_03_l | 40.97619, 3.25051, 70.31135 | 1.29319 | 1.20367 | 33157 | 1.37657 |
| middle_01_l | 45.69842, 0.36504, 76.66744 | 1.69266 | 1.67025 | 33905 | 1.76987 |
| middle_02_l | 45.07233, 0.41093, 71.73730 | 1.37139 | 1.35866 | 33694 | 1.39815 |
| middle_03_l | 43.61570, -0.11711, 69.01858 | 1.37493 | 1.33699 | 33604 | 1.50331 |
| ring_01_l | 46.82816, -3.36258, 76.66744 | 1.67737 | 1.62974 | 33977 | 1.76476 |
| ring_02_l | 46.58078, -3.29625, 72.32193 | 1.47442 | 1.43853 | 34804 | 1.53958 |
| ring_03_l | 45.09004, -3.60352, 69.47938 | 1.25106 | 1.23878 | 45154 | 1.43746 |
| pinky_01_l | 46.37344, -7.18042, 77.06744 | 1.47037 | 1.43964 | 45478 | 1.43967 |
| pinky_02_l | 45.33385, -7.49608, 73.73598 | 1.15317 | 1.14973 | 44764 | 1.15042 |
| pinky_03_l | 43.94290, -7.55371, 72.00976 | 1.05594 | 1.03967 | 44689 | 1.20078 |
| thumb_01_r | -36.41102, 4.26841, 81.46744 | 1.60673 | 1.57324 | 9916 | 1.75614 |
| thumb_02_r | -35.57527, 4.94545, 78.90057 | 1.56267 | 1.50584 | 9942 | 1.56552 |
| thumb_03_r | -35.17966, 5.71446, 77.31856 | 1.22341 | 1.20507 | 9520 | 1.53324 |
| index_01_r | -43.71344, 3.91431, 77.06744 | 1.76650 | 1.71553 | 4841 | 1.73310 |
| index_02_r | -42.32298, 4.01048, 72.68531 | 1.37162 | 1.35835 | 8874 | 1.50362 |
| index_03_r | -40.99650, 3.26276, 70.34933 | 1.29036 | 1.20366 | 8758 | 1.38594 |
| middle_01_r | -45.69842, 0.35995, 76.66744 | 1.69077 | 1.66763 | 9385 | 1.76694 |
| middle_02_r | -45.14184, 0.41360, 71.79588 | 1.43962 | 1.41843 | 4924 | 1.47397 |
| middle_03_r | -43.62870, -0.09405, 69.04615 | 1.37767 | 1.33104 | 9085 | 1.52888 |
| ring_01_r | -46.82816, -3.36257, 76.66744 | 1.67737 | 1.62974 | 5289 | 1.76476 |
| ring_02_r | -46.58580, -3.29588, 72.33937 | 1.47351 | 1.45018 | 18504 | 1.50643 |
| ring_03_r | -45.09306, -3.60290, 69.48560 | 1.25271 | 1.23719 | 18517 | 1.43837 |
| pinky_01_r | -46.37344, -7.18041, 77.06744 | 1.47037 | 1.39663 | 18956 | 1.41619 |
| pinky_02_r | -45.37821, -7.49316, 73.77672 | 1.19637 | 1.18266 | 18682 | 1.19644 |
| pinky_03_r | -43.95288, -7.55239, 72.03154 | 1.06610 | 1.04971 | 18668 | 1.20487 |

measurements.json also records each nearest vertex index/coordinate, nearest triangle point/component, accepted-track segment/fraction, donor fractions and ray hits. local_support.json records ordered-polygon clearances, independent regeneration error, dense path parity, source-boundary endpoint distances and the synthetic controls.

## 3. Justified policy correction

**A versioned validator policy correction is justified for both classes.** This is a change to the definitions of geometric support and must be recorded honestly as such. It should not be reported as an unchanged-rule pass. Moving accepted anatomy, broadening the 1.2 cm threshold to fit John, suppressing the failures, or manually granting downstream authority would be unsupported.

Minimal legitimate proposed scope:

1. **Body:** add a Phase4F-local, garment-aware section-envelope routine that reconstructs an ordered outline across demonstrably corresponding source boundary seams. Require reciprocal/unambiguous endpoint matching, compatible garment provenance, a declared bounded gap allowance, no invalid intersections or non-manifold branching, and actual polygon containment with the existing placement allowance. John’s witnessed gaps are all below 0.506 cm; the present 0.8 cm screening budget is a defensible upper bound for a proposed reconstruction allowance, but its new seam meaning must be explicit and regression-tested. Do not union arbitrary fragment or whole-character bounding boxes. Do not hard-code John’s component numbers. Unpaired, excessive or ambiguous gaps remain blocked. Preserve source geometry; reconstruction exists only for measurement.
2. **Fingers:** replace the hard unsigned nearest-vertex cap with independent containment in the actual local finger section associated with the accepted named track, supported by correctly scoped triangle geometry. Test procedural centres and segment support, preserve the existing identity/signature, side, length, uniqueness and inter-finger collision gates, and keep vertex/triangle distances as diagnostics. Robustly handle exact plane/vertex hits and quantisation so valid closed contours remain closed. Open/ambiguous support remains blocked. Being on a generated path alone cannot certify support: the source polygon/triangles must independently support it. Keep the original 1.2 cm result in migration evidence; do not relabel it as a passed unchanged criterion.
3. **Verification before revalidation:** apply the correction generically to Phase4F only, version its policy and provenance, and exercise synthetic closed/open seam, oversized/ambiguous gap, concave-outside-pivot, exact-plane/vertex, inside-thick-finger, exterior-near-surface, wrong-digit, swapped-track, moved-root and inter-finger collision controls. Compare all existing check outcomes, human evidence signatures and protected-file hashes. Failure or ambiguous geometry must continue to block downstream. The scripts here are diagnostic probes, not production policy implementations.

This is a narrowly targeted correction to two flawed support screens. It does not redesign the review backend or remove hard geometry gating.

## 4. Revalidation and required human action

John can be revalidated against the same persisted proposal and genuine review evidence after a legitimate validator-only correction. No additional anatomy review is indicated by these findings, provided positions, tracks, identities, chain generation and every evidence-bound signature remain unchanged. If implementation changes any reviewed input or reveals a genuine contradiction, the existing invalidation rules still apply.

A full corrected gate run is still required. This diagnosis does not assert 186/186 or grant downstream_authorised. The current genuine result remains 173/186 and false. The next action is engineering implementation/review of the proposed correction, not moving John’s accepted landmarks.

## 5. Preservation and reproducibility

Both read-only diagnostics verified all 339 protected inputs/outputs against SHA-256 baselines: zero changes. Protected files include John and Jane Working/Documentation state, current proposal/review evidence, existing validator outputs, Phase4F backend scripts, inherited geometry_tools.py and evaluation_policy.json. Newly added diagnostic scripts and diagnosis artefacts are outside the persisted review state.

Run the read-only diagnostics from the project root:

    python -B Working/Phase4F/diagnose_john_geometry.py
    python -B Working/Phase4F/diagnose_john_local_support.py

The first script overwrites only diagnosis measurements/baseline; the second overwrites only local-support measurements/plots. Neither calls review commands, exports proposals, runs the validator or launches UE. Nearest-triangle calculations include self-checks for face, edge, outside-triangle and degenerate cases; ordered sections and independent ray queries cross-check the support interpretation.

Artefacts:

- measurements.json — every original section fragment, phalange support measurement and sensitivity probe.
- local_support.json — local topology, ordered polygon, independent procedural regeneration and negative-control evidence.
- source_sections.png — actual source triangle-plane intersections, body pivots and finger roots with the original 1.2 cm circles.
- preservation_before.json — protected SHA-256 baseline.

No skeleton, skinning, IK, retarget or bake work performed. Jane was not started. Stopped after diagnosis and proposed corrective action.
