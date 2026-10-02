"""Owned body-region controls plus unchanged v2 human/finger safeguard suite."""
import copy,json,sys,unittest,tempfile,shutil
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
import body_region_support as body
import geometry_support_policy_v3 as policy
import geometry_support_policy as v2
import apose_review_core as core
from test_geometry_support_policy import extrude,RegressionControls as V2Controls

SQUARE=[[-3,-2],[3,-2],[3,2],[-3,2]]
def supported(mesh,p=(0.,0.,2.),orientation=1.,binding=None):
    if binding is None:binding={'role':'torso_test','garment_groups':['shirt'],'source_components':[]}
    return body.evaluate(mesh,p,orientation,policy.POLICY,binding)
def seam(gap=.4,extra=None,provenance=None):
    lines=[[[-gap/2,2],[-3,2],[-3,-2],[-gap/2,-2]],[[gap/2,-2],[3,-2],[3,2],[gap/2,2]]]
    if extra is not None:lines.append(extra)
    return extrude(lines,provenance=provenance)
def one_owner(mesh):
    mesh.components[:]=0;mesh.provenance={0:('source','cloth')};mesh.garments={0:'shirt'}
    return mesh

class RegionControls(unittest.TestCase):
    def test_closed_owned_source(self):
        passed,r=supported(extrude([SQUARE],closed=True));self.assertTrue(passed)
        self.assertTrue(r['containing_regions'][0]['source_triangle_ids'])
        self.assertTrue(r['containing_regions'][0]['source_sheet_ids'])
        for s in r['source_section_records']:
            self.assertEqual(len(s['raw_vertex_ids']),3);self.assertEqual(len(s['normal']),3);self.assertIsNotNone(s['provenance'])

    def test_valid_directional_seam(self):
        passed,r=supported(seam());self.assertTrue(passed);self.assertEqual(len(r['seam_bridges']),2)

    def test_open_seam_and_genuine_opening(self):
        self.assertFalse(supported(extrude([SQUARE[:-1]]))[0])
        mesh=seam();mesh.garments={};self.assertFalse(supported(mesh)[0])

    def test_oversized_gap(self):self.assertFalse(supported(seam(1.))[0])

    def test_ambiguous_reciprocal_match(self):
        self.assertFalse(supported(seam(extra=[[-.1,2.1],[.1,2.1]]))[0])

    def test_incompatible_provenance_and_wrong_garment(self):
        self.assertFalse(supported(seam(provenance={0:('mesh','cloth'),1:('mesh','skin')}))[0])
        mesh=seam();mesh.garments={0:'shirt',1:'trouser'};self.assertFalse(supported(mesh)[0])

    def test_missing_provenance(self):
        mesh=extrude([SQUARE],closed=True);mesh.provenance={};self.assertFalse(supported(mesh)[0])

    def test_directionally_inconsistent_seam(self):
        mesh=seam();ids=np.where(mesh.components[mesh.f[:,0]]==1)[0];mesh.f[ids]=mesh.f[ids,::-1];mesh.tri=mesh.v[mesh.f]
        passed,r=supported(mesh);self.assertFalse(passed);self.assertTrue(r['seam_rejections'])

    def test_dangling_fold_owned_closed_boundary(self):
        mesh=one_owner(extrude([SQUARE+[SQUARE[0]],[[3,2],[5,3]]]))
        passed,r=supported(mesh);self.assertTrue(passed);self.assertGreater(sum(a['unused_noncycle_edges'] for a in r['ownership_arrangements']),0)

    def test_tail_cannot_fill_missing_boundary(self):
        mesh=one_owner(extrude([SQUARE[:-1],[[3,2],[5,3]]]))
        mesh.garments={};self.assertFalse(supported(mesh)[0])

    def test_opposed_coincident_boundary_is_ambiguous(self):
        mesh=one_owner(extrude([SQUARE,list(reversed(SQUARE))],closed=True))
        passed,r=supported(mesh);self.assertFalse(passed)
        self.assertTrue(any(a['ambiguous_coincident_edges'] for a in r['ownership_arrangements']))

    def test_duplicate_same_direction_multiplicity_retained(self):
        mesh=one_owner(extrude([SQUARE,SQUARE],closed=True));passed,r=supported(mesh);self.assertTrue(passed)
        self.assertGreater(len(r['containing_regions'][0]['source_triangle_ids']),8)

    def test_nested_filled_layers(self):
        mesh=extrude([SQUARE,[[-1,-1],[1,-1],[1,1],[-1,1]]],closed=True)
        mesh.garments[1]='shirt'
        mesh.garments[1]='shirt'
        passed,r=supported(mesh);self.assertTrue(passed);self.assertEqual(len(r['containing_regions']),2)

    def test_owned_cavity_explicit_hole(self):
        mesh=one_owner(extrude([SQUARE,[[-1,-1],[-1,1],[1,1],[1,-1]]],closed=True))
        self.assertFalse(supported(mesh)[0]);passed,r=supported(mesh,(2.,0.,2.));self.assertTrue(passed)
        self.assertTrue(r['containing_regions'][0]['hole_boundaries_xy_cm'])

    def test_filled_island_inside_owned_cavity(self):
        mesh=one_owner(extrude([SQUARE,[[-1,-1],[-1,1],[1,1],[1,-1]],[[-.5,-.5],[.5,-.5],[.5,.5],[-.5,.5]]],closed=True))
        self.assertTrue(supported(mesh)[0]);self.assertFalse(supported(mesh,(.75,0.,2.))[0])

    def test_disconnected_nested_inward_shell_not_filled(self):
        mesh=extrude([SQUARE,[[-1,-1],[-1,1],[1,1],[1,-1]]],closed=True)
        passed,r=supported(mesh);self.assertFalse(passed);self.assertTrue(r['cavity_veto'])

    def test_cavity_no_external_allowance(self):
        mesh=one_owner(extrude([SQUARE,[[-1,-1],[-1,1],[1,1],[1,-1]]],closed=True))
        self.assertFalse(supported(mesh,(.99,0.,2.))[0])

    def test_overlapping_filled_owned_loops(self):
        mesh=one_owner(extrude([SQUARE,[[0,-1],[4,-1],[4,1],[0,1]]],closed=True))
        self.assertTrue(supported(mesh,(1.,0.,2.))[0])

    def test_independently_closed_loop_survives_intersecting_unused_fold(self):
        mesh=one_owner(extrude([SQUARE,[[2,-1],[2,1],[4,1],[4,-1]]],closed=True))
        self.assertTrue(supported(mesh)[0])

    def test_boot_overlap_closes_without_large_gap_links(self):
        lower=[[-3,.5],[-3,-2],[3,-2],[3,.5]];upper=[[3,-.5],[3,2],[-3,2],[-3,-.5]]
        mesh=one_owner(extrude([lower,upper]));mesh.garments={}
        passed,r=supported(mesh,binding={'role':'foot_test','garment_groups':[],'source_components':[0]})
        self.assertTrue(passed);self.assertFalse(r['seam_bridges'])

    def test_closed_accessory_without_role_binding_rejected(self):
        mesh=extrude([SQUARE],closed=True);mesh.garments={}
        self.assertFalse(body.evaluate(mesh,[0.,0.,2.],1.,policy.POLICY)[0])
        self.assertFalse(supported(mesh)[0])

    def test_closed_wrong_garment_or_opposite_boot_rejected(self):
        mesh=extrude([SQUARE],closed=True);mesh.garments={0:'opposite_boot'}
        self.assertFalse(supported(mesh)[0])
        mesh.garments={0:'trouser'};self.assertFalse(supported(mesh)[0])

    def test_foot_association_requires_both_named_landmarks_and_side(self):
        mesh=extrude([[[1,-2],[7,-2],[7,2],[1,2]]],closed=True);mesh.garments={}
        joints={'foot_l':{'position_cm':[4.,0.,2.]},'ball_l':{'position_cm':[20.,0.,1.]}}
        ownership=[{'family':'footwear','side':'l','components':[0]}]
        binding=policy.role_binding(mesh,'foot_l',joints,{},ownership)
        self.assertFalse(supported(mesh,(4.,0.,2.),binding=binding)[0])
        joints['ball_l']['position_cm']=[5.,0.,1.];binding=policy.role_binding(mesh,'foot_l',joints,{},ownership)
        self.assertTrue(supported(mesh,(4.,0.,2.),binding=binding)[0])
        joints={'foot_r':{'position_cm':[4.,0.,2.]},'ball_r':{'position_cm':[5.,0.,1.]}}
        self.assertFalse(policy.role_binding(mesh,'foot_r',joints,{},ownership)['source_components'])

    def test_closed_accessory_with_both_foot_landmarks_still_rejected(self):
        mesh=extrude([[[1,-3],[9,-3],[9,3],[1,3]]],closed=True);mesh.garments={}
        joints={'foot_l':{'position_cm':[4.,0.,2.]},'ball_l':{'position_cm':[6.,0.,1.]}}
        binding=policy.role_binding(mesh,'foot_l',joints,{})
        self.assertFalse(supported(mesh,(4.,0.,2.),binding=binding)[0])

    def test_ownership_geometry_evidence_and_frame_binding_fail_closed(self):
        core.configure('John');fit=core.read(core.O/'current_proposal.json')
        for mutation in ['source_hash','evidence_hash','frame','duplicate_owner']:
            with tempfile.TemporaryDirectory() as temporary:
                docs=Path(temporary)
                for name in ['geometry_summary.json','clothing_classification.json','coordinate_frame.json','body_region_ownership.json','finger_tracks.json']:
                    shutil.copyfile(core.O/name,docs/name)
                path=docs/('coordinate_frame.json' if mutation=='frame' else 'body_region_ownership.json');data=json.loads(path.read_text())
                if mutation=='source_hash':data['normalised_geometry_sha256']='invalid'
                elif mutation=='evidence_hash':data['evidence_sha256']='invalid'
                elif mutation=='duplicate_owner':data['regions'].append(copy.deepcopy(data['regions'][0]))
                else:data['rotation_columns_world'][0][0]=-data['rotation_columns_world'][0][0];data['handedness_determinant']=-data['handedness_determinant']
                path.write_text(json.dumps(data))
                checks=[{'name':'surface_envelope_foot_l','pass':True,'kind':'hard'}]
                migration=policy.apply_policy(checks,fit,core.W,docs,core)
                self.assertFalse(checks[0]['pass']);self.assertIsNotNone(migration['source_error'])

    def test_intersecting_inward_shell_ownership_rejected(self):
        mesh=one_owner(extrude([SQUARE,[[-4,-1],[-4,1],[1,1],[1,-1]]],closed=True))
        self.assertFalse(supported(mesh)[0])

    def test_intersecting_inward_shell_separate_component_rejected(self):
        mesh=extrude([SQUARE,[[-4,-1],[-4,1],[1,1],[1,-1]]],closed=True)
        self.assertFalse(supported(mesh)[0])

    def test_uncertain_nested_shell_orientation_rejected(self):
        mesh=extrude([SQUARE,[[-1,-1],[-1,1],[1,1],[1,-1]]],closed=True)
        tid=int(np.where(mesh.components[mesh.f[:,0]]==1)[0][0]);mesh.f[tid]=mesh.f[tid,::-1];mesh.tri=mesh.v[mesh.f]
        self.assertFalse(supported(mesh)[0])

    def test_boot_almost_touching_real_gap_fails(self):
        lower=[[-3,-.1],[-3,-2],[3,-2],[3,-.1]];upper=[[3,.1],[3,2],[-3,2],[-3,.1]]
        mesh=one_owner(extrude([lower,upper]));mesh.garments={};self.assertFalse(supported(mesh)[0])

    def test_unrelated_open_components_and_accessory_cannot_make_cell(self):
        lower=[[-3,.5],[-3,-2],[3,-2],[3,.5]];upper=[[3,-.5],[3,2],[-3,2],[-3,-.5]]
        mesh=extrude([lower,upper]);mesh.garments={};self.assertFalse(supported(mesh)[0])

    def test_satellite_chain_cannot_accumulate_reconstruction(self):
        # Middle satellite terminals would have to match another unanchored
        # satellite, rather than bind directly to the same principal garment.
        mesh=extrude([[[-.2,2],[-3,2],[-3,-2],[-.2,-2]],[[.2,-2],[3,-2],[3,1.2]],[[3,1.6],[3,2],[.2,2]]])
        self.assertFalse(supported(mesh)[0])

    def test_concavity_not_bounding_box(self):
        mesh=extrude([[[-3,-3],[3,-3],[3,3],[1,3],[1,-1],[-1,-1],[-1,3],[-3,3]]],closed=True)
        self.assertFalse(supported(mesh,(0.,2.,2.))[0]);self.assertTrue(supported(mesh,(2.,2.,2.))[0])

    def test_existing_external_placement_allowance(self):
        mesh=extrude([SQUARE],closed=True)
        self.assertTrue(supported(mesh,(3.79,0.,2.))[0]);self.assertFalse(supported(mesh,(3.81,0.,2.))[0])

    def test_exact_plane_vertices_edges_and_end_planes(self):
        mesh=extrude([SQUARE],closed=True,levels=(0.,2.,4.))
        for z in [0.,2.,4.]:self.assertTrue(supported(mesh,(0.,0.,z))[0])

    def test_exact_endpoint_contact(self):
        mesh=one_owner(extrude([SQUARE+[SQUARE[0]],[[0,2],[0,4]]]))
        self.assertTrue(supported(mesh)[0])

    def test_collinear_overlap_retains_source_ids(self):
        mesh=one_owner(extrude([SQUARE+[SQUARE[0]],[[3,-1],[3,1]]]))
        passed,r=supported(mesh);self.assertTrue(passed)
        ids={s['triangle_id'] for s in r['source_section_records']}
        self.assertTrue(ids)

    def test_tiny_real_gap_not_numerical_snap(self):
        mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2],[-3,-1.99999]]]);mesh.garments={}
        self.assertFalse(supported(mesh)[0])

    def test_missing_or_inconsistent_orientation(self):
        mesh=extrude([SQUARE],closed=True);self.assertFalse(supported(mesh,orientation=0.)[0])
        mesh.f[0]=mesh.f[0,::-1];mesh.tri=mesh.v[mesh.f];self.assertFalse(supported(mesh)[0])

    def test_reflected_source_frame_preserves_normals(self):
        mesh=extrude([SQUARE],closed=True);mesh.v[:,1]*=-1;mesh.tri=mesh.v[mesh.f]
        self.assertTrue(supported(mesh,orientation=-1.)[0]);self.assertFalse(supported(mesh)[0])

    def test_retessellation_and_component_renumbering(self):
        mesh=extrude([SQUARE],closed=True);verts=mesh.v.tolist();faces=[]
        for f in mesh.f:
            k=len(verts);verts.append(mesh.v[f].mean(0).tolist())
            faces.extend([[int(f[0]),int(f[1]),k],[int(f[1]),int(f[2]),k],[int(f[2]),int(f[0]),k]])
        changed=v2.SourceSupport(np.array(verts),np.array(faces),np.full(len(verts),987),{987:('source','cloth')},{987:'shirt'})
        self.assertTrue(supported(changed)[0]);self.assertTrue(supported(mesh)[0])

    def test_current_body_approval_and_moved_landmark(self):
        core.configure('John');state=core.read(core.W/'session.json')
        for n,a in state['approvals'].items():self.assertEqual(a['signature'],core.review_signature(state,n))
        altered=copy.deepcopy(state);joint=next(j for j in altered['joints'] if j['role']=='thigh_r');joint['position_cm'][0]+=.01
        self.assertNotEqual(altered['approvals']['thigh_r']['signature'],core.review_signature(altered,'thigh_r'))

    def test_persisted_event_and_review_binding_current(self):
        core.configure('John');state=core.read(core.W/'session.json');review=core.read(core.O/'human_review.json')
        self.assertEqual(review['proposal_sha256'],core.file_sha(core.O/'current_proposal.json'))
        for e in state['events']:self.assertEqual(e,core.read(core.W/'InteractionEvidence'/f"event_{e['id']:05}.json"))
        for a in list(review['roles'].values())+list(review['fingers'].values()):self.assertEqual(a['evidence_sha256'],core.file_sha(Path(a['evidence_artifact'])))

    def test_changed_identity_or_approval_is_not_accepted(self):
        core.configure('John');fit=core.read(core.O/'current_proposal.json');review=core.read(core.O/'human_review.json')
        chain=copy.deepcopy(fit['finger_chains']['index_l']);approval=review['fingers']['index_l'];chain['digit']='middle'
        self.assertFalse(policy.finger_approval_current(core,chain,approval,'index_l',core.W))
        bad=copy.deepcopy(approval);bad['evidence_sha256']='invalid'
        self.assertFalse(policy.finger_approval_current(core,fit['finger_chains']['index_l'],bad,'index_l',core.W))

    def test_open_volume_not_certified_by_winding_or_finite_rays(self):
        mesh=extrude([SQUARE[:-1]]);mesh.garments={};passed,r=supported(mesh)
        self.assertFalse(passed);self.assertFalse(r['three_dimensional_fallback'])

    def test_finite_ray_false_positive_with_small_open_slit(self):
        from diagnose_john_geometry import ray_hits
        mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2],[-3,-1.99999]]]);mesh.garments={}
        rays=[np.array([np.cos(a),np.sin(a),0.]) for a in np.linspace(0,2*np.pi,16,endpoint=False)]
        self.assertTrue(all(ray_hits(np.array([0.,0.,2.]),r,mesh.tri) for r in rays))
        self.assertFalse(supported(mesh)[0])

    def test_open_cube_high_winding_is_not_volume_certificate(self):
        from diagnose_body_topology import winding
        mesh=extrude([SQUARE],closed=True)
        # Remove one whole side. Retain the caps; source winding remains high.
        f=mesh.f[2:];open_mesh=v2.SourceSupport(mesh.v,f,mesh.components,mesh.provenance,mesh.garments)
        open_mesh.garments={};value=winding(np.array([0.,0.,2.]),open_mesh.tri)
        self.assertGreater(value,.5);self.assertFalse(supported(open_mesh)[0])

if __name__=='__main__':
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(V2Controls),unittest.defaultTestLoader.loadTestsFromTestCase(RegionControls)])
    names=[t.id() for group in suite for t in group]
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    output=Path(__file__).resolve().parents[2]/'Documentation/Phase4F/JohnLocalRegionPolicy/regression_results.json'
    output.write_text(json.dumps({'version':policy.POLICY['version'],'tests_run':result.testsRun,'controls':names,'successful':result.wasSuccessful(),
                                  'failures':[str(t) for t,_ in result.failures],'errors':[str(t) for t,_ in result.errors]},indent=2))
    sys.exit(0 if result.wasSuccessful() else 1)
