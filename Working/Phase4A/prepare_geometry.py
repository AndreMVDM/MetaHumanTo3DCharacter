import bpy,json,hashlib,sys,argparse,numpy as np
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');W=P/'Working/Phase4A';O=P/'Documentation/Phase4A'
args=argparse.ArgumentParser();args.add_argument('--height',type=float,default=180);opt=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert 20<=opt.height<=300
def h(x):return hashlib.sha256(np.asarray(x).tobytes()).hexdigest()
rows=[];raw=[]
for case in ['MixamoRecovered','Unrigged']:
    bpy.ops.wm.read_factory_settings(use_empty=True);fbx=next((W/'Inputs'/case).glob('*.fbx'));bpy.ops.import_scene.fbx(filepath=str(fbx),automatic_bone_orientation=False)
    meshes=[x for x in bpy.context.scene.objects if x.type=='MESH'];assert len(meshes)==1;ob=meshes[0];me=ob.data
    vs=np.array([list(ob.matrix_world@v.co) for v in me.vertices]);faces=[list(p.vertices) for p in me.polygons];uvs=np.array([list(l.uv) for u in me.uv_layers for l in u.data]);raw.append((vs,faces,uvs))
    row={'case':case,'source':str(fbx),'vertices':len(vs),'polygons':len(faces),'triangles':sum(len(f)-2 for f in faces),'uv_layers':len(me.uv_layers),'uv_loop_count':len(uvs),'uv_sha256':h(uvs),'face_index_sha256':hashlib.sha256(json.dumps(faces).encode()).hexdigest(),'materials':[m.name for m in me.materials],'bounds_metres':{'min':vs.min(0).tolist(),'max':vs.max(0).tolist()},'armatures':sum(x.type=='ARMATURE' for x in bpy.context.scene.objects),'vertex_groups_before':len(ob.vertex_groups),'modifiers_before':[m.type for m in ob.modifiers]}
    row['source_height_cm']=float(np.ptp(vs[:,2])*100);row['height_requested_cm']=opt.height;factor=opt.height/row['source_height_cm'];row['uniform_factor']=factor
    # Recover raw reference geometry; do not evaluate or carry the source armature modifier.
    ob.parent=None;ob.matrix_world.identity();ob.modifiers.clear();ob.vertex_groups.clear()
    scaled=(vs-vs.min(0)*np.array([0,0,1]))*100*factor
    for v,co in zip(me.vertices,scaled):v.co=co
    for x in list(bpy.context.scene.objects):
        if x!=ob:bpy.data.objects.remove(x,do_unlink=True)
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=0.01
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    dest=W/'Geometry'/case;dest.mkdir(parents=True,exist_ok=True)
    for im in bpy.data.images:
        if im.source=='FILE':
            match=list((W/'Inputs'/case).rglob(Path(im.filepath).name))
            if match:im.filepath=str(match[0])
    out=dest/'Lara_Geometry.fbx';bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',global_scale=1,axis_forward='-Y',axis_up='Z',bake_anim=False,path_mode='ABSOLUTE',use_mesh_modifiers=False,mesh_smooth_type='FACE')
    row.update({'export':str(out),'height_output_cm':float(np.ptp(scaled[:,2])),'uv_sha256_after':h(np.array([list(l.uv) for u in me.uv_layers for l in u.data])),'vertex_groups_after':len(ob.vertex_groups),'modifiers_after':[m.type for m in ob.modifiers],'vertex_positions_cm':scaled.tolist(),'faces':faces,'uv_loops':uvs.tolist()})
    (W/(case+'_geometry.json')).write_text(json.dumps(row),encoding='utf-8');bpy.ops.wm.save_as_mainfile(filepath=str(dest/'Lara_Geometry.blend'));rows.append({k:v for k,v in row.items() if k not in ['vertex_positions_cm','faces','uv_loops']})
comparison={'cases':rows,'vertex_count_equal':len(raw[0][0])==len(raw[1][0]),'face_indices_identical':raw[0][1]==raw[1][1]}
if len(raw[0][0])==len(raw[1][0]):comparison['index_matched_max_world_distance_cm']=float(np.linalg.norm((raw[0][0]-raw[1][0])*100,axis=1).max())
(O/'geometry_comparison.json').write_text(json.dumps(comparison,indent=2),encoding='utf-8');print('PHASE4A_GEOMETRY_DONE',json.dumps(comparison))
