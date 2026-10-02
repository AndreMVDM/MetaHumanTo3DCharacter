🟢 **High confidence**

# John — completed human-review anatomy validation

Existing validator executed: `python -B Working\Phase4F\John\validate.py`. Process exit code 0; the complete anatomy gate failed.

**Final score: 173/186 passed; 13 failed. `downstream_authorised=false`.**

The expanded gate now checks the ten named procedural finger chains; the earlier 106-check score was the pre-identification snapshot. All 39 anatomical-kind checks pass. John remains finished with 30 review commands, 12 digit identifications, zero placements and zero moved landmarks. All 19 required human body roles and ten named finger chains have valid current approval signatures and genuine human evidence.

## Every remaining failure

All remaining failures have validator kind `hard`. Classifications below describe the failed numerical screen, not an established root cause or a claim that the human anatomical decision was wrong.

| Failed check | Measured result | Required criterion | Classification |
| --- | --- | --- | --- |
| `surface_envelope_spine_03` | 0 enclosing contours | At least one section envelope with ±0.8 cm allowance | Hard body section-envelope geometry screen |
| `surface_envelope_clavicle_l` | 0 enclosing contours | At least one section envelope with ±0.8 cm allowance | Hard body section-envelope geometry screen |
| `surface_envelope_clavicle_r` | 0 enclosing contours | At least one section envelope with ±0.8 cm allowance | Hard body section-envelope geometry screen |
| `finger_surface_thumb_l` | Maximum nearest-vertex distance 1.606735 cm | Every generated phalange centre <1.2 cm from a target vertex | Hard procedural finger surface-support geometry screen |
| `finger_surface_index_l` | Maximum nearest-vertex distance 1.766498 cm | Every generated phalange centre <1.2 cm from a target vertex | Hard procedural finger surface-support geometry screen |
| `finger_surface_middle_l` | Maximum nearest-vertex distance 1.692659 cm | Every generated phalange centre <1.2 cm from a target vertex | Hard procedural finger surface-support geometry screen |
| `finger_surface_ring_l` | Maximum nearest-vertex distance 1.677371 cm | Every generated phalange centre <1.2 cm from a target vertex | Hard procedural finger surface-support geometry screen |
| `finger_surface_pinky_l` | Maximum nearest-vertex distance 1.470372 cm | Every generated phalange centre <1.2 cm from a target vertex | Hard procedural finger surface-support geometry screen |
| `finger_surface_thumb_r` | Maximum nearest-vertex distance 1.606735 cm | Every generated phalange centre <1.2 cm from a target vertex | Hard procedural finger surface-support geometry screen |
| `finger_surface_index_r` | Maximum nearest-vertex distance 1.766498 cm | Every generated phalange centre <1.2 cm from a target vertex | Hard procedural finger surface-support geometry screen |
| `finger_surface_middle_r` | Maximum nearest-vertex distance 1.690768 cm | Every generated phalange centre <1.2 cm from a target vertex | Hard procedural finger surface-support geometry screen |
| `finger_surface_ring_r` | Maximum nearest-vertex distance 1.677371 cm | Every generated phalange centre <1.2 cm from a target vertex | Hard procedural finger surface-support geometry screen |
| `finger_surface_pinky_r` | Maximum nearest-vertex distance 1.470372 cm | Every generated phalange centre <1.2 cm from a target vertex | Hard procedural finger surface-support geometry screen |

The three body checks concern `spine_03` and both clavicle roots. The ten finger checks measure generated joint centres against target vertices. These are retained coarse geometry screens. This run does not distinguish an incorrect position/path from a surface sampling or screen-definition limitation. No threshold, criterion, identity, position or approval was changed to force acceptance.

All current identity/review, finger side, finger segment and sampled inter-finger collision checks pass. The `automatic_anatomical_passed=false` field indicates that manual anatomical evidence was used; it does not mean the genuine human review is incomplete. The full gate remains blocked by the thirteen hard checks.

## Preservation and next action

334 protected files remained byte-identical across John/Jane inputs, sessions, human evidence, metrics, proposals and validator dependencies. All 218 John events matched their immutable files. Approval signatures and genuine accepting-event provenance were checked. The current proposal SHA matches both the review binding and validation result. Only the existing validator's three derived output files were regenerated; previous versions are retained in `Before/`.

No additional human acceptance or identification is currently flagged. Technical diagnosis of the failed geometry screens is required before downstream work can be authorised. No corrective user movement is prescribed from these numbers alone; any later justified changes would require the existing placement and re-review workflow.

No skeleton, skinning, IK, retarget or bake work was performed. Jane was neither started nor validated. Work stopped at this requested reporting boundary.

## Artefacts

- Current result: `Documentation/Phase4F/John/anatomical_validation.json`.
- Derived inherited result: `Documentation/Phase4F/John/inherited_anatomical_validation_corrected.json`.
- Updated derived experiment result: `Documentation/Phase4F/John/experiment_result.json`.
- [Preservation/provenance audit and complete measurements](validation_audit.json).
- [Before-run protected-file hashes](preservation_before.json).

Level 1 self-review confirms every failed check is listed, aggregate counts agree with individual results, all anatomical-kind checks pass, authorisation remains false, genuine inputs/evidence are unchanged, and the user's stop boundary was respected.
