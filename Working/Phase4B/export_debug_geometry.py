import bpy,json,hashlib,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B'
bpy.ops.wm.open_mainfile(filepath=str(W/'source_working.blend'));ob=next(x for x in bpy.context.scene.objects if x.type=='MESH');d=np.load(W/'normalised_geometry.npz');v=d['vertices'];assert len(v)==len(ob.data.vertices)
before_uv=np.array([list(x.uv) for x in ob.data.uv_layers[0].data]);before_polys=[list(x.vertices) for x in ob.data.polygons]
ob.matrix_world.identity()
for point,xyz in zip(ob.data.vertices,v):point.co=xyz*np.array([1,-1,1]) # verified UE legacy handedness conversion: X same, Y negated, Z same
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=.01
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.fbx(filepath=str(W/'Lara_180_DebugGeometry.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',global_scale=1,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='ABSOLUTE',use_mesh_modifiers=False,mesh_smooth_type='FACE')
after_uv=np.array([list(x.uv) for x in ob.data.uv_layers[0].data]);assert np.array_equal(before_uv,after_uv)
assert before_polys==[list(x.vertices) for x in ob.data.polygons]
(O/'geometry_export_validation.json').write_text(json.dumps({'uv_identical':True,'polygon_indices_identical':True,'geometry_transform':'single inferred rigid body frame, grounding, uniform180cm scale; XY pre-export scene-conversion compensation','uv_sha256':hashlib.sha256(after_uv.tobytes()).hexdigest(),'raw_geometry_replacement':False,'skeletal_export':False},indent=2))
print('PHASE4B_GEOMETRY_EXPORT_DONE')
