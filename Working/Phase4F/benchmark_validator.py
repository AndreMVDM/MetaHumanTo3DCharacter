"""Frozen Phase4F benchmark rules. Read-only; NumPy and standard library only.

This is a prototype evaluation API, not a benchmark runner or plugin integration.
Canonical frame: centimetres, left +X, forward Y, up +Z. Source associations
must be independently classified; a tested pivot cannot define its own support.
"""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np

import apose_review_core as core
import geometry_support_policy_v3 as shared

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / 'Documentation/Phase4F/Benchmark/frozen_policy.json'
POLICY = json.loads(POLICY_PATH.read_text(encoding='utf-8'))
VERSION = POLICY['version']
PASS, FAIL, NON_CERTIFYING = 'PASS', 'FAIL', 'NON_CERTIFYING'
EPS = POLICY['numerical_epsilon_cm']


def result(name, status, reason, *, roles=(), eligible=False, measured=None):
    if status not in (PASS, FAIL, NON_CERTIFYING):
        raise ValueError('invalid result status')
    return dict(name=name, status=status, reason=reason, review_roles=sorted(set(roles)),
                experimental_confirmation_eligible=bool(eligible), measured=measured or {})


def verify_dependencies(root=ROOT):
    for relative, expected in POLICY['dependency_sha256'].items():
        if core.file_sha(Path(root) / relative) != expected:
            raise ValueError('frozen dependency changed: ' + relative)


def verify_freeze(root=ROOT):
    """Reject edits to the frozen implementation, specifications and regressions."""
    lock = core.read(Path(root) / 'Documentation/Phase4F/Benchmark/frozen_lock.json')
    if lock['policy_version'] != VERSION or not lock['files_sha256']:
        raise ValueError('invalid benchmark freeze lock')
    for relative, expected in lock['files_sha256'].items():
        path = (Path(root) / relative).resolve()
        if not path.is_relative_to(Path(root).resolve()) or core.file_sha(path) != expected:
            raise ValueError('frozen benchmark file changed: ' + relative)


def preflight(mode, facts):
    """Facts are results of input inspection, not inference from filename."""
    if mode not in POLICY['modes']:
        return result('input_mode', FAIL, 'unknown input mode')
    required = ['humanoid', 'finite_geometry', 'canonical_frame_valid', 'rigged', 'clothed',
                'integrated_clothing', 'body_only', 'neutral_a_pose']
    if any(type(facts.get(k)) is not bool for k in required):
        return result('input_mode', FAIL, 'missing or invalid inspected input facts')
    if not all(facts[k] for k in ['humanoid', 'finite_geometry', 'canonical_frame_valid']):
        return result('input_mode', FAIL, 'invalid humanoid geometry/frame')
    if facts['body_only'] == facts['clothed'] or facts['integrated_clothing'] and not facts['clothed']:
        return result('input_mode', FAIL, 'contradictory inspected clothing facts')
    if mode == 'rigged_character':
        ok = facts['rigged']
    elif mode == 'unrigged_body_only':
        ok = (not facts['rigged'] and facts['body_only'] and
              not facts['integrated_clothing'] and facts['neutral_a_pose'])
    else:
        ok = not facts['rigged'] and facts['clothed'] and not facts['body_only']
    return result('input_mode', PASS if ok else FAIL,
                  'input matches selected mode' if ok else 'input contradicts selected mode')


def aggregate(mode, checks, confirmed_roles=(), *, coherent=False):
    """NC remains NC after acceptance; only experimental authorisation changes."""
    names = [c['name'] for c in checks]
    if not checks or len(names) != len(set(names)) or mode not in POLICY['modes']:
        raise ValueError('empty/duplicate checks or unknown mode')
    if any(c['status'] not in (PASS, FAIL, NON_CERTIFYING) for c in checks):
        raise ValueError('invalid check status')
    failures = [c for c in checks if c['status'] == FAIL]
    uncertain = [c for c in checks if c['status'] == NON_CERTIFYING]
    confirmed = set(confirmed_roles)
    accepted = bool(uncertain) and all(
        c['experimental_confirmation_eligible'] and c['review_roles'] and
        set(c['review_roles']) <= confirmed for c in uncertain)
    authorised = not failures and (not uncertain or (
        mode == 'unrigged_clothed_experimental' and coherent is True and accepted))
    status = FAIL if failures else NON_CERTIFYING if uncertain else PASS
    return dict(policy_version=VERSION, mode=mode, status=status,
                downstream_authorised=bool(authorised), geometry_certified=status == PASS,
                non_certifying_human_confirmed=bool(authorised and uncertain),
                fully_supported_anatomy_acceptance=bool(authorised and status == PASS and
                                                        mode != 'unrigged_clothed_experimental'),
                product_quality_accepted=False,
                counts={s: sum(c['status'] == s for c in checks) for s in (PASS, FAIL, NON_CERTIFYING)},
                checks=checks)


def audit_human(work, docs):
    """Verify every session event and approval; no creation, repair or invalidation."""
    work, docs = Path(work).resolve(), Path(docs).resolve()
    fit = core.read(docs / 'current_proposal.json')
    session = core.read(work / 'session.json')
    review = core.read(docs / 'human_review.json')
    if session['joints'] != fit['joints'] or session['fingers'] != fit['finger_chains']:
        raise ValueError('persisted proposal/session mismatch')
    baseline = core.file_sha(docs / 'automatic_starting_proposal.json')
    if session['baseline_sha256'] != baseline or fit['baseline_sha256'] != baseline:
        raise ValueError('baseline signature mismatch')
    if (review['proposal_sha256'] != core.file_sha(docs / 'current_proposal.json') or
            review['provenance_kind'] != 'human_anatomical_review'):
        raise ValueError('human review proposal binding mismatch')
    events = session['events']
    if [e['id'] for e in events] != list(range(1, len(events) + 1)):
        raise ValueError('invalid immutable event sequence')
    event_paths = {e['id']: work / 'InteractionEvidence' / f"event_{e['id']:05}.json" for e in events}
    if {p.name for p in (work / 'InteractionEvidence').glob('event_*.json')} != {
            p.name for p in event_paths.values()}:
        raise ValueError('immutable event inventory mismatch')
    for e in events:
        if core.read(event_paths[e['id']]) != e:
            raise ValueError('immutable event content mismatch')
    confirmed = []
    joints = {j['role']: j for j in fit['joints']}
    if len(joints) != len(fit['joints']):
        raise ValueError('duplicate joint identity')
    for name, approval in session['approvals'].items():
        if (approval['provenance'] != 'human_editor_action' or
                approval['signature'] != core.review_signature(session, name)):
            raise ValueError('stale or non-human approval')
        eid = approval['event_id']
        if type(eid) is not int or not 1 <= eid <= len(events):
            raise ValueError('invalid approval event id')
        e = events[eid - 1]
        if (e['kind'] != 'review' or e['provenance'] != 'human_editor_action' or
                e['details']['judgement'] != 'accept' or name not in e['details']['roles'] or
                e['details']['category'] != approval['category']):
            raise ValueError('approval does not refer to a genuine acceptance')
        reviewed = fit['finger_chains'][name] if name in fit['finger_chains'] else joints[name]['position_cm']
        if e['details'].get('reviewed_positions', {}).get(name) != reviewed:
            raise ValueError('acceptance event does not bind current reviewed anatomy')
        group = 'fingers' if name in fit['finger_chains'] else 'roles'
        bound = review[group][name]
        path = Path(bound['evidence_artifact']).resolve()
        if (path != event_paths[eid] or not path.is_relative_to(work) or
                core.file_sha(path) != bound['evidence_sha256'] or bound['event_id'] != eid or
                bound['anatomical_valid'] is not True or bound['category'] != approval['category']):
            raise ValueError('review evidence signature mismatch')
        if group == 'fingers':
            if bound['chain_sha256'] != core.digest(fit['finger_chains'][name]):
                raise ValueError('reviewed chain changed')
        elif (bound['position_cm'] != joints[name]['position_cm'] or
              sorted(bound['resolved_ambiguity_flags']) != sorted(joints[name]['ambiguity_flags'])):
            raise ValueError('reviewed body anatomy changed')
        # A later explicit rejection must not leave an earlier acceptance current.
        later = [x for x in events[eid:] if x['kind'] == 'review' and name in x['details']['roles']]
        if later:
            raise ValueError('approval event superseded by a later review')
        confirmed.append(name)
    if set(review['roles']) | set(review['fingers']) != set(confirmed):
        raise ValueError('orphan human review approval')
    return dict(confirmed_roles=sorted(confirmed), event_count=len(events),
                proposal_sha256=core.file_sha(docs / 'current_proposal.json'),
                session_sha256=core.file_sha(work / 'session.json'),
                review_sha256=core.file_sha(docs / 'human_review.json'))


class SourceRegions:
    """Independent source association contract, preserving original triangle IDs.

    The evidence artifact must classify region semantics independently of tested
    joints. Hash binding detects stale evidence; it cannot prove a false label.
    No automatic semantic classifier is claimed by this prototype.
    """
    def __init__(self, vertices, triangles, document, geometry_sha, evidence_sha):
        self.v = np.asarray(vertices, dtype=float)
        self.f = np.asarray(triangles)
        if (self.v.ndim != 2 or self.v.shape[1] != 3 or not np.isfinite(self.v).all() or
                self.f.ndim != 2 or self.f.shape[1] != 3 or self.f.dtype.kind not in 'iu' or
                self.f.size == 0 or self.f.min() < 0 or self.f.max() >= len(self.v)):
            raise ValueError('invalid source geometry')
        if (document.get('schema_version') != 1 or document.get('geometry_sha256') != geometry_sha or
                document.get('evidence_sha256') != evidence_sha or
                document.get('derivation') != 'independent_source_semantic_regions'):
            raise ValueError('source association binding/derivation mismatch')
        self.tri = self.v[self.f]
        self.geometry_sha = geometry_sha
        self.persisted_evidence_verified = False
        self.regions = document['regions']
        for name, r in self.regions.items():
            ids = r['triangle_ids']
            if (not isinstance(ids, list) or not ids or len(set(ids)) != len(ids) or
                    any(type(i) is not int or not 0 <= i < len(self.f) for i in ids) or
                    r['role'] != name or r['ownership'] not in ('unique', 'ambiguous')):
                raise ValueError('invalid region triangle identity or ownership')
        # Semantic aliases cannot use the same source triangle to certify both sides.
        named = [(n, set(r['triangle_ids'])) for n, r in self.regions.items() if n != 'midline']
        for i, (a, ids) in enumerate(named):
            for b, other in named[i + 1:]:
                if ids & other:
                    raise ValueError('ambiguous overlapping semantic region ownership')

    @classmethod
    def load(cls, work, docs, association_path):
        """Read independent engineering classification, never write an adapter."""
        docs = Path(docs).resolve()
        path = Path(association_path).resolve()
        if not path.is_relative_to(docs):
            raise ValueError('source association outside character documentation')
        document = core.read(path)
        evidence = Path(document['evidence_artifact']).resolve()
        if not evidence.is_relative_to(docs) or evidence == path:
            raise ValueError('source association evidence must be independent and character-local')
        geometry_path = Path(work) / 'normalised_geometry.npz'
        with np.load(geometry_path, allow_pickle=False) as geometry:
            obj = cls(geometry['vertices'], geometry['triangles'], document,
                      core.file_sha(geometry_path), core.file_sha(evidence))
        obj.persisted_evidence_verified = True
        return obj

    def region(self, name):
        entry = self.regions.get(name)
        if entry is None or entry['ownership'] != 'unique':
            return None
        return self.tri[entry['triangle_ids']]

    def centre(self, name):
        tri = self.region(name)
        if tri is None:
            return None
        area = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) / 2
        if area.sum() <= EPS ** 2:
            return None
        return np.average(tri.mean(axis=1), axis=0, weights=area)


def _point(p):
    p = np.asarray(p, dtype=float)
    if p.shape != (3,) or not np.isfinite(p).all():
        raise ValueError('finite canonical point required')
    return p


def pose_checks(joints, source):
    """Compare paired points with independent area-weighted source pose cues.

    True left/right ordering is always checked. Same-height midline is derived
    from source central-region triangles intersecting that height (never from
    the evaluated joints). Missing/ambiguous intersections cannot certify side.
    Symmetry uses source-conditioned mirrored displacement with unchanged 6cm cap.
    """
    pairs = sorted(n[:-2] for n in joints if n.endswith('_l') and n[:-2] + '_r' in joints)
    if not pairs:
        return [result(n, FAIL, 'no bilateral anatomical pairs') for n in
                ('left_right_not_crossed', 'bilateral_body_consistency')]
    roles = [stem + '_' + side for stem in pairs for side in ('l', 'r')]
    side_fail, side_unknown, sym_fail, sym_unknown = [], [], [], []
    measures = {}
    for stem in pairs:
        a, b = [_point(joints[stem + '_' + s]) for s in ('l', 'r')]
        if a[0] <= b[0] + EPS:
            side_fail.append(stem + ':crossed_or_collapsed_pair')
        cue = [source.centre(stem + '_' + s) if source else None for s in ('l', 'r')]
        for side, p in zip(('l', 'r'), (a, b)):
            tri = source.region('midline') if source else None
            # Intersect independently classified central-surface triangles with
            # exact role height. A single connected X interval is required.
            intervals = []
            if tri is not None:
                for t in tri:
                    hits = []
                    for v, w in zip(t, np.roll(t, -1, axis=0)):
                        if abs(v[2] - p[2]) <= EPS:
                            hits.append(v[0])
                        if (v[2] < p[2] - EPS and w[2] > p[2] + EPS or
                                w[2] < p[2] - EPS and v[2] > p[2] + EPS):
                            hits.append(v[0] + (w[0] - v[0]) * (p[2] - v[2]) / (w[2] - v[2]))
                    if len(hits) >= 2:
                        intervals.append((min(hits), max(hits)))
            merged = []
            for lo, hi in sorted(intervals):
                if merged and lo <= merged[-1][1] + EPS:
                    merged[-1] = (merged[-1][0], max(hi, merged[-1][1]))
                else:
                    merged.append((lo, hi))
            if len(merged) != 1:
                side_unknown.append(stem + '_' + side)
            else:
                mid = sum(merged[0]) / 2
                signed = (1 if side == 'l' else -1) * (p[0] - mid)
                measures[stem + '_' + side] = {'source_midline_x_cm': mid, 'signed_cm': signed}
                if signed <= EPS:
                    side_fail.append(stem + '_' + side + ':wrong_source_side')
        if any(x is None for x in cue):
            sym_unknown.extend([stem + '_l', stem + '_r'])
        else:
            if cue[0][0] <= cue[1][0] + EPS:
                sym_unknown.extend([stem + '_l', stem + '_r'])
            else:
                mirror = np.array([-1., 1., 1.])
                residual = float(np.linalg.norm((a * mirror - b) - (cue[0] * mirror - cue[1])))
                measures[stem] = {'source_conditioned_mirror_residual_cm': residual}
                if residual > POLICY['pose_residual_limit_cm']:
                    sym_fail.append(stem)
    def conclude(name, failures, unknown):
        return result(name, FAIL if failures else NON_CERTIFYING if unknown else PASS,
                      'source-pose contradiction' if failures else 'source association incomplete' if unknown
                      else 'source-conditioned anatomical relations certified', roles=roles,
                      eligible=not failures, measured=dict(details=measures, failures=failures,
                                                          unresolved_source_roles=unknown))
    return [conclude('left_right_not_crossed', side_fail, side_unknown),
            conclude('bilateral_body_consistency', sym_fail, sym_unknown)]


def sole_check(source, ground_z_cm, roles=('foot_l', 'foot_r', 'ball_l', 'ball_r'), *, orientation=1.):
    """Positive 2D downward source footprint in canonical 0.5cm ground band.

    Clip actual source triangles; no vertex-density threshold or contact/balance
    claim. Empty, raised, zero-area, upward/vertical-only regions fail. Missing
    source association remains NC. Ground is independently supplied source frame.
    """
    if isinstance(ground_z_cm, bool) or not np.isfinite(ground_z_cm):
        raise ValueError('finite source ground required')
    if isinstance(orientation, bool) or orientation not in (-1., 1.):
        raise ValueError('verified source orientation required')
    details, unknown, failures = {}, [], []
    top = float(ground_z_cm) + POLICY['sole_band_canonical_cm']
    for name in ('foot_l', 'foot_r'):
        tri = source.region(name) if source else None
        if tri is None:
            unknown.append(name)
            continue
        area = 0.
        for t in tri:
            normal = np.cross(t[1] - t[0], t[2] - t[0])
            if normal[2] * orientation >= -EPS ** 2:
                continue
            clipped = []
            for a, b in zip(t, np.roll(t, -1, axis=0)):
                inside_a, inside_b = a[2] <= top, b[2] <= top
                if inside_a:
                    clipped.append(a)
                if inside_a != inside_b:
                    clipped.append(a + (b - a) * ((top - a[2]) / (b[2] - a[2])))
            for k in range(1, len(clipped) - 1):
                c = np.cross(clipped[k] - clipped[0], clipped[k + 1] - clipped[0])
                area += abs(float(c[2])) / 2
        # Orientation and a positive projected triangle area give two independent
        # physical axes; duplicating points/lines cannot create this footprint.
        details[name] = dict(min_z_cm=float(tri[:, :, 2].min()),
                             downward_projected_triangle_area_cm2=area,
                             area_is_not_union_contact_area=True)
        if tri[:, :, 2].min() < ground_z_cm - EPS:
            failures.append(name + ':source_below_ground_frame')
        elif tri[:, :, 2].min() > top + EPS:
            failures.append(name + ':raised_above_ground_band')
        elif area <= EPS ** 2:
            failures.append(name + ':missing_or_degenerate_downward_footprint')
    return result('paired_sole_up_evidence', FAIL if failures else NON_CERTIFYING if unknown else PASS,
                  'sole contradiction' if failures else 'independent foot ownership missing' if unknown
                  else 'paired nondegenerate source sole/up support', roles=roles, eligible=not failures,
                  measured=dict(details=details, failures=failures, unresolved_source_roles=unknown,
                                band_cm=POLICY['sole_band_canonical_cm']))


def classify_geometry(check, fit, mesh):
    """Only explicitly recognised topology uncertainty is human-confirmable.

    A source bounding box is used solely as a necessary negative test; it never
    certifies any positive support. Unknown errors/false hard checks fail closed.
    """
    name = check['name']
    if check['pass'] is True:
        return result(name, PASS, 'unchanged shared geometry certificate')
    failures = check.get('measured', {}).get('failures', [])
    if name.startswith('surface_envelope_'):
        role = name.removeprefix('surface_envelope_')
        p = _point(next(j['position_cm'] for j in fit['joints'] if j['role'] == role))
        allowance = POLICY['body_placement_allowance_cm']
        if np.any(p < mesh.v.min(axis=0) - allowance) or np.any(p > mesh.v.max(axis=0) + allowance):
            return result(name, FAIL, 'accepted point demonstrably outside source extents', roles=[role])
        if failures == ['no_owned_closed_oriented_region']:
            if _closed_region_contradiction(check['measured'], p):
                return result(name, FAIL, 'outside independently closed owned regions or in certified cavity',
                              roles=[role], measured=check['measured'])
            # This predicate reports a certification absence, not an exterior
            # proof. Do not convert arbitrary absent provenance into acceptance.
            return result(name, NON_CERTIFYING, 'owned source region not certifiable',
                          roles=[role], eligible=True, measured=check['measured'])
    elif name.startswith('finger_surface_'):
        role = name.removeprefix('finger_surface_')
        topology = {'open_or_ambiguous_named_track_section'}
        reasons = {f.split(':')[-1] for f in failures}
        if reasons and reasons <= topology:
            return result(name, NON_CERTIFYING, 'named source finger topology not certifiable',
                          roles=[role], eligible=True, measured=check['measured'])
    return result(name, FAIL, 'shared geometry contradiction or invalid evidence',
                  measured=check.get('measured'))


def _closed_region_contradiction(measured, p):
    """Negative certificate only when every possible bound section is closed.

    Open/branched alternatives prevent an exterior proof. Actual oriented source
    loops and explicit holes are used; neither bbox nor ray count is sufficient.
    Ambiguous cavity ownership remains NC, never a claimed contradiction.
    """
    body = shared.body
    binding = measured.get('role_owner_binding') or {}
    records = measured.get('source_section_records', [])
    owners = {r['owner'] for r in records}
    assessed = []
    for owner in owners:
        source = [r for r in records if r['owner'] == owner]
        groups = {r['garment'] for r in source if r.get('garment') is not None}
        components = {r['component'] for r in source if r.get('component') is not None}
        if not (groups and groups <= set(binding.get('garment_groups', [])) or
                not groups and components and components <= set(binding.get('source_components', []))):
            continue
        if any(r.get('provenance') is None or r.get('synthetic') for r in source):
            return False  # Negative proof does not bridge even a bounded seam.
        source = [dict(r, a=np.asarray(r['a']), b=np.asarray(r['b'])) for r in source]
        points, edges, _ = body.arrangement(source)
        cycles, detail = body.closed_cycles(points, edges, source)
        if (detail['ambiguous_coincident_edges'] or detail['unused_noncycle_edges'] or
                detail['rejected_boundaries'] or not cycles):
            return False
        positive = [c for c in cycles if c['area_cm2'] > 0]
        negative = [c for c in cycles if c['area_cm2'] < 0]
        if not positive:
            return False
        holes = {}
        for i, h in enumerate(negative):
            candidates = [c for c in positive if all(shared.v2.polygon_contains(c['polygon'], q)[0]
                                                      for q in h['polygon'])]
            if not candidates:
                return False
            holes[i] = min(candidates, key=lambda c: c['area_cm2'])
        for c in positive:
            inside = shared.v2.polygon_contains(c['polygon'], p, POLICY['body_placement_allowance_cm'])[0]
            in_hole = any(parent is c and shared.v2.polygon_contains(negative[i]['polygon'], p)[0]
                          for i, parent in holes.items())
            if inside and not in_hole:
                return False
        assessed.append(owner)
    return bool(assessed)


def verified_source_ground(docs, migration):
    """Ground is canonical frame origin Z=0, not a selectable validation plane.

    The retained v3 transform proof binds this frame to the original geometry.
    Input inspection must independently validate the physical source up/ground.
    """
    provenance = migration.get('source_provenance') or {}
    determinant = provenance.get('source_orientation_determinant')
    if (migration.get('source_error') or not provenance.get('coordinate_frame_sha256') or
            isinstance(determinant, bool) or not isinstance(determinant, (int, float)) or
            not np.isfinite(determinant) or abs(abs(determinant) - 1.) > EPS or
            core.file_sha(Path(docs) / 'coordinate_frame.json') != provenance['coordinate_frame_sha256']):
        raise ValueError('source ground/frame certification invalid')
    return 0.


def evaluate_assisted(base_checks, work, docs, mode, facts, *, source_regions=None):
    """Consume unchanged base checks, persisted inputs and shared v2/v3 policy.

    Caller computes the established base/anatomical checks read-only. This API
    enforces their complete frozen schema and re-evaluates shared geometry, then
    replaces ONLY the three explicitly versioned numeric screens. No launcher,
    character metadata, AI service or persistent output is loaded or written.
    """
    if mode == 'rigged_character':
        raise ValueError('rigged inputs use evaluate_rigged; no skeleton reconstruction')
    verify_dependencies()
    expected = {c['name']: c['kind'] for c in POLICY['assisted_base_schema']}
    if (len(base_checks) != len(expected) or
            {c['name']: c['kind'] for c in base_checks} != expected or
            any(type(c.get('pass')) is not bool for c in base_checks)):
        raise ValueError('incomplete or invalid frozen base check schema')
    verify_freeze()
    human = audit_human(work, docs)
    fit = core.read(Path(docs) / 'current_proposal.json')
    checks = copy.deepcopy(base_checks)
    migration = shared.apply_policy(checks, fit, work, docs, core)
    mesh, provenance = shared.v2.load_source(work, docs, fit)
    if source_regions is not None:
        if (not source_regions.persisted_evidence_verified or
                source_regions.geometry_sha != fit['input_geometry_sha256'] or
                not np.array_equal(source_regions.v, mesh.v) or
                not np.array_equal(source_regions.f, mesh.f)):
            raise ValueError('source semantic regions do not match persisted source')
    joints = {j['role']: j['position_cm'] for j in fit['joints']}
    replacements = {c['name']: c for c in pose_checks(joints, source_regions)}
    replacements['paired_sole_up_evidence'] = sole_check(source_regions, verified_source_ground(docs, migration),
        orientation=float(np.sign(migration['source_provenance']['source_orientation_determinant'])))
    outputs = [preflight(mode, facts)]
    for c in checks:
        if c['name'] in replacements:
            outputs.append(replacements[c['name']])
        elif c['name'].startswith(('surface_envelope_', 'finger_surface_')):
            outputs.append(classify_geometry(c, fit, mesh))
        else:
            # Retain all identity, chain, length, uniqueness, hierarchy and
            # collision screens. An unrecognised false check can never be NC.
            outputs.append(result(c['name'], PASS if c['pass'] else FAIL,
                                  'unchanged base/anatomical check', measured=c.get('measured')))
    answer = aggregate(mode, outputs, human['confirmed_roles'], coherent=all(
        c['status'] != FAIL for c in outputs))
    answer.update(human_evidence=human, source_provenance=provenance,
                  legacy_base_checks=copy.deepcopy(base_checks), shared_geometry_checks=checks,
                  migration=migration)
    return answer


def evaluate_rigged(checks, facts):
    """Preserve existing skeleton. Requires real rig inspection checks upstream."""
    expected = set(POLICY['rigged_required_checks'])
    if (len(checks) != len(expected) or {c['name'] for c in checks} != expected or
            any(type(c.get('pass')) is not bool for c in checks)):
        raise ValueError('incomplete rigged inspection schema')
    verify_dependencies()
    verify_freeze()
    outputs = [preflight('rigged_character', facts)] + [
        result(c['name'], PASS if c['pass'] else FAIL, 'existing rig inspection', measured=c.get('measured'))
        for c in checks]
    answer = aggregate('rigged_character', outputs)
    answer['skeleton_action'] = 'preserve_existing'
    return answer
