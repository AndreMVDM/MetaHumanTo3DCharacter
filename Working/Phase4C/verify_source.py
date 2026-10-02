import bpy,json,hashlib,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4C';O=P/'Documentation/Phase4C'
bpy.ops.wm.open_mainfile(filepath=str(W/'source_working.blend'))
ob=next(x for x in bpy.context.scene.objects if x.type=='MESH');v=np.array([list(ob.matrix_world@x.co) for x in ob.data.vertices])*100
uv=np.array([list(x.uv) for x in ob.data.uv_layers[0].data]);polys=[list(x.vertices) for x in ob.data.polygons]
before=json.loads((O/'geometry_input.json').read_text());r={'verified_by':'Fresh Blender reload after solve; retained original world geometry, polygon topology and UV arrays',
 'vertices_unchanged':hashlib.sha256(v.tobytes()).hexdigest()==before['vertex_sha256'],
 'uv_unchanged':hashlib.sha256(uv.tobytes()).hexdigest()==before['uv_sha256'],
 'polygon_topology_unchanged':hashlib.sha256(json.dumps(polys).encode()).hexdigest()==before['faces_sha256'],
 'armature_count':len([x for x in bpy.context.scene.objects if x.type=='ARMATURE']), 'vertex_group_count':len(ob.vertex_groups),
 'material_names':[x.name for x in ob.data.materials], 'archive_entries_byte_identical':True}
inv=json.loads((O/'input_inventory.json').read_text())
for row in inv['entries']:
    r['archive_entries_byte_identical'] &= hashlib.sha256((W/'Inputs'/row['name']).read_bytes()).hexdigest()==row['sha256']
r['passed']=all(r[k] for k in ['vertices_unchanged','uv_unchanged','polygon_topology_unchanged','archive_entries_byte_identical']) and r['armature_count']==0 and r['vertex_group_count']==0
(O/'source_preservation.json').write_text(json.dumps(r,indent=2));assert r['passed'];print('SOURCE_PRESERVATION',r)
