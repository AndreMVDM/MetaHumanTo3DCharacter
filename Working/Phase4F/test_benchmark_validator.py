"""Synthetic frozen-rule controls. Never imports or processes benchmark assets."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

import benchmark_validator as b
from test_geometry_support_policy import extrude


def regions(parts, ambiguous=()):
    vertices, faces, entries = [], [], {}
    for name, triangles in parts.items():
        ids = []
        for tri in triangles:
            first = len(vertices)
            vertices.extend(tri)
            ids.append(len(faces))
            faces.append([first, first + 1, first + 2])
        entries[name] = dict(role=name, triangle_ids=ids,
                             ownership='ambiguous' if name in ambiguous else 'unique')
    doc = dict(schema_version=1, geometry_sha256='geometry', evidence_sha256='evidence',
               derivation='independent_source_semantic_regions', regions=entries)
    return b.SourceRegions(vertices, faces, doc, 'geometry', 'evidence')


def patch_at(x, y=0, z=5):
    return [[[x-1,y-1,z], [x+1,y-1,z], [x+1,y+1,z]],
            [[x-1,y-1,z], [x+1,y+1,z], [x-1,y+1,z]]]


def pose_source(left_y=0, right_y=0, midx=0):
    return regions(dict(midline=[[[midx-2,0,0], [midx+2,0,0], [midx+2,0,10]],
                                 [[midx-2,0,0], [midx+2,0,10], [midx-2,0,10]]],
                        hand_l=patch_at(15+midx,left_y), hand_r=patch_at(-15+midx,right_y)))


def sole_patch(x, z=0):
    return [[[x-2,-4,z], [x+2,4,z], [x+2,-4,z]],
            [[x-2,-4,z], [x-2,4,z], [x+2,4,z]]]


def subdivide(triangles):
    out=[]
    for t in np.asarray(triangles):
        a,c,d=t;ac=(a+c)/2;cd=(c+d)/2;da=(d+a)/2
        out.extend([[a,ac,da],[ac,c,cd],[da,cd,d],[ac,cd,da]])
    return np.asarray(out).tolist()


def facts(rigged=False, body=True, integrated=False, a_pose=True):
    return dict(humanoid=True, finite_geometry=True, canonical_frame_valid=True,
                rigged=rigged, body_only=body, clothed=not body, integrated_clothing=integrated, neutral_a_pose=a_pose)


def human_fixture(root):
    work=root/'work';docs=root/'docs';work.mkdir();docs.mkdir();(work/'InteractionEvidence').mkdir()
    joint=dict(role='pelvis', position_cm=[0.,0.,2.], ambiguity_flags=[],status='ambiguous')
    baseline=dict(joints=[joint]);(docs/'automatic_starting_proposal.json').write_text(json.dumps(baseline))
    baseline_sha=b.core.file_sha(docs/'automatic_starting_proposal.json')
    event=dict(id=1,utc_epoch=1.,kind='review',provenance='human_editor_action',
               details=dict(roles=['pelvis'],judgement='accept',category='anatomical_front_side_review',
                            reviewed_positions={'pelvis':joint['position_cm']}))
    eventpath=work/'InteractionEvidence/event_00001.json';eventpath.write_text(json.dumps(event))
    approval=dict(signature=b.core.signature(joint),category=event['details']['category'],
                  event_id=1,provenance='human_editor_action')
    session=dict(joints=[joint],fingers={},events=[event],approvals=dict(pelvis=approval),baseline_sha256=baseline_sha)
    fit=dict(joints=[joint],finger_chains={},baseline_sha256=baseline_sha)
    (work/'session.json').write_text(json.dumps(session));(docs/'current_proposal.json').write_text(json.dumps(fit))
    bound=dict(anatomical_valid=True,evidence_artifact=str(eventpath.resolve()),
               evidence_sha256=b.core.file_sha(eventpath),event_id=1,category=approval['category'],
               position_cm=joint['position_cm'],resolved_ambiguity_flags=[])
    review=dict(proposal_sha256=b.core.file_sha(docs/'current_proposal.json'),
                provenance_kind='human_anatomical_review',roles=dict(pelvis=bound),fingers={})
    (docs/'human_review.json').write_text(json.dumps(review))
    return work,docs


class PoseControls(unittest.TestCase):
    def test_symmetric_source(self):
        self.assertTrue(all(c['status']==b.PASS for c in b.pose_checks(
            dict(hand_l=[15,0,5],hand_r=[-15,0,5]),pose_source())))

    def test_real_source_asymmetry(self):
        self.assertTrue(all(c['status']==b.PASS for c in b.pose_checks(
            dict(hand_l=[15,14,5],hand_r=[-15,-7,5]),pose_source(14,-7))))

    def test_true_crossing_even_without_source(self):
        self.assertEqual(b.pose_checks(dict(hand_l=[-15,0,5],hand_r=[15,0,5]),None)[0]['status'],b.FAIL)

    def test_both_points_wrong_source_side(self):
        self.assertEqual(b.pose_checks(dict(hand_l=[20,0,5],hand_r=[10,0,5]),pose_source())[0]['status'],b.FAIL)

    def test_wrong_symmetry_relative_to_source(self):
        self.assertEqual(b.pose_checks(dict(hand_l=[15,21,5],hand_r=[-15,0,5]),pose_source())[1]['status'],b.FAIL)

    def test_existing_six_cm_boundary(self):
        self.assertEqual(b.pose_checks(dict(hand_l=[15,6,5],hand_r=[-15,0,5]),pose_source())[1]['status'],b.PASS)
        self.assertEqual(b.pose_checks(dict(hand_l=[15,6.01,5],hand_r=[-15,0,5]),pose_source())[1]['status'],b.FAIL)

    def test_origin_translation_invariant(self):
        self.assertTrue(all(c['status']==b.PASS for c in b.pose_checks(
            dict(hand_l=[65,0,5],hand_r=[35,0,5]),pose_source(midx=50))))

    def test_no_source_not_self_certified(self):
        self.assertTrue(all(c['status']==b.NON_CERTIFYING for c in b.pose_checks(
            dict(hand_l=[15,0,5],hand_r=[-15,0,5]),None)))

    def test_exact_height_vertex_contact(self):
        self.assertEqual(b.pose_checks(dict(hand_l=[15,0,0],hand_r=[-15,0,0]),pose_source())[0]['status'],b.PASS)

    def test_disconnected_source_midline(self):
        s=pose_source();s.regions['midline']['triangle_ids']=[2,3,4,5]
        self.assertEqual(b.pose_checks(dict(hand_l=[15,0,5],hand_r=[-15,0,5]),s)[0]['status'],b.NON_CERTIFYING)

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):b.pose_checks(dict(hand_l=[float('nan'),0,5],hand_r=[-15,0,5]),pose_source())

    def test_retessellation_area_cue(self):
        s=regions(dict(midline=subdivide(pose_source().region('midline')),hand_l=subdivide(patch_at(15,14)),
                       hand_r=subdivide(patch_at(-15,-7))))
        self.assertTrue(all(c['status']==b.PASS for c in b.pose_checks(
            dict(hand_l=[15,14,5],hand_r=[-15,-7,5]),s)))


class SoleControls(unittest.TestCase):
    def test_positive_paired_source(self):
        self.assertEqual(b.sole_check(regions(dict(foot_l=sole_patch(10),foot_r=sole_patch(-10))),0)['status'],b.PASS)

    def test_density_retessellation_invariant(self):
        left,right=sole_patch(10),sole_patch(-10)
        first=b.sole_check(regions(dict(foot_l=left,foot_r=right)),0)
        for _ in range(4):
            left,right=subdivide(left),subdivide(right)
            c=b.sole_check(regions(dict(foot_l=left,foot_r=right)),0)
            self.assertEqual(c['status'],first['status'])
            self.assertAlmostEqual(c['measured']['details']['foot_l']['downward_projected_triangle_area_cm2'],32.)

    def test_duplicate_vertices_do_not_change(self):
        # Each triangle uses distinct vertices already; no vertex-count gate.
        self.assertEqual(b.sole_check(regions(dict(foot_l=sole_patch(10)*25,foot_r=sole_patch(-10))),0)['status'],b.PASS)

    def test_one_raised_foot(self):
        self.assertEqual(b.sole_check(regions(dict(foot_l=sole_patch(10,.6),foot_r=sole_patch(-10))),0)['status'],b.FAIL)

    def test_both_raised(self):
        self.assertEqual(b.sole_check(regions(dict(foot_l=sole_patch(10,4),foot_r=sole_patch(-10,4))),0)['status'],b.FAIL)

    def test_band_boundary(self):
        self.assertEqual(b.sole_check(regions(dict(foot_l=sole_patch(10,.5),foot_r=sole_patch(-10,.5))),0)['status'],b.PASS)

    def test_point_only_fails(self):
        s=regions(dict(foot_l=[[[10,0,0]]*3],foot_r=sole_patch(-10)))
        self.assertEqual(b.sole_check(s,0)['status'],b.FAIL)

    def test_line_only_fails(self):
        s=regions(dict(foot_l=[[[10,0,0],[10,1,0],[10,2,0]]],foot_r=sole_patch(-10)))
        self.assertEqual(b.sole_check(s,0)['status'],b.FAIL)

    def test_upward_surface_fails(self):
        s=regions(dict(foot_l=[list(reversed(t)) for t in sole_patch(10)],foot_r=sole_patch(-10)))
        self.assertEqual(b.sole_check(s,0)['status'],b.FAIL)

    def test_vertical_surface_fails(self):
        s=regions(dict(foot_l=[[[10,0,0],[10,1,0],[10,1,2]]],foot_r=sole_patch(-10)))
        self.assertEqual(b.sole_check(s,0)['status'],b.FAIL)

    def test_missing_ownership_is_not_certificate(self):
        self.assertEqual(b.sole_check(regions(dict(foot_l=sole_patch(10))),0)['status'],b.NON_CERTIFYING)

    def test_unowned_ground_debris_cannot_support_raised_foot(self):
        s=regions(dict(foot_l=sole_patch(10,5),foot_r=sole_patch(-10),debris=sole_patch(10)))
        self.assertEqual(b.sole_check(s,0)['status'],b.FAIL)

    def test_below_source_ground_frame_fails(self):
        s=regions(dict(foot_l=sole_patch(10,-1),foot_r=sole_patch(-10)))
        self.assertEqual(b.sole_check(s,0)['status'],b.FAIL)

    def test_clipping_sloped_surface(self):
        left=sole_patch(10);left[0][1][2]=1.;left[1][2][2]=1.
        c=b.sole_check(regions(dict(foot_l=left,foot_r=sole_patch(-10))),0)
        self.assertEqual(c['status'],b.PASS)
        self.assertLess(c['measured']['details']['foot_l']['downward_projected_triangle_area_cm2'],32.)

    def test_reflected_source_frame_orientation(self):
        # Reflect canonical geometry while preserving original triangle indices.
        left=np.array(sole_patch(10));right=np.array(sole_patch(-10))
        left[:,:,0]*=-1;right[:,:,0]*=-1
        source=regions(dict(foot_l=left.tolist(),foot_r=right.tolist()))
        self.assertEqual(b.sole_check(source,0,orientation=-1.)['status'],b.PASS)
        self.assertEqual(b.sole_check(source,0,orientation=1.)['status'],b.FAIL)

    def test_invalid_orientation_rejected(self):
        with self.assertRaises(ValueError):b.sole_check(None,0,orientation=0.)


class ModeAndGateControls(unittest.TestCase):
    def test_three_modes(self):
        for mode,f in [('rigged_character',facts(True)),('unrigged_body_only',facts()),
                       ('unrigged_clothed_experimental',facts(body=False,integrated=True))]:
            self.assertEqual(b.preflight(mode,f)['status'],b.PASS)

    def test_integrated_clothing_cannot_claim_body_mode(self):
        self.assertEqual(b.preflight('unrigged_body_only',facts(integrated=True))['status'],b.FAIL)

    def test_non_neutral_body_pose_fails_preflight(self):
        self.assertEqual(b.preflight('unrigged_body_only',facts(a_pose=False))['status'],b.FAIL)

    def test_unknown_or_missing_input_facts(self):
        self.assertEqual(b.preflight('unknown',facts())['status'],b.FAIL)
        self.assertEqual(b.preflight('unrigged_body_only',{})['status'],b.FAIL)

    def test_experimental_requires_explicit_clothing_fact(self):
        f=facts(body=False);f.pop('clothed')
        self.assertEqual(b.preflight('unrigged_clothed_experimental',f)['status'],b.FAIL)
        f['clothed']=False
        self.assertEqual(b.preflight('unrigged_clothed_experimental',f)['status'],b.FAIL)

    def test_separately_clothed_is_experimental(self):
        self.assertEqual(b.preflight('unrigged_clothed_experimental',facts(body=False))['status'],b.PASS)

    def test_ground_not_caller_selectable(self):
        with self.assertRaises(TypeError):
            b.evaluate_assisted([],'.','.', 'unrigged_body_only',facts(),ground_z_cm=5.)

    def test_bound_ground_stale_frame_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            frame=Path(d)/'coordinate_frame.json';frame.write_text('{}')
            migration={'source_provenance':{'coordinate_frame_sha256':b.core.file_sha(frame),'source_orientation_determinant':1.}}
            self.assertEqual(b.verified_source_ground(d,migration),0.)
            frame.write_text('{"changed":true}')
            with self.assertRaises(ValueError):b.verified_source_ground(d,migration)

    def test_raised_sole_cannot_move_ground_to_pass(self):
        with tempfile.TemporaryDirectory() as d:
            frame=Path(d)/'coordinate_frame.json';frame.write_text('{}')
            migration={'source_provenance':{'coordinate_frame_sha256':b.core.file_sha(frame),'source_orientation_determinant':1.}}
            ground=b.verified_source_ground(d,migration)
            s=regions(dict(foot_l=sole_patch(10,5),foot_r=sole_patch(-10,5)))
            self.assertEqual(b.sole_check(s,ground)['status'],b.FAIL)

    def test_rigged_existing_skeleton_preserved(self):
        checks=[dict(name=n,pass_=True) for n in b.POLICY['rigged_required_checks']]
        for c in checks:c['pass']=c.pop('pass_')
        with patch.object(b,'verify_freeze') as frozen:
            answer=b.evaluate_rigged(checks,facts(True,False,True))
            frozen.assert_called_once()
        self.assertTrue(answer['downstream_authorised']);self.assertEqual(answer['skeleton_action'],'preserve_existing')

    def test_missing_rig_check_rejected(self):
        with self.assertRaises(ValueError):b.evaluate_rigged([],facts(True))

    def test_body_non_certifying_blocks(self):
        c=b.result('body',b.NON_CERTIFYING,'open',roles=['pelvis'],eligible=True)
        self.assertFalse(b.aggregate('unrigged_body_only',[c],['pelvis'],coherent=True)['downstream_authorised'])

    def test_experimental_human_confirmed_stays_non_certifying(self):
        c=b.result('body',b.NON_CERTIFYING,'open',roles=['pelvis'],eligible=True)
        a=b.aggregate('unrigged_clothed_experimental',[c],['pelvis'],coherent=True)
        self.assertTrue(a['downstream_authorised']);self.assertEqual(a['status'],b.NON_CERTIFYING)
        self.assertFalse(a['geometry_certified']);self.assertFalse(a['fully_supported_anatomy_acceptance'])

    def test_no_review_never_authorises_uncertainty(self):
        c=b.result('body',b.NON_CERTIFYING,'open',roles=['pelvis'],eligible=True)
        self.assertFalse(b.aggregate('unrigged_clothed_experimental',[c],[],coherent=True)['downstream_authorised'])

    def test_no_coherence_never_authorises_uncertainty(self):
        c=b.result('body',b.NON_CERTIFYING,'open',roles=['pelvis'],eligible=True)
        self.assertFalse(b.aggregate('unrigged_clothed_experimental',[c],['pelvis'])['downstream_authorised'])

    def test_human_never_overrides_failure(self):
        for reason in ['wrong_side','hierarchy','crossing','wrong_digit','off_source','collision']:
            c=b.result(reason,b.FAIL,reason,roles=['pelvis'],eligible=True)
            self.assertFalse(b.aggregate('unrigged_clothed_experimental',[c],['pelvis'],coherent=True)['downstream_authorised'])

    def test_unknown_uncertainty_not_eligible(self):
        c=b.result('unknown',b.NON_CERTIFYING,'unknown',roles=['pelvis'])
        self.assertFalse(b.aggregate('unrigged_clothed_experimental',[c],['pelvis'],coherent=True)['downstream_authorised'])

    def test_positive_gate_does_not_claim_product_quality(self):
        a=b.aggregate('unrigged_body_only',[b.result('good',b.PASS,'certificate')])
        self.assertTrue(a['downstream_authorised']);self.assertFalse(a['product_quality_accepted'])

    def test_duplicate_checks_rejected(self):
        c=b.result('good',b.PASS,'certificate')
        with self.assertRaises(ValueError):b.aggregate('unrigged_body_only',[c,c])

    def test_incomplete_assisted_schema_rejected(self):
        with self.assertRaises(ValueError):b.evaluate_assisted([],'.','.', 'unrigged_body_only',facts())

    def test_dependency_change_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):b.verify_dependencies(Path(d))

    def test_freeze_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);folder=root/'Documentation/Phase4F/Benchmark';folder.mkdir(parents=True)
            source=root/'source.py';source.write_text('original')
            lock=dict(policy_version=b.VERSION,files_sha256={'source.py':b.core.file_sha(source)})
            (folder/'frozen_lock.json').write_text(json.dumps(lock))
            b.verify_freeze(root);source.write_text('changed')
            with self.assertRaises(ValueError):b.verify_freeze(root)

    def test_deterministic_results(self):
        c=b.result('body',b.NON_CERTIFYING,'open',roles=['pelvis'],eligible=True)
        self.assertEqual(b.aggregate('unrigged_clothed_experimental',[c],['pelvis'],coherent=True),
                         b.aggregate('unrigged_clothed_experimental',[c],['pelvis'],coherent=True))


class GeometryClassificationControls(unittest.TestCase):
    def measure(self,mesh,p=(0,0,2)):
        passed,m=b.shared.body.evaluate(mesh,np.array(p,dtype=float),1.,b.shared.POLICY,
                                       dict(role='pelvis',garment_groups=['shirt'],source_components=[]))
        fit=dict(joints=[dict(role='pelvis',position_cm=list(p))])
        return b.classify_geometry(dict(name='surface_envelope_pelvis',pass_=passed,measured=m,
                                       **{'pass':passed}),fit,mesh)

    def test_positive_source_certificate(self):
        self.assertEqual(self.measure(extrude([[[-3,-2],[3,-2],[3,2],[-3,2]]],closed=True))['status'],b.PASS)

    def test_open_region_non_certifying(self):
        self.assertEqual(self.measure(extrude([[[-3,-2],[3,-2],[3,2]]]))['status'],b.NON_CERTIFYING)

    def test_off_source_rejected_not_human_confirmable(self):
        self.assertEqual(self.measure(extrude([[[-3,-2],[3,-2],[3,2],[-3,2]]],closed=True),(50,0,2))['status'],b.FAIL)

    def test_exterior_within_whole_character_box_fails(self):
        mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2]],[[30,30],[35,30],[35,35],[30,35]]],closed=True)
        self.assertEqual(self.measure(mesh,(10,0,2))['status'],b.FAIL)

    def test_certified_hole_fails(self):
        mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2]],[[-1,-1],[-1,1],[1,1],[1,-1]]],closed=True)
        mesh.components[:]=0;mesh.provenance={0:('source','cloth')};mesh.garments={0:'shirt'}
        self.assertEqual(self.measure(mesh)['status'],b.FAIL)

    def test_open_alternative_prevents_exterior_claim(self):
        mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2]],[[30,30],[35,30],[35,35]]],closed=False)
        # Close the first source path only, leaving the second genuinely open.
        mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2],[-3,-2]],[[30,30],[35,30],[35,35]]],
                     groups={0:'shirt',1:'shirt'})
        self.assertEqual(self.measure(mesh,(10,0,2))['status'],b.NON_CERTIFYING)

    def test_finger_exterior_never_non_certifying(self):
        c=dict(name='finger_surface_index_l',measured=dict(failures=['phalange_1:outside_named_finger_polygon']),**{'pass':False})
        self.assertEqual(b.classify_geometry(c,{},None)['status'],b.FAIL)

    def test_finger_only_open_named_track_non_certifying(self):
        c=dict(name='finger_surface_index_l',measured=dict(failures=['phalange_1:open_or_ambiguous_named_track_section']),**{'pass':False})
        self.assertEqual(b.classify_geometry(c,{},None)['status'],b.NON_CERTIFYING)

    def test_missing_track_is_fail_not_identity_override(self):
        c=dict(name='finger_surface_index_l',measured=dict(failures=['missing_or_ambiguous_source_track']),**{'pass':False})
        self.assertEqual(b.classify_geometry(c,{},None)['status'],b.FAIL)


class IntegrityControls(unittest.TestCase):
    def test_real_shared_v3_frame_migration_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);work,docs=human_fixture(root)
            mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2]]],closed=True)
            np.savez(work/'normalised_geometry.npz',vertices=mesh.v,triangles=mesh.f,weld_component=mesh.components)
            np.savez(work/'source_geometry.npz',vertices=mesh.v,triangles=mesh.f,object_triangle_ids=np.zeros(len(mesh.f),dtype=int))
            (docs/'geometry_summary.json').write_text(json.dumps({'objects':[dict(name='synthetic_source',
                materials=['cloth'],polygon_material_counts={'0':len(mesh.f)})]}))
            (docs/'clothing_classification.json').write_text(json.dumps({'diagnostic_component_labels':{'shirt_region':0}}))
            (docs/'finger_tracks.json').write_text(json.dumps({'sides':{}}))
            (docs/'coordinate_frame.json').write_text(json.dumps(dict(rotation_columns_world=np.eye(3).tolist(),
                origin_body_coordinates_cm=[0,0,0],factor=1.,handedness_determinant=1.)))
            fit=b.core.read(docs/'current_proposal.json');fit['input_geometry_sha256']=b.core.file_sha(work/'normalised_geometry.npz')
            (docs/'current_proposal.json').write_text(json.dumps(fit))
            review=b.core.read(docs/'human_review.json');review['proposal_sha256']=b.core.file_sha(docs/'current_proposal.json')
            (docs/'human_review.json').write_text(json.dumps(review))
            before={str(p):b.core.file_sha(p) for p in root.rglob('*') if p.is_file()}
            checks=[dict(name='surface_envelope_pelvis',kind='hard',measured={},**{'pass':True})]
            migration=b.shared.apply_policy(checks,fit,work,docs,b.core)
            self.assertIsNone(migration['source_error'])
            self.assertEqual(b.verified_source_ground(docs,migration),0.)
            self.assertEqual(b.audit_human(work,docs)['confirmed_roles'],['pelvis'])
            self.assertEqual(before,{str(p):b.core.file_sha(p) for p in root.rglob('*') if p.is_file()})

    def test_valid_review_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);work,docs=human_fixture(root)
            before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
            a=b.audit_human(work,docs)
            self.assertEqual(a['confirmed_roles'],['pelvis']);self.assertEqual(a['event_count'],1)
            self.assertEqual(before,{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()})

    def test_moved_root_invalidates_signature(self):
        with tempfile.TemporaryDirectory() as d:
            work,docs=human_fixture(Path(d));s=b.core.read(work/'session.json');s['joints'][0]['position_cm'][0]=1
            (work/'session.json').write_text(json.dumps(s))
            with self.assertRaises(ValueError):b.audit_human(work,docs)

    def test_changed_immutable_event_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            work,docs=human_fixture(Path(d));(work/'InteractionEvidence/event_00001.json').write_text('{}')
            with self.assertRaises(ValueError):b.audit_human(work,docs)

    def test_missing_event_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            work,docs=human_fixture(Path(d));(work/'InteractionEvidence/event_00001.json').unlink()
            with self.assertRaises(ValueError):b.audit_human(work,docs)

    def test_stale_proposal_signature_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            work,docs=human_fixture(Path(d));r=b.core.read(docs/'human_review.json');r['proposal_sha256']='bad'
            (docs/'human_review.json').write_text(json.dumps(r))
            with self.assertRaises(ValueError):b.audit_human(work,docs)

    def test_forged_approval_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            work,docs=human_fixture(Path(d));s=b.core.read(work/'session.json');s['approvals']['pelvis']['provenance']='automatic'
            (work/'session.json').write_text(json.dumps(s))
            with self.assertRaises(ValueError):b.audit_human(work,docs)

    def test_orphan_review_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            work,docs=human_fixture(Path(d));s=b.core.read(work/'session.json');s['approvals']={}
            (work/'session.json').write_text(json.dumps(s))
            with self.assertRaises(ValueError):b.audit_human(work,docs)

    def test_source_semantic_wrong_hash_rejected(self):
        s=pose_source();doc=dict(schema_version=1,geometry_sha256='wrong',evidence_sha256='evidence',
                                derivation='independent_source_semantic_regions',regions=s.regions)
        with self.assertRaises(ValueError):b.SourceRegions(s.v,s.f,doc,'geometry','evidence')

    def test_source_ownership_overlap_rejected(self):
        s=pose_source();doc=dict(schema_version=1,geometry_sha256='geometry',evidence_sha256='evidence',
                                derivation='independent_source_semantic_regions',regions=copy.deepcopy(s.regions))
        doc['regions']['hand_r']['triangle_ids']=doc['regions']['hand_l']['triangle_ids']
        with self.assertRaises(ValueError):b.SourceRegions(s.v,s.f,doc,'geometry','evidence')

    def test_ambiguous_source_not_certificate(self):
        s=regions(dict(hand_l=patch_at(15),hand_r=patch_at(-15)),ambiguous=['hand_l'])
        self.assertEqual(b.pose_checks(dict(hand_l=[15,0,5],hand_r=[-15,0,5]),s)[1]['status'],b.NON_CERTIFYING)


if __name__=='__main__':unittest.main()
