import bpy, json
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter')
out={}
for rig in ['UE5','Mixamo']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    src=next((P/'Working/Phase2'/rig).glob('*.fbx'))
    bpy.ops.import_scene.fbx(filepath=str(src),use_anim=False,automatic_bone_orientation=False)
    obs=[]
    for ob in bpy.context.scene.objects:
        item={'name':ob.name,'type':ob.type,'location':list(ob.location),'scale':list(ob.scale),'matrix_world':[list(r) for r in ob.matrix_world]}
        if ob.type=='MESH':
            vs=[ob.matrix_world@v.co for v in ob.data.vertices]
            item['bounds_cm']={'min':[min(v[i] for v in vs)*100 for i in range(3)],'max':[max(v[i] for v in vs)*100 for i in range(3)]}
            item['vertices']=len(vs);item['groups']=[g.name for g in ob.vertex_groups]
        if ob.type=='ARMATURE':item['bones']=[{'name':b.name,'parent':b.parent.name if b.parent else None,'head_cm':list((ob.matrix_world@b.head_local)*100),'tail_cm':list((ob.matrix_world@b.tail_local)*100)} for b in ob.data.bones]
        obs.append(item)
    out[rig]=obs
(P/'Documentation/Phase3B/dcc_probe.json').write_text(json.dumps(out,indent=2))
