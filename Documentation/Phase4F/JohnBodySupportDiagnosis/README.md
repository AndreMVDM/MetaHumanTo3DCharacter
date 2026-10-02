🟠 **Medium confidence** — The source topology and preservation results are directly measured. Nine failures have candidate enclosing regions using actual section geometry and bounded seams. The right thigh has a real open section at its pivot height; neither these experiments nor winding/ray corroboration certify it as a closed supported region. No anatomical contradiction has been demonstrated, and no new pass rule is implemented.

# John: ten remaining body-support failures

Date: 2026-10-02, Australia/Sydney. Level 1: single-agent investigation and self-review. This is a diagnosis and proposed correction, not validation under a new policy.

The authoritative gate remains **176/186**, **downstream_authorised = false**, under **phase4f.geometry-support/2.0.0**. All 39 anatomical-kind checks, ten finger support checks and 20 inter-finger collision checks retain their existing results. No validator rerun, source modification, landmark movement, identity change, approval change or review event occurred. No Jane or downstream work occurred.

## Evidence and method

- [measurements.json](measurements.json): each accepted pivot, every intersecting source triangle, component membership, section endpoint graph, branch incident faces, actual crossing coordinates, triangle normals, UV texture samples, permitted v2 links, alternative diagnostic links, region boundaries, nearest source triangle, 22 ray probes and oriented solid-angle measurements.
- [endpoint_contacts.json](endpoint_contacts.json): trouser endpoint-to-source-segment distances and right-thigh section sweep.
- Twenty PNGs: ROLE_section.png preserves the full section and pivot neighbourhood; ROLE_regions_and_junctions.png preserves candidate boundaries and source defect insets. Individual links appear below.
- [diagnostic_controls.json](diagnostic_controls.json): ten assertions passed, plus explicit nested-shell and open-volume limitations. These verify diagnostic operations; they do not replace the required future validator regressions.
- [preservation_after.json](preservation_after.json): 385 existing files remained byte-identical, including the current John inputs, review evidence, validator, policy, outputs and Jane files.
- [protected_preservation.json](protected_preservation.json): separate read-only audit against the established 3,614-file protected baseline.

The section calculations use the frozen canonical source triangle coordinates in centimetres. Blender was used solely to read original UV coordinates; the returned triangle index array was checked against the frozen source array. No Blender file was saved. Component IDs below identify this evidence, not proposed generic policy constants.

All branch nodes occur in **raw source connectivity**, without positional welding. At their source edges, three or four actual triangles share the same raw vertex pair. They are not introduced by the positional weld. At the 50 initial probe planes (each pivot Z and ±0.01/±0.2 cm), no raw source vertex lies exactly on the plane. Nearby planes still contain the non-manifold/crossing problems. The right-thigh sweep additionally shows a genuine topology transition across a nearby source vertex; that distinction is detailed below.

The arrangement experiment splits real segment intersections and exact endpoint-on-edge contacts, retains every source trace in the evidence, and traverses bounded faces after removing dangling edges only from the face traversal. It never fills a geometric gap by numerical snapping. Repeated boundary walks are decomposed into simple cycles, with touching negative cycles retained as holes. **Disconnected nested loops still require oriented shell ownership:** a bounded face count alone cannot distinguish a cavity from a filled clothing layer. Candidate region counts are therefore not production support certificates.

## Participating components/surfaces

Labels are connected-component labels used by the current support reader. Raw labels are included to make raw-versus-weld correspondence explicit. All these surfaces originate from one imported object/material; common material alone does not establish garment compatibility. Texture and spatial shape support the descriptions below; the source does not supply authoritative tailoring or layer labels.

| Component (raw label) | Surface represented | Triangles | Boundary / non-manifold edges |
| --- | --- | ---: | ---: |
| 34 (36) | Principal blue-grey shirt/torso and shoulder panels; current shirt_region anchor | 5,709 | 329 / 57 |
| 1 (16) | Separate negative-X shirt sleeve panel | 1,218 | 124 / 0 |
| 20 (34) | Skin patch spanning neck/chest/face, not a complete underlying torso | 1,196 | 41 / 1 |
| 25 (29) | Trousers; current trouser_region anchor | 6,729 | 127 / 13 |
| 3 (15) | Negative-X arm skin | 1,044 | 0 / 0 |
| 36 (32) | Positive-X arm/hand skin | 4,716 | 0 / 0 |
| 0 (13) | Negative-X hand skin, remote from the thigh pivots | 3,628 | 0 / 0 |
| 7 (12) | Negative-X/right boot upper | 1,635 | 106 / 1 |
| 32 (27) | Positive-X/left boot, including its lower shell/sole | 3,169 | 165 / 0 |
| 10 (10) | Separate right sole, below both foot section planes | 1,850 | 64 / 0 |
| 35 (33) | Positive-X sleeve/cuff patch, below the failing shoulder planes | 622 | 58 / 0 |
| 24 (30) | Belt, below the failing spine_02 plane | 2,204 | 90 / 0 |

Components 10, 35 and 24 participate in the 3D corroboration, **not** the respective horizontal section. The component record contains exact extents and all raw label mappings. Remote arms/hands and the opposite boot are not evidence for enclosing the selected pivot.

## Diagnosis of each failed check

The table lists **all** components intersecting each plane. B/C denotes branch nodes/proper section crossings across the complete character section; remote crossings are separated in the explanations.

| Check suffix | Accepted Z (cm) | All section components | B/C | Cause and candidate result |
| --- | ---: | --- | --- | --- |
| spine_02 | 115.406311 | 3, 34, 36 | 2/0 | Two four-face shirt seam junctions; raw shirt traces already bound a region containing the pivot. |
| spine_03 | 129.211426 | 1, 34 | 0/3 | Sleeve/torso overlap plus shirt fold crossing; existing v2 seams produce a containing region after arrangement decomposition. |
| clavicle_l | 141.705185 | 1, 20, 34 | 0/5 | Collar skin/shirt intersections and shirt fold overlaps; existing v2 seams produce a candidate containing region. |
| clavicle_r | 141.652695 | 1, 20, 34 | 0/5 | Same collar/shoulder layers as left, at its own accepted plane; candidate containing region with existing v2 seams. |
| upperarm_l | 138.057434 | 1, 20, 34 | 1/3 | Shirt seam branch on the opposite shoulder invalidates the entire part; local reciprocal bounded seam pairs plus arrangement produce a candidate containing region. |
| upperarm_r | 138.151352 | 1, 20, 34 | 1/3 | Same non-manifold shirt seam near this shoulder; local reciprocal bounded seam pairs plus arrangement produce a candidate containing region. |
| thigh_l | 90.338554 | 0, 3, 25, 36 | 3/6 | Trouser seam incidence/fold branches. Six crossings are remote hand/arm skin, not trousers. Raw trouser traces bound a containing region. |
| thigh_r | 90.402695 | 0, 3, 25, 36 | 2/6 | Trouser seam branch and real open flap connectivity above a source vertex. No containing trouser region certified at this height. |
| foot_l | 9.819073 | 7, 32 | 0/4 | Two open, overlapping traces per boot. Actual crossings in component 32 bound the pivot region without any gap bridge. |
| foot_r | 9.603378 | 7, 32 | 0/4 | Same type of boot overlap. Actual crossings in component 7 bound the pivot region without any gap bridge. |

### spine_02

The two branch positions are (-9.448891, 11.545956) and (10.328231, 11.194219) in XY. Shirt component 34 contains raw edges (10746,10749), incident faces 13921/13924/13926/13928, and (20402,20404), faces 36487/36496/36498/36500. Each edge has four incident faces. Differently oriented, sometimes opposing, panels/folds meet along actual source edges.

This is reconstructed garment seam topology, not an accessory or an arm intersection. Skin components 3/36 are remote. Rejecting the entire branched shirt part discards a real bounded region around the accepted torso pivot. The raw region needs no seam link. The nearest source triangle is 13.427 cm away, and all 16 horizontal probes exit into a source surface with consistent normal orientation.

[Full section](spine_02_section.png) · [Region and junctions](spine_02_regions_and_junctions.png).

### spine_03

Two real crossings involve sleeve 1 against torso 34, faces 13849/13852 and 13850/13852, near (-20.57, 0.8). Their normal dot products are -0.994 and -0.943: nearly opposing overlapping garment traces. A third is within shirt 34, faces 37011/37021, near (20.84, 1.117). These crossings existed before reconstruction; the seam links do not create them.

The four existing v2 links are 0.066162, 0.157430, 0.354172 and 0.224770 cm. They respect the current 0.8 cm limit. Treating the combined path as one simple polygon rejects it, whereas its actual planar arrangement has a candidate bounded region containing the unchanged pivot. This is a fold/panel representation defect, not demonstrated spinal displacement. Nearest source distance is 12.371 cm; the closest surface happens to be skin patch 20 above the section plane, not a complete torso shell.

[Full section](spine_03_section.png) · [Region and junctions](spine_03_regions_and_junctions.png).

### clavicle_l and clavicle_r

Each plane has five actual crossings. Skin patch 20 and shirt 34 cross at faces 14613/14671 and 37761/37808, near the collar (approximately X -3 and +4.5, Y +3). Three further crossings are within shirt 34: faces 38085/38087, 41048/41050 and 50884/50936, at the shoulder/panel folds. Sleeve component 1 is also present.

This combines layered collar skin/clothing with overlapping shirt folds. Skin 20 has an open collar/chest trace and cannot be promoted to a complete supporting body volume. The current six shirt seam links are at most 0.505536 cm on the left and 0.497022 cm on the right. Arrangement decomposition yields candidate containing shirt regions without closing the skin opening or widening any limit. Nearest source distances are 4.674 and 4.713 cm; all horizontal first-hit normals are consistent with an interior point. Neither pivot is implicated in the surface crossings.

[Left section](clavicle_l_section.png) · [Left regions](clavicle_l_regions_and_junctions.png) · [Right section](clavicle_r_section.png) · [Right regions](clavicle_r_regions_and_junctions.png).

### upperarm_l and upperarm_r

Both planes intersect raw shirt edge (10851,10854), incident faces 14201/14205/14208. Its branch lies at approximately (-20.0, 3.1); two incident faces have normal dot -0.997. This is an overlapping/folded shirt seam with three source faces on one edge. For upperarm_l, it is on the opposite side from the accepted pivot at X +23.373. Whole-part rejection lets that remote defect block useful local support.

Both planes also cross sleeve/torso faces 14115/14117 and shirt fold pairs 41021/41030 and 50867/50872. Current v2 rejects the branched part before most seam pairs can be considered. The diagnostic local-pair experiment retains genuine source-boundary endpoints, compatible anchored garment provenance, reciprocal unique matches and the **same** 0.8 cm budget. Pair gaps are 0.065–0.342 cm on the left and 0.071–0.341 cm on the right. It permits individually valid pairs on an anchored branched part rather than requiring every terminal to be matched. The remaining dangling trace is preserved; it is not used as a region boundary.

That experiment produces a candidate containing region for each pivot. This is a narrowly justified change in the unit of certification—from entire component/path to selected region boundary—not permission to approve an ambiguous branch or arbitrary open contour. Nearest source distances are 5.304 and 5.444 cm. A production rule still needs boundary ownership/orientation checks and the regression controls below.

[Left section](upperarm_l_section.png) · [Left regions](upperarm_l_regions_and_junctions.png) · [Right section](upperarm_r_section.png) · [Right regions](upperarm_r_regions_and_junctions.png).

### thigh_l

Only trousers 25 cause the branch failure. Raw edges (724,725), (724,727) and (3955,3956) have respectively four, three and three incident faces. Incident face sets are 499/501/502/503; 501/504/11478; and 2991/3001/35983. They sit on the two trouser seam/fold regions, around XY (-15.45,5.4) and (16.42,3.83).

The six section crossings belong to hand/arm components 0/3/36, far outside the trousers. Joining them to the trouser region would be invalid. Component 25 alone has a real containing bounded region, despite small open/dangling seam-flap traces. No gap bridge is required. Nearest source distance is 8.652 cm. This is a source seam/non-manifold representation defect, not a demonstrated hip contradiction.

[Full section](thigh_l_section.png) · [Region and junctions](thigh_l_regions_and_junctions.png).

### thigh_r — real remaining uncertainty

Trouser edge (724,728), faces 502/11478/12338, has three nearly parallel incident facets (normal dots about 0.98–0.999). Edge (3955,3956), faces 2991/3001/35983, is the other branch. The accepted plane lies **0.006994 cm above vertex 724**, whose Z is 90.395701 cm. Immediately below that vertex, the extra edge incidence supports a closed outer trace. Immediately above it, the trace routes into open flap boundaries. This is an actual source patch transition, not an exact plane/vertex hit, an arithmetic tolerance problem, or a weld artifact.

The two true open trouser endpoints are (16.040882,3.443388) and (-14.782830,5.206811). Their nearest non-incident section traces are respectively 0.390294 and 0.579583 cm away, but those are **not reciprocal unique boundary-end partners**: multiple nearby facets and non-boundary junctions exist. Their being below 0.8 cm does not authorise a bridge. Pairing the two distant endpoints would be grossly invalid.

The source-only trouser region contains the projected point at offsets -2, -1, -0.2, -0.01, -0.008 and -0.007 cm. It does not enclose it at -0.006, 0, +0.006, +0.01, +0.2, +1 or +2 cm. The accepted pivot is never moved in these probes. Selecting the convenient lower slice or using a majority vote would change the rule without a valid enclosure proof.

All 16 horizontal rays still hit component 25 first with the same interior-oriented normal sign. Nearest triangle distance is 8.582 cm; trouser-only winding is -0.85898. These strongly corroborate an anatomically plausible internal hip location, but do not prove a closed 3D volume across the slit. No anatomical error is demonstrated. **A planar-region correction alone cannot legitimately clear this check.** The cause is reconstructed trouser seam/flap topology with a real open section; whether it is an intended garment opening or reconstruction defect cannot be established from unlabeled triangles alone.

[Full section](thigh_r_section.png) · [Junctions](thigh_r_regions_and_junctions.png) · [Endpoint/plane evidence](endpoint_contacts.json).

### foot_l and foot_r

Every foot plane intersects both boot components 7 and 32, with two actual self-crossings in each boot. At the left plane, component 32 crosses at faces 28858/28862 and 31067/31070. At the right plane, component 7 crosses at faces 6267/6282 and 6832/7109. These are overlapping boot-upper traces, not an accessory crossing or underlying skin layer. The separate right sole 10 lies below the plane and helps explain the 3D volume, but is not used to fabricate a 2D boundary.

Each boot has two open traces. The nearby endpoint-pair gaps are 1.921/3.007 cm for the selected left boot and 1.701/2.763 cm for the selected right boot—well above 0.8 cm. V2 also lacks a named garment anchor for artificial boot seam reconstruction. Both reasons correctly prohibit stitching those ends.

Nevertheless, the real overlap intersections already bound a simple closed region around each selected pivot. No synthetic edge, cross-boot union, sole projection or new garment anchor is needed for that candidate region. Open traces continue beyond its boundary as tails/flaps. Demanding that their entire source paths close is the wrong abstraction. The measurements establish the overlap geometry; they do not establish the maker's intended boot construction. Nearest source distances are 5.078 and 4.928 cm, with consistent interior first-hit normals in all horizontal directions.

[Left section](foot_l_section.png) · [Left regions](foot_l_regions_and_junctions.png) · [Right section](foot_r_section.png) · [Right regions](foot_r_regions_and_junctions.png).

## What is sound, and what remains unproved?

No failure demonstrates that John’s accepted anatomy is outside its local clothing/body envelope. All ten accepted pivots have 16/16 horizontal source hits; every first-hit normal has the same interior-oriented sign. Canonical geometry has reflected handedness, so consistently oriented enclosing surfaces give negative solid-angle winding. Whole-mesh winding magnitudes range from 1.013 to 1.417; nearest triangle distances are 4.67–13.43 cm. These are corroborating diagnostics, not new thresholds.

The branch/self-intersection labels are genuine properties of the reconstructed source mesh. The engineering defect is treating them as proof that **no useful local region exists**, or requiring a whole garment trace to be one simple polygon. Nine diagnostic candidates contradict that assumption. The right thigh adds a real open section that remains a support-certification problem even under the better planar representation.

No accessory component causes any of the ten failures. Collar skin/shirt layers affect the clavicle planes. Shirt fold/sleeve overlaps affect spine_03 and shoulders. Non-manifold trouser seams affect the hips. Boot flap/shell overlaps create open paths with bounded overlap regions. These input surfaces are not globally clean watertight clothing solids.

## Proposed minimal generic correction

**Propose a versioned, provenance-preserving local region certificate for body support. Do not implement it from this diagnostic face-count function.**

1. Keep original source triangle identity, orientation, component/sheet ownership and garment provenance on every section edge. Construct an arrangement with robust proper crossings, exact contacts and collinear overlaps; carry multiplicity rather than deleting it into an undirected set.
2. Identify bounded, role-local regions whose complete boundary consists of independently supported source traces or currently permitted seam links. Use outer cycles plus holes and multiple sheet-owned regions. Certify the selected boundary, not the entire connected garment graph. A remote branch or irrelevant dangling flap need not invalidate a separately valid boundary. Unresolved branch continuation, ambiguous ownership, unsupported boundaries and genuine openings remain blocking.
3. Retain the existing **0.8 cm** placement allowance and seam budget. Retain reciprocal unique matching, true source-boundary endpoints and compatible anchored garment provenance. For upper arms, allow a locally valid pair within a branched anchored part only when the final selected boundary is closed and independently certified. Do not demand closure of unused tails; do not silently delete a tail that is required to close support.
4. At actual intersecting layered surfaces, determine region interior from oriented sheet/component ownership. Global odd/even XOR across all clothing/body surfaces is wrong: two filled layers can produce even parity while the pivot is inside both. Likewise, accepting any bounded arrangement cell could certify an empty overlap/cavity. Preserve true cavities and exclude exterior cells. Common imported material alone cannot establish semantic compatibility. Boot regions require source-owned local sheet continuity; they cannot borrow the other boot or an accessory merely because it intersects.
5. If any boundary ownership/interior classification is ambiguous, fail. Keep the old fragment/path result and current v2 rejection as provenance. This would be another explicitly versioned body-policy correction; all finger, identity, signature, anatomical-kind and collision rules remain intact.

This is the smallest defensible representation change suggested for **nine** failures. It does not imply nine automatic passes: oriented boundary ownership still has to be implemented and tested. It does not solve the right thigh.

For the right thigh, investigate a **component/sheet-scoped 3D region certificate** around the accepted location and seam opening. It must establish source-supported local interior across that opening, or leave the check failed. A cut-cell/volumetric representation with explicit surface orientation and uncertainty is a defensible research direction. It must not cap an open garment arbitrarily, extrapolate from a lower slice, or treat a high winding value / a finite number of ray hits as proof. No complete minimal 3D acceptance rule is justified by this investigation; propose it separately with its proof obligations before implementation.

Generalised winding numbers offer a useful oriented field for non-manifold, intersecting and open triangle meshes, but the research distinguishes that field from guaranteed watertight classification and uses additional segmentation machinery. They are promising corroboration/segmentation inputs here, not a licence to introduce a 0.5 cutoff on an open garment. [Jacobson, Kavan and Sorkine-Hornung, 2013](https://users.cs.utah.edu/~ladislav/jacobson13robust/jacobson13robust.html). Oriented winding-based Boolean operations also support investigating separate layer ownership rather than global parity. [Jacobson, 2016](https://arxiv.org/abs/1601.07953).

## Required regression controls before a new rule

| Class | Must accept | Must reject / remain uncertain |
| --- | --- | --- |
| Provenance and scope | Compatible source garment region; one boot's own supported boundary | Wrong garment, opposite limb/boot, ring/accessory enclosure, body-to-garment stitching based only on common material, ID-specific exceptions |
| Seam links | Existing valid closed, bounded, reciprocal unique seam; local valid pair with irrelevant open tail | Open needed boundary, oversized gap, ambiguous/branched match, non-boundary endpoint-to-edge guess, excessive accumulated reconstruction |
| Region topology | Multiple overlapping owned clothing loops; certified boundary with unused non-manifold fold/tail | Arbitrary crossing transition between unrelated sheets; fake enclosed cell created by unrelated open curves; ambiguous branch continuation |
| Interior semantics | Nested filled garment layers and consistent shell orientation | Real cavity/hole, exterior point inside an AABB, concave-outline outside point, inconsistent/missing orientation |
| Boot overlaps | Real same-boot overlaps close a source-supported region despite external flap ends | Almost-touching boot flaps without actual closure; bridging 1.7–3.0 cm gaps; borrowing sole/opposite boot geometry in the section |
| Sampling stability | Exact plane/vertex/edge hits, collinear multiplicity, robust endpoint contacts; equivalent retessellation and component renumbering | Numerical snapping that closes a real gap; selecting a convenient adjacent slice across an actual open transition |
| 3D fallback | A separately justified source-scoped volume with a valid interior certificate | Open cube/slit with high winding, finite-ray false positive, arbitrary caps, orientation cancellation, remote-shell winding, lower-slice extrapolation without continuity |
| Existing safeguards | Original human signatures, review events and all anatomical-kind/finger/collision checks unchanged | Moved root, swapped track, wrong digit, identity changes, stale approvals and inter-finger collision |

The diagnostic controls deliberately demonstrate that nested boundaries need additional semantics and that an open cube can have a substantial nonzero winding at its centre. They prevent presenting these probes as a finished validator.

## Revalidation and stopping point

John can be revalidated against the same persisted proposal and genuine human-review evidence after an authorised generic policy correction and its regression controls. **No further human review is indicated by this diagnosis.** Revalidation must retain all evidence signatures; a pass is not promised. The right-thigh open section may legitimately remain blocked until a source-supported 3D certificate is justified.

No existing rule, threshold, source geometry, proposal, signature, identity, approval or gate output was changed. The current result remains **176/186**, with ten failed body-support checks and downstream authorisation false. Stop here; no Jane, skeleton, skinning, IK, retarget or bake.
