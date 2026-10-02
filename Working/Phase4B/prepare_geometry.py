"""Fresh ZIP working copy -> world surface. No Phase4A data or joint imports."""
import bpy,json,hashlib,zipfile,sys
import numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[2];W=P/'Working/Phase4B';O=P/'Documentation/Phase4B';dest=W/'Inputs';dest.mkdir(exist_ok=True)
archive=P/'Characters/Lara_UnRigged_Textured.zip'
with zipfile.ZipFile(archive) as z:
    for entry in z.infolist():
        path=(dest/entry.filename).resolve();assert path.is_relative_to(dest.resolve())
        if not entry.is_dir():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(entry))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(dest/'Lara_UnRigged_Textured.fbx'),automatic_bone_orientation=False)
meshes=[x for x in bpy.context.scene.objects if x.type=='MESH'];assert len(meshes)==1
ob=meshes[0];assert not ob.vertex_groups and not any(x.type=='ARMATURE' for x in bpy.context.scene.objects)
v=np.array([list(ob.matrix_world@x.co) for x in ob.data.vertices])*100
ob.data.calc_loop_triangles();tris=np.array([list(x.vertices) for x in ob.data.loop_triangles])
uv=np.array([list(x.uv) for x in ob.data.uv_layers[0].data]);polys=[list(x.vertices) for x in ob.data.polygons]
np.savez(W/'source_geometry.npz',vertices=v,triangles=tris,uv_loops=uv)
info={'source':'Authoritative ZIP, fresh Phase4B extraction','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'vertices':len(v),'triangles':len(tris),'polygons':len(polys),'uv_loops':len(uv),'vertex_sha256':hashlib.sha256(v.tobytes()).hexdigest(),'uv_sha256':hashlib.sha256(uv.tobytes()).hexdigest(),'faces_sha256':hashlib.sha256(json.dumps(polys).encode()).hexdigest(),'raw_world_bounds_cm':[v.min(0).tolist(),v.max(0).tolist()],'coordinate_semantics':'DCC world cm only; fitter must infer body frame from surface','materials':[x.name for x in ob.data.materials]}
(O/'geometry_input.json').write_text(json.dumps(info,indent=2))
for im in bpy.data.images:
    if im.source=='FILE':
        matches=list(dest.rglob(Path(im.filepath).name))
        if matches:im.filepath=str(matches[0])
bpy.ops.wm.save_as_mainfile(filepath=str(W/'source_working.blend'))
print('PHASE4B_SOURCE',info)
