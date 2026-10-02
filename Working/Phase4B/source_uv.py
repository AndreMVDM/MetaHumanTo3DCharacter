import bpy,json,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';bpy.ops.wm.open_mainfile(filepath=str(W/'source_working.blend'));ob=next(x for x in bpy.context.scene.objects if x.type=='MESH');v=np.load(W/'normalised_geometry.npz')['vertices'];uv=ob.data.uv_layers[0].data
rows=[[*v[l.vertex_index],*uv[l.index].uv] for l in ob.data.loops]
(W/'normalised_source_uv_corners.json').write_text(json.dumps(rows));print('SOURCE_UV_CORNERS',len(rows))
