"""Synthetic rejection controls and exact persisted-evidence regression checks."""
import copy
import json
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
import geometry_support_policy as policy
import apose_review_core as core


def extrude(lines,closed=False,provenance=None,groups=None,levels=(0.,4.)):
    vertices=[];faces=[];components=[]
    for component,line in enumerate(lines):
        offset=len(vertices);n=len(line)
        vertices.extend([[x,y,z] for z in levels for x,y in line]);components.extend([component]*(len(levels)*n))
        for layer in range(len(levels)-1):
            start=offset+layer*n
            for i in range(n if closed else n-1):
                j=(i+1)%n
                faces.extend([[start+i,start+j,start+n+j],[start+i,start+n+j,start+n+i]])
        if closed:
            top=offset+(len(levels)-1)*n
            for i in range(1,n-1):faces.extend([[offset,offset+i+1,offset+i],[top,top+i,top+i+1]])
    return policy.SourceSupport(np.array(vertices,dtype=float),np.array(faces),np.array(components),
                                provenance or {i:('source','cloth') for i in range(len(lines))},groups or {0:'shirt'})


def seam_mesh(gap=.4,extra=None,provenance=None):
    lines=[[[-gap/2,2],[-3,2],[-3,-2],[-gap/2,-2]],[[gap/2,2],[3,2],[3,-2],[gap/2,-2]]]
    if extra:lines.append(extra)
    return extrude(lines,provenance=provenance)


def finger_fixture():
    angle=np.linspace(0,2*np.pi,16,endpoint=False)
    lines=[np.column_stack([x+2*np.cos(angle),2*np.sin(angle)]).tolist() for x in [3.,11.]]
    mesh=extrude(lines,closed=True,levels=(-2.,2.,6.))
    path=[[3.,0.,3.],[3.,0.,1.]]
    chain={'path_cm':path,'root_cm':path[0],'tip_cm':path[-1],'phalanges_cm':[[3.,0.,3.],[3.,0.,2.],[3.,0.,1.5]]}
    return mesh,chain,path


class RegressionControls(unittest.TestCase):
    def test_valid_closed_source(self):
        mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2]]],closed=True)
        self.assertTrue(mesh.body([0.,0.,2.])[0])

    def test_valid_closed_seam(self):
        mesh=seam_mesh();passed,evidence=mesh.body([0.,0.,2.])
        self.assertTrue(passed);self.assertEqual(len(evidence['seam_bridges']),2)
        self.assertTrue(evidence['containing_polygons'][0]['reconstructed'])

    def test_open_seam(self):
        mesh=extrude([[[-.2,2],[-3,2],[-3,-2],[-.2,-2]]])
        self.assertFalse(mesh.body([0.,0.,2.])[0])

    def test_single_fragment_bounded_seam(self):
        mesh=extrude([[[-.2,2],[-3,2],[-3,-2],[3,-2],[3,2],[.2,2]]])
        self.assertTrue(mesh.body([0.,0.,2.])[0])

    def test_oversized_gap(self):
        self.assertFalse(seam_mesh(gap=1.).body([0.,0.,2.])[0])

    def test_ambiguous_seam_match(self):
        self.assertFalse(seam_mesh(extra=[[-.1,2.1],[.1,2.1]]).body([0.,0.,2.])[0])

    def test_incompatible_garment_provenance(self):
        mesh=seam_mesh(provenance={0:('source','cloth'),1:('source','skin')})
        self.assertFalse(mesh.body([0.,0.,2.])[0])
        mesh=seam_mesh();mesh.garments={0:'shirt',1:'trousers'}
        self.assertFalse(mesh.body([0.,0.,2.])[0])

    def test_unanchored_source_cannot_reconstruct(self):
        mesh=seam_mesh();mesh.garments={}
        self.assertFalse(mesh.body([0.,0.,2.])[0])

    def test_branched_section(self):
        # A spur shares the outer boundary vertex, producing degree three.
        mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2],[-3,-2]],[[3,2],[4,3]]],closed=False)
        graph,_,_,_=mesh.sections(2.)
        self.assertTrue(any(len(v)==3 for v in graph.values()))
        self.assertFalse(mesh.body([0.,0.,2.])[0])

    def test_invalid_crossed_polygon(self):
        mesh=extrude([[[-3,-2],[3,2],[-3,2],[3,-2]]],closed=True)
        self.assertFalse(mesh.body([0.,0.,2.])[0])

    def test_concave_outline_outside_pivot(self):
        mesh=extrude([[[-3,-3],[3,-3],[3,3],[1,3],[1,-1],[-1,-1],[-1,3],[-3,3]]],closed=True)
        self.assertFalse(mesh.body([0.,2.,2.])[0])
        self.assertTrue(mesh.body([2.,2.,2.])[0])

    def test_existing_placement_allowance(self):
        mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2]]],closed=True)
        self.assertTrue(mesh.body([3.79,0.,2.])[0])
        self.assertFalse(mesh.body([3.81,0.,2.])[0])

    def test_exact_plane_vertex_and_coplanar_hits(self):
        mesh=extrude([[[-3,-2],[3,-2],[3,2],[-3,2]]],closed=True)
        for z in [0.,2.,4.]:
            with self.subTest(z=z):
                loops,_,_=mesh.loops(z);self.assertEqual(len(loops),1)
                self.assertTrue(mesh.body([0.,0.,z])[0])

    def test_interior_thick_finger(self):
        mesh,chain,path=finger_fixture();passed,result=mesh.finger(chain,path,path)
        self.assertTrue(passed,result['failures'])
        self.assertGreater(result['phalanges'][0]['nearest_vertex_cm'],1.2)
        self.assertGreater(result['phalanges'][0]['nearest_triangle']['distance_cm'],1.2)

    def test_exterior_near_surface(self):
        mesh,chain,path=finger_fixture();chain['phalanges_cm'][1]=[5.1,0.,2.]
        passed,result=mesh.finger(chain,path,path)
        self.assertFalse(passed);self.assertLess(result['phalanges'][1]['nearest_vertex_cm'],1.2)

    def test_wrong_digit_support(self):
        mesh,chain,path=finger_fixture();chain['phalanges_cm'][1]=[11.,0.,2.]
        self.assertFalse(mesh.finger(chain,path,path)[0])

    def test_open_finger_support(self):
        mesh,chain,path=finger_fixture()
        mesh=extrude([[[5,0],[3,2],[1,0],[3,-2]]],closed=False)
        self.assertFalse(mesh.finger(chain,path,path)[0])

    def test_ambiguous_finger_support(self):
        angle=np.linspace(0,2*np.pi,16,endpoint=False)
        lines=[np.column_stack([3+r*np.cos(angle),r*np.sin(angle)]).tolist() for r in [2.,2.5]]
        mesh=extrude(lines,closed=True,levels=(-2.,2.,6.));_,chain,path=finger_fixture()
        self.assertFalse(mesh.finger(chain,path,path)[0])

    def test_supported_centres_do_not_excuse_exterior_path(self):
        mesh=extrude([[[-3,-3],[3,-3],[3,3],[1,3],[1,-1],[-1,-1],[-1,3],[-3,3]]],closed=True)
        path=[[-2.,2.,3.],[2.,2.,1.]]
        chain={'path_cm':path,'root_cm':path[0],'tip_cm':path[-1],'phalanges_cm':path}
        passed,result=mesh.finger(chain,path,path)
        self.assertTrue(all(p['supported'] for p in result['phalanges']))
        self.assertFalse(passed);self.assertTrue(any('path_' in reason for reason in result['failures']))

    def test_path_alone_cannot_certify_support(self):
        mesh,chain,path=finger_fixture();outside=[[5.1,0.,3.],[5.1,0.,1.]]
        chain.update(path_cm=outside,root_cm=outside[0],tip_cm=outside[-1],phalanges_cm=outside)
        self.assertFalse(mesh.finger(chain,outside,outside)[0])

    def test_segment_exits_concave_source(self):
        mesh=extrude([[[-3,-3],[3,-3],[3,3],[1,3],[1,-1],[-1,-1],[-1,3],[-3,3]]],closed=True)
        self.assertTrue(mesh.segment_crosses(np.array([-2.,2.,2.]),np.array([2.,2.,2.]),{0}))

    def test_current_signature_swapped_track_and_moved_root(self):
        core.configure('John');fit=core.read(core.O/'current_proposal.json');review=core.read(core.O/'human_review.json')
        chain=fit['finger_chains']['index_l'];approval=review['fingers']['index_l']
        self.assertTrue(policy.finger_approval_current(core,chain,approval,'index_l',core.W))
        swapped=copy.deepcopy(chain);swapped['track_id']=fit['finger_chains']['middle_l']['track_id']
        self.assertFalse(policy.finger_approval_current(core,swapped,approval,'index_l',core.W))
        moved=copy.deepcopy(chain);moved['root_cm'][0]+=.01
        self.assertFalse(policy.finger_approval_current(core,moved,approval,'index_l',core.W))

    def test_inter_finger_collision(self):
        a=np.array([[3.,0.,3.],[3.,0.,1.]]);b=np.array([[3.,0.,3.],[3.,0.,1.]])
        self.assertLessEqual(policy.path_separation(core,a,b),.25)
        self.assertGreater(policy.path_separation(core,a,b+np.array([1.,0.,0.])),.25)

    def test_component_numbers_are_not_policy(self):
        mesh=seam_mesh();renamed=np.where(mesh.components==0,91,503)
        changed=policy.SourceSupport(mesh.v,mesh.f,renamed,{91:('source','cloth'),503:('source','cloth')},{91:'shirt'})
        self.assertTrue(changed.body([0.,0.,2.])[0])

    def test_changed_source_binding_fails_closed(self):
        core.configure('John');fit=copy.deepcopy(core.read(core.O/'current_proposal.json'));fit['input_geometry_sha256']='invalid'
        checks=[{'name':'surface_envelope_pelvis','pass':True,'kind':'hard'}]
        result=policy.apply_policy(checks,fit,core.W,core.O,core)
        self.assertFalse(checks[0]['pass']);self.assertIn('source_provenance_error',result)

    def test_missing_source_tracks_fail_closed(self):
        core.configure('John');fit=core.read(core.O/'current_proposal.json')
        with tempfile.TemporaryDirectory() as directory:
            docs=Path(directory)
            for name in ['geometry_summary.json','clothing_classification.json']:shutil.copyfile(core.O/name,docs/name)
            checks=[{'name':'finger_surface_index_l','pass':True,'kind':'hard'}]
            result=policy.apply_policy(checks,fit,core.W,docs,core)
            self.assertFalse(checks[0]['pass']);self.assertIsNotNone(result['source_tracks_error'])

    def test_nearest_triangle_diagnostics(self):
        tri=np.array([[[0.,0,0],[2.,0,0],[0.,2,0]]])
        for p,want in [([.5,.5,3],3),([1,1,0],0),([3,0,0],1),([-1,-1,0],np.sqrt(2))]:
            self.assertAlmostEqual(policy.nearest_triangle(np.array(p),tri)['distance_cm'],want)


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(RegressionControls)
    names=[test.id() for test in suite]
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    output=Path(__file__).resolve().parents[2]/'Documentation/Phase4F/JohnGeometryPolicyCorrection/regression_results.json'
    output.write_text(json.dumps({'policy_version':policy.POLICY['version'],'tests_run':result.testsRun,
                                  'controls':names,'successful':result.wasSuccessful(),'failures':[str(t) for t,_ in result.failures],
                                  'errors':[str(t) for t,_ in result.errors]},indent=2),encoding='utf-8')
    sys.exit(0 if result.wasSuccessful() else 1)
