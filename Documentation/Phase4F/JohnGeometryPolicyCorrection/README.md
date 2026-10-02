🟢 **High confidence** — The versioned validator correction is implemented and tested. John remains blocked: **176/186**, ten hard body-support failures, **downstream_authorised = false**.

# Phase4F validator policy correction — John result

Date: 2026-10-02 (Australia/Sydney). Workflow: Level 1, single agent plus self-review. No Git directory is present; no commit, staging or branch operations performed.

## Result

- Policy: **phase4f.geometry-support/2.0.0**. This is explicitly a changed-rule result.
- Complete validator: **176/186**; all **39/39 anatomical-kind checks pass**.
- All ten finger support checks now pass; no finger support failures remain.
- All 20 existing inter-finger collision gates pass.
- John trial remains finished, with 30 review commands, 12 digit identifications, zero placements and zero moved landmarks.
- All 29 accepted session approval signatures are current: 19 body roles and 10 finger chains. Proposal/review binding, all evidence hashes and all 218 immutable events were independently verified.
- No skeleton, skinning, IK, retarget or bake work performed. Jane remains untouched.

## Every remaining failure

| Check | Classification | Old screen passed? |
| --- | --- | --- |
| surface_envelope_spine_02 | Branched source section; no unambiguous valid enclosing polygon | Yes |
| surface_envelope_spine_03 | Invalid reconstructed shirt polygon: non-adjacent source-section edges self-intersect | No |
| surface_envelope_clavicle_l | Invalid reconstructed shirt polygon: non-adjacent source-section edges self-intersect | No |
| surface_envelope_upperarm_l | Branched source section; no unambiguous valid enclosing polygon | Yes |
| surface_envelope_thigh_l | Branched source section; no unambiguous valid enclosing polygon | Yes |
| surface_envelope_foot_l | Open boot outlines; corresponding endpoint gaps exceed 0.8 cm and no compatible garment anchor is available | Yes |
| surface_envelope_clavicle_r | Invalid reconstructed shirt polygon: non-adjacent source-section edges self-intersect | No |
| surface_envelope_upperarm_r | Branched source section; no unambiguous valid enclosing polygon | Yes |
| surface_envelope_thigh_r | Branched source section; no unambiguous valid enclosing polygon | Yes |
| surface_envelope_foot_r | Open boot outlines; corresponding endpoint gaps exceed 0.8 cm and no compatible garment anchor is available | Yes |

There are three retained failures and seven newly exposed failures. The old fragment bounding-box rule admitted the seven new cases; actual valid polygon support does not. The remaining failures do not demonstrate that human-accepted anatomy should move or that reviews must be invalidated.

## Limitation exposed in the preceding diagnosis

The earlier diagnostic counterfactual tested whether joined outlines contained the pivots, but did not test whether those outlines were simple polygons. The implemented invalid-outline control exposed genuine crossings between non-adjacent source section edges around shirt seams. The current policy must reject these outlines under the explicit requirement to block invalid reconstruction.

Examples at spine_03 (XY centimetres): the source segment (-20.60345, 0.86904) to (-20.57506, 0.80991) crosses the non-adjacent source segment (-20.53228, 0.56483) to (-20.58642, 0.85102). Both are original surface intersections, not newly fabricated seam links. Another source-edge crossing occurs around X=20.8, Y=1.1. Clavicle sections similarly cross around the right sleeve/back and front seam regions. No seam rule was weakened to accept these self-intersections.

The foot sections also have genuine open outlines. The corresponding positive-X endpoint gaps at the left-foot height are approximately 1.92 and 3.01 cm, both above the declared 0.8 cm seam budget. Existing provenance supplies shirt, trousers and belt anchors, not a compatible boot anchor. Adding provenance alone would therefore not resolve the excessive boot gaps.

## Implemented policy

The shared Working/Phase4F/geometry_support_policy.py contains no John/Jane component constants. Character-local classification anchors and original object/material metadata provide provenance; all source hashes are recorded in migration evidence. A regression renumbers every synthetic component and obtains the same result.

Body support:

- Intersects original triangles with the exact horizontal plane, including vertex/edge hits and coplanar face perimeters. Source-edge keys maintain connectivity without the old 0.005 cm section-point aliasing.
- Reconstructs only source-boundary endpoints within 0.8 cm. Matches must be reciprocal and unique. Principal garment group/object/material provenance must agree. A satellite fragment needs both terminals matched directly to the same anchored garment.
- Allows a single open garment fragment to close only when its two terminals satisfy the same bounded reciprocal requirements.
- Refuses unsupported provenance, ambiguous partners, excessive gaps, branched sections, zero-area and self-crossing/touching outlines. Does not union bounding boxes or edit source geometry.
- Tests actual ordered polygons, retaining the existing 0.8 cm placement allowance.

Finger support:

- Associates source polygons independently with the original named source track at each tested height. Requires exactly one closed supporting polygon; no finger seam reconstruction is allowed.
- Validates all generated phalange centres, the complete accepted path and the straight phalange segments. Uses samples no farther than 0.2 cm apart, plus continuous segment/source-triangle crossing rejection.
- Binds the path to its source track and accepted endpoints. Being on a path cannot establish geometric support.
- Keeps nearest-vertex and nearest-triangle distances as diagnostics. The old strict 1.2 cm results remain intact in migration evidence.
- Preserves identity, side, signature, length, uniqueness and the exact existing 41-sample/0.25 cm inter-finger collision rules.

A missing/mismatched source binding or missing source-track evidence fails closed. The routines make no review command or source/proposal write.

## Policy version and migration

Documentation/Phase4F/anatomy_geometry_policy_v2.json defines the policy, provenance requirements, numerical conventions and explicit seam-budget justification. The output declares baseline_numeric_thresholds_unchanged = false.

Documentation/Phase4F/John/geometry_policy_migration.json preserves **32 complete legacy check records** (22 body envelopes, 10 finger screens), their old measurements/criteria/pass results, and the new outcomes. It also records policy/source/provenance hashes. Exact equality against the saved original check records was verified.

All **154 other checks are identical** to their pre-correction records. The inherited validator and its legacy corrected result are unchanged; that result intentionally remains historical fragment-envelope evidence. The final anatomical_validation.json is the complete version-2 gate authority.

## Regression controls and self-review

**27 tests passed.** Controls include valid closed source and repaired seams, single-fragment closure, open/oversized/ambiguous seams, incompatible and absent garment provenance, branched sections, crossed polygons, concave outside pivots, preserved placement allowance, exact plane/vertex/coplanar hits, thick interior fingers, exterior points near vertices, wrong-digit geometry, open/ambiguous finger support, exterior paths with supported centres, continuous source crossings, swapped tracks, moved roots, inter-finger collision, nearest-triangle calculations, component renumbering, changed source binding and missing track evidence.

Two initial synthetic fixtures were corrected: the thick-finger tube cap was too close to its test root, and the exterior control needed a vertex at its sampled height to exercise the legacy vertex rule. Self-review also added explicit missing-input rejection and verified that body self-intersections remain blocked. No threshold was adjusted to make John pass.

Reproducible commands:

    python -B Working/Phase4F/test_geometry_support_policy.py
    python -B Working/Phase4F/John/validate.py

## Preservation and files

Baseline: 346 existing files. All **342 immutable files** remain byte-identical. Three authorised existing files changed: the John validator adapter and its anatomical_validation.json / experiment_result.json derived outputs. The fourth allowed derived file, inherited_anatomical_validation_corrected.json, was rerun and remains byte-identical. No unexpected change occurred. All **42 Jane files** in the baseline remain byte-identical.

New implementation files:

- Working/Phase4F/geometry_support_policy.py
- Working/Phase4F/test_geometry_support_policy.py
- Documentation/Phase4F/anatomy_geometry_policy_v2.json

New derived evidence:

- John/geometry_policy_migration.json
- This correction folder: prior gate/validator snapshots, preservation baseline, regression_results.json, validation_audit.json and remaining_failures.json.

The frozen evaluation_policy.json, prior-phase library, original diagnosis, review core, current proposal, geometry, tracks, identities, approvals, session, events and correction metrics are unchanged.

## Next boundary

Further engineering diagnosis of self-overlapping/branched body sections and open boot support is required before a genuinely complete gate pass. There is no evidence here requiring additional human anatomy review or accepted landmark movement. No further policy relaxation, source repair or downstream work has been authorised by this result.

Stopped and returned control after implementation, regression tests, complete John revalidation and preservation audit.
