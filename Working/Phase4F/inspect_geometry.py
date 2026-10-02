"""Fresh DCC readback, exact source arrays and topology; no rig or anatomy approval."""
import bpy, sys, json, hashlib
import numpy as np
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[2]; W=P/'Working/Phase4F'; O=P/'Documentation/Phase4F'
def components(vertices, triangles, tolerance=None):
    ids=np.arange(len(vertices))
    if tolerance is not None: _,ids=np.unique(np.round(vertices/tolerance).astype(np.int64),axis=0,return_inverse=True)
    parent=list(range(int(ids.max())+1))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]];x=parent[x]
        return x
    for tri in ids[triangles]:
        for b in tri[1:]:
            a=find(int(tri[0]));b=find(int(b));parent[b]=a
    roots=np.array([find(int(i)) for i in ids]); _,labels=np.unique(roots,return_inverse=True)
    return labels
for character in ['Lara','Bill','Jill']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fbx=list((W/'Inputs'/character).rglob('*.fbx')); assert len(fbx)==1
    bpy.ops.import_scene.fbx(filepath=str(fbx[0]),automatic_bone_orientation=False)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    rig=[o.name for o in bpy.context.scene.objects if o.type=='ARMATURE']
    allv=[];allt=[];uvs=[];mi=[];obs=[];offset=0
    for ob in meshes:
        mesh=ob.data;mesh.calc_loop_triangles()
        v=np.array([list(ob.matrix_world@p.co) for p in mesh.vertices])*100
        t=np.array([list(t.vertices) for t in mesh.loop_triangles],dtype=np.int64)
        u=np.array([list(p.uv) for p in mesh.uv_layers[0].data]) if mesh.uv_layers else np.empty((0,2))
        obs.append({'name':ob.name,'vertices':len(v),'polygons':len(mesh.polygons),'triangles':len(t),'edges':len(mesh.edges),
            'vertex_groups':list(ob.vertex_groups.keys()),'modifiers':[{'name':m.name,'type':m.type} for m in ob.modifiers],
            'matrix_world':[list(r) for r in ob.matrix_world],'bounds_world_cm':[v.min(0).tolist(),v.max(0).tolist()],
            'materials':[m.name if m else None for m in mesh.materials],
            'polygon_material_counts':{str(k):sum(p.material_index==k for p in mesh.polygons) for k in set(p.material_index for p in mesh.polygons)},
            'uv_layers':[{'name':l.name,'loops':len(l.data)} for l in mesh.uv_layers],
            'uv_bounds':[u.min(0).tolist(),u.max(0).tolist()] if len(u) else None,
            'uv_nonfinite':int((~np.isfinite(u)).sum()),'uv_sha256':hashlib.sha256(u.tobytes()).hexdigest()})
        allv.append(v);allt.append(t+offset);uvs.append(u);mi.extend([len(obs)-1]*len(t));offset+=len(v)
    v=np.concatenate(allv);t=np.concatenate(allt);u=np.concatenate(uvs)
    raw=components(v,t);weld=components(v,t,1e-5)
    shells=[]
    for k in np.unique(weld):
        ids=np.where(weld==k)[0];ts=np.where(weld[t[:,0]]==k)[0]
        shells.append({'id':int(k),'vertices':len(ids),'triangles':len(ts),'bounds_cm':[v[ids].min(0).tolist(),v[ids].max(0).tolist()],'object_ids':sorted(set(np.array(mi)[ts].tolist()))})
    shells.sort(key=lambda x:x['vertices'],reverse=True)
    images=[]
    for im in bpy.data.images:
        if im.source!='FILE':continue
        matches=list((W/'Inputs'/character).rglob(Path(im.filepath).name))
        if matches:im.filepath=str(matches[0]);im.reload()
        images.append({'name':im.name,'source_path':im.filepath,'resolved':bool(matches),'dimensions':list(im.size),'channels':im.channels,'colour_space':im.colorspace_settings.name})
    materials=[]
    for mat in bpy.data.materials:
        materials.append({'name':mat.name,'use_nodes':mat.use_nodes,'image_nodes':[{'node':n.name,'image':n.image.name if n.image else None} for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'] if mat.use_nodes else []})
    dst=W/character;dst.mkdir(exist_ok=True)
    np.savez(dst/'source_geometry.npz',vertices=v,triangles=t,uv_loops=u,weld_component=weld,raw_component=raw,object_triangle_ids=np.array(mi))
    result={'character':character,'blender_version':bpy.app.version_string,'source_fbx':str(fbx[0]),'objects':obs,'armatures':rig,
        'unrigged_verified':not rig and all(not o['vertex_groups'] and not any(m['type']=='ARMATURE' for m in o['modifiers']) for o in obs),
        'vertices':len(v),'triangles':len(t),'bounds_world_cm':[v.min(0).tolist(),v.max(0).tolist()],
        'coordinate_space':'Blender RH world centimetres; +Z is DCC up after importer axis conversion. Geometric pose/frame inspected separately.',
        'materials':materials,'images':images,'raw_connected_components':len(np.unique(raw)),'position_welded_components':len(shells),
        'diagnostic_weld_tolerance_cm':1e-5,'source_welded':False,'components':shells,
        'reference_pose':'Requires image and section inspection, no anatomical judgement inferred from FBX label.',
        'clothing_classification':'pending_connectivity_and_visual_review'}
    (O/f'{character.lower()}_geometry_summary.json').write_text(json.dumps(result,indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(dst/'source_working.blend'))
    print('GEOMETRY',character,len(v),len(t),len(shells),[(s['vertices'],s['bounds_cm']) for s in shells[:4]],flush=True)
