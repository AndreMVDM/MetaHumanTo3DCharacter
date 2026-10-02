"""Read-only Blender UV readback into a NEW diagnosis artifact, no blend save."""
import json
import sys
from pathlib import Path
import bpy
import numpy as np
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2]
D=P/'Documentation/Phase4F/JohnBodySupportDiagnosis'
source=np.load(P/'Working/Phase4F/John/source_geometry.npz')
faces=[];uv=[];offset=0
for ob in [o for o in bpy.context.scene.objects if o.type=='MESH']:
    mesh=ob.data;mesh.calc_loop_triangles()
    for triangle in mesh.loop_triangles:
        faces.append(np.array(triangle.vertices)+offset)
        uv.append([list(mesh.uv_layers[0].data[i].uv) for i in triangle.loops])
    offset+=len(mesh.vertices)
assert np.array_equal(np.array(faces),source['triangles']), 'readback indexing does not match frozen source'
np.savez(D/'triangle_uv_readback.npz',triangle_uv=np.array(uv))
print('READ_ONLY_UV_READBACK',len(faces), 'no source or blend save')
