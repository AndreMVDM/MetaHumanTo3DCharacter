"""Uniform DCC authoring: transform mesh and rest skeleton together, preserve weights."""
import bpy, json, math, hashlib, argparse, sys
from mathutils import Matrix
from pathlib import Path
P=Path(r'E:/Repo/UE/Projects/MetaHumanTo3DCharacter');O=P/'Documentation/Phase3B';W=P/'Working/Phase3B'
args=argparse.ArgumentParser();args.add_argument('--heights',nargs='+',type=float,default=[160,175,180,200])
cfg=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert all(math.isfinite(h) and 20<=h<=300 for h in cfg.heights),'Experiment height range 20–300 cm'
results=[]
def vec(v):return [float(x) for x in v]
for rig in ['UE5','Mixamo']:
    for requested in [None]+cfg.heights:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        src=next((P/'Working/Phase2'/rig).glob('*.fbx'))
        bpy.ops.import_scene.fbx(filepath=str(src),use_anim=False,automatic_bone_orientation=False)
        arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
        vertices=[mesh.matrix_world@v.co for v in mesh.data.vertices]
        bones={b.name:{'parent':b.parent.name if b.parent else None,'head':arm.matrix_world@b.head_local,'matrix':arm.matrix_world@b.matrix_local} for b in arm.data.bones}
        head_name='head' if rig=='UE5' else 'mixamorig:Head';head=bones[head_name]['head']
        feet=['foot_l','ball_l','foot_r','ball_r'] if rig=='UE5' else ['mixamorig:'+s+b for s in ['Left','Right'] for b in ['Foot','ToeBase','Toe_End']]
        head_id=mesh.vertex_groups.find(head_name);foot_ids={mesh.vertex_groups.find(n) for n in feet}
        crown=[v for v,raw in zip(vertices,mesh.data.vertices) if sum(g.weight for g in raw.groups if g.group==head_id)>=0.5 and abs(v.x-head.x)<0.06 and abs(v.y-head.y)<0.08 and v.z>head.z]
        soles=[v for v,raw in zip(vertices,mesh.data.vertices) if sum(g.weight for g in raw.groups if g.group in foot_ids)>=0.5 and v.z<0.12]
        assert crown and soles,'Semantic vertex measurement failed'
        ground=min(v.z for v in soles);top=max(v.z for v in crown);height=(top-ground)*100
        factor=1.0 if requested is None else requested/height
        label='OriginalHeight' if requested is None else 'Height'+format(requested,'g').replace('.','p')
        dest=W/rig/label;dest.mkdir(parents=True,exist_ok=True)
        weights=[[ (mesh.vertex_groups[g.group].name,float(g.weight)) for g in v.groups ] for v in mesh.data.vertices]
        sums=[sum(w for n,w in gs) for gs in weights]
        weight_hash=hashlib.sha256(json.dumps(weights).encode()).hexdigest()
        # Repair only undefined weights. Existing influences are copied unchanged.
        source_weights=weights
        repairs=[]
        weighted=[i for i,s in enumerate(sums) if s>0]
        for index,s in enumerate(sums):
            if s>0:continue
            neighbour=min(weighted,key=lambda j:(vertices[j]-vertices[index]).length_squared)
            for name,weight in source_weights[neighbour]:mesh.vertex_groups[name].add([index],weight,'REPLACE')
            repairs.append({'vertex':index,'nearest_weighted_vertex':neighbour,'distance_cm':(vertices[neighbour]-vertices[index]).length*100,'assigned_influences':source_weights[neighbour]})
        weights=[[ (mesh.vertex_groups[g.group].name,float(g.weight)) for g in v.groups ] for v in mesh.data.vertices]
        assert all(a==b for a,b in zip(source_weights,weights) if a),'Existing source influences changed'
        # Blender works in metres here. Bake centimetre coordinates directly in mesh and rest armature.
        # Detach the mesh while preserving world space: scaling a parent AND its child doubles scale.
        worlds={ob:ob.matrix_world.copy() for ob in [arm,mesh]}
        for ob in [arm,mesh]:
            ob.parent=None
            ob.matrix_world=Matrix.Scale(100*factor,4)@worlds[ob]
        bpy.ops.object.select_all(action='DESELECT')
        for ob in [arm,mesh]:ob.select_set(True)
        bpy.context.view_layer.objects.active=arm
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=0.01
        bpy.context.view_layer.update()
        transformed=[mesh.matrix_world@v.co for v in mesh.data.vertices]
        geom_error=max((v-original*100*factor).length for v,original in zip(transformed,vertices))
        bone_error=max(((arm.matrix_world@arm.data.bones[n].head_local)-b['head']*100*factor).length for n,b in bones.items())
        hierarchy={b.name:b.parent.name if b.parent else None for b in arm.data.bones}
        assert hierarchy=={n:b['parent'] for n,b in bones.items()}
        weights_after=[[ (mesh.vertex_groups[g.group].name,float(g.weight)) for g in v.groups ] for v in mesh.data.vertices]
        assert weights==weights_after
        dg=bpy.context.evaluated_depsgraph_get();ev=mesh.evaluated_get(dg);evaluated=ev.to_mesh()
        bind_error=max(((ev.matrix_world@v.co)-p).length for v,p in zip(evaluated.vertices,transformed));ev.to_mesh_clear()
        assert geom_error<0.001 and bone_error<0.001 and bind_error<0.001,(geom_error,bone_error,bind_error)
        fbx=dest/('Lara_'+rig+'_'+label+'.fbx')
        bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1.0,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',add_leaf_bones=False,use_armature_deform_only=False,bake_anim=False,axis_forward='-Y',axis_up='Z',path_mode='AUTO',use_mesh_modifiers=False)
        blend=dest/('Lara_'+rig+'_'+label+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        results.append({'rig':rig,'label':label,'source_fbx':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'requested_height_cm':height if requested is None else requested,'measured_original_height_cm':height,'factor':factor,'raw_original_bounds_height_cm':(max(v.z for v in vertices)-min(v.z for v in vertices))*100,'ground_cm':ground*100,'crown_cm':top*100,'head_joint_cm':head.z*100,'measurement':'Head-weight >= 0.5, central 12x16 cm crown ROI; feet/toes-weight >= 0.5 sole below 12 cm, neutral imported pose. ROI determined before scaling. Hair cannot be segmented in unlabelled head surface.','vertex_count':len(vertices),'bone_count':len(bones),'hierarchy':hierarchy,'source_weight_sha256':weight_hash,'output_weight_sha256':hashlib.sha256(json.dumps(weights).encode()).hexdigest(),'existing_weights_unchanged':True,'weights_unchanged_by_scaling':True,'missing_weight_repairs':repairs,'source_min_weight_sum':min(sums),'max_weight_sum':max(sums),'source_unweighted_vertices':sum(s==0 for s in sums),'output_unweighted_vertices':sum(not gs for gs in weights),'max_influences':max(map(len,weights)),'max_geometry_uniform_error_cm':geom_error,'max_bone_uniform_error_cm':bone_error,'max_reference_deformation_error_cm':bind_error,'output_bounds_cm':{'min':[min(v[i] for v in transformed) for i in range(3)],'max':[max(v[i] for v in transformed) for i in range(3)]},'expected_anatomical_height_cm':height*factor,'fbx':str(fbx),'blend':str(blend),'export_options':{'unit_scale':0.01,'apply_scale_options':'FBX_SCALE_ALL','global_scale':1,'add_leaf_bones':False,'bake_anim':False},'fbx_sha256':hashlib.sha256(fbx.read_bytes()).hexdigest()})
        (O/'dcc_candidates.json').write_text(json.dumps(results,indent=2))
print('PHASE3B_DCC_DONE',len(results))
