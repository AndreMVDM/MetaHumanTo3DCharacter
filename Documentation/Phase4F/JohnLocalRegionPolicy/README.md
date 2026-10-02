🟢 **High confidence** — The implemented policy, 73 regression results, complete John gate and preservation audit are directly verified. The separate right-thigh research supplies a source-scoped rejection witness; it does not establish a new acceptance rule or a physical anatomical contradiction.

# John: versioned local-region body support

Date: 2026-10-02, Australia/Sydney. Execution: Level 2, implementation and self-review with one focused independent reviewer. Authority: the completed [body-support diagnosis](../JohnBodySupportDiagnosis/README.md) and the user's explicit implementation instruction.

**John: 185/186. HOLD. downstream_authorised = false.** The nine justified body-support failures now pass. The sole remaining failure is **surface_envelope_thigh_r**, a hard geometry/support failure: no owned closed oriented region is certified at the accepted right-thigh pivot. No additional human review, position correction or identity change is indicated. No right-thigh 3D acceptance rule, Jane work, skeleton, skinning, IK, retarget or bake has been implemented.

## Explicit policy change

The new body policy is **phase4f.geometry-support/3.0.0**, defined in [anatomy_geometry_policy_v3.json](../anatomy_geometry_policy_v3.json). This is a changed-rule evaluation, not an unchanged-rule pass. Finger support remains **phase4f.geometry-support/2.0.0**. Both the placement allowance and maximum reconstructed seam gap remain **0.8 cm**; the 1e-8 cm numerical tolerance is used for arithmetic/contact handling, not as a new placement allowance.

The implementation changes the unit of body certification from a whole fragment graph/simple polygon to an independently source-supported, role-owned local region:

1. Read the frozen source triangles. Preserve original triangle and vertex IDs, component, oriented manifold sheet, original triangle normal, object/material provenance and named garment association on every section record. Check that the original source coordinate frame exactly reproduces the bound canonical geometry, including its handedness.
2. Split actual proper crossings, exact endpoint/T contacts and collinear overlap endpoints into planar arrangements. Preserve coincident multiplicity. Opposed coincident directions cannot certify a boundary. Numerical snapping cannot bridge a real opening.
3. Construct source-directed closed cycles within a component or an ownership scope connected by eligible seams. Keep independently closed oriented source loops as separate certificates when another unused fold crosses them. Retain all dangling traces and rejected branches in diagnostic evidence; remove noncycle tails only from boundary traversal.
4. Use actual polygon containment and explicit inward holes, including nested/crossing shell uncertainty. An external placement allowance cannot fill a cavity. A filled island requires its own independently supported positive boundary. Missing/inconsistent orientation, ambiguous ownership and unsupported boundaries fail.
5. Reconstruct only true source-boundary terminals with reciprocal unique matches, compatible anchored garment provenance, compatible endpoint directions and the existing seam budget. Unanchored satellite chains cannot accumulate arbitrary reconstruction. No endpoint-to-edge guesses, arbitrary caps, source repair or bounding-box union is used.
6. Require an anatomical role association before any region can pass. Principal torso/limb garments use the existing shirt/trouser classification. Existing unclassified skin associations still undergo the new orientation/hole checks. Footwear requires explicit source-bound semantic classification, correct side and actual triangle footprint association at both accepted ankle/ball landmarks. Footprint association is not an enclosure or a volumetric certificate.

The added [John footwear ownership evidence](../John/body_region_ownership.json) records source-specific engineering classification from the already completed diagnosis. Its source and diagnostic-evidence hashes and original provenance tokens are checked. Component numbers occur in that bound source metadata, not as John-specific policy constants. Geometry and human review files are unchanged. A ring/accessory around the landmarks receives no footwear association merely because it encloses them.

Sheet IDs remain attached to every contributing source trace; a certificate is not required to stay on one manifold sheet. Actual intersections between consistently directed traces in the same classified source component can bound the owned local region, as required by the diagnosed same-boot overlaps. Separate components cannot acquire common boundary ownership merely by crossing: only eligible seams create a shared scope. An ambiguous direction/branch cannot certify a face. The focused reviewer identified a synthetic limitation: forcing unrelated open sheets into one component/garment label would make them eligible for this within-component rule. That forced relabelling is not the frozen John source component evidence, and no John false pass was demonstrated. The ownership classification remains an explicit engineering input; it must not merge unrelated sheets into one garment component. Future classifiers that do so need an additional sheet compatibility relation and rejection control before their metadata can be trusted.

Production files: [body_region_support.py](../../../Working/Phase4F/body_region_support.py), [geometry_support_policy_v3.py](../../../Working/Phase4F/geometry_support_policy_v3.py), and the updated [John validator](../../../Working/Phase4F/John/validate.py). There is no 3D fallback in this policy.

## Complete gate result

The complete validator was rerun after the production corrections. [Validator output](validator_stdout.txt), [full 186 checks](../John/anatomical_validation.json) and [final audit](validation_audit.json) preserve the result.

| Former failure | v3 result |
| --- | --- |
| surface_envelope_spine_02 | Pass |
| surface_envelope_spine_03 | Pass |
| surface_envelope_clavicle_l | Pass |
| surface_envelope_clavicle_r | Pass |
| surface_envelope_upperarm_l | Pass |
| surface_envelope_upperarm_r | Pass |
| surface_envelope_thigh_l | Pass |
| surface_envelope_foot_l | Pass |
| surface_envelope_foot_r | Pass |
| surface_envelope_thigh_r | **Fail: no_owned_closed_oriented_region** |

All **39 anatomical-kind**, **10 finger support** and **20 inter-finger collision** checks pass. All **164 non-body checks** are exactly equal to the prior v2 results. The gate contains the original 186 checks.

The [migration evidence](../John/geometry_policy_migration.json) retains all **22 exact v2 body results** and **32 exact legacy results**, including the original fragment-envelope failures and ten hard 1.2 cm nearest-vertex finger results. Exact prior outputs are also saved as before_anatomical_validation.json, before_geometry_policy_migration.json and before_experiment_result.json in this folder. Neither historical policy is overwritten.

## Regression and review evidence

**73/73 regressions pass:** 27 inherited v2 controls plus 46 v3 controls. The [test suite](../../../Working/Phase4F/test_geometry_support_policy_v3.py), [individual results](regression_results.json) and [test output](regression_stdout.txt) are preserved.

The suite covers compatible closed seams; open/excessive/ambiguous seams and direction conflicts; unanchored reconstruction; layered and overlapping owned loops; explicit cavities and filled islands; allowance around cavities; inconsistent or uncertain shell orientation; opposite coincident boundaries; independently closed loops crossed by unused folds; dangling flaps versus needed missing boundaries; actual boot overlap versus a real gap; wrong garment, side and accessory association; exact plane/vertex/edge/end-plane contacts; proper/T/collinear contacts and source multiplicity; concave outside points; retessellation and component renumbering; stale geometry/evidence ownership bindings; reflected coordinate frames; open volumes with high winding or misleading finite ray hits; and all existing human/finger identity, signature, moved-root, path support and collision safeguards.

The focused reviewer found and demonstrated two material counterexamples: an unbound accessory enclosure and an inward crossing shell not represented as a nested hole. These were fixed and given rejection controls. A second footwear counterexample showed that footprint association alone could admit an accessory; explicit diagnosis-backed semantic ownership now precedes the footprint test. The reviewer accepted that correction by direct probe and hash checks. The final sheet scrutiny concluded **Accepted with Non-Blocking Recommendation** to document the within-component sheet-switch semantics, addressed above. The parent's complete regression run and validator/audit run are separate from the reviewer's targeted inspection. See [focused review record](focused_review.md).

## Human and protected-file preservation

The [read-only audit script](../../../Working/Phase4F/audit_local_region_policy.py) verifies:

- Proposal SHA-256: **57d4c45a3f0ddda765d66e76c7453f99f754affba4fc067c75775095b677fad2**.
- All **29 approval signatures** are current; persisted joints/finger chains exactly match the proposal. Every referenced review-evidence hash and finger-chain signature remains valid.
- All **218 immutable interaction events** still match their individual event files. Trial remains finished; **30 review commands**, **12 digit identifications**, **0 placement commands**, **0 moved landmarks**. No identities, approvals, positions or review events changed.
- Of **1,856 baseline files**, **1,851** are byte-identical. The four authorised existing changes are John validate.py and its three derived gate/migration/result outputs. The fifth change is the live panel's derived runtime status snapshot, written by the unchanged Bridge.publish heartbeat publisher; its revision, session, metrics and fingers match the unchanged persisted session. It was not restored or treated as human evidence.
- **42 Jane files** are byte-identical. Against the established **3,614-file protected baseline**, no files are missing and no new/unexpected deviation exists. The four recorded historical shared-document differences predate this correction and are unchanged by it.

## Right thigh: separate 3D-support research

The accepted pivot stays at **(-8.8984441757, -1.8754589558, 90.4026947021) cm**. Research is scoped to the source garment already classified as trouser_region. No garment cap, lower slice, plane vote, winding cutoff or finite-ray acceptance was introduced.

The [research script](../../../Working/Phase4F/research_right_thigh_3d.py) and [measurements](right_thigh_3d_research.json) establish two different results:

1. Edge-incidence elimination leaves **zero of 6,729 original trouser triangles** eligible for a nonzero closed nonnegative oriented whole-source-triangle 2-chain. This is a necessary-condition result for original whole triangles; it does not exhaust arrangements that split intersecting triangles.
2. At the **exact accepted Z**, a complete two-segment collision-free path runs from the pivot through the source opening to (-25,20), then continues towards negative X indefinitely above every section trace. It has no intersection with any scoped source triangle. Minimum section clearances are approximately **0.00000579 cm** and **0.00009888 cm**, above the 1e-8 cm numerical tolerance but very small; the opening is narrow. This is an explicit exterior-connectivity rejection witness, not acceptance inferred from a finite collection of rays.

![Right-thigh source opening and exterior escape path](right_thigh_escape.png)

The witness contradicts a bounded cell in this component-scoped, source-only surface complement. It does not demonstrate a wrong anatomical pivot: the garment's opening prevents geometric certification. Any future legitimate seam-supported model must account for that opening explicitly and independently; the present research has not justified such a completion.

### Proof obligations before any 3D acceptance implementation

1. Establish unambiguous role/side/component/sheet ownership and source provenance. Exclude remote garments, opposite limbs and accessory enclosures.
2. Build a complete local 3D arrangement, retaining original oriented triangle provenance through proper intersections, coplanar overlaps and exact contacts. Define which owned material cell is being certified and how layered shells and cavities are distinguished.
3. Demonstrate a genuinely closed oriented boundary with cancelling edge incidence, positive volume and no connection to the unbounded exterior. Every boundary face must come from actual source geometry or an independently justified, uniquely matched, compatible seam completion within the existing budget. No arbitrary cap may supply a missing face.
4. Prove that the exact accepted pivot lies inside that certified cell, with explicit uncertainty handling. Nearby closed slices, majority voting, winding greater than 0.5 and finite hit counts cannot substitute for this proof.
5. Reject the current exterior escape if it remains valid in the proposed ownership model. Identify any legitimate source-supported completion that blocks it and preserve its evidence; otherwise right thigh must remain failed.
6. Add rejection controls for open boxes and narrow slits despite high winding or finite-ray hits; genuine openings/missing panels; wrong-side/accessory/remote shells; nested cavities and cancelling/opposed layers; ambiguous or excessive seams; exact contacts; and equivalent retessellation/component renumbering. Retain all human-evidence and downstream gating safeguards.

**Stopping point:** Part 1 is implemented and verified. Part 2 remains research with explicit rejection evidence and proof obligations. Right thigh is the sole blocker, downstream authorisation remains false, and control returns to the user before any further policy implementation or downstream work.
