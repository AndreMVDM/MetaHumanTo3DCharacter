import bpy,json
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter')
for rig in ['UE5','Mixamo']:
    bpy.ops.wm.open_mainfile(filepath=str(next((P/'Working/Phase3B'/rig/'OriginalHeight').glob('*.blend'))))
    mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
    vs=[mesh.matrix_world@v.co for v in mesh.data.vertices]
    # UE importer uses X,-Y,Z relative to this Blender export.
    vertices=[[v.x,-v.y,v.z] for v in vs]
    weights=[[[mesh.vertex_groups[g.group].name.removeprefix('mixamorig:'),g.weight] for g in v.groups] for v in mesh.data.vertices]
    mesh.data.calc_loop_triangles();triangles=[list(t.vertices) for t in mesh.data.loop_triangles]
    (P/'Working/Phase3B'/('skin_'+rig+'.json')).write_text(json.dumps({'vertices_cm':vertices,'weights':weights,'triangles':triangles}))
